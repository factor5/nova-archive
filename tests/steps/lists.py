"""Steps for 04-reading-lists.feature (beyond the smoke steps in common.py)."""
import json, re, time
from playwright.sync_api import expect
from steps.common import step, go_tab, dialog, T, btn, card, saved, bid, wait_ready, li, scope
from steps import common
from steps.shelf import seed
from steps.library import DATA

TITLES = r'"[^"]+"(?: \(read\))?(?:, "[^"]+"(?: \(read\))?)*(?: and "[^"]+"(?: \(read\))?)?'


def parse_titles(s): return re.findall(r'"([^"]+)"( \(read\))?', s)


def lists_now(env): return saved(env).get('lists', [])


def add_list(env, name, titles):
    """Create a list straight in the saved data and reload."""
    cur = env.page.evaluate("JSON.parse(localStorage.getItem('nova-archive-v1')||'{}')")
    lists = cur.get('lists', [])
    lists.append({'id': 'seed%d' % (len(lists) + 1), 'name': name, 'books': [bid(t) for t in titles]})
    cur.update({'v': 2, 'lists': lists, 'updatedAt': int(time.time() * 1000)})
    env.page.evaluate("o=>localStorage.setItem('nova-archive-v1', JSON.stringify(o))", cur)
    env.page.reload(); wait_ready(env)


def open_list(env, name):
    go_tab(env, 'lists'); env.page.locator('#app .litem', has_text=name).first.click(); env.page.wait_for_timeout(120)


def item_titles(env): return env.page.eval_on_selector_all('#app .item .t a', 'e=>e.map(x=>x.textContent)')


@step(r'the list "(?P<n>[^"]+)" holds (?P<ts>%s)' % TITLES)
def _list_holds(env, n, ts):
    """Then: the saved list contains these books. Given: if there is no such list yet, create it."""
    pairs = parse_titles(ts); titles = [t for t, _ in pairs]
    existing = [l for l in lists_now(env) if l['name'] == n]
    if existing:
        assert existing[0]['books'] == [bid(t) for t in titles] or all(bid(t) in existing[0]['books'] for t in titles), existing[0]['books']
        return
    seed(env, read=[t for t, r in pairs if r], reload=False)
    add_list(env, n, titles)


@step(r'I type "(?P<n>[^"]+)" in the new list box and press Enter')
def _enter_create(env, n):
    env.page.fill('#newListName', n); env.page.press('#newListName', 'Enter'); env.page.wait_for_timeout(150)


@step(r'the list "(?P<n>[^"]+)" exists')
def _exists(env, n): assert n in [l['name'] for l in lists_now(env)]


@step(r'I tap "Create" with the new list box empty')
def _create_empty(env): env.page.fill('#newListName', ''); env.page.click('[data-act="newlist"]'); env.page.wait_for_timeout(150)


@step(r'no list is created')
def _none_created(env): assert lists_now(env) == []


@step(r'the new list box has focus')
def _box_focus(env): assert env.page.evaluate("document.activeElement.id") == 'newListName'


@step(r'I create a list named with 80 characters')
def _create_80(env):
    go_tab(env, 'lists'); env.page.locator('#newListName').focus(); env.page.keyboard.insert_text('a' * 80)
    env.page.click('[data-act="newlist"]'); env.page.wait_for_timeout(150)


@step(r'the saved name has 60 characters')
def _name60(env): assert len(lists_now(env)[0]['name']) == 60


@step(r'I create a list named "(?P<n>[^"]+)"')
def _create_named(env, n): common.make_list(env, n)


@step(r'the name is shown literally as "(?P<n>[^"]+)"')
def _literal(env, n):
    expect(env.page.locator('#app .litem span', has_text=n)).to_be_visible(); expect(env.page.locator('#app .litem i')).to_have_count(0)


@step(r'"(?P<t>[^"]+)" is on the list "(?P<n>[^"]+)"')
def _is_on(env, t, n): add_list(env, n, [t])


@step(r'I tap "＋ List \(1\)" on "(?P<t>[^"]+)" and uncheck "(?P<n>[^"]+)"')
def _uncheck(env, t, n):
    card(env, t).get_by_role('button', name=re.compile(r'＋ List')).click()
    dialog(env).locator('[data-act]', has_text=n).first.click(); dialog(env).get_by_role('button', name='Done').click(); env.page.wait_for_timeout(120)


@step(r'the card for "(?P<t>[^"]+)" shows "＋ List" without a count')
def _no_count(env, t): expect(card(env, t).get_by_role('button', name=re.compile(r'＋ List')).first).to_have_text('＋ List')


@step(r'I have lists "(?P<a>[^"]+)" and "(?P<b>[^"]+)"')
def _two_lists(env, a, b): add_list(env, a, []); add_list(env, b, [])


@step(r'I add "(?P<t>[^"]+)" to both')
def _add_both(env, t):
    for n in ('A', 'B'):
        card(env, t).get_by_role('button', name=re.compile(r'＋ List')).click()
        dialog(env).locator('[data-act]', has_text=re.compile('^.*%s' % n)).first.click(); dialog(env).get_by_role('button', name='Done').click(); env.page.wait_for_timeout(120)


@step(r'both lists hold "(?P<t>[^"]+)"')
def _both_hold(env, t): assert all(bid(t) in l['books'] for l in lists_now(env)) and len(lists_now(env)) == 2


@step(r'I selected the "(?P<a>[^"]+)" award filter')
def _selected_award(env, a): common._award(env, a)


@step(r'I use "Add all results to a list" and tap "(?P<n>[^"]+)"')
def _use_addall(env, n):
    env.page.click('[data-act="addall"]'); dialog(env).locator('[data-act]', has_text=n).first.click(); env.page.wait_for_timeout(150)


@step(r'the list holds (?P<c>\d+) books')
def _holds_count(env, c): assert len(lists_now(env)[0]['books']) == int(c)


@step(r'I open the list and tap "(?P<b>[^"]+)" on "(?P<t>[^"]+)"')
def _open_tap(env, b, t):
    go_tab(env, 'lists'); env.page.locator('#app .litem').first.click(); btn(li(env, t), b).click(); env.page.wait_for_timeout(150)


@step(r'"(?P<t>[^"]+)" shows "✓ Finish" and "Stop"')
def _fin_stop(env, t): expect(btn(li(env, t), '✓ Finish')).to_be_visible(); expect(btn(li(env, t), 'Stop')).to_be_visible()


@step(r'the rating dialog opens')
def _rating_opens(env): expect(dialog(env).locator('#noteTxt')).to_be_visible()


@step(r'I tap the title "(?P<t>[^"]+)" in the list')
def _title_in_list(env, t):
    go_tab(env, 'lists'); env.page.locator('#app .litem').first.click(); li(env, t).locator('a.bl').click(); env.page.wait_for_selector('.bpage')


@step(r'I have lists "(?P<a>[^"]+)" holding "(?P<x>[^"]+)" and "(?P<b>[^"]+)" holding "(?P<y>[^"]+)"')
def _two_holding(env, a, x, b, y): add_list(env, a, [x]); add_list(env, b, [y])


@step(r'I tap "(?P<n>[^"]+)" in the side list')
def _side_tap(env, n): go_tab(env, 'lists'); env.page.locator('#app .litem', has_text=n).first.click(); env.page.wait_for_timeout(120)


@step(r'the list "(?P<n>[^"]+)" is open and shows "(?P<t>[^"]+)"')
def _open_shows(env, n, t):
    expect(env.page.locator('#listName')).to_have_value(n); expect(env.page.locator('#app .item .t a')).to_have_text(t)


@step(r'the order is still (?P<ts>.+)')
def _order_still(env, ts): assert item_titles(env) == re.findall(r'"([^"]+)"', ts)


@step(r'I moved "(?P<a>[^"]+)" above "(?P<b>[^"]+)" in "(?P<n>[^"]+)"')
def _moved(env, a, b, n):
    add_list(env, n, [b, a]); open_list(env, n)
    li(env, b).get_by_label('Move down').click(); env.page.wait_for_timeout(150)
    assert item_titles(env) == [a, b]


@step(r'I reload the page and open "(?P<n>[^"]+)"')
def _reload_open(env, n): env.page.reload(); wait_ready(env); open_list(env, n)


@step(r'I choose "(?P<v>[^"]+)" in the list\'s sort menu')
def _lsort(env, v):
    open_list(env, 'Classics') if not env.page.locator('#lsort').count() else None
    env.page.select_option('#lsort', label=v); env.page.wait_for_timeout(120)


@step(r'I choose "My order"')
def _my_order(env): env.page.select_option('#lsort', label='My order'); env.page.wait_for_timeout(120)


@step(r'the order shown is (?P<ts>.+)')
def _order_shown(env, ts): assert item_titles(env) == re.findall(r'"([^"]+)"', ts), item_titles(env)


@step(r'the "↑" and "↓" buttons are hidden')
def _arrows_hidden(env): expect(env.page.locator('#app [data-act="up"], #app [data-act="down"]')).to_have_count(0)


@step(r'the "↑" and "↓" buttons are back')
def _arrows_back(env): expect(env.page.locator('#app [data-act="up"]').first).to_be_visible()


@step(r'"(?P<t>[^"]+)" is last')
def _is_last(env, t): assert item_titles(env)[-1] == t


@step(r'I tap "✕" on "(?P<t>[^"]+)"')
def _remove(env, t):
    if not env.page.locator('#app .item').count(): open_list(env, 'Classics')
    li(env, t).get_by_label('Remove from list').click(); env.page.wait_for_timeout(150)


@step(r'the list holds only "(?P<t>[^"]+)"')
def _holds_only(env, t): assert lists_now(env)[0]['books'] == [bid(t)]


@step(r'I clear its name and leave the field')
def _clear_name(env):
    go_tab(env, 'lists'); env.page.locator('#app .litem').first.click()
    env.page.fill('#listName', ''); env.page.locator('#listName').blur(); env.page.wait_for_timeout(150)


@step(r'the name goes back to "(?P<n>[^"]+)"')
def _name_back(env, n): expect(env.page.locator('#listName')).to_have_value(n)


@step(r'I opened the "(?P<n>[^"]+)" list and tapped "Delete list" once')
def _del_once(env, n): open_list(env, n); env.page.click('[data-act="dellist"]')


@step(r'(?P<s>\d+) seconds pass')
def _pass(env, s): env.page.wait_for_timeout(int(s) * 1000 + 400)


@step(r'the button reads "Delete list" again')
def _del_again(env): expect(env.page.locator('[data-act="dellist"]')).to_have_text('Delete list')


@step(r'I open the "(?P<n>[^"]+)" list')
def _open_named(env, n): open_list(env, n)


@step(r'the clipboard holds these lines:')
def _clip(env, docstring):
    got = env.page.evaluate("navigator.clipboard.readText()")
    assert got.strip() == docstring.strip(), got


@step(r'the clipboard cannot be written')
def _clip_blocked(env):
    env.page.evaluate("Object.defineProperty(navigator.clipboard,'writeText',{value:()=>Promise.reject(new Error('blocked')),configurable:true})")


@step(r'a dialog "Copy list" shows the same text in a selectable box')
def _copy_dlg(env):
    expect(dialog(env)).to_contain_text('Copy list')
    v = dialog(env).locator('textarea').input_value()
    assert v.strip() == 'Classics\n1. Dune — Frank Herbert [read]\n2. Hyperion — Dan Simmons', v


@step(r'the list still holds "(?P<t>[^"]+)"')
def _still_holds(env, t):
    open_list(env, 'Classics') if not env.page.locator('#app .item').count() else None
    expect(env.page.locator('#app .item .t a')).to_have_text(t)


@step(r'a list with a long name and several books with long titles')
def _long_list(env):
    longest = [b['title'] for b in sorted(DATA, key=lambda b: -len(b['title']))[:5]]
    add_list(env, 'A list with a very long name that keeps on going and going beyond any screen width', longest)
    env.page.set_viewport_size({'width': 390, 'height': 844}); open_list(env, 'A list')


@step(r'each item\'s buttons wrap below its text')
def _wrap(env):
    bad = env.page.evaluate("""()=>[...document.querySelectorAll('#app .item')].filter(it=>{
      const t=it.querySelector('.t').getBoundingClientRect(), b=it.querySelector('.ib').getBoundingClientRect();
      return !(b.top>=t.bottom-1 || b.right<=t.left+1) || b.right>document.documentElement.clientWidth}).length""")
    assert bad == 0, bad


@step(r'the saved data has a list that holds an unknown book id')
def _unknown_id(env):
    cur = {'v': 2, 'read': [], 'reading': {}, 'meta': {}, 'custom': [], 'updatedAt': 1,
           'lists': [{'id': 'x1', 'name': 'Classics', 'books': ['gone--nobody', bid('Dune')]}]}
    env.page.evaluate("o=>localStorage.setItem('nova-archive-v1', JSON.stringify(o))", cur)
    env.console_errors.clear(); env.page.reload(); wait_ready(env)


@step(r'I open the list')
def _open_the_list(env): go_tab(env, 'lists'); env.page.locator('#app .litem').first.click(); env.page.wait_for_timeout(150)


@step(r'the unknown entry is not shown and the page does not fail')
def _unknown_skipped(env):
    assert item_titles(env) == ['Dune']; assert not env.console_errors, env.console_errors


@step(r'the book page for "(?P<t>[^"]+)" is shown')
def _bp_shown(env, t):
    expect(env.page.locator('.bpage')).to_be_visible(); expect(env.page.locator('.bpage h2').first).to_contain_text(t)
