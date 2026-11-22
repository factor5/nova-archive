"""Steps for 02-reading-status and 03-ratings-and-notes (beyond the smoke steps in common.py)."""
import json, re, time
from playwright.sync_api import expect
from steps.common import step, go_tab, dialog, T, btn, card, saved, bid, wait_ready, go_book
from steps import common
from steps.library import DATA


def seed(env, read=(), reading=None, meta=None, lists=None, reload=True):
    """Put state straight into the saved data (fast and deterministic), then reload."""
    cur = env.page.evaluate("JSON.parse(localStorage.getItem('nova-archive-v1')||'{}')")
    cur.setdefault('v', 2); cur['updatedAt'] = int(time.time() * 1000)
    cur['read'] = sorted(set(cur.get('read', [])) | {bid(t) for t in read})
    cur['reading'] = {**cur.get('reading', {}), **{bid(k): v for k, v in (reading or {}).items()}}
    m = cur.get('meta', {})
    for k, v in (meta or {}).items(): m.setdefault(bid(k), {}).update(v)
    cur['meta'] = m; cur.setdefault('lists', []); cur.setdefault('custom', [])
    env.page.evaluate("o=>localStorage.setItem('nova-archive-v1', JSON.stringify(o))", cur)
    if reload: env.page.reload(); wait_ready(env)


def now_ms(): return int(time.time() * 1000)


# ---------------------------------------------------------------- reading status
@step(r'I mark (?P<n>\d+) books as read')
def _mark_n(env, n): seed(env, read=[b['id'] for b in DATA[:int(n)]])


@step(r'the progress bar is about (?P<p>\d+) percent full')
def _bar(env, p):
    w = env.page.evaluate("parseFloat(document.getElementById('hudBar').style.width)")
    assert abs(w - int(p)) <= 1, w


@step(r'"(?P<t>[^"]+)" shows "Mark read" and "▶ Start" buttons again')
def _again_btns(env, t):
    c = card(env, t); expect(btn(c, 'Mark read')).to_be_visible(); expect(btn(c, '▶ Start')).to_be_visible()


@step(r'"(?P<t>[^"]+)" is not marked read')
def _not_marked(env, t): assert bid(t) not in saved(env)['read']


@step(r'"(?P<t>[^"]+)" shows no "(?P<b>[^"]+)" button')
def _no_button(env, t, b): expect(card(env, t).get_by_role('button', name=b, exact=True)).to_have_count(0)


@step(r'the "Now reading" row shows "(?P<t>[^"]+)"')
def _row_shows(env, t): expect(env.page.locator('#nowReading .nt')).to_have_text(t)


@step(r'the preview closes and the rating dialog opens')
def _preview_to_rating(env):
    expect(dialog(env).locator('#noteTxt')).to_be_visible(); expect(dialog(env).locator('.st')).to_have_count(5)


@step(r'I started reading (?P<ts>"[^"]+"(?:, "[^"]+")* and "[^"]+") in that order')
def _started_order(env, ts):
    titles = re.findall(r'"([^"]+)"', ts); base = now_ms() - 10000
    seed(env, reading={t: base + i * 1000 for i, t in enumerate(titles)})


@step(r'I started reading (?P<ts>"[^"]+"(?:, "[^"]+")* and "[^"]+")')
def _started_many(env, ts): _started_order(env, ts)


@step(r'the card in the row shows only the title, the author, "Day 1" and a "›"')
def _compact_text(env):
    t = env.page.locator('#nowReading .ncard').inner_text()
    parts = [x.strip() for x in re.split(r'\n|·', t) if x.strip()]
    assert [x.lower() for x in parts] == ['hyperion', 'dan simmons', 'day 1', '›'], parts


@step(r'it has no buttons')
def _no_btns(env): expect(env.page.locator('#nowReading .ncard button')).to_have_count(0)


@step(r'the card is no taller than 90 pixels on a phone')
def _compact_h(env):
    env.page.set_viewport_size({'width': 390, 'height': 844}); env.page.wait_for_timeout(100)
    assert env.page.locator('#nowReading .ncard').bounding_box()['height'] <= 90


@step(r'I started reading "(?P<t>[^"]+)" (?P<d>\d+) days ago')
def _started_ago(env, t, d): seed(env, reading={t: now_ms() - int(d) * 864000 * 100 - 5000})


@step(r'its card in the row shows "(?P<s>[^"]+)"')
def _its_card(env, s): expect(env.page.locator('#nowReading .ncard .nd')).to_have_text(s)


@step(r'I saved the note "(?P<n>[^"]+)" for it')
def _note_for_it(env, n):
    t = env.page.locator('#nowReading .nt').first.inner_text(); seed(env, meta={t: {'n': n}})


@step(r'the card shows a "✎" before the "›"')
def _hint(env): expect(env.page.locator('#nowReading .ncard .chev')).to_have_text(re.compile(r'✎\s*›'))


@step(r'I opened its preview|I opened the preview of a book being read')
def _opened_preview(env):
    if not env.page.locator('#nowReading .ncard').count(): common._started(env, 'Hyperion')
    env.page.locator('#nowReading .ncard').first.click(); expect(dialog(env)).to_be_visible()


@step(r'I tap "✎ Add note", write "(?P<n>[^"]+)", and save')
def _preview_note(env, n):
    btn(dialog(env), '✎ Add note').click(); env.page.fill('#noteTxt', n); btn(dialog(env), 'Save').click(); env.page.wait_for_timeout(150)


@step(r'I am back in the app and the "Now reading" card shows a "✎"')
def _back_hint(env):
    expect(dialog(env)).to_have_count(0); _hint(env)


@step(r'I tap "Open full page ›"')
def _open_full(env): dialog(env).locator('a', has_text='Open full page').click(); env.page.wait_for_timeout(200)


@step(r'the preview closes')
def _preview_closes(env): expect(dialog(env)).to_have_count(0)


@step(r'the book page for that book is shown')
def _that_page(env): expect(env.page.locator('.bhead h2')).to_have_text('Hyperion')


@step(r'I focus the "(?P<t>[^"]+)" card in the row and press Enter')
def _focus_enter(env, t):
    env.page.locator('#nowReading .ncard', has_text=t).focus(); env.page.keyboard.press('Enter'); env.page.wait_for_timeout(150)


@step(r'the preview opens')
def _preview_opens(env): expect(dialog(env)).to_be_visible()


@step(r'part of the second card is visible beside the first on a phone')
def _peek(env):
    env.page.set_viewport_size({'width': 390, 'height': 844}); env.page.wait_for_timeout(150)
    b = env.page.locator('#nowReading .ncard').nth(1).bounding_box()
    assert b['x'] < 390 < b['x'] + b['width'], b


@step(r'the page itself does not scroll sideways')
def _no_side(env): assert env.page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth") <= 0


# ---------------------------------------------------------------- ratings and notes
@step(r'I rated "(?P<t>[^"]+)" (?P<n>\d) stars?')
def _rated(env, t, n): seed(env, read=[t], meta={t: {'r': int(n)}})


@step(r'I rated (?P<spec>"[^"]+" \d stars?(?: and "[^"]+" \d stars?)+)')
def _rated_many(env, spec):
    pairs = re.findall(r'"([^"]+)" (\d) star', spec)
    seed(env, read=[t for t, _ in pairs], meta={t: {'r': int(n)} for t, n in pairs})


@step(r'no stars are filled on "(?P<t>[^"]+)"')
def _none_filled(env, t): expect(card(env, t).locator('.st.on')).to_have_count(0)


@step(r'the saved data has no rating for "(?P<id>[^"]+)"')
def _no_rating(env, id): assert 'r' not in saved(env).get('meta', {}).get(id, {})


@step(r'each star is a button labelled "1 star", "2 stars", "3 stars", "4 stars" and "5 stars"')
def _star_labels(env):
    got = card(env, 'Dune').locator('.st').evaluate_all('e=>e.map(x=>[x.tagName,x.getAttribute("aria-label")])')
    assert [g[1] for g in got] == ['1 star', '2 stars', '3 stars', '4 stars', '5 stars'] and all(g[0] == 'BUTTON' for g in got), got


@step(r'a filled star has aria-pressed "true" and an empty one "false"')
def _pressed(env):
    got = card(env, 'Dune').locator('.st').evaluate_all('e=>e.map(x=>x.getAttribute("aria-pressed"))')
    assert got == ['true', 'true', 'false', 'false', 'false'], got


@step(r'I saved the note "(?P<n>[^"]+)" for "(?P<t>[^"]+)"')
def _saved_note_for(env, n, t): seed(env, read=[t], meta={t: {'n': n}})


@step(r'I opened the note dialog for "(?P<t2>[^"]+)"')
def _opened_note(env, t2): _open_note(env, t2)


@step(r'I open the note dialog for "(?P<t>[^"]+)"')
def _open_note(env, t): btn(card(env, t), re.compile(r'✎')).click(); expect(dialog(env)).to_be_visible()


@step(r'the notes box contains "(?P<n>[^"]+)"')
def _box_has(env, n): expect(env.page.locator('#noteTxt')).to_have_value(n)


@step(r'I clear the box and tap "Save"')
def _clear_save(env): env.page.fill('#noteTxt', ''); btn(dialog(env), 'Save').click(); env.page.wait_for_timeout(150)


@step(r'the button on the card reads "(?P<b>✎ Add note)" again')
def _reads_again(env, b): expect(btn(card(env, 'Dune'), b)).to_be_visible()


@step(r'the saved data has no note for "(?P<id>[^"]+)"')
def _no_note(env, id): assert 'n' not in saved(env).get('meta', {}).get(id, {})


@step(r'I type 2100 characters')
def _type_2100(env):
    env.page.locator('#noteTxt').focus(); env.page.keyboard.insert_text('x' * 2100)


@step(r'the notes box holds 2000 characters')
def _holds_2000(env): assert len(env.page.input_value('#noteTxt')) == 2000


@step(r'I replace it with "(?P<n>[^"]*)" and tap "Save"')
def _replace_save(env, n): env.page.fill('#noteTxt', n); btn(dialog(env), 'Save').click(); env.page.wait_for_timeout(150)


@step(r'the saved note is "(?P<n>[^"]*)"')
def _note_is(env, n): assert saved(env)['meta']['dune--frank-herbert']['n'] == n


@step(r'I opened the note dialog for "(?P<t>[^"]+)" and typed "(?P<x>[^"]+)"')
def _open_typed(env, t, x): _open_note(env, t); env.page.fill('#noteTxt', x)


@step(r'I click outside the dialog')
def _click_outside(env): env.page.locator('#ovRoot .ov').click(position={'x': 3, 'y': 3})


@step(r'I tap star (?P<n>\d) in the dialog')
def _star_dlg(env, n): dialog(env).locator('.st').nth(int(n) - 1).click(); env.page.wait_for_timeout(100)


@step(r'5 stars are filled in the dialog and on the card behind it')
def _both(env):
    expect(dialog(env).locator('.st.on')).to_have_count(5); expect(card(env, 'Dune').locator('.st.on')).to_have_count(5)


@step(r'the card for "(?P<t>[^"]+)" shows "✎ Add note" and no stars')
def _note_no_stars(env, t):
    c = card(env, t); expect(btn(c, '✎ Add note')).to_be_visible(); expect(c.locator('.rate')).to_have_count(0)


@step(r'I save the note "(?P<n>.+)" for "(?P<t>[^"]+)"')
def _save_note_ui(env, n, t):
    env.alerts = []; env.page.on('dialog', lambda d: (env.alerts.append(d.message), d.dismiss()))
    btn(card(env, t), '✎ Add note').click(); env.page.fill('#noteTxt', n); btn(dialog(env), 'Save').click(); env.page.wait_for_timeout(300)


@step(r'the notes box contains exactly "(?P<n>.+)"')
def _box_exact(env, n): expect(env.page.locator('#noteTxt')).to_have_value(n)


@step(r'no script ran and no bold text appeared')
def _no_xss(env):
    assert not env.alerts; expect(env.page.locator('#ovRoot b, #results b')).to_have_count(0)


@step(r'I rated "(?P<t>[^"]+)" (?P<n>\d) stars and saved the note "(?P<x>[^"]+)" for it')
def _rated_noted(env, t, n, x): seed(env, read=[t], meta={t: {'r': int(n), 'n': x}})


@step(r'the card shows no stars')
def _card_no_stars(env): expect(card(env, env.last_title).locator('.rate')).to_have_count(0)


@step(r'(?P<n>\d) stars are filled and the button reads "(?P<b>[^"]+)"')
def _filled_and_btn(env, n, b):
    c = card(env, 'Dune'); expect(c.locator('.st.on')).to_have_count(int(n)); expect(btn(c, b)).to_be_visible()


@step(r'the cards are "Dune", "Neuromancer", "Hyperion"')
def _cards_ordered(env):
    assert env.page.eval_on_selector_all('#results .card h3 a', 'e=>e.map(x=>x.textContent)') == ['Dune', 'Neuromancer', 'Hyperion']


@step(r'I tap "✓ Finish" on "(?P<t>[^"]+)" and then "Save"')
def _finish_save(env, t):
    common._tap_on(env, '✓ Finish', t); btn(dialog(env), 'Save').click(); env.page.wait_for_timeout(150)


@step(r'the "Finished on" date shows today')
def _fin_today(env):
    today = env.page.evaluate("(()=>{const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')})()")
    expect(env.page.locator('#pageFin')).to_have_value(today)


@step(r'I set "Finished on" to the 1st of last month')
def _set_fin(env):
    d = env.page.evaluate("(()=>{const d=new Date();d.setDate(1);d.setMonth(d.getMonth()-1);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-01'})()")
    env.fin = d; env.page.fill('#pageFin', d); env.page.locator('#pageFin').blur(); env.page.wait_for_timeout(150)


@step(r'the saved data has that date for "(?P<id>[^"]+)"')
def _has_date(env, id):
    ts = saved(env)['meta'][id]['f']
    assert env.page.evaluate("t=>{const d=new Date(t);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')}", ts) == env.fin


@step(r'the date cannot be set in the future')
def _no_future(env):
    mx = env.page.get_attribute('#pageFin', 'max')
    today = env.page.evaluate("(()=>{const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')})()")
    assert mx == today, mx


@step(r'I finished "(?P<t>[^"]+)" today')
def _finished_today(env, t): seed(env, read=[t], meta={t: {'f': now_ms()}}); go_book(env, t)


@step(r'I clear the "Finished on" date on its book page')
def _clear_fin(env): env.page.fill('#pageFin', ''); env.page.locator('#pageFin').blur(); env.page.wait_for_timeout(150)


@step(r'the saved data has no finish date for "(?P<id>[^"]+)"')
def _no_fin(env, id): assert 'f' not in saved(env).get('meta', {}).get(id, {})
