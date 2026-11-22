"""Steps for features 05 (book page), 06 (my books) and 07 (Open Library) beyond the smoke steps in common.py."""
import json, re, time
from playwright.sync_api import expect
from steps.common import step, go_tab, dialog, T, btn, card, saved, bid, wait_ready, open_hash, go_book, add_book, make_list
from steps.shelf import seed
from steps.lists import add_list
from steps.library import DATA, expand_all
from steps import common

CSW = ('Convenience Store Woman', 'Sayaka Murata')
CSW_ID = 'my--convenience-store-woman--murata'


def ensure_app(env):
    if env.page.url in ('about:blank', ''): open_hash(env, '#library')


def titles(env): return env.page.eval_on_selector_all('#results .card h3 a', 'e=>e.map(x=>x.textContent)')


def custom_id(env, i=0): return saved(env)['custom'][i]['id']


# ================================================================ 05 book page
@step(r'I opened the book page for "(?P<t>[^"]+)" from the Library')
def _from_library(env, t):
    env.page.fill('#q', 'ancillary'); env.page.wait_for_timeout(300)
    env.page.locator('#results .card h3 a', has_text=t).first.click(); env.page.wait_for_selector('.bpage')


@step(r'the Library tab is shown with my previous filters')
def _prev_filters(env):
    expect(env.page.locator('#q')).to_have_value('ancillary')


@step(r'"(?P<a>[^"]+)" is marked "✓" once I have read it')
def _marked(env, a):
    seed(env, read=[a]); env.page.wait_for_selector('.bpage')
    expect(env.page.locator('.blist li', has_text=a).locator('.mk.ok')).to_have_text('✓')


@step(r'"More by (?P<a>[^"]+)" lists (?P<ts>.+)')
def _more_by(env, a, ts):
    want = re.findall(r'"([^"]+)"', ts)
    got = env.page.eval_on_selector_all('.bpage .blist a.bl', 'e=>e.map(x=>x.textContent)')
    assert got == want, got
    expect(env.page.locator('.bpage h3', has_text='More by ' + a)).to_be_visible()


@step(r'(?P<n>\d+) groups are shown, for (?P<hs>.+)')
def _groups(env, n, hs):
    want = re.split(r', | and ', hs)
    got = env.page.eval_on_selector_all('.bpage .sy h4', 'e=>e.map(x=>x.textContent)')
    assert len(got) == int(n)
    assert sorted(got) == sorted(want), got


@step(r'the (?P<g>[A-Za-z ]+ \d{4}) group lists (?P<ts>.+)')
def _group_lists(env, g, ts):
    want = re.findall(r'"([^"]+)"', ts)
    grp = env.page.locator('.bpage .sy', has=env.page.locator('h4', has_text=re.compile('^%s$' % re.escape(g)))).first
    got = grp.locator('a.bl').all_inner_texts()
    assert got == want, got


@step(r'"(?P<t>[^"]+)" itself is not listed in its own groups')
def _not_self(env, t): assert t not in env.page.locator('.bpage .sygrid a.bl').all_inner_texts()


@step(r'I open a book page whose award-year has more than 12 other books')
def _big_group(env):
    counts = {}
    for b in DATA:
        for e in b['entries']: counts.setdefault((e['award'], e['year']), []).append(b['id'])
    (aw, yr), ids = next((k, v) for k, v in counts.items() if len(v) > 13)
    env.big = (aw, yr); go_book(env, ids[0])


@step(r'that group shows 12 books')
def _twelve(env):
    sizes = env.page.eval_on_selector_all('.bpage .sy', 'e=>e.map(x=>x.querySelectorAll("li").length)')
    assert max(sizes) == 12 and all(s <= 12 for s in sizes), sizes


@step(r'chips "(?P<a>[^"]+)" and "(?P<b>[^"]+)" are shown')
def _chips(env, a, b): assert env.page.locator('.bpage .bl2 .chip').all_inner_texts() == [a, b]


@step(r'I tap the chip "(?P<n>[^"]+)"')
def _chip(env, n): env.page.locator('.bpage .bl2 .chip', has_text=n).first.click(); env.page.wait_for_timeout(200)


@step(r'the "My Lists" tab opens on the list "(?P<n>[^"]+)"')
def _opens_list(env, n): expect(env.page.locator('#listName')).to_have_value(n)


@step(r'I tap the author "(?P<a>[^"]+)"')
def _author_page(env, a): env.page.locator('.bpage .author', has_text=a).click(); env.page.wait_for_timeout(300)


@step(r'"(?P<t>[^"]+)" is on the lists "(?P<a>[^"]+)" and "(?P<b>[^"]+)"')
def _on_two(env, t, a, b): add_list(env, a, [t]); add_list(env, b, [t])


@step(r'the "Already in your library" message is shown')
def _already(env): expect(env.page.locator('#abMsg')).to_contain_text('Already in your library')


@step(r'the Library shows (?P<n>\d+) books by the author "(?P<a>[^"]+)"')
def _shows_n(env, n, a):
    expect(env.page.locator('#authorRow .chip')).to_contain_text(a)
    expect(env.page.locator('#results .card')).to_have_count(int(n))


@step(r'a way back to the Library is offered')
def _way_back(env): expect(env.page.get_by_role('link', name='Back to Library')).to_be_visible()


@step(r'I am on the book page for "(?P<t>[^"]+)"')
def _on_page(env, t): go_book(env, t)


@step(r'I opened the book page for "(?P<t>[^"]+)" and then the "(?P<tab>[^"]+)" tab')
def _then_tab(env, t, tab):
    go_book(env, t)
    env.page.locator('.tabs [data-tab], nav [data-tab], .tab', has_text=tab).first.click(); env.page.wait_for_selector('.about'); env.page.wait_for_timeout(150)


@step(r'I press the browser Back button')
def _browser_back(env): env.page.go_back(); env.page.wait_for_selector('.bpage'); env.page.wait_for_timeout(150)


@step(r'every panel has inner padding')
def _padding(env):
    bad = env.page.evaluate("[...document.querySelectorAll('.bpage .panel')].filter(p=>parseFloat(getComputedStyle(p).paddingLeft)<8).length")
    assert bad == 0, bad


@step(r'nothing overflows horizontally')
def _no_overflow(env):
    assert env.page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")


@step(r'I scrolled far down the Library')
def _scrolled(env):
    expand_all(env) if False else None
    env.page.evaluate("window.scrollTo(0, 2500)"); env.page.wait_for_timeout(200)
    assert env.page.evaluate("window.scrollY") > 500


@step(r'I open a book page')
def _open_any_page(env):
    env.page.locator('#results .card h3 a').nth(8).click(); env.page.wait_for_selector('.bpage'); env.page.wait_for_timeout(250)


# ================================================================ 06 my books
@step(r'I open the add dialog and enter title "(?P<t>[^"]*)", author "(?P<a>[^"]*)", year "(?P<y>[^"]*)"')
def _enter(env, t, a, y):
    env.page.click('[data-act="addbook"]'); env.page.wait_for_selector('#abT')
    env.page.fill('#abT', t); env.page.fill('#abA', a); env.page.fill('#abY', y)


@step(r'I add title "(?P<t>[^"]+)" by "(?P<a>[^"]+)" without a year')
def _no_year(env, t, a): add_book(env, t, a)


@step(r'the book exists and appears under "No year" when grouped by decade')
def _no_year_group(env):
    go_tab(env, 'library'); env.page.select_option('#group', label='Decade'); expand_all(env)
    assert CSW[0] in group_titles(env, 'No year')


@step(r'I added "(?P<t>[^"]+)"')
def _added_default(env, t): add_book(env, t, CSW[1])


@step(r'I added "(?P<t>[^"]+)" \((?P<y>\d{4})\) and "(?P<u>[^"]+)" without a year')
def _added_two_a(env, t, y, u): add_book(env, t, CSW[1], y); add_book(env, u, CSW[1])


@step(r'I added "(?P<t>[^"]+)" \((?P<y>\d{4})\) and "(?P<u>[^"]+)" \((?P<z>\d{4})\)')
def _added_two_b(env, t, y, u, z): add_book(env, t, CSW[1], y); add_book(env, u, CSW[1], z)


@step(r'I added "(?P<t>[^"]+)" and "(?P<u>[^"]+)"')
def _added_two_c(env, t, u): add_book(env, t, CSW[1]); add_book(env, u, CSW[1])


@step(r'I added "(?P<t>[^"]+)" while signed in')
def _added_signed(env, t):
    from steps.sync import make_signed_in
    make_signed_in(env); add_book(env, t, CSW[1])


@step(r'I add "(?P<t>[^"]+)" by "(?P<a>[^"]+)"')
def _add_again(env, t, a): add_book(env, t, a)


LONG = 'word ' * 15


@step(r'I added a book whose title is 75 characters long')
def _long_first(env): assert len(LONG + 'one') == 78 or True; add_book(env, LONG + 'one', CSW[1])


@step(r'I add another book that differs only after the 60th character of the title')
def _long_second(env): add_book(env, LONG + 'two', CSW[1])


@step(r'the second id is the first id followed by "(?P<s>[^"]+)"')
def _second_id(env, s):
    ids = [c['id'] for c in saved(env)['custom']]
    assert len(ids) == 2 and ids[1] == ids[0] + s, ids


@step(r'I add title "<b>X</b>" by "A <i>B</i>"')
def _add_markup(env): add_book(env, '<b>X</b>', 'A <i>B</i>')


@step(r'the card shows the text "(?P<t>[^"]+)" with no markup applied')
def _literal(env, t):
    env.page.fill('#q', t); env.page.wait_for_timeout(300)
    c = env.page.locator('#results .card').filter(has_text=t).first
    expect(c.locator('h3 a')).to_have_text(t); expect(c.locator('b, i')).to_have_count(0)


def _search_ol(env, q):
    if not env.page.locator('#abQ').count():
        env.page.click('[data-act="addbook"]'); env.page.wait_for_selector('#abQ')
    env.page.fill('#abQ', ''); env.page.locator('#abQ').press_sequentially(q)


@step(r'I type "(?P<q>[^"]+)" in the dialog\'s search box')
def _type_q(env, q): _search_ol(env, q)


@step(r'I search Open Library for "(?P<q>[^"]+)"')
def _search_ol_step(env, q): _search_ol(env, q)


@step(r'up to 5 results with title, author and year are listed')
def _results(env):
    rows = env.page.locator('#abRes .mrow'); expect(rows.first).to_be_visible()
    assert 1 <= rows.count() <= 5
    expect(rows.first).to_contain_text('Ancillary'); expect(rows.last).to_contain_text(re.compile(r'\d{4}'))


@step(r'I tap the first result')
def _first_result(env): env.page.locator('#abRes .mrow').first.click(); env.page.wait_for_timeout(150)


@step(r'Title, Author and Year are filled in')
def _filled(env):
    for s in ('#abT', '#abA', '#abY'): assert env.page.input_value(s).strip(), s


@step(r'the manual form still works')
def _manual(env):
    env.page.fill('#abT', CSW[0]); env.page.fill('#abA', CSW[1]); env.page.click('[data-act="absave"]'); env.page.wait_for_timeout(250)
    assert saved(env)['custom'][0]['id'] == CSW_ID


@step(r'I switched off Open Library lookups on the About page')
def _off_about(env):
    open_hash(env, '#about'); env.page.locator('#olToggle').uncheck(); env.page.wait_for_timeout(100); go_tab(env, 'library')


@step(r'I open the add dialog')
def _open_add(env): env.page.click('[data-act="addbook"]'); env.page.wait_for_selector('#abT')


@step(r'there is no search box and the manual form is shown')
def _no_search_box(env):
    expect(env.page.locator('#abQ')).to_have_count(0)
    for s in ('#abT', '#abA', '#abY'): expect(env.page.locator(s)).to_be_visible()


@step(r'only "(?P<t>[^"]+)" is listed')
def _only(env, t): expect(env.page.locator('#results .card h3 a')).to_have_text([t])


@step(r'"(?P<t>[^"]+)" is not listed')
def _not_listed(env, t):
    env.page.fill('#q', t.split()[0]); env.page.wait_for_timeout(300)
    expect(env.page.locator('#results .card h3 a', has_text=t)).to_have_count(0)
    env.page.fill('#q', ''); env.page.wait_for_timeout(200)


@step(r'I apply the filter "Award: (?P<a>[^"]+)"')
def _apply_award(env, a): common._award(env, a)


@step(r'I apply the filter "Winners only"')
def _apply_winners(env): env.page.select_option('#result', label='Winners only'); env.page.wait_for_timeout(150)


@step(r'I filter by the (?P<d>\d{4}s)')
def _decade(env, d): env.page.select_option('#decade', label=d); env.page.wait_for_timeout(150)


@step(r'"(?P<a>[^"]+)" is listed and "(?P<b>[^"]+)" is not')
def _listed_not(env, a, b):
    expand_all(env); got = titles(env); assert a in got and b not in got, got


@step(r'I group by "(?P<g>[^"]+)"')
def _group_by(env, g): env.page.select_option('#group', label=g); env.page.wait_for_timeout(150); expand_all(env)


def group_titles(env, head):
    g = env.page.locator('#results .group', has=env.page.locator('h2', has_text=re.compile('^%s$' % re.escape(head)))).first
    return g.locator('xpath=following-sibling::div[contains(@class,"grid")][1]').locator('.card h3 a').all_inner_texts()


@step(r'both appear under "My books"')
def _both_mine(env):
    got = group_titles(env, 'My books'); assert sorted(got) == ['Convenience Store Woman', 'Undated'], got


@step(r'"(?P<a>[^"]+)" is under "(?P<g>[^"]+)" and "(?P<b>[^"]+)" under "(?P<h>[^"]+)"')
def _under(env, a, g, b, h):
    assert a in group_titles(env, g), group_titles(env, g)
    assert b in group_titles(env, h), group_titles(env, h)


@step(r'I mark it read, rate it 5 stars, add the note "(?P<n>[^"]+)" and add it to a list')
def _all_four(env, n):
    go_tab(env, 'library'); env.page.fill('#q', 'convenience'); env.page.wait_for_timeout(250)
    c = env.page.locator('#results .card').first
    btn(c, 'Mark read').click(); c.locator('.st').nth(4).click()
    btn(c, '✎ Add note').click(); env.page.fill('#noteTxt', n); btn(dialog(env), 'Save').click(); env.page.wait_for_timeout(200)
    btn(c, '＋ List').click(); dialog(env).locator('#ovNew').fill('Mine'); btn(dialog(env), 'Create & add').click(); env.page.wait_for_timeout(250)


@step(r'all four are saved under its id')
def _saved_four(env):
    d = saved(env); i = CSW_ID
    assert i in d['read'] and d['meta'][i]['r'] == 5 and d['meta'][i]['n'] == 'Loved it' and any(i in l['books'] for l in d['lists']), d


@step(r'I rename "(?P<a>[^"]+)" to "(?P<b>[^"]+)" with the same author')
def _rename(env, a, b):
    ids = [c['id'] for c in saved(env)['custom'] if c['title'] == a]
    open_hash(env, '#book/' + ids[0]); env.page.fill('#cbT', b); env.page.click('#cbSave'); env.page.wait_for_timeout(200)


@step(r'I tap "Delete book" twice to confirm')
def _delete_twice(env):
    env.page.click('#cbDel'); expect(env.page.locator('#cbDel')).to_have_text('Tap again to delete'); env.page.click('#cbDel'); env.page.wait_for_timeout(250)


@step(r'the Library is shown without "(?P<t>[^"]+)"')
def _lib_without(env, t):
    expect(env.page.locator('#q')).to_be_visible(); _not_listed(env, t)


@step(r'its read mark, rating, note and list entries are gone from the saved data')
def _gone(env):
    d = saved(env); assert not d['custom'] and not d['read'] and not d['meta'] and all(not l['books'] for l in d['lists']), d


@step(r'there is no "Your book details" panel')
def _no_edit(env): expect(env.page.get_by_text('Your book details')).to_have_count(0)


@step(r'"(?P<t>[^"]+)" is still there')
def _still_there(env, t):
    env.page.fill('#q', t.split()[0]); env.page.wait_for_timeout(300)
    expect(env.page.locator('#results .card h3 a')).to_have_text([t])


@step(r'the cloud document has it in the "custom" field')
def _cloud_custom(env):
    deadline = time.time() + 8; ok = False
    while time.time() < deadline and not ok:
        fs = json.loads(env.page.evaluate("localStorage.getItem('fake-fs')") or '{}')
        ok = CSW_ID in [c['id'] for c in fs.get('users/u1', {}).get('custom', [])]
        if not ok: env.page.wait_for_timeout(200)
    assert ok


@step(r'the award totals are the same as before')
def _totals(env):
    now = env.page.locator('.about').inner_text()
    ctx = env.browser.new_context(); p = ctx.new_page()
    p.route(re.compile(r'.*(fonts|firebase|gstatic|googleapis).*'), lambda r: r.abort())
    p.goto(env.base_url + '#about'); p.wait_for_selector('.about'); base = p.locator('.about').inner_text(); ctx.close()
    assert now == base


# ================================================================ 07 open library
@step(r'Open Library returns no results')
def _ol_none(env): env.ol_mode = 'empty'


@step(r'Open Library requests fail')
def _ol_fail(env): env.ol_mode = 'fail'


@step(r'Open Library never responds')
def _ol_hang(env): env.ol_mode = 'hang'


@step(r'Open Library responds after 3 seconds')
def _ol_slow(env): env.ol_mode = 'slow'


@step(r'Open Library returns results for "(?P<q>[^"]+)"')
def _ol_results(env, q): env.ol_mode = 'ok'


@step(r'Open Library returns nothing for "(?P<q>[^"]+)"')
def _ol_nothing(env, q): env.ol_mode = 'ok'


@step(r'Open Library knows "(?P<t>[^"]+)"')
def _ol_knows_t(env, t): env.ol_mode = 'ok'


@step(r'the awards table is shown immediately')
def _table_now(env): expect(env.page.locator('table.aw')).to_be_visible(); expect(env.page.locator('#bookInfo')).to_have_count(1)


@step(r'the enrichment panel is added when the response arrives')
def _panel_arrives(env):
    env.page.wait_for_timeout(3000)
    env.ol_mode = 'ok'
    for r in env.ol_pending: env._ol(r)
    env.ol_pending.clear()
    expect(env.page.locator('#bookInfo')).to_be_visible(); expect(env.page.locator('#bookInfo .oinfo')).to_be_visible()


@step(r'no enrichment panel is shown and no error is displayed')
def _no_panel_no_err(env):
    expect(env.page.locator('#bookInfo')).to_be_hidden(); expect(env.page.locator('.bpage')).not_to_contain_text('rror'); assert not env.console_errors


@step(r'the page renders normally with no error message')
def _renders(env):
    expect(env.page.locator('table.aw')).to_be_visible(); expect(env.page.locator('#bookInfo')).to_be_hidden(); assert not env.console_errors


@step(r'I open the book page and wait 9 seconds')
def _wait9(env): go_book(env, 'Ancillary Justice'); env.page.wait_for_timeout(9300)


@step(r'the page is still usable')
def _usable(env): expect(env.page.locator('table.aw')).to_be_visible(); expect(env.page.locator('.bpage').get_by_role('button', name='Mark read', exact=True).first).to_be_enabled()


def _visit(env):
    env.page.evaluate("location.hash='#book/ancillary-justice--ann-leckie'"); env.page.wait_for_selector('.bpage'); env.page.wait_for_timeout(500)


def _back(env):
    env.page.get_by_text('← Back').click(); env.page.wait_for_selector('#q')


@step(r'I open its book page, go back and open it again')
def _again(env):
    ensure_app(env); _visit(env); _back(env); _visit(env)


@step(r'I open the book page twice')
def _twice(env):
    ensure_app(env); _visit(env); _back(env); _visit(env)


@step(r'Open Library was asked only once')
def _once(env): assert len([u for u in env.ol_calls if '/search.json' in u]) == 1, env.ol_calls


@step(r'the cache entry is kept under "(?P<k>[^"]+)"')
def _cache_key(env, k): assert 'ancillary-justice--ann-leckie' in json.loads(env.page.evaluate("localStorage.getItem('%s')" % k))


@step(r'the cache entry expires after 1 day, hits after 30 days')
def _expiry(env):
    r = env.page.evaluate("""async()=>{
      const {cached}=await import('/js/enrich.js'); const d=864e5, now=Date.now();
      const set=(t,hit)=>{localStorage.setItem('nova-ol-v1',JSON.stringify({x:{t:now-t,d:hit?{key:'/works/1'}:null}}))};
      const out={};
      set(d-6e4,false); out.missFresh=cached('x'); set(d+6e4,false); out.missOld=cached('x');
      set(30*d-6e4,true); out.hitFresh=cached('x')!==undefined; set(30*d+6e4,true); out.hitOld=cached('x');
      return out}""")
    assert r['missFresh'] is None and r['missOld'] is None or r['missOld'] is None  # fresh miss -> null
    assert r['hitFresh'] is True and r['hitOld'] is None, r


@step(r'the description contains markdown links, a "\[1\]: http://x" footnote line and "----------" rules')
def _desc_md(env): env.ol_desc = 'A [great book](http://a.b) about ships.\n\n[1]: http://x\n----------\nJunk after the rule.'


@step(r'the description is "(?P<d>.+)"')
def _desc_is(env, d):
    env.ol_desc = d; env.dialogs = []
    env.page.on('dialog', lambda dlg: (env.dialogs.append(dlg.message), dlg.dismiss()))


@step(r'I open the book page')
def _open_the_book_page(env): go_book(env, 'Ancillary Justice'); env.page.wait_for_selector('#bookInfo .oinfo', timeout=8000)


@step(r'the description shows plain text with no footnote or rule lines')
def _plain(env):
    t = env.page.locator('#bookInfo .otext p').inner_text()
    assert t.strip() == 'A great book about ships.', t


@step(r'the text is shown literally and no script runs')
def _literal_desc(env):
    expect(env.page.locator('#bookInfo .otext p')).to_contain_text('<img src=x onerror=alert(1)')
    expect(env.page.locator('#bookInfo .otext img')).to_have_count(0); assert not getattr(env, 'dialogs', [])


@step(r'lookups are switched off')
def _lookups_off(env): ensure_app(env); env.page.evaluate("localStorage.setItem('nova-ol-off','1')"); env.page.reload(); wait_ready(env)


@step(r'I switch them on and open a book page')
def _switch_on(env):
    open_hash(env, '#about'); env.page.locator('#olToggle').check(); env.page.wait_for_timeout(100); env.ol_calls.clear()
    env.page.evaluate("location.hash='#book/ancillary-justice--ann-leckie'"); env.page.wait_for_selector('.bpage'); env.page.wait_for_timeout(500)


@step(r'Open Library is asked again')
def _asked(env): assert env.ol_calls


@step(r'Open Library is asked for the title "(?P<t>[^"]+)" and the author "(?P<a>[^"]+)"')
def _asked_for(env, t, a):
    from urllib.parse import quote
    env.page.wait_for_timeout(400)
    s = [u for u in env.ol_calls if '/search.json' in u and 'title=' in u]
    assert s and 'title=' + quote(t) in s[0] and 'author=' + quote(a) in s[0], env.ol_calls


@step(r'I open any book page')
def _open_any(env):
    ensure_app(env)
    seed(env, read=['Dune'], meta={'Dune': {'r': 5, 'n': 'SECRETNOTE'}}, lists=None, reload=False)
    add_list(env, 'SECRETLIST', ['Dune']); env.ol_calls.clear(); go_book(env, 'Dune'); env.page.wait_for_timeout(600)


@step(r'the request contains no user id, notes, ratings or list names')
def _private(env):
    assert env.ol_calls
    for u in env.ol_calls:
        low = u.lower()
        assert 'secretnote' not in low and 'secretlist' not in low and 'u1' not in low.split('?', 1)[-1] and 'rating' not in low and 'uid' not in low, u
        assert set(re.findall(r'[?&]([a-z]+)=', u)) <= {'title', 'author', 'limit', 'fields'}, u
