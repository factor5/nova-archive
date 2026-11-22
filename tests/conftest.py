"""Playwright + pytest-bdd wiring. See tests/README.md.

Each scenario gets a brand-new browser context (empty storage). Outside services are
always replaced: Firebase by tests/support/mocks, Open Library by canned data, fonts blocked.
"""
import functools, http.server, json, os, re, socketserver, threading
import pytest
from playwright.sync_api import sync_playwright

pytest_plugins = ['steps.common', 'steps.sync', 'steps.offline', 'steps.themes', 'steps.nav', 'steps.integrity']
from playwright.sync_api import expect as _expect
_expect.set_options(timeout=6000)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MOCKS = os.path.join(os.path.dirname(__file__), 'support', 'mocks')
OL = json.load(open(os.path.join(MOCKS, 'openlibrary.json')))
PNG = bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c6360000002000001e221bc330000000049454e44ae426082')


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store'); super().end_headers()


@pytest.fixture(scope='session')
def base_url():
    h = functools.partial(_Quiet, directory=ROOT)
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), h)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield 'http://127.0.0.1:%d/' % srv.server_address[1]
    srv.shutdown()


@pytest.fixture(scope='session')
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


class Env:
    """Per-scenario state shared by the steps."""
    def __init__(self, browser, base_url, request):
        self.browser, self.base_url = browser, base_url
        marks = {m.name for m in request.node.iter_markers()}
        self.mobile = 'mobile' in marks
        self.sw = 'sw' in marks
        self.firebase = 'firebase-mock' in marks
        self.ol_calls = []
        self.ol_mode = 'ok'
        self.ol_off = False
        self.console_errors = []
        self.ctx = None
        self.page = None
        self.last_card = None

    def new_page(self, firebase=None, mobile=None):
        if self.ctx: self.ctx.close()
        mob = self.mobile if mobile is None else mobile
        self.ctx = self.browser.new_context(
            viewport={'width': 390, 'height': 844} if mob else {'width': 1280, 'height': 900},
            service_workers='allow' if self.sw else 'block',
            reduced_motion='reduce', locale='en-US', accept_downloads=False)
        self.ctx.grant_permissions(['clipboard-read', 'clipboard-write'], origin=self.base_url.rstrip('/'))
        fb = self.firebase if firebase is None else firebase
        self.ctx.route(re.compile(r'https://(fonts\.googleapis|fonts\.gstatic)\.com/.*'), lambda r: r.abort())
        self.ctx.route(re.compile(r'.*/firebase-config\.js(\?.*)?$'), lambda r: r.fulfill(
            status=200, content_type='text/javascript',
            body=open(os.path.join(MOCKS, 'firebase-config.js')).read() if fb else '/* local only */'))
        for n in ('app', 'auth', 'firestore'):
            self.ctx.route(re.compile(r'https://www\.gstatic\.com/firebasejs/[^/]+/firebase-%s\.js' % n), lambda r, req=None, n=n: r.fulfill(
                status=200, content_type='text/javascript', headers={'access-control-allow-origin': '*'},
                body=open(os.path.join(MOCKS, 'firebase-%s.js' % n)).read()))
        self.ctx.route(re.compile(r'https://covers\.openlibrary\.org/.*'), lambda r: r.fulfill(status=200, body=PNG, content_type='image/png', headers={'access-control-allow-origin': '*'}))
        self.ctx.route(re.compile(r'https://openlibrary\.org/.*'), self._ol)
        self.page = self.ctx.new_page()
        self.page.set_default_timeout(8000)
        self.page.on('pageerror', lambda e: self.console_errors.append(str(e)))
        self.page.on('console', lambda m: m.type == 'error' and 'Failed to load resource' not in m.text and self.console_errors.append(m.text))
        return self.page

    def _ol(self, route):
        url = route.request.url
        self.ol_calls.append(url)
        cors = {'access-control-allow-origin': '*'}
        if self.ol_mode == 'fail': return route.abort()
        if self.ol_mode == 'hang': return
        if '/search.json' in url:
            low = url.lower()
            if self.ol_mode == 'empty' or 'nothing' in low or 'zzzz' in low: body = OL['searchEmpty']
            elif 'solaris' in low: body = OL['searchSolaris']
            else: body = OL['searchAncillary']
            return route.fulfill(status=200, content_type='application/json', headers=cors, body=json.dumps(body))
        if '/works/' in url:
            return route.fulfill(status=200, content_type='application/json', headers=cors, body=json.dumps(OL['work']))
        route.fulfill(status=404, body='{}', headers=cors)

    def close(self):
        if self.ctx: self.ctx.close()


@pytest.fixture
def env(browser, base_url, request):
    e = Env(browser, base_url, request)
    yield e
    e.close()


def pytest_collection_modifyitems(items):
    """Mark every scenario with its feature number (marker f01..f12) so one area can be run: -m f09."""
    for item in items:
        if item.get_closest_marker('wip'): item.add_marker(pytest.mark.skip(reason='wip: automation not possible yet (see tests/README.md)'))
        if item.get_closest_marker('manual'): item.add_marker(pytest.mark.skip(reason='manual scenario: needs a person, a device or real services'))
        from pytest_bdd.scenario import scenario_wrapper_template_registry as reg
        tpl = reg.get(getattr(item, 'function', None))
        if tpl is not None:
            m = re.match(r'(\d\d)-', os.path.basename(tpl.feature.filename))
            if m: item.add_marker(getattr(pytest.mark, 'f' + m.group(1)))
