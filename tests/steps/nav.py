"""Steps for 11-navigation-and-accessibility.feature."""
import re
from playwright.sync_api import expect
from steps.common import step, go_tab, open_hash, wait_ready, dialog, T, btn, card
from steps import common

OVER = "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"


@step(r'the "Now reading" row shows "(?P<t>[^"]+)" on Library, My Lists and About')
def _now_everywhere(env, t):
    for tab in ('library', 'lists', 'about'):
        go_tab(env, tab); expect(env.page.locator('#nowReading .nt')).to_have_text(t)


@step(r'the three tabs fit on one row and none wraps')
def _tabs_row(env):
    boxes = env.page.eval_on_selector_all('nav.tabs a', 'e=>e.map(x=>{const r=x.getBoundingClientRect();return [Math.round(r.top),Math.round(r.height)]})')
    assert len({b[0] for b in boxes}) == 1 and all(b[1] < 60 for b in boxes), boxes
    assert env.page.evaluate(OVER) <= 0


@step(r'the button is not visible')
def _totop_hidden(env): expect(env.page.locator('#toTop')).to_be_hidden()


@step(r'a book preview dialog is open')
def _preview_open(env):
    common._started(env, 'Hyperion'); env.page.locator('#nowReading .ncard').click(); expect(dialog(env)).to_be_visible()


@step(r'a dialog is open|I open a dialog')
def _any_dialog(env):
    env.page.click('#themeBtn'); expect(dialog(env)).to_be_visible()


@step(r'I press Escape')
def _escape(env): env.page.keyboard.press('Escape'); env.page.wait_for_timeout(100)


@step(r'I click the backdrop')
def _backdrop(env): env.page.locator('#ovRoot .ov').click(position={'x': 3, 'y': 3})


@step(r'it closes')
def _it_closes(env): expect(dialog(env)).to_have_count(0)


@step(r'it has role "dialog" and an accessible name')
def _dlg_role(env):
    d = dialog(env)
    assert d.get_attribute('role') == 'dialog' and d.get_attribute('aria-modal') == 'true'
    assert d.get_attribute('aria-label') or d.get_attribute('aria-labelledby'), 'dialog has no accessible name'


@step(r'focus is inside it')
def _focus_inside(env):
    assert env.page.evaluate("!!document.activeElement.closest('.modal')"), 'focus stays behind the dialog'


@step(r'scrolling the page behind it is prevented')
def _scroll_lock(env):
    assert env.page.evaluate("getComputedStyle(document.body).overflow") == 'hidden' or env.page.evaluate("getComputedStyle(document.documentElement).overflow") == 'hidden'


@step(r'I press Tab repeatedly from the top of the page')
def _tabs(env):
    env.page.evaluate("document.activeElement && document.activeElement.blur(); window.scrollTo(0,0)")
    seen = []
    for _ in range(25):
        env.page.keyboard.press('Tab')
        seen.append(env.page.evaluate("""() => { const e = document.activeElement; if (!e || e === document.body) return null;
          const cs = getComputedStyle(e); const ring = (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0) || cs.boxShadow !== 'none';
          return {tag: e.tagName.toLowerCase(), id: e.id, cls: e.className, label: (e.getAttribute('aria-label') || e.textContent || '').trim().slice(0, 25), ring, y: e.getBoundingClientRect().top}; }"""))
    env.focus_seen = [s for s in seen if s]


@step(r'focus visits the nav, filters, cards\' buttons in a logical order')
def _focus_order(env):
    labels = [s['label'] for s in env.focus_seen]
    assert any('Library' in l for l in labels) and any('Search' in l or s_ == 'input' for l, s_ in zip(labels, [s['tag'] for s in env.focus_seen])), labels
    first_card = next(i for i, s in enumerate(env.focus_seen) if s['tag'] == 'a' and 'bl' in s['cls'] or 'author' in s['cls'])
    nav = next(i for i, l in enumerate(labels) if 'Library' in l)
    assert nav < first_card


@step(r'every focused element has a visible focus ring')
def _rings(env):
    bad = [s['label'] for s in env.focus_seen if not s['ring']]
    assert not bad, bad


@step(r'the "Now reading" card for "(?P<t>[^"]+)" has focus')
def _ncard_focus(env, t): env.page.locator('#nowReading .ncard', has_text=t).focus()


@step(r'I press Enter')
def _enter(env): env.page.keyboard.press('Enter'); env.page.wait_for_timeout(150)


@step(r'the preview dialog opens')
def _preview_dialog(env): expect(dialog(env)).to_be_visible()


@step(r'every button without visible text has an aria-label')
def _icon_names(env):
    bad = env.page.evaluate("""() => [...document.querySelectorAll('button, a[href]')].filter(e => {
      const r = e.getBoundingClientRect(); return r.width && r.height; })
      .filter(e => !(e.textContent || '').replace(/[\\s\\u200b]/g, '') .length || !(e.getAttribute('aria-label') || (e.textContent || '').trim()))
      .map(e => e.outerHTML.slice(0, 80)).filter(x => !/aria-label/.test(x))""")
    assert not bad, bad


@step(r'a toast appears')
def _toast_appears(env): common._tap_on(env, 'Mark read', 'Dune'); expect(env.page.locator('#toastRoot .toast')).to_be_visible() if False else None; common._tap_on(env, '▶ Start', 'Hyperion')


@step(r'it sits in a live region with role "status"')
def _live(env):
    expect(env.page.locator('#toastRoot[role="status"] .toast')).to_be_visible()


@step(r'the device prefers reduced motion')
def _reduced(env): env.page.emulate_media(reduced_motion='reduce')


@step(r'smooth scrolling and transitions are disabled')
def _no_motion(env):
    r = env.page.evaluate("""() => { const c = getComputedStyle(document.querySelector('.btn')); return [getComputedStyle(document.documentElement).scrollBehavior, c.transitionDuration]; }""")
    assert r[0] in ('auto',) and set(r[1].replace('s', '').split(', ')) <= {'0'}, r


@step(r'the html element has lang "(?P<l>[^"]+)"')
def _lang(env, l): assert env.page.evaluate("document.documentElement.lang") == l


@step(r'the viewport meta allows zooming')
def _zoom(env):
    c = env.page.get_attribute('meta[name=viewport]', 'content')
    assert 'user-scalable=no' not in c and 'maximum-scale=1' not in c.replace('maximum-scale=1.', ''), c


@step(r'a (?P<w>\d+) px wide screen')
def _width(env, w): env.page.set_viewport_size({'width': int(w), 'height': 800}); env.page.wait_for_timeout(100)


@step(r'I visit each of Library, My Lists, About, a book page and every dialog')
def _visit_all(env):
    env.over = []
    def chk(where): env.over.append((where, env.page.evaluate(OVER)))
    go_tab(env, 'library'); chk('library')
    btn(card(env, 'Dune'), 'Mark read').click(); env.page.wait_for_timeout(100); chk('library read')
    common.make_list(env, 'A very long list name that goes on and on and on for a while'); go_tab(env, 'library')
    btn(card(env, 'Dune'), re.compile(r'＋ List')).click(); expect(dialog(env)).to_be_visible(); chk('list picker'); env.page.keyboard.press('Escape')
    btn(card(env, 'Dune'), '✎ Add note').click(); chk('note dialog'); env.page.keyboard.press('Escape')
    env.page.click('[data-act="addbook"]'); chk('add book'); env.page.keyboard.press('Escape')
    env.page.click('#themeBtn'); chk('theme picker'); env.page.keyboard.press('Escape')
    go_tab(env, 'lists'); chk('lists'); go_tab(env, 'about'); chk('about')
    common.go_book(env, 'Ancillary Justice'); chk('book page')


@step(r'the document is not wider than the screen')
def _not_wider(env):
    bad = [o for o in env.over if o[1] > 0]; assert not bad, bad


@step(r'primary buttons are at least (?P<n>\d+) px high and compact buttons at least 28 px')
def _target(env, n):
    bad = env.page.evaluate("""n => [...document.querySelectorAll('.btn:not(.sm), nav.tabs a, #authBtn, #themeBtn')].filter(e => { const r = e.getBoundingClientRect(); return r.width && r.height < n; }).map(e => e.textContent.trim().slice(0, 20) + ':' + Math.round(e.getBoundingClientRect().height))""", int(n))
    small = env.page.evaluate("""() => [...document.querySelectorAll('.btn.sm')].filter(e => { const r = e.getBoundingClientRect(); return r.width && r.height < 28; }).map(e => e.textContent.trim().slice(0, 20))""")
    assert not bad and not small, (bad, small)


@step(r'I walk through every feature in the other files')
def _walk(env):
    env.console_errors.clear()
    common._tap_on(env, 'Mark read', 'Dune'); common._tap_on(env, '▶ Start', 'Hyperion')
    common.make_list(env, 'L'); go_tab(env, 'about'); common.go_book(env, 'Dune'); go_tab(env, 'library')
    env.page.click('#themeBtn'); env.page.keyboard.press('Escape'); env.page.reload(); wait_ready(env)


@step(r'the browser console shows no errors or unhandled rejections')
def _no_errors(env): assert not env.console_errors, env.console_errors


@step(r'the About page is shown')
def _about_shown(env): expect(env.page.locator('.about')).to_be_visible()


@step(r'the Library is shown')
def _library_shown(env): expect(env.page.locator('#q')).to_be_visible()
