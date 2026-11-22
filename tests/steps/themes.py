"""Steps for 08-themes.feature."""
import json, re
from playwright.sync_api import expect
from steps.common import step, go_tab, open_hash, wait_ready, dialog, T, saved, btn, card
from steps import common, sync

LUM_JS = """
() => {
  const parse = c => { const m = c.match(/rgba?\\(([^)]+)\\)/); if (!m) return null; const p = m[1].split(',').map(x => parseFloat(x)); return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1}; };
  const lum = c => { const f = v => { v/=255; return v<=0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); }; return 0.2126*f(c.r)+0.7152*f(c.g)+0.0722*f(c.b); };
  const bgOf = el => { let layers = []; for (let e = el; e; e = e.parentElement) { const c = parse(getComputedStyle(e).backgroundColor); if (c && c.a > 0) { layers.push(c); if (c.a >= 1) break; } }
    let base = {r:0,g:0,b:0}; if (!layers.length || layers[layers.length-1].a < 1) { const b = parse(getComputedStyle(document.body).backgroundColor); base = b && b.a ? b : {r:0,g:0,b:0}; }
    for (let i = layers.length-1; i >= 0; i--) { const l = layers[i]; base = {r:l.r*l.a+base.r*(1-l.a), g:l.g*l.a+base.g*(1-l.a), b:l.b*l.a+base.b*(1-l.a)}; } return base; };
  const bad = [];
  const root = document.querySelector('.modal') || document.body;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    if (!n.textContent.trim()) continue;
    const el = n.parentElement; if (!el || seen.has(el)) continue; seen.add(el);
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) continue;
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
    if (el.closest('[disabled]')) continue;
    if (cs.webkitTextFillColor === 'rgba(0, 0, 0, 0)' || cs.backgroundClip === 'text' || cs.webkitBackgroundClip === 'text') continue; // gradient text
    if (el.classList.contains('st')) continue; // star glyphs are graphics, not text
    const fg = parse(cs.color); if (!fg) continue; const bg = bgOf(el);
    const a = fg.a; const f2 = {r:fg.r*a+bg.r*(1-a), g:fg.g*a+bg.g*(1-a), b:fg.b*a+bg.b*(1-a)};
    const L1 = lum(f2), L2 = lum(bg); const ratio = (Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
    if (ratio < 4.5) bad.push(ratio.toFixed(2) + ' ' + el.tagName.toLowerCase() + '.' + el.className + ' "' + n.textContent.trim().slice(0, 30) + '"');
  }
  return bad;
}
"""

OVERFLOW_JS = "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"


@step(r'the device prefers (?P<s>dark|light)')
def _prefers(env, s):
    env.page.emulate_media(color_scheme=s); env.page.reload(); wait_ready(env)


@step(r'I open the theme picker')
def _open_picker(env): env.page.click('#themeBtn'); expect(dialog(env)).to_be_visible()


@step(r'I see "Auto", "Nova", "Paper", "Terminal" and "Dune", each with a swatch')
def _picker_items(env):
    rows = dialog(env).locator('.mrow')
    texts = rows.all_inner_texts()
    for name in ('Nova', 'Paper', 'Terminal', 'Dune', 'Auto'):
        assert any(name in t for t in texts), (name, texts)
    assert rows.count() == 5
    expect(dialog(env).locator('.mrow i, .mrow .sw, .mrow [style*="background"]').first).to_be_attached()


@step(r'the current one is marked')
def _current_marked(env):
    expect(dialog(env).locator('.mrow.on')).to_have_count(1)
    expect(dialog(env).locator('.mrow.on')).to_contain_text('Auto')


@step(r'I chose "(?P<l>[^"]+)"')
def _chose(env, l):
    env.page.click('#themeBtn'); dialog(env).locator('[data-act]', has_text=l).first.click(); env.page.wait_for_timeout(150)
    if dialog(env).count(): env.page.keyboard.press('Escape')
    env.page.wait_for_timeout(100)


@step(r'html\[data-theme\] is "(?P<id>[^"]+)" before the first paint')
def _before_paint(env, id):
    env.ctx.add_init_script("""(() => { window.__themes = []; const rec = () => window.__themes.push(document.documentElement.dataset.theme || '');
      new MutationObserver(rec).observe(document, {subtree:true, attributes:true, attributeFilter:['data-theme']}); })()""")
    env.page.wait_for_timeout(800)  # let the earlier choice be saved
    env.page.reload(); wait_ready(env)
    first = env.page.evaluate("window.__themes[0]")
    assert first == id, 'first theme set was %r' % first


@step(r'I am signed in and chose "(?P<l>[^"]+)" on device A')
def _device_a(env, l):
    sync.make_signed_in(env); _chose(env, l); env.page.wait_for_timeout(1200)
    env.cloud_a = env.page.evaluate("localStorage.getItem('fake-fs')")
    assert json.loads(env.cloud_a)['users/u1']['theme'] == 'dune'


@step(r'I sign in on device B')
def _device_b(env):
    env.new_page(firebase=True); env.page.goto(env.base_url); wait_ready(env)
    env.page.evaluate("v=>localStorage.setItem('fake-fs', v)", env.cloud_a)
    env.page.reload(); wait_ready(env); sync.sign_in_ui(env)


@step(r'device B uses "(?P<id>[^"]+)"')
def _b_uses(env, id): assert env.page.evaluate("document.documentElement.dataset.theme") == id


@step(r'the theme "(?P<id>[^"]+)" is active')
def _theme_active(env, id):
    names = {'dark': 'Nova', 'paper': 'Paper', 'terminal': 'Terminal', 'dune': 'Dune'}
    env.page.set_viewport_size({'width': 390, 'height': 844})
    _chose(env, names[id]); env.contrast, env.overflow = [], []


def _audit(env, where):
    for s in env.page.evaluate(LUM_JS): env.contrast.append('%s: %s' % (where, s))
    env.overflow.append((where, env.page.evaluate(OVERFLOW_JS)))


@step(r'on the Library, My Lists, About and Book pages')
def _pages(env):
    go_tab(env, 'library'); _audit(env, 'library')
    btn(card(env, 'Dune'), 'Mark read').click(); env.page.wait_for_timeout(100); _audit(env, 'library (read card)')
    common.make_list(env, 'Classics'); go_tab(env, 'library')
    btn(card(env, 'Dune'), re.compile(r'＋ List')).click(); dialog(env).locator('[data-act]', has_text='Classics').first.click()
    dialog(env).get_by_role('button', name='Done').click()
    go_tab(env, 'lists'); _audit(env, 'lists')
    go_tab(env, 'about'); _audit(env, 'about')
    common.go_book(env, 'Ancillary Justice'); _audit(env, 'book page')


@step(r'in the book and rating dialogs')
def _dialogs(env):
    open_hash(env, '#library')
    btn(card(env, 'Dune'), '✎ Add note').click(); expect(dialog(env)).to_be_visible(); _audit(env, 'note dialog')
    env.page.keyboard.press('Escape')
    btn(card(env, 'Hyperion'), '▶ Start').click(); env.page.locator('#nowReading .ncard').click(); expect(dialog(env)).to_be_visible(); _audit(env, 'book preview')
    env.page.keyboard.press('Escape')


@step(r'all text has at least 4\.5:1 contrast with its background')
def _contrast(env): assert not env.contrast, '\n'.join(env.contrast[:60])


@step(r'nothing overflows a 390 px screen')
def _no_overflow(env):
    bad = [o for o in env.overflow if o[1] > 0]
    assert not bad, bad


@step(r'I filtered the Library and opened page 2')
def _filtered_page2(env):
    env.page.select_option('#sort', label='Title A–Z'); env.page.click('#awardPills .pill:has-text("Hugo")')
    env.page.wait_for_timeout(200)
    env.page.click('[data-act="more"]'); env.page.wait_for_timeout(200)
    env.before = env.page.evaluate("({q:document.querySelector('#count').textContent, cards:document.querySelectorAll('#results .card').length, sort:document.querySelector('#sort').value, pills:[...document.querySelectorAll('#awardPills .pill.on')].length})")


@step(r'I switch theme')
def _switch(env): _chose(env, 'Paper')


@step(r'the filters and page are unchanged')
def _unchanged_state(env):
    after = env.page.evaluate("({q:document.querySelector('#count').textContent, cards:document.querySelectorAll('#results .card').length, sort:document.querySelector('#sort').value, pills:[...document.querySelectorAll('#awardPills .pill.on')].length})")
    assert after == env.before, (after, env.before)
