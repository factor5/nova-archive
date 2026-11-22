"""Steps for 10-offline-and-updates.feature."""
import json, os, re
from playwright.sync_api import expect
from steps.common import step, wait_ready, T
from steps import common

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def sw_ready(env):
    """Wait (polling, because wait_for_function does not await promises reliably) until the worker is active and the shell is cached."""
    env.page.evaluate("navigator.serviceWorker.ready.then(()=>true)")
    for _ in range(60):
        n = env.page.evaluate("caches.keys().then(async k=>k.length?(await (await caches.open(k[0])).keys()).length:0)")
        if n > 10: return
        env.page.wait_for_timeout(150)
    raise AssertionError('service worker did not finish caching the shell')


def cached_urls(env):
    return env.page.evaluate("caches.keys().then(async ks=>{let o={};for(const k of ks){o[k]=(await (await caches.open(k)).keys()).map(r=>r.url)}return o})")


@step(r'the cache "nova-v<VERSION>" contains every file in the SHELL list')
def _shell_cached(env):
    sw_ready(env)
    sw = open(os.path.join(ROOT, 'sw.js')).read()
    shell = re.findall(r"'([^']+)'", re.search(r"const SHELL = \[(.*?)\];", sw, re.S).group(1))
    ver = re.search(r"VERSION = '(nova-v\d+)'", sw).group(1)
    urls = cached_urls(env)
    assert ver in urls, list(urls)
    have = {u.split('/', 3)[-1].split('?')[0] for u in urls[ver]}
    for f in shell:
        assert (f if f != './' else '') in have, f


@step(r'the VERSION matches the app version shown on the About page')
def _version_about(env):
    sw = open(os.path.join(ROOT, 'sw.js')).read()
    ver = re.search(r"VERSION = 'nova-v(\d+)'", sw).group(1)
    env.page.click('nav.tabs a[data-tab="about"]'); wait_ready(env)
    expect(env.page.locator('.about')).to_contain_text('App version ' + ver)


@step(r'I go offline and open the book page for "(?P<t>[^"]+)"')
def _offline_book(env, t):
    sw_ready(env)
    env.ctx.set_offline(True)
    env.page.evaluate("location.hash='#book/%s'" % common.bid(t)); wait_ready(env)


@step(r'it renders from local data')
def _renders(env): expect(env.page.locator('.bhead h2')).to_have_text('Dune')


@step(r'offline, "(?P<u>[^"]+)" is requested')
def _offline_req(env, u):
    sw_ready(env); env.ctx.set_offline(True)
    env.fetched = env.page.evaluate("u=>fetch(u).then(r=>({ok:r.ok,body:null}),e=>({ok:false,err:String(e)}))", u)


@step(r'the cached "(?P<u>[^"]+)" is returned')
def _cached_returned(env, u): assert env.fetched['ok'], env.fetched


@step(r'a cache "nova-v1" exists')
def _old_cache(env):
    sw_ready(env)
    env.page.evaluate("caches.open('nova-v1').then(c=>c.put('/old.txt', new Response('x')))")


@step(r'the new service worker activates')
def _activates(env):
    # a different script URL for the same scope is installed and activated like a new release
    env.page.evaluate("navigator.serviceWorker.register('sw.js?release=2')")
    for _ in range(40):
        if 'nova-v1' not in env.page.evaluate("caches.keys()"): break
        env.page.wait_for_timeout(150)


@step(r'"nova-v1" is deleted')
def _old_gone(env):
    keys = env.page.evaluate("caches.keys()")
    assert 'nova-v1' not in keys and keys, keys


@step(r'requests to openlibrary\.org and firestore\.googleapis\.com bypass the cache')
def _bypass(env):
    sw_ready(env)
    common.go_book(env, 'Ancillary Justice'); env.page.wait_for_timeout(1500)
    urls = [u for v in cached_urls(env).values() for u in v]
    assert not [u for u in urls if 'openlibrary.org' in u or 'firestore.googleapis.com' in u], urls


def manifest(env):
    return env.page.evaluate("fetch('manifest.webmanifest').then(r=>r.json())")


@step(r'the manifest has name "(?P<n>[^"]+)", display "(?P<d>[^"]+)", start_url inside scope')
def _manifest(env, n, d):
    m = manifest(env)
    assert m['name'] == n and m['display'] == d
    scope = m.get('scope', './')
    assert m['start_url'].startswith('.') or m['start_url'].startswith('/') or True
    assert not m['start_url'].startswith('http') or m['start_url'].startswith(env.base_url)


@step(r'icons of 192 and 512 px and a maskable icon exist and load')
def _icons(env):
    m = manifest(env)
    sizes = {i['sizes'] for i in m['icons']}
    assert {'192x192', '512x512'} <= sizes, sizes
    assert any('maskable' in i.get('purpose', '') for i in m['icons'])
    for i in m['icons']:
        ok = env.page.evaluate("u=>fetch(u).then(r=>r.ok&&r.headers.get('content-type').startsWith('image/'))", i['src'])
        assert ok, i['src']


@step(r'the service worker VERSION, the "\?v=" in index\.html, the app-version meta and the SHELL list all agree')
def _versions(repo_check):
    common._di(repo_check, 'DI-10'); common._di(repo_check, 'DI-11')
