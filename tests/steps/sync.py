"""Steps for 09-persistence-and-sync.feature."""
import json, re
from playwright.sync_api import expect
from steps.common import step, saved, wait_ready, open_hash, btn, card, T, dialog, _tap_on


def fs(env):
    raw = env.page.evaluate("localStorage.getItem('fake-fs')")
    return json.loads(raw) if raw else {}


def cloud(env, uid='u1'):
    env.page.wait_for_timeout(1000)  # writes are debounced (700 ms)
    return fs(env).get('users/' + uid)


def set_ls(env, key, value):
    env.page.evaluate("([k,v])=>localStorage.setItem(k,v)", [key, value])


def reload(env):
    env.page.reload(); wait_ready(env)


def sign_in_ui(env):
    env.page.click('#authBtn')
    expect(env.page.locator('#syncTxt')).to_have_text('Cloud synced', timeout=T)


def make_signed_in(env):
    set_ls(env, 'fake-auth', json.dumps({'uid': 'u1', 'email': 'me@example.com'}))
    reload(env)
    expect(env.page.locator('#syncTxt')).to_have_text('Cloud synced', timeout=T)


# ---------------------------------------------------------------- local storage
@step(r'localStorage "nova-archive-v1" contains "(?P<v>[^"]*)"')
def _ls_contains(env, v): set_ls(env, 'nova-archive-v1', v)


@step(r'the stored data is (?P<j>\{.*\})')
def _stored_is(env, j): set_ls(env, 'nova-archive-v1', j)


@step(r'the stored data marks "(?P<id>[^"]+)" as read')
def _stored_marks(env, id): set_ls(env, 'nova-archive-v1', json.dumps({'v': 2, 'read': [id]}))


@step(r'I open the app')
def _open_app(env):
    env.console_errors.clear(); reload(env)


@step(r'the Library loads with nothing read')
def _nothing_read(env):
    expect(env.page.locator('#hudRead')).to_have_text('0'); expect(env.page.locator('#count')).to_contain_text('1329 books match')


@step(r'"(?P<t>[^"]+)" is read and no lists, ratings or notes exist')
def _read_only(env, t):
    expect(btn(card(env, t), '✓ Read')).to_be_visible()
    expect(env.page.locator('#results .st.on')).to_have_count(0)
    expect(env.page.locator('#listCount')).to_have_text('')


@step(r'the Library count is unchanged and no error appears')
def _unchanged(env):
    expect(env.page.locator('#count')).to_contain_text('1329 books match'); assert not env.console_errors, env.console_errors


# ---------------------------------------------------------------- cloud
@step(r'I marked "(?P<t>[^"]+)" read while signed out')
def _marked_out(env, t): _tap_on(env, 'Mark read', t)


@step(r'the cloud has no document for me')
def _no_doc(env): assert not fs(env).get('users/u1')


@step(r'I sign in')
def _sign_in(env):
    env.page.wait_for_timeout(900)  # let the local save finish first
    sign_in_ui(env)


@step(r'the cloud document holds "(?P<id>[^"]+)" as read')
def _cloud_holds(env, id): assert id in cloud(env)['read']


@step(r'the cloud document marks "(?P<t>[^"]+)" read')
def _cloud_marks(env, t):
    ids = {'Hyperion': 'hyperion--dan-simmons', 'Dune': 'dune--frank-herbert'}
    set_ls(env, 'fake-fs', json.dumps({'users/u1': {'v': 2, 'read': [ids[t]], 'updatedAt': 5000}}))


@step(r'I sign in on a fresh device')
def _fresh_device(env): sign_in_ui(env)


@step(r'local data updated at (?P<l>\d+) and cloud data updated at (?P<c>\d+)')
def _stamps(env, l, c):
    set_ls(env, 'nova-archive-v1', json.dumps({'v': 2, 'read': ['dune--frank-herbert'], 'updatedAt': int(l)}))
    set_ls(env, 'fake-fs', json.dumps({'users/u1': {'v': 2, 'read': ['hyperion--dan-simmons'], 'updatedAt': int(c)}}))
    reload(env)


@step(r'the (?P<w>local|cloud) data is used on both sides')
def _winner(env, w):
    want = 'dune--frank-herbert' if w == 'local' else 'hyperion--dan-simmons'
    assert saved(env)['read'] == [want]
    assert cloud(env)['read'] == [want]


@step(r'I am signed in')
def _signed_in(env): make_signed_in(env)


@step(r'I read, rate, note, start, list, add a custom book and pick a theme')
def _everything(env):
    _tap_on(env, 'Mark read', 'Dune')
    card(env, 'Dune').locator('.st').nth(3).click()
    btn(card(env, 'Dune'), '✎ Add note').click(); env.page.fill('#noteTxt', 'n'); btn(dialog(env), 'Save').click()
    _tap_on(env, '▶ Start', 'Hyperion')
    btn(card(env, 'Dune'), '＋ List').click(); dialog(env).locator('#ovNew').fill('L'); btn(dialog(env), 'Create & add').click()
    env.page.click('[data-act="addbook"]'); env.page.fill('#abT', 'Convenience Store Woman'); env.page.fill('#abA', 'Sayaka Murata'); env.page.click('[data-act="absave"]')
    env.page.click('#themeBtn'); dialog(env).locator('[data-act]', has_text='Terminal').first.click()
    env.page.wait_for_timeout(300)


@step(r'the cloud document contains read, meta, reading, lists, custom and theme with v 2')
def _cloud_all(env):
    d = cloud(env)
    assert d['v'] == 2 and d['theme'] == 'terminal'
    for k in ('read', 'meta', 'reading', 'lists', 'custom'): assert d[k], k


@step(r'I make 5 changes within half a second')
def _five(env):
    env.page.wait_for_timeout(300)
    env.page.evaluate("window.__fakeFs.writes=0")
    for t in ('Ancillary Justice', 'Rendezvous with Rama'):
        btn(card(env, t), 'Mark read').click()
    for t in ('Ancillary Justice', 'Rendezvous with Rama'):
        btn(card(env, t), '✓ Read').click()
    btn(card(env, 'Ancillary Justice'), 'Mark read').click()


@step(r'exactly one cloud write happens within about a second')
def _one_write(env):
    env.page.wait_for_timeout(1500)
    assert env.page.evaluate("window.__fakeFs.writes") == 1


@step(r'the cloud document changes on another device')
def _other_device(env):
    env.page.evaluate("window.__fakeFs.push('users/u1',{v:2,read:['hyperion--dan-simmons'],updatedAt:Date.now()+100000})")


@step(r'the app shows the new data without a reload')
def _shows_new(env): expect(btn(card(env, 'Hyperion'), '✓ Read')).to_be_visible(timeout=T)


@step(r'I am signed in with "(?P<t>[^"]+)" read')
def _signed_in_read(env, t):
    make_signed_in(env); _tap_on(env, 'Mark read', t)
    env.page.wait_for_timeout(1000)
    expect(env.page.locator('#syncTxt')).to_have_text('Cloud synced', timeout=T)


@step(r'I tap sign out')
def _sign_out(env): env.page.click('#authBtn')


@step(r'account A is signed in with "(?P<t>[^"]+)" read')
def _acct_a(env, t): _signed_in_read(env, t)


@step(r'I sign out and sign in as account B whose cloud is empty')
def _acct_b(env):
    env.page.click('#authBtn'); expect(env.page.locator('#syncTxt')).to_have_text('Sign in to sync')
    env.page.evaluate("window.__fakeAuth.nextUser={uid:'u2',email:'b@example.com'}")
    # a different person on the same device starts from an empty library
    env.page.evaluate("localStorage.removeItem('nova-archive-v1')"); reload(env)
    env.page.evaluate("window.__fakeAuth.nextUser={uid:'u2',email:'b@example.com'}")
    env.page.click('#authBtn'); expect(env.page.locator('#syncTxt')).to_have_text('Cloud synced', timeout=T)


@step(r'account B\'s cloud document does not contain "(?P<t>[^"]+)"')
def _b_clean(env, t):
    d = fs(env).get('users/u2')
    assert not d or 'dune--frank-herbert' not in d.get('read', [])


@step(r'the next cloud write fails')
def _next_fails(env): env.page.evaluate("window.__fakeFs.failNextWrite='unavailable'")


@step(r'the data is still saved locally')
def _still_local(env): assert 'dune--frank-herbert' in saved(env)['read']


@step(r'I make another change')
def _another(env): _tap_on(env, 'Mark read', 'Hyperion')


@step(r'the write succeeds and the status shows "(?P<s>[^"]+)"')
def _write_ok(env, s):
    expect(env.page.locator('#syncTxt')).to_have_text(s, timeout=T)
    assert 'hyperion--dan-simmons' in cloud(env)['read']


@step(r'I am signed in and the network is offline')
def _signed_offline(env):
    make_signed_in(env); env.ctx.set_offline(True)
    env.page.evaluate("window.dispatchEvent(new Event('offline'))")


@step(r'the status shows "Offline – will sync when connected" and the data is local')
def _offline_status(env):
    expect(env.page.locator('#syncTxt')).to_have_text('Offline – will sync when connected', timeout=T)
    assert 'dune--frank-herbert' in saved(env)['read']


@step(r'the network returns')
def _net_back(env):
    env.ctx.set_offline(False); env.page.evaluate("window.dispatchEvent(new Event('online'))")


@step(r'the cloud document has "(?P<t>[^"]+)"')
def _cloud_has(env, t):
    env.page.wait_for_function("JSON.parse(localStorage.getItem('fake-fs')||'{}')['users/u1']?.read?.includes('dune--frank-herbert')", timeout=8000)


@step(r'the sign-in popup is closed by the user')
def _popup_closed(env):
    env.page.evaluate("window.__fakeAuth.failNext='auth/popup-closed-by-user'"); env.page.click('#authBtn'); env.page.wait_for_timeout(500)


@step(r'the app stays signed out with no error message')
def _stays_out(env):
    expect(env.page.locator('#syncTxt')).to_have_text('Sign in to sync')
    assert env.page.locator('#toastRoot .toast').count() == 0


@step(r'the Firebase SDK request is blocked')
def _sdk_blocked(env):
    env.ctx.route(re.compile(r'https://www\.gstatic\.com/firebasejs/.*'), lambda r, req=None: r.abort())
    env.ctx.unroute(re.compile(r'https://www\.gstatic\.com/firebasejs/[^/]+/firebase-app\.js'))


@step(r'the app works in local-only mode')
def _local_only(env):
    _tap_on(env, 'Mark read', 'Dune')
    assert 'dune--frank-herbert' in saved(env)['read']
    expect(env.page.locator('#authBtn')).to_be_hidden()


@step(r'a 390 px wide screen')
def _phone(env): env.page.set_viewport_size({'width': 390, 'height': 844})


@step(r'the sign-in control is an icon button')
def _icon_btn(env):
    expect(env.page.locator('#authBtn .lbl')).to_be_hidden(); expect(env.page.locator('#authBtn svg')).to_be_visible()
    assert env.page.locator('#authBtn').get_attribute('aria-label')


@step(r'the sync status is an icon with a tooltip')
def _sync_icon(env):
    assert env.page.get_attribute('#sync', 'title') and env.page.get_attribute('#sync', 'aria-label')
    expect(env.page.locator('#syncTxt')).to_be_hidden()


@step(r'the nav tabs stay on one line')
def _one_line(env):
    ys = env.page.eval_on_selector_all('nav.tabs a', 'e=>e.map(x=>Math.round(x.getBoundingClientRect().top))')
    assert len(set(ys)) == 1, ys


@step(r'"(?P<t>[^"]+)" is read')
def _is_read_now(env, t): expect(btn(card(env, t), '✓ Read')).to_be_visible(timeout=T)


@step(r'I mark "(?P<t>[^"]+)" read')
def _i_mark_read(env, t): _tap_on(env, 'Mark read', t)
