"""Steps for 01-library-browsing.feature (beyond the smoke steps in common.py)."""
import json, os, re, urllib.parse
from playwright.sync_api import expect
from steps.common import step, go_tab, dialog, T, btn, card, saved, FILTERS
from steps import common

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA = json.load(open(os.path.join(ROOT, 'data.json')))
AWARD_KEYS = {'Hugo': 'Hugo Award', 'Nebula': 'Nebula Award', 'Clarke': 'Arthur C. Clarke Award', 'Campbell': 'John W. Campbell Memorial Award',
              'Locus': 'Locus Award', 'PKD': 'Philip K. Dick Award', 'BSFA': 'BSFA Award'}


def expand_all(env):
    """Click 'Show more' until every card/group is rendered."""
    for _ in range(40):
        m = env.page.locator('[data-act="more"]')
        if not m.count(): return
        m.first.click(); env.page.wait_for_timeout(60)


def headings(env):
    return [h.strip() for h in env.page.eval_on_selector_all('#results .group h2', 'e=>e.map(x=>x.textContent)')]


@step(r'(?P<n>\d+) cards are shown')
def _n_cards(env, n): expect(env.page.locator('#results .card')).to_have_count(int(n))


@step(r'a "(?P<t>[^"]+)" button is shown')
def _btn_shown(env, t): expect(env.page.get_by_role('button', name=t, exact=True)).to_be_visible()


@step(r'the "Show more" button reads "(?P<t>[^"]+)"')
def _more_reads(env, t): expect(env.page.locator('[data-act="more"]')).to_have_text(t)


@step(r'I look at the "(?P<l>[^"]+)" link of the card for "(?P<t>[^"]+)"')
def _look_link(env, l, t):
    row, name = l.split(' ', 1)
    env.href = card(env, t).locator('.lr', has_text=row).locator('a', has_text=name).first.get_attribute('href')


@step(r'its address contains "(?P<site>[^"]+)" and the text "(?P<needle>[^"]+)"')
def _link_has(env, site, needle):
    assert site in env.href and needle in urllib.parse.unquote_plus(env.href), env.href


@step(r'every card has the author "(?P<a>[^"]+)"')
def _every_author(env, a):
    got = set(env.page.eval_on_selector_all('#results .card .author', 'e=>e.map(x=>x.textContent)'))
    assert got == {a}, got


@step(r'the card for "(?P<t>[^"]+)" is shown')
def _card_shown(env, t): expect(env.page.locator('#results .card h3 a', has_text=t).first).to_be_visible()


@step(r'I select the "(?P<a>[^"]+)" award filter again')
def _award_again(env, a): common._award(env, a)


@step(r'both pills are shown as selected')
def _pills_on(env): expect(env.page.locator('#awardPills .pill[aria-pressed="true"]')).to_have_count(2)


@step(r'only books with a Hugo win between 2010 and 2019 are shown')
def _hugo_2010s(env):
    expand_all(env)
    cards = env.page.locator('#results .card')
    assert cards.count() > 0
    for badges in env.page.eval_on_selector_all('#results .card', "els=>els.map(c=>[...c.querySelectorAll('.b.w')].map(b=>b.textContent.trim()))"):
        assert any(re.fullmatch(r'★ Hugo 201\d', b) for b in badges), badges


@step(r'I have typed "dune", selected "Hugo", chosen "Winners only", "1960s", "Title A–Z" and grouped by "Year"')
def _everything_set(env):
    env.page.fill('#q', 'dune'); common._award(env, 'Hugo')
    for v, f in (('Winners only', 'Show'), ('1960s', 'Decade'), ('Title A–Z', 'Sort'), ('Year', 'Group by')):
        common._choose(env, v, f)


@step(r'every filter is back to its default')
def _defaults(env):
    for f, v in (('Show', 'Winners & finalists'), ('Status', 'All books'), ('Source', 'All books'), ('Decade', 'All years'), ('Group by', 'No grouping'), ('Sort', 'Most honoured')):
        common._filter_is(env, f, v)
    assert env.page.input_value('#q') == ''
    expect(env.page.locator('#awardPills .pill.on')).to_have_count(0)


@step(r'the "(?P<f>[^"]+)" filter is still "(?P<v>[^"]+)"')
def _still(env, f, v): common._filter_is(env, f, v)


@step(r'the first group heading is "(?P<h>[^"]+)"')
def _first_group(env, h): assert headings(env)[0] == h, headings(env)[:3]


@step(r'the last group heading is "(?P<h>[^"]+)"')
def _last_group(env, h):
    expand_all(env); assert headings(env)[-1] == h, headings(env)[-3:]


@step(r'headings are in descending order')
def _desc(env):
    expand_all(env); hs = [int(h) for h in headings(env)]
    assert hs == sorted(hs, reverse=True), hs


@step(r'each heading shows how many books it holds')
def _counts(env):
    spans = env.page.eval_on_selector_all('#results .group span', 'e=>e.map(x=>x.textContent)')
    assert spans and all(re.fullmatch(r'\d+ books?', t) for t in spans), spans[:3]


@step(r'a book appears once in every year it has a nomination or win')
def _once_per_year(env):
    expand_all(env)
    total = sum(int(t.split()[0]) for t in env.page.eval_on_selector_all('#results .group span', 'e=>e.map(x=>x.textContent)'))
    want = sum(len({e['year'] for e in b['entries']}) for b in DATA)
    assert total == want, (total, want)


@step(r'the group headings are, in order, (?P<hs>.+)')
def _award_groups(env, hs):
    expand_all(env)
    assert headings(env) == re.findall(r'"([^"]+)"', hs), headings(env)


@step(r'in the "(?P<g>[^"]+)" group the first card is "(?P<t>[^"]+)"')
def _group_first(env, g, t):
    env.group = g; expand_all(env)
    h = env.page.locator('#results .group', has=env.page.locator('h2', has_text=re.compile('^%s$' % g))).first
    first = h.locator('xpath=following-sibling::div[contains(@class,"grid")][1]').locator('.card h3 a').first
    expect(first).to_have_text(t)


@step(r'the group has (?P<n>\d+) books')
def _group_size(env, n):
    h = env.page.locator('#results .group', has=env.page.locator('h2', has_text=re.compile('^%s$' % env.group))).first
    expect(h.locator('span')).to_have_text('%s books' % n)


@step(r'the first card has its latest award year equal to (?P<y>\d+)')
def _latest(env, y):
    years = env.page.eval_on_selector_all('#results .card:first-child .badges .b', "e=>e.map(x=>+x.textContent.match(/\\d{4}/)[0])")
    assert max(years) == int(y), years


@step(r'the first card has the author "(?P<a>[^"]+)"')
def _first_author(env, a): expect(env.page.locator('#results .card .author').first).to_have_text(a)


@step(r'the card titles are in ascending locale order')
def _title_order(env):
    assert env.page.evaluate("""()=>{const t=[...document.querySelectorAll('#results .card h3 a')].map(a=>a.textContent);
      return t.every((x,i)=>i===0||t[i-1].localeCompare(x)<=0)}""")


@step(r'I have selected the "(?P<a>[^"]+)" award filter')
def _have_award(env, a): common._award(env, a)


@step(r'a dialog "Your next transmission" shows one book card')
def _surprise_dlg(env):
    expect(dialog(env)).to_contain_text('Your next transmission'); expect(dialog(env).locator('.card')).to_have_count(1)


@step(r'that book has a Hugo badge')
def _has_hugo(env): expect(dialog(env).locator('.badges .b', has_text='Hugo').first).to_be_visible()


@step(r'that book is not marked read')
def _not_read(env): expect(dialog(env).get_by_role('button', name='Mark read')).to_be_visible()


@step(r'the dialog shows a book card again')
def _again(env): expect(dialog(env).locator('.card')).to_have_count(1)


@step(r'I close the dialog')
def _close_dlg(env): btn(dialog(env), 'Close').click()


@step(r'the dialog is gone')
def _dlg_gone(env): expect(dialog(env)).to_have_count(0)


@step(r'I mark every book that matches the "Locus" filter as read')
def _all_locus_read(env):
    ids = [b['id'] for b in DATA if any(e['award'].startswith('Locus Award') for e in b['entries'])]
    env.page.evaluate("ids=>localStorage.setItem('nova-archive-v1', JSON.stringify({v:2,read:ids,lists:[],reading:{},meta:{},custom:[],updatedAt:1}))", ids)
    env.page.reload(); common.wait_ready(env); common._award(env, 'Locus')


@step(r'I have a reading list called "(?P<n>[^"]+)"')
def _have_list_called(env, n):
    common.make_list(env, n); go_tab(env, 'library')


@step(r'I tap "(?P<n>[^"]+)" in the list dialog')
def _tap_list_dlg(env, n): dialog(env).locator('[data-act]', has_text=n).first.click(); env.page.wait_for_timeout(150)


@step(r'the list "(?P<n>[^"]+)" holds (?P<c>\d+) books')
def _list_count(env, n, c):
    l = [x for x in saved(env)['lists'] if x['name'] == n][0]
    assert len(l['books']) == int(c), len(l['books'])


@step(r'I typed "(?P<t>[^"]*)" in the search box')
def _typed(env, t): common._search(env, t)


@step(r'nothing overflows the screen horizontally')
def _no_over(env): assert env.page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth") <= 0


@step(r'the header, tabs and filters are fully visible without sideways scrolling')
def _header_visible(env):
    for sel in ('header, .hud', 'nav.tabs', '#q', '#sort', '#awardPills'):
        box = env.page.locator(sel).first.bounding_box()
        assert box and box['x'] >= 0 and box['x'] + box['width'] <= 390 + 1, (sel, box)


@step(r'the author "(?P<a>[^"]+)" comes before "(?P<b>[^"]+)"')
def _author_before(env, a, b):
    h = headings(env); assert a in h and b in h, (a, b)
    assert h.index(a) < h.index(b), (h.index(a), h.index(b))
