"""Steps for 13-games.feature (book games: beta switch, game shell, Spice Run smoke checks).

The game reads window.__novaGameTest = {seed, speed} when it first loads: a fixed seed makes runs repeatable,
speed > 1 runs the game faster so a whole run fits in a test. window.__novaGameState() then returns the game state."""
from playwright.sync_api import expect
from steps.common import step, go_tab, go_book, T

SEED = 7
GAME = '#gameRoot'


def hook(env, speed=1):
    js = 'window.__novaGameTest={seed:%d,speed:%s};' % (SEED, speed)
    env.page.context.add_init_script(js)
    env.page.evaluate(js)


def state(env): return env.page.evaluate('window.__novaGameState && window.__novaGameState()')


def phase(env, p): expect(env.page.locator(GAME)).to_have_attribute('data-phase', p, timeout=T)


def beta_on(env):
    go_tab(env, 'about')
    env.page.check('#gamesToggle')


def start_playing(env, speed):
    hook(env, speed)
    beta_on(env)
    go_book(env, 'Dune')
    env.page.click('#playBtn')
    phase(env, 'start')
    env.page.click('#gPanel button:text-is("Start")')
    phase(env, 'play')


@step(r'games \(beta\) are switched on')
def _beta_on(env): hook(env); beta_on(env)


@step(r'"Show games \(beta\)" is on')
def _beta_is_on(env): expect(env.page.locator('#gamesToggle')).to_be_checked()


@step(r'I switch games \(beta\) off')
def _beta_off(env): env.page.uncheck('#gamesToggle')


@step(r'the book page shows no game')
def _no_game(env):
    expect(env.page.locator('.bpage')).to_be_visible()
    expect(env.page.locator('#bookGame')).to_have_count(0)


@step(r'the book page shows the game "(?P<t>[^"]+)" with a Play button')
def _game_panel(env, t):
    expect(env.page.locator('#bookGame')).to_contain_text(t)
    expect(env.page.locator('#playBtn')).to_be_visible()


@step(r'I tap Play')
def _tap_play(env):
    env.page.click('#playBtn')
    expect(env.page.locator(GAME)).to_be_visible()


@step(r'the game screen shows "(?P<t>[^"]+)" with a play area')
def _screen(env, t):
    expect(env.page.locator(GAME + ' .gtitle')).to_have_text(t)
    box = env.page.locator('#gCanvas').bounding_box()
    assert box and box['width'] > 100 and box['height'] > 100, box


@step(r'the game shows its start screen with "Start" and "Back to book"')
def _start_screen(env):
    phase(env, 'start')
    for label in ('Start', 'Back to book'):
        expect(env.page.locator('#gPanel button', has_text=label)).to_be_visible()


@step(r'I tap the game button "(?P<b>[^"]+)"')
def _game_btn(env, b):
    if b == 'Pause': env.page.click(GAME + ' [data-g=pause]')
    elif b == '← Book': env.page.click(GAME + ' .gbar [data-g=back]')
    else: env.page.click('#gPanel button:text-is("%s")' % b)


@step(r'the game is running')
def _running(env): phase(env, 'play')


@step(r'the game is paused')
def _paused(env): phase(env, 'paused')


@step(r'the game does not move while paused')
def _frozen(env):
    a = state(env)['t']; env.page.wait_for_timeout(500); b = state(env)['t']
    assert a == b, (a, b)


@step(r'the score is 0')
def _score0(env): expect(env.page.locator('#gScore')).to_have_text('0')


@step(r'the game screen is closed')
def _closed(env): expect(env.page.locator(GAME)).to_have_count(0)


@step(r'I go back in the browser')
def _back(env): env.page.go_back(); env.page.wait_for_selector('.bpage', timeout=T)


@step(r'I am playing "Spice Run" from the Dune book page')
def _playing(env): start_playing(env, 1)


@step(r'I am playing "Spice Run" fast from the Dune book page')
def _playing_fast(env): start_playing(env, 3)


@step(r'the page becomes hidden')
def _hidden(env):
    env.page.evaluate("Object.defineProperty(document,'hidden',{value:true,configurable:true});document.dispatchEvent(new Event('visibilitychange'))")


@step(r'I hold the right arrow key for a moment')
def _hold_right(env):
    env.x0 = state(env)['x']
    env.page.keyboard.down('ArrowRight'); env.page.wait_for_timeout(600); env.page.keyboard.up('ArrowRight')


@step(r'the player has moved (?P<d>right|left)')
def _moved(env, d):
    x = state(env)['x']
    assert (x > env.x0 + 10) if d == 'right' else (x < env.x0 - 10), (env.x0, x)


@step(r'I drag far to the left on the play area and hold')
def _drag(env):
    env.x0 = state(env)['x']
    b = env.page.locator('#gCanvas').bounding_box()
    cx, cy = b['x'] + b['width'] * 0.6, b['y'] + b['height'] * 0.6
    m = env.page.mouse
    m.move(cx, cy); m.down(); m.move(cx - 120, cy, steps=6)
    env.page.wait_for_timeout(500)


@step(r"the noise meter is above the worm's hearing level")
def _loud(env):
    n = state(env)['noise']; env.page.mouse.up()
    assert n > 0.3, n


@step(r'I wait for the run to end')
def _until_over(env):
    """Walk to the nearest spice once (so the score is above 0), then stand still until the storm or the worm ends the run."""
    kb, held = env.page.keyboard, set()
    def hold(keys):
        for k in held - keys: kb.up(k)
        for k in keys - held: kb.down(k)
        held.clear(); held.update(keys)
    for _ in range(600):
        s = state(env)
        if not s['alive'] or s['score'] >= 1: break
        sp = min(s['spice'], key=lambda p: (p['x'] - s['x']) ** 2 + (p['y'] - s['y']) ** 2)
        dx, dy = sp['x'] - s['x'], sp['y'] - s['y']
        keys = set()
        if abs(dx) > 4: keys.add('ArrowRight' if dx > 0 else 'ArrowLeft')
        if abs(dy) > 4: keys.add('ArrowDown' if dy > 0 else 'ArrowUp')
        hold(keys)
        env.page.wait_for_timeout(40)
    hold(set())
    env.page.wait_for_selector(GAME + '[data-phase=over]', timeout=60000)
    env.final = int(env.page.locator('#gFinal').inner_text())


@step(r'the game over screen shows the score and "Play again"')
def _over(env):
    expect(env.page.locator('#gFinal')).to_be_visible()
    expect(env.page.locator('#gPanel button', has_text='Play again')).to_be_visible()


@step(r'the game panel shows the best score')
def _best(env):
    assert env.final >= 1, 'the run should have collected at least one spice'
    expect(env.page.locator('.bpage')).to_be_visible()
    expect(env.page.locator('#bookBest')).to_have_text('Best: %d' % env.final)


@step(r'the play area fills the screen below the top bar')
def _fills(env):
    vw, vh = env.page.viewport_size['width'], env.page.viewport_size['height']
    bar = env.page.locator(GAME + ' .gbar').bounding_box()
    c = env.page.locator('#gCanvas').bounding_box()
    assert abs(c['width'] - vw) <= 1 and abs(c['y'] - (bar['y'] + bar['height'])) <= 1 and abs(c['y'] + c['height'] - vh) <= 1, (bar, c, vw, vh)


@step(r'nothing on the game screen overflows horizontally')
def _no_overflow(env):
    d = env.page.evaluate("[document.documentElement.scrollWidth-document.documentElement.clientWidth, (e=>e.scrollWidth-e.clientWidth)(document.getElementById('gameRoot'))]")
    assert d[0] <= 0 and d[1] <= 0, d


def drag_from_middle(env, dx, at=0.5):
    b = env.page.locator('#gCanvas').bounding_box()
    cx, cy = b['x'] + b['width'] * at, b['y'] + b['height'] * 0.6
    env.page.mouse.move(cx, cy); env.page.mouse.down(); env.page.mouse.move(cx + dx, cy, steps=6)
    return cx + dx, cy


@step(r'I drag a short way to the left on the play area and hold')
def _drag_short(env):
    env.x0 = state(env)['x']
    drag_from_middle(env, -40)
    env.page.wait_for_timeout(700)


@step(r"the noise meter is below the worm's hearing level")
def _quiet(env):
    n = state(env)['noise']; env.page.mouse.up()
    assert n < 0.3, n


@step(r'I drag far to the right, then move my thumb back a little to the left and hold')
def _drag_turn(env):
    # start at 20% of the width, push 260 px right (past the 110 px edge, so the base follows),
    # then come back 200 px: a clear left drag if the base followed (a fixed base would still be 60 px to the left of the thumb)
    x, y = drag_from_middle(env, 140, at=0.2)
    env.page.mouse.move(x + 120, y, steps=6)
    env.page.wait_for_timeout(200)
    env.x0 = state(env)['x']
    env.page.mouse.move(x + 120 - 200, y, steps=4)
    env.page.wait_for_timeout(500)


@step(r'the player has moved left since the turn')
def _left_since(env):
    x = state(env)['x']; env.page.mouse.up()
    assert x < env.x0 - 10, (env.x0, x)
