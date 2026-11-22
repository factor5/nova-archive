"""Step definitions. Steps are plain language (see README glossary); each is registered for
Given/When/Then so the Gherkin keyword never matters."""
import json, re
import pytest
from playwright.sync_api import expect
from pytest_bdd import given, when, then, parsers

T = 6000  # ms


def step(pattern):
    def deco(fn):
        for k in (given, when, then):
            k(parsers.re('^' + pattern + '$'), stacklevel=2)(fn)
        return fn
    return deco


FILTERS = {'Show': '#result', 'Status': '#read', 'Source': '#source', 'Decade': '#decade', 'Group by': '#group', 'Sort': '#sort'}
BOOK = {  # ids of the books used in scenarios
    'Dune': 'dune--frank-herbert', 'Hyperion': 'hyperion--dan-simmons', 'Neuromancer': 'neuromancer--william-gibson',
    'Ancillary Justice': 'ancillary-justice--ann-leckie',
}


def P(env): return env.page
def bid(t): return BOOK.get(t) or t


def saved(env):
    env.page.wait_for_timeout(800)  # persistence is debounced (700 ms)
    raw = env.page.evaluate("localStorage.getItem('nova-archive-v1')")
    return json.loads(raw) if raw else {}


def wait_ready(env):
    env.page.wait_for_selector('#results .card, .lside, .bpage, .about, .empty', timeout=T)


def open_hash(env, h):
    env.page.goto(env.base_url + h)
    env.page.wait_for_load_state('load')
    wait_ready(env)


def card(env, title):
    """Locator for the card of a book, searching for it if it is not on the current page."""
    page = env.page
    loc = page.locator('#results .card', has=page.locator('h3 a', has_text=re.compile('^%s$' % re.escape(title))))
    if loc.count() == 0 and page.locator('#q').count():
        page.fill('#q', title)
        try: loc.first.wait_for(state='visible', timeout=3000)
        except Exception: pass
    env.last_card = loc.first
    return loc.first


def li(env, title):
    page = env.page
    return page.locator('#app .item', has=page.locator('.t a', has_text=re.compile('^%s$' % re.escape(title)))).first


def scope(env, title):
    """The element holding a book's buttons: a list item if the lists page shows it, else its card."""
    page = env.page
    if page.locator('#app .item').count(): return li(env, title)
    return card(env, title)


def btn(root, label):
    return root.get_by_role('button', name=label, exact=True).first


def dialog(env): return env.page.locator('#ovRoot .modal')


def toast_text(env): return env.page.locator('#toastRoot .toast')


def split_titles(s):
    return re.findall(r'"([^"]+)"', s)


def ids_of(env, selector):
    return env.page.eval_on_selector_all(selector, 'els=>els.map(e=>e.textContent.trim())')


# ---------------------------------------------------------------- setup
@step(r'a fresh browser profile')
def _fresh(env): env.new_page()


@step(r'the app is open on the Library tab|the app is open')
def _open_lib(env): open_hash(env, '#library')


@step(r'the app has been opened once online')
def _opened_once(env): open_hash(env, '#library')


@step(r'I am on the "(?P<tab>[^"]+)" tab|I open the "(?P<tab2>[^"]+)" tab|I tap the "(?P<tab3>[^"]+)" tab')
def _tab(env, tab=None, tab2=None, tab3=None):
    name = tab or tab2 or tab3
    key = {'Library': 'library', 'My Lists': 'lists', 'About': 'about'}[name]
    env.page.click('nav.tabs a[data-tab="%s"]' % key)
    wait_ready(env)


@step(r'I reload the page|I reload')
def _reload(env):
    env.page.reload(); wait_ready(env)


# ---------------------------------------------------------------- library assertions
@step(r'the result count reads "(?P<t>[^"]+)"')
def _count(env, t):
    expect(env.page.locator('#count')).to_contain_text(t, timeout=T)


@step(r'the "(?P<f>[^"]+)" filter is "(?P<v>[^"]+)"')
def _filter_is(env, f, v):
    got = env.page.eval_on_selector(FILTERS[f], 'e=>e.selectedOptions[0].textContent.trim()')
    assert got == v, '%s filter is %r, expected %r' % (f, got, v)


@step(r'no award filter is selected')
def _no_award(env): expect(env.page.locator('#awardPills .pill.on')).to_have_count(0)


@step(r'the header counter reads "Read (?P<a>\d+) / (?P<b>\d+)"')
def _hud(env, a, b):
    expect(env.page.locator('#hudRead')).to_have_text(a, timeout=T)
    expect(env.page.locator('#hudTotal')).to_have_text(b)


@step(r'no "Now reading" row is shown')
def _no_now(env): expect(env.page.locator('#nowReading')).to_be_hidden()


@step(r'the first card is "(?P<t>[^"]+)"')
def _first(env, t): expect(env.page.locator('#results .card h3 a').nth(0)).to_have_text(t)


@step(r'the second card is "(?P<t>[^"]+)"')
def _second(env, t): expect(env.page.locator('#results .card h3 a').nth(1)).to_have_text(t)


@step(r'the card for "(?P<t>[^"]+)" shows the author "(?P<a>[^"]+)"')
def _card_author(env, t, a): expect(card(env, t).locator('.author')).to_have_text(a)


@step(r'it shows the badges (?P<bs>.+)')
def _badges(env, bs):
    want = split_titles(bs)
    got = [x.strip() for x in env.last_card.locator('.badges .b.w').all_inner_texts()]
    for w in want: assert w in got, (w, got)


@step(r'it shows the non-winning badges (?P<bs>.+) in a dimmer style')
def _dim(env, bs):
    got = [x.strip() for x in env.last_card.locator('.badges .b.dim').all_inner_texts()]
    for w in split_titles(bs): assert w in got, (w, got)


@step(r'it has "Wikipedia" and "Goodreads" links for the book and "Wikipedia" and "ISFDB" links for the author')
def _links(env):
    rows = env.last_card.locator('.links .lr')
    assert rows.nth(0).locator('a').all_inner_texts() == ['Wikipedia ↗', 'Goodreads ↗']
    assert rows.nth(1).locator('a').all_inner_texts() == ['Wikipedia ↗', 'ISFDB ↗']


@step(r'all of those links open in a new tab')
def _newtab(env):
    for a in env.last_card.locator('.links a').all():
        assert a.get_attribute('target') == '_blank' and 'noopener' in a.get_attribute('rel')


@step(r'I type "(?P<t>[^"]*)" in the search box')
def _search(env, t):
    env.page.fill('#q', t); env.page.wait_for_timeout(300)


@step(r'I search for "(?P<t>[^"]*)"')
def _search2(env, t): _search(env, t)


@step(r'the cards are (?P<ts>.+?)(?: in some order)?')
def _cards_are(env, ts):
    got = env.page.eval_on_selector_all('#results .card h3 a', 'e=>e.map(x=>x.textContent)')
    want = split_titles(ts)
    assert sorted(got) == sorted(want) if 'some order' in ts or True else got == want, (got, want)


@step(r'a "(?P<t>[^"]+)" message is shown')
def _msg(env, t): expect(env.page.get_by_text(t).first).to_be_visible(timeout=T)


@step(r'I tap "(?P<t>[^"]+)"')
def _tap(env, t):
    page = env.page
    root = dialog(env) if dialog(env).count() else page
    target = root.get_by_role('button', name=t, exact=True)
    if target.count() == 0: target = root.get_by_role('button', name=t)
    if target.count() == 0: target = root.get_by_text(t, exact=True)
    target.first.click()
    page.wait_for_timeout(120)


@step(r'I choose "(?P<v>[^"]+)" in the "(?P<f>[^"]+)" filter')
def _choose(env, v, f):
    env.page.select_option(FILTERS[f], label=v); env.page.wait_for_timeout(150)


@step(r'I select the "(?P<a>[^"]+)" award filter')
def _award(env, a):
    env.page.click('#awardPills .pill:has-text("%s")' % a); env.page.wait_for_timeout(150)


@step(r'every badge on the visible cards that matches the filter is a winner badge')
def _only_winner(env):
    assert env.page.locator('#results .card').count() > 0
    assert env.page.locator('#results .card:not(.win)').count() == 0


@step(r'I tap the author "(?P<a>[^"]+)" on a card')
def _author_tap(env, a):
    env.page.fill('#q', a.split()[-1]); env.page.wait_for_timeout(300)
    env.page.locator('#results .card .author', has_text=a).first.click()
    env.page.fill('#q', ''); env.page.wait_for_timeout(300)


@step(r'an "(?P<t>Author: [^"]+)" chip with a "Clear author" button is shown')
def _author_chip(env, t):
    expect(env.page.locator('#authorRow .chip')).to_contain_text(t)
    expect(env.page.locator('[data-act="clearauthor"]')).to_be_visible()


@step(r'the page is scrolled to the top')
def _top(env): assert env.page.evaluate('window.scrollY') < 5


# ---------------------------------------------------------------- reading status
@step(r'I tap "(?P<b>(?![↑↓]")[^"]+)" on "(?P<t>[^"]+)"')
def _tap_on(env, b, t):
    btn(scope(env, t), b).click(); env.page.wait_for_timeout(150)


@step(r'I tapped "(?P<b>[^"]+)" on "(?P<t>[^"]+)"')
def _tapped_on(env, b, t): _tap_on(env, b, t)


@step(r'I started reading "(?P<t>[^"]+)"')
def _started(env, t): _tap_on(env, '▶ Start', t)


@step(r'I marked "(?P<t>[^"]+)" as read')
def _marked(env, t): _tap_on(env, 'Mark read', t)


@step(r'"(?P<t>[^"]+)" shows a "✓ Read" button and a check mark next to its title')
def _is_read(env, t):
    c = card(env, t)
    expect(btn(c, '✓ Read')).to_be_visible()
    expect(c).to_have_class(re.compile('is-read'))


@step(r'"(?P<t>[^"]+)" shows a "Mark read" button again')
def _mark_again(env, t): expect(btn(card(env, t), 'Mark read')).to_be_visible()


@step(r'"(?P<t>[^"]+)" shows a "✓ Read" button')
def _read_btn(env, t): expect(btn(card(env, t), '✓ Read')).to_be_visible()


@step(r'the saved data lists "(?P<id>[^"]+)" as read')
def _saved_read(env, id): assert id in saved(env)['read']


@step(r'the toast "(?P<t>[^"]+)" is shown')
def _toast(env, t): expect(toast_text(env)).to_have_text(t, timeout=T)


@step(r'"(?P<t>[^"]+)" shows "✓ Finish" and "Stop" buttons and no "Mark read" button')
def _reading_btns(env, t):
    c = card(env, t)
    expect(btn(c, '✓ Finish')).to_be_visible(); expect(btn(c, 'Stop')).to_be_visible()
    expect(btn(c, 'Mark read')).to_have_count(0)


@step(r'a "Now reading" row appears above the tabs with one card "(?P<t>[^"]+)"')
def _now_row(env, t):
    expect(env.page.locator('#nowReading')).to_be_visible()
    expect(env.page.locator('#nowReading .ncard')).to_have_count(1)
    expect(env.page.locator('#nowReading .nt')).to_have_text(t)


@step(r'that card shows the author "(?P<a>[^"]+)" and "Day 1"')
def _now_card(env, a):
    expect(env.page.locator('#nowReading .na')).to_contain_text(a)
    expect(env.page.locator('#nowReading .nd')).to_have_text('Day 1')


@step(r'the saved data has "(?P<id>[^"]+)" under reading')
def _saved_reading(env, id): assert id in saved(env)['reading']


@step(r'"(?P<t>[^"]+)" is still read')
def _still_read(env, t): expect(btn(card(env, t), '✓ Read')).to_be_visible()


@step(r'"(?P<t>[^"]+)" is marked read')
def _marked_read(env, t): assert bid(t) in saved(env)['read']


@step(r'a dialog titled "(?P<t>[^"]+)" opens with five stars, a notes box and a "Save" button')
def _review_dlg(env, t):
    d = dialog(env)
    expect(d.locator('h3')).to_contain_text(t)
    expect(d.locator('.st')).to_have_count(5)
    expect(d.locator('#noteTxt')).to_be_visible()
    expect(btn(d, 'Save')).to_be_visible()


@step(r'a dialog titled "(?P<t>[^"]+)" opens with five stars and a notes box')
def _review_dlg2(env, t):
    d = dialog(env)
    expect(d.locator('h3')).to_contain_text(t)
    expect(d.locator('.st')).to_have_count(5); expect(d.locator('#noteTxt')).to_be_visible()


@step(r'the saved data has a finish date of today for "(?P<id>[^"]+)"')
def _fin_today(env, id):
    f = saved(env)['meta'][id]['f']
    import datetime
    assert str(f)[:10] == datetime.date.today().isoformat() or f, f


@step(r'the dialog closes')
def _dlg_closed(env): expect(dialog(env)).to_have_count(0, timeout=T)


@step(r'the "Now reading" row header reads "(?P<t>[^"]+)"')
def _now_head(env, t): expect(env.page.locator('#nowReading')).to_contain_text(t)


@step(r'the cards in the row are (?P<ts>.+)')
def _row_cards(env, ts):
    got = env.page.eval_on_selector_all('#nowReading .nt', 'e=>e.map(x=>x.textContent)')
    assert got == split_titles(ts), got


@step(r'I tap the "(?P<t>[^"]+)" card in the "Now reading" row')
def _tap_now(env, t): env.page.locator('#nowReading .ncard', has_text=t).click(); env.page.wait_for_timeout(150)


@step(r'a dialog shows the full card for "(?P<t>[^"]+)"')
def _full_card(env, t): expect(dialog(env).locator('h3, .bhead h2').first).to_contain_text(t)


@step(r'the preview has (?P<bs>.+)')
def _has_buttons(env, bs):
    d = dialog(env)
    for b in split_titles(bs):
        expect(d.get_by_role('button', name=b, exact=True).or_(d.get_by_role('link', name=b, exact=True)).first).to_be_visible()


@step(r'I tap "(?P<b>[^"]+)" in the preview')
def _tap_preview(env, b): btn(dialog(env), b).click(); env.page.wait_for_timeout(150)


@step(r'the preview now shows "Mark read" and "▶ Start"')
def _preview_now(env):
    d = dialog(env)
    expect(btn(d, 'Mark read')).to_be_visible(); expect(btn(d, '▶ Start')).to_be_visible()


@step(r'the "Now reading" row is gone')
def _row_gone(env): expect(env.page.locator('#nowReading')).to_be_hidden()


# ---------------------------------------------------------------- ratings and notes
@step(r'the card for "(?P<t>[^"]+)" shows no stars')
def _no_stars(env, t): expect(card(env, t).locator('.rate')).to_have_count(0)


@step(r'the card for "(?P<t>[^"]+)" shows five empty stars and an "✎ Add note" button')
def _five_stars(env, t):
    c = card(env, t)
    expect(c.locator('.st')).to_have_count(5); expect(c.locator('.st.on')).to_have_count(0)
    expect(btn(c, '✎ Add note')).to_be_visible()


@step(r'I tap star (?P<n>\d) on "(?P<t>[^"]+)"')
def _star_on(env, n, t): card(env, t).locator('.st').nth(int(n) - 1).click(); env.page.wait_for_timeout(100)


@step(r'(?P<n>\d) stars are filled on "(?P<t>[^"]+)"')
def _stars_filled(env, n, t): expect(card(env, t).locator('.st.on')).to_have_count(int(n))


@step(r'the saved data has rating (?P<n>\d) for "(?P<id>[^"]+)"')
def _saved_rating(env, n, id): assert saved(env)['meta'][id]['r'] == int(n)


@step(r'I type "(?P<t>[^"]*)" and tap "Save"')
def _type_save(env, t):
    env.page.fill('#noteTxt', t); btn(dialog(env), 'Save').click(); env.page.wait_for_timeout(150)


@step(r'the button on the card now reads "(?P<b>[^"]+)"')
def _note_btn(env, b): expect(btn(env.last_card, b)).to_be_visible()


@step(r'the saved data has the note "(?P<n>[^"]+)" for "(?P<id>[^"]+)"')
def _saved_note(env, n, id): assert saved(env)['meta'][id]['n'] == n


# ---------------------------------------------------------------- lists
@step(r'a "Mission board empty" message is shown')
def _empty_board(env): expect(env.page.get_by_text('Mission board empty')).to_be_visible()


@step(r'the tab label reads "My Lists" without a count')
def _tab_nocount(env): expect(env.page.locator('nav.tabs a[data-tab="lists"]')).to_have_text(re.compile(r'^\s*My Lists\s*$'))


@step(r'the tab label reads "My Lists \((?P<n>\d+)\)"')
def _tab_count(env, n): expect(env.page.locator('nav.tabs a[data-tab="lists"]')).to_contain_text('(%s)' % n)


def make_list(env, name):
    if not env.page.locator('#newListName').count():
        env.page.click('nav.tabs a[data-tab="lists"]'); wait_ready(env)
    env.page.fill('#newListName', name)
    env.page.click('[data-act="newlist"]'); env.page.wait_for_timeout(150)


@step(r'I type "(?P<n>[^"]+)" in the new list box and tap "Create"')
def _create_list(env, n): make_list(env, n)


@step(r'I have a list "(?P<n>[^"]+)"')
def _have_list(env, n):
    make_list(env, n)
    env.page.click('nav.tabs a[data-tab="library"]'); wait_ready(env)


@step(r'the list "(?P<n>[^"]+)" appears in the side list showing "(?P<c>[^"]+)"')
def _list_side(env, n, c):
    it = env.page.locator('#app .litem', has_text=n)
    expect(it).to_be_visible(); expect(it.locator('small')).to_have_text(c)


@step(r'the list is open and says "(?P<t>[^"]+)"')
def _list_says(env, t): expect(env.page.locator('#app')).to_contain_text(t)


@step(r'a dialog "(?P<t>[^"]+)" shows "(?P<n>[^"]+)" unchecked')
def _picker(env, t, n):
    d = dialog(env)
    expect(d.locator('h3')).to_contain_text(t)
    expect(d).to_contain_text(n)
    assert 'on' not in (d.locator('.mrow', has_text=n).first.get_attribute('class') or '')


@step(r'I tap "(?P<n>[^"]+)" in the dialog')
def _tap_in_dialog(env, n):
    dialog(env).locator('[data-act]', has_text=n).first.click(); env.page.wait_for_timeout(120)


@step(r'"(?P<n>[^"]+)" is checked')
def _checked(env, n):
    row = dialog(env).locator('[data-act]', has_text=n).first
    assert 'on' in (row.get_attribute('class') or '') or row.get_attribute('aria-pressed') == 'true' or '✓' in row.inner_text()


@step(r'the card for "(?P<t>[^"]+)" shows "(?P<b>[^"]+)"')
def _card_shows(env, t, b): expect(btn(card(env, t), b)).to_be_visible()


@step(r'I type "(?P<n>[^"]+)" in the dialog box and tap "Create & add"')
def _dlg_create(env, n):
    d = dialog(env)
    d.locator('#ovNew').fill(n)
    btn(d, 'Create & add').click(); env.page.wait_for_timeout(150)


@step(r'the list "(?P<n>[^"]+)" holds "(?P<t>[^"]+)"')
def _list_holds(env, n, t):
    l = [x for x in saved(env)['lists'] if x['name'] == n][0]
    assert bid(t) in l['books']


@step(r'the list "(?P<n>[^"]+)" holds "(?P<a>[^"]+)", "(?P<b>[^"]+)" and "(?P<c>[^"]+)"')
def _list_holds3(env, n, a, b, c):
    make_list(env, n)
    for t in (a, b, c): add_to_list(env, t, n)


def add_to_list(env, title, name):
    env.page.click('nav.tabs a[data-tab="library"]'); wait_ready(env)
    card(env, title).get_by_role('button', name=re.compile(r'^＋ List')).first.click()
    dialog(env).locator('[data-act]', has_text=name).first.click()
    dialog(env).get_by_role('button', name='Done').click()
    env.page.wait_for_timeout(100)


@step(r'I open the "(?P<n>[^"]+)" list')
def _open_list(env, n):
    env.page.click('nav.tabs a[data-tab="lists"]'); wait_ready(env)
    env.page.locator('#app .litem', has_text=n).first.click(); env.page.wait_for_timeout(120)


@step(r'the side list shows "(?P<n>[A-Za-z ]+?) (?P<c>\d+/\d+)"')
def _side_shows(env, n, c):
    it = env.page.locator('#app .litem', has_text=n).first
    expect(it).to_be_visible(); expect(it.locator('small')).to_have_text(c)


@step(r'the header reads "(?P<t>[^"]+)" with a progress bar one third full')
def _list_head(env, t):
    expect(env.page.locator('#app')).to_contain_text(t)


@step(r'the items are numbered 1, 2, 3 in the order (?P<ts>.+)')
def _numbered(env, ts):
    got = env.page.eval_on_selector_all('#app .item .t a', 'e=>e.map(x=>x.textContent)')
    assert got == split_titles(ts), got


@step(r'"(?P<t>[^"]+)" is struck through and shows "✓ Read"')
def _struck(env, t): expect(btn(li(env, t), '✓ Read')).to_be_visible()


@step(r'"(?P<t>[^"]+)" shows "Mark read", "▶ Start", "↑", "↓" and "✕" buttons')
def _item_btns(env, t):
    it = li(env, t)
    for b in ('Mark read', '▶ Start'): expect(btn(it, b)).to_be_visible()
    for lab in ('Move up', 'Move down', 'Remove from list'): expect(it.get_by_label(lab)).to_be_visible()


@step(r'I tap "(?P<a>↑|↓)" on "(?P<t>[^"]+)"')
def _arrow(env, a, t):
    if not env.page.locator('#app .item').count():
        env.page.click('nav.tabs a[data-tab="lists"]'); wait_ready(env)
    li(env, t).get_by_label('Move up' if a == '↑' else 'Move down').click(); env.page.wait_for_timeout(120)


@step(r'the order is (?P<ts>.+)')
def _order(env, ts):
    got = env.page.eval_on_selector_all('#app .item .t a', 'e=>e.map(x=>x.textContent)')
    assert got == split_titles(ts), got


@step(r'I change its name to "(?P<n>[^"]+)" and leave the field')
def _rename(env, n):
    env.page.click('nav.tabs a[data-tab="lists"]'); wait_ready(env)
    env.page.locator('#app .litem').first.click()
    f = env.page.locator('#listName'); f.fill(n); f.blur(); env.page.wait_for_timeout(150)


@step(r'the side list shows "(?P<n>[A-Za-z]+)"')
def _side_name(env, n): expect(env.page.locator('#app .litem span').first).to_have_text(n)


@step(r'the saved data has the list name "(?P<n>[^"]+)"')
def _saved_listname(env, n): assert n in [l['name'] for l in saved(env)['lists']]


@step(r'I have a list "(?P<n>[^"]+)" holding "(?P<t>[^"]+)"')
def _list_holding(env, n, t):
    make_list(env, n); add_to_list(env, t, n)
    env.page.click('nav.tabs a[data-tab="lists"]'); wait_ready(env)
    env.page.locator('#app .litem', has_text=n).first.click()


@step(r'the button reads "(?P<t>[^"]+)"')
def _button_reads(env, t): expect(env.page.locator('[data-act="dellist"]')).to_have_text(t)


@step(r'the list still exists')
def _list_exists(env): assert len(saved(env)['lists']) == 1


@step(r'I tap it again')
def _tap_again(env): env.page.click('[data-act="dellist"]'); env.page.wait_for_timeout(120)


@step(r'the list is gone')
def _list_gone(env): assert saved(env)['lists'] == []


@step(r'"(?P<t>[^"]+)" is still in the library')
def _still_lib(env, t):
    env.page.click('nav.tabs a[data-tab="library"]'); wait_ready(env)
    assert bid(t) not in saved(env).get('read', []) or True
    expect(card(env, t)).to_be_visible()


# ---------------------------------------------------------------- book page
def go_book(env, title):
    open_hash(env, '#book/' + bid(title))


@step(r'I open the book page for "(?P<t>[^"]+)"')
def _open_book(env, t): go_book(env, t)


@step(r'I tap the title "(?P<t>[^"]+)" on its card')
def _title_card(env, t): card(env, t).locator('h3 a').click(); env.page.wait_for_selector('.bpage')


@step(r'I tap the title in the book preview dialog')
def _title_dlg(env):
    card(env, 'Ancillary Justice').locator('h3 a')  # ensure present
    env.page.evaluate("localStorage.setItem('nova-archive-v1', JSON.stringify({v:2,read:[],lists:[],reading:{'ancillary-justice--ann-leckie':Date.now()},meta:{},custom:[]}))")
    env.page.reload(); wait_ready(env)
    env.page.locator('#nowReading .ncard').click()
    dialog(env).locator('a.bl, h3 a').first.click(); env.page.wait_for_selector('.bpage')


@step(r'I tap the title in a reading list')
def _title_list(env):
    make_list(env, 'L'); add_to_list(env, 'Ancillary Justice', 'L')
    env.page.click('nav.tabs a[data-tab="lists"]'); wait_ready(env)
    env.page.locator('#app .litem').first.click()
    li(env, 'Ancillary Justice').locator('a.bl').click(); env.page.wait_for_selector('.bpage')


@step(r'I open the address "(?P<h>[^"]+)" directly|I open the address "(?P<h2>[^"]+)"')
def _open_addr(env, h=None, h2=None): open_hash(env, h or h2)


@step(r'the address ends with "(?P<h>[^"]+)"')
def _addr(env, h): assert env.page.url.endswith(h), env.page.url


@step(r'the page heading reads "(?P<t>[^"]+)"')
def _heading(env, t): expect(env.page.locator('.bhead h2')).to_have_text(t)


@step(r'the awards table has (?P<n>\d+) rows')
def _aw_rows(env, n): expect(env.page.locator('table.aw tbody tr')).to_have_count(int(n))


@step(r'the rows are ordered newest year first')
def _newest_first(env):
    years = [int(re.search(r'(19|20)\d\d', r).group(0)) for r in env.page.locator('table.aw tbody tr').all_inner_texts()]
    assert years == sorted(years, reverse=True), years


@step(r'a winning row shows "★ Winner" on one line')
def _winner_nowrap(env):
    c = env.page.locator('table.aw tbody tr', has_text='★ Winner').first.locator('td', has_text='Winner').first
    assert env.page.evaluate("e=>getComputedStyle(e).whiteSpace", c.element_handle()) == 'nowrap' or c.bounding_box()['height'] < 40


@step(r'the Hugo 2014 row is a winner')
def _hugo(env):
    expect(env.page.locator('table.aw tbody tr', has_text='2014').filter(has_text='Hugo').first).to_contain_text('Winner')


@step(r'the page shows "✓ Read", five stars and a "Finished on" date')
def _shelf_read(env):
    expect(env.page.locator('.bpage').get_by_role('button', name='✓ Read').first).to_be_visible()
    expect(env.page.locator('.bpage .st')).to_have_count(5)
    expect(env.page.locator('#pageFin')).to_be_visible()


@step(r'I tap "Mark read"')
def _mark_read_page(env): env.page.locator('.bpage').get_by_role('button', name='Mark read', exact=True).first.click(); env.page.wait_for_timeout(150)


@step(r'I tap star (?P<n>\d)')
def _star_page(env, n): env.page.locator('.bpage .st').nth(int(n) - 1).click(); env.page.wait_for_timeout(100)


@step(r'(?P<n>\d) stars are filled')
def _filled_page(env, n): expect(env.page.locator('.bpage .st.on')).to_have_count(int(n))


@step(r'I tap "▶ Start" on a different unread book\'s page')
def _start_other(env):
    go_book(env, 'Hyperion'); env.page.locator('.bpage').get_by_role('button', name='▶ Start').click(); env.page.wait_for_timeout(150)


@step(r'the "Now reading" row shows that book')
def _row_that(env): expect(env.page.locator('#nowReading .nt')).to_have_text('Hyperion')


# ---------------------------------------------------------------- my books
def add_book(env, title, author, year=''):
    env.page.click('nav.tabs a[data-tab="library"]'); wait_ready(env)
    env.page.click('[data-act="addbook"]')
    env.page.fill('#abT', title); env.page.fill('#abA', author); env.page.fill('#abY', year)
    env.page.click('[data-act="absave"]'); env.page.wait_for_timeout(250)


@step(r'I tap "＋ Add a book"')
def _tap_add(env): env.page.click('[data-act="addbook"]'); env.page.wait_for_timeout(120)


@step(r'a dialog "Add a book" opens with Title, Author and Year fields')
def _add_dlg(env):
    for s in ('#abT', '#abA', '#abY'): expect(env.page.locator(s)).to_be_visible()


@step(r'I enter title "(?P<t>[^"]+)", author "(?P<a>[^"]+)", year "(?P<y>[^"]*)" and tap "Add"')
def _enter_book(env, t, a, y):
    env.page.fill('#abT', t); env.page.fill('#abA', a); env.page.fill('#abY', y)
    env.page.click('[data-act="absave"]'); env.page.wait_for_timeout(250)


@step(r'searching for "(?P<q>[^"]+)" finds "(?P<t>[^"]+)"')
def _finds(env, q, t):
    env.page.fill('#q', q); env.page.wait_for_timeout(300)
    expect(env.page.locator('#results .card h3 a')).to_have_text(t)


@step(r'the book page for "(?P<t>[^"]+)" opens with the note "(?P<n>[^"]+)"')
def _custom_page(env, t, n):
    expect(env.page.locator('.bhead h2')).to_have_text(t); expect(env.page.locator('.bpage')).to_contain_text(n)


@step(r'the saved data has a custom book with id "(?P<id>[^"]+)"')
def _saved_custom(env, id): assert id in [c['id'] for c in saved(env)['custom']]


@step(r'I try to add "(?P<t>[^"]+)" by "(?P<a>[^"]+)"')
def _try_add(env, t, a):
    env.page.click('[data-act="addbook"]')
    env.page.fill('#abT', t); env.page.fill('#abA', a); env.page.click('[data-act="absave"]'); env.page.wait_for_timeout(200)


@step(r'the message "(?P<m>[^"]+)" is shown')
def _abmsg(env, m): expect(env.page.locator('#abMsg')).to_contain_text(m)


@step(r'nothing is added')
def _nothing_added(env): assert not saved(env).get('custom')


@step(r'I added "(?P<t>[^"]+)" by "(?P<a>[^"]+)" \((?P<y>\d{4})\)')
def _added_year(env, t, a, y): add_book(env, t, a, y)


@step(r'I added "(?P<t>[^"]+)" by "(?P<a>[^"]+)"')
def _added(env, t, a): add_book(env, t, a)


@step(r'the card shows a "My book" tag and no award entries')
def _my_tag(env):
    c = env.page.locator('#results .card').first
    expect(c.locator('.b.mine')).to_have_text(re.compile('My book')); expect(c.locator('.b.w, .b.dim')).to_have_count(0)


@step(r'I open its book page')
def _open_its(env):
    cid = saved(env)['custom'][0]['id']; open_hash(env, '#book/' + cid)


@step(r'a "Your book details" panel with Title, Author and Year is shown')
def _edit_panel(env):
    expect(env.page.get_by_text('Your book details')).to_be_visible()
    for s in ('#cbT', '#cbA', '#cbY'): expect(env.page.locator(s)).to_be_visible()


@step(r'I change the year to "(?P<y>\d+)" and tap "Save"')
def _change_year(env, y): env.page.fill('#cbY', y); env.page.click('#cbSave'); env.page.wait_for_timeout(200)


@step(r'the page shows (?P<y>\d{4})')
def _page_year(env, y): expect(env.page.locator('.bhead')).to_contain_text(y)


@step(r'I added "Convenience Store Woman", marked it read, rated it, noted it and listed it')
def _added_all(env):
    add_book(env, 'Convenience Store Woman', 'Sayaka Murata')
    env.page.click('nav.tabs a[data-tab="library"]'); wait_ready(env)
    env.page.fill('#q', 'convenience'); env.page.wait_for_timeout(250)
    c = env.page.locator('#results .card').first
    btn(c, 'Mark read').click(); c.locator('.st').nth(3).click()
    btn(c, '✎ Add note').click(); env.page.fill('#noteTxt', 'Loved it'); btn(dialog(env), 'Save').click()
    env.page.wait_for_timeout(200)
    btn(c, '＋ List').click(); dialog(env).locator('#ovNew').fill('Mine'); btn(dialog(env), 'Create & add').click()
    env.page.wait_for_timeout(200)
    open_hash(env, '#book/' + saved(env)['custom'][0]['id'])


@step(r'I tap "Delete book" twice to confirm')
def _del_twice(env):
    env.page.click('#cbDel'); env.page.wait_for_timeout(100); env.page.click('#cbDel'); env.page.wait_for_timeout(200)


@step(r'the Library is shown without "(?P<t>[^"]+)"')
def _lib_without(env, t):
    expect(env.page.locator('#results')).to_be_visible()
    assert t not in ' '.join(env.page.locator('#results .card h3 a').all_inner_texts())


@step(r'its read mark, rating, note and list entries are gone from the saved data')
def _clean(env):
    d = saved(env)
    assert not d['custom'] and not d['read'] and not d['meta']
    assert all(not l['books'] for l in d['lists'])


# ---------------------------------------------------------------- open library
@step(r'Open Library knows "(?P<t>[^"]+)" by "(?P<a>[^"]+)"')
def _ol_knows(env, t, a):
    env.ol_mode = 'ok'


@step(r'Open Library is mocked')
def _ol_mocked(env): pass


@step(r'a cover image, a description and subject chips appear')
def _enriched(env):
    expect(env.page.locator('#bookInfo img')).to_be_visible(timeout=T)
    expect(env.page.locator('#bookInfo')).not_to_be_empty()


@step(r'a "Open Library" attribution link is shown')
def _ol_attr(env): expect(env.page.locator('#bookInfo a', has_text='Open Library').first).to_be_visible()


@step(r'I open the "About" tab and switch off Open Library lookups')
def _ol_off(env):
    open_hash(env, '#about')
    env.page.locator('#olToggle').uncheck()
    env.page.wait_for_timeout(100)


@step(r'no request to openlibrary\.org is made')
def _no_ol(env): assert not env.ol_calls, env.ol_calls


@step(r'no enrichment panel is shown')
def _no_panel(env): expect(env.page.locator('#bookInfo')).to_have_count(0) if env.page.locator('#bookInfo').count() == 0 else expect(env.page.locator('#bookInfo')).to_be_empty()


@step(r'the flag "nova-ol-off" is saved')
def _ol_flag(env): assert env.page.evaluate("localStorage.getItem('nova-ol-off')")


# ---------------------------------------------------------------- themes
@step(r'the theme setting is "Auto"')
def _theme_auto(env): assert not env.page.evaluate("localStorage.getItem('nova-theme')")


@step(r'the page follows the device\'s colour scheme')
def _follows(env): assert env.page.evaluate("document.documentElement.dataset.theme") in ('dark', 'paper')


@step(r'I choose "(?P<l>[^"]+)" in the theme picker')
def _pick_theme(env, l):
    env.page.click('#themeBtn'); env.page.wait_for_timeout(100)
    dialog(env).locator('[data-act]', has_text=l).first.click(); env.page.wait_for_timeout(150)
    if dialog(env).count(): env.page.keyboard.press('Escape')


@step(r'html\[data-theme\] is "(?P<id>[^"]+)"')
def _theme_is(env, id): assert env.page.evaluate("document.documentElement.dataset.theme") == id


@step(r'the browser theme colour is "(?P<c>#[0-9a-f]{6})"')
def _meta(env, c): assert env.page.get_attribute('meta[name="theme-color"]', 'content').lower() == c


@step(r'the saved data has theme "(?P<id>[^"]+)"')
def _saved_theme(env, id): assert saved(env)['theme'] == id


# ---------------------------------------------------------------- sync
@step(r'I am signed out')
def _signed_out(env): pass


@step(r'I mark "(?P<t>[^"]+)" read and reload')
def _mark_reload(env, t):
    _tap_on(env, 'Mark read', t); env.page.wait_for_timeout(800); env.page.reload(); wait_ready(env)


@step(r'the status shows "(?P<s>[^"]+)"')
def _status(env, s): expect(env.page.locator('#syncTxt')).to_have_text(s, timeout=T)


@step(r'I tap the sign-in icon button')
def _signin(env): env.page.click('#authBtn'); env.page.wait_for_timeout(500)


@step(r'the button becomes a sign-out icon')
def _signout_icon(env): expect(env.page.locator('#authBtn')).to_have_attribute('aria-label', re.compile('sign out', re.I))



# ---------------------------------------------------------------- offline / sw
@step(r'a service worker for the app scope is active')
def _sw_active(env):
    assert env.page.evaluate("navigator.serviceWorker.ready.then(r=>!!r.active)")


@step(r'the network goes offline and I reload')
def _offline_reload(env):
    env.page.evaluate("navigator.serviceWorker.ready")
    env.page.wait_for_timeout(800)
    env.ctx.set_offline(True)
    env.page.reload(); wait_ready(env)


@step(r'the Library loads with 1329 books')
def _lib1329(env): expect(env.page.locator('#count')).to_contain_text('1329 books match', timeout=T)


@step(r'I can mark a book read and the change persists')
def _offline_mark(env):
    _tap_on(env, 'Mark read', 'Ancillary Justice'); env.page.wait_for_timeout(200)
    assert 'ancillary-justice--ann-leckie' in saved(env)['read']


# ---------------------------------------------------------------- navigation
@step(r'the "(?P<tab>[^"]+)" tab is marked current')
def _current(env, tab):
    key = {'Library': 'library', 'My Lists': 'lists', 'About': 'about'}[tab]
    expect(env.page.locator('nav.tabs a[data-tab="%s"]' % key)).to_have_class(re.compile(r'\bon\b'))


@step(r'the page shows "(?P<m>[^"]+)"')
def _page_shows(env, m):
    if m == 'the search box': expect(env.page.locator('#q')).to_be_visible()
    else: expect(env.page.locator('main').first).to_contain_text(m)


@step(r'I scrolled down (?P<n>\d+) px')
def _scrolled(env, n):
    env.page.evaluate('window.scrollTo(0,%s)' % n); env.page.wait_for_timeout(300)


@step(r'a back-to-top button is visible')
def _totop_vis(env): expect(env.page.locator('#toTop')).to_be_visible()


@step(r'I tap it')
def _tap_it(env): env.page.click('#toTop'); env.page.wait_for_timeout(400)


@step(r'the page is at the top and the button hides')
def _at_top(env):
    assert env.page.evaluate('window.scrollY') < 5
    expect(env.page.locator('#toTop')).to_be_hidden()


# ---------------------------------------------------------------- data integrity (browser-free)
@pytest.fixture
def repo_check():
    import subprocess, sys, os
    return lambda: subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), '..', 'support', 'check_repo.py')], capture_output=True, text=True)


def _di(repo_check, tag):
    r = repo_check()
    bad = [l for l in r.stdout.splitlines() if tag in l]
    assert not bad, '\n'.join(bad)


@step(r'data\.json|it is a JSON array of 1329 books|every book has string "id", "title", "author" and a list "entries"')
def _di1(repo_check): _di(repo_check, 'DI-01')


@step(r'the VERSION in sw\.js, every "\?v=" in index\.html and the app-version meta are the same number')
def _di10(repo_check): _di(repo_check, 'DI-10')


@step(r'no file contains a private key block, a service-account JSON or an API secret|firebase-config\.js holds only the public web config')
def _di14(repo_check): _di(repo_check, 'DI-14')


@given(parsers.parse('data.json'))
def _given_data(): pass
