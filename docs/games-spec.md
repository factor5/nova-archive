# Book games: spec

Status: **PR 2 built: shell, engine and a rough playable *Dune*, hidden behind the beta switch.** Decisions below were settled in a Q&A with the author on 2026-11-28. The pilot is one game (*Dune*); more games are decided only after it has been played.

## 1. The idea (author's words, lightly edited)

Introduce some interactivity in the app: a simple game for each of the winner books, based on the book's plot.

Follow-up: a data-only quiz is not interactive enough. The author prefers real games: **puzzle, mapping, top-down RPG, run and gun, questing** and similar. Start with a few to see how it goes, using either an open-source light game engine or a handcrafted one. Spoilers are not a concern.

One game per winner book is out of scope: 296 of the 1,329 books have at least one win, and handcrafting that many is not realistic.

## 2. Goals and non-goals

### Goals
- Small, real games (not quizzes) tied to individual books, played on the author's phone.
- Audience: the author. Other visitors may see the games once they are released, but nothing is tuned for them (no tutorials, no onboarding).
- Short sessions: **2 to 5 minutes per run**, with a reason to replay (score or time), not a long campaign.

### Success and stop rule
- **Success:** the author finishes the first game on the phone at least twice unprompted and wants another one.
- **Stop:** if it is not fun or not comfortable after two rounds of playtest changes, the games idea stops there.

### Scope cap
- **At most 3 games.** Build one, play it, then decide on the next. More than 3 only after all 3 have been played.
- One pilot at a time: the second game does not start until the first has passed or failed the success test.

### Non-goals
- A game for every winner book.
- Data-only quizzes (may return later as a cheap extra, see section 11).
- Sound in the pilot.
- Syncing results to Firestore in the pilot.
- Menus, levels, story screens or achievements before the core loop has been played (see 9.3).

## 3. Player experience and navigation

- **Entry point:** a **Play** button on the book page, shown only for books that have a game. No Games tab or library filter while there are at most 3 games.
- **Beta switch:** until the author approves a game, games are hidden for everyone. A **"Show games (beta)"** switch on the About page shows them on that device (stored in local storage, not synced). The switch is removed once games are released.
- **Shell around every game:** start screen, pause, restart, score and best score, and an always visible **Back to book**. The game never traps the user.
- **Pause:** automatic when the tab is hidden or the app goes to the background; manual pause button.
- **Orientation:** designed for portrait, still playable in landscape, never scrolls.
- **Spoilers:** allowed. Games may show plot events and endings. Games are not locked behind marking a book read.

## 4. Technical architecture

### 4.1 Engine
- **Kaplay** (successor to Kaboom), copied into the repo at `js/vendor/kaplay.mjs`, pinned to a version noted in the file header.
- Measured before committing: **KAPLAY 3001.0.19, `dist/kaplay.mjs`: 188.5 KB minified, 69 KB gzipped**, under the ~250 KB limit, so LittleJS was not needed. MIT licence, copied as `js/vendor/kaplay.LICENSE.md`.
- KAPLAY is given the game stage as its `root`; without one it sets `width`, `height` and `margin` on the app's `<html>` and `<body>`. After `quit()` the shell clears KAPLAY's module state (`_k.k = null`) so the next Play starts clean.
- Fits the existing setup: plain ES module, no build step.

### 4.2 Files and loading
- One file per game: `js/games/<slug>.js`, loaded with dynamic `import()` only when **Play** is tapped, so the main app stays light.
- Shared shell: `js/games/shell.js` (start, pause, restart, score, best score, back, auto-pause), loaded on Play.
- Registry, beta switch, best scores and open/close: `js/games.js`. It sits directly in `js/` (so it is precached and the book page works offline) and is kept small.
- Route: `#play/<book id>` shows the book page with the game layer on top, so the phone's Back button closes the game.

### 4.3 Game module interface
Each game module (`js/games/<slug>.js`) exports:

```
export const meta = {background: '#rrggbb', help: ['line', ...]}
export default function start(k, {seed, canvas, reducedMotion, onScore, onGameOver})
  -> {update(dt), draw(), destroy(), state?()}
```

- `k`: the KAPLAY context, created by the shell on a canvas it owns. The game uses it for drawing, `dt` and keys.
- The **shell owns the loop**: it calls `update(dt)` only while playing (in steps of at most 1/30 s) and `draw()` every frame. Pause therefore needs nothing from the game.
- `seed`: random seed (fixed in tests, random in play). `onScore(n)` reports the running score; `onGameOver(score, reason)` ends the run.
- Touch and mouse: the game listens to pointer events on `canvas` itself and removes them in `destroy()`.
- `state()` is optional and only used by tests (`window.__novaGameState()` when the test hook is set).
- Test hook: `window.__novaGameTest = {seed, speed}`, set by the test suite before Play. Never set in normal use.

### 4.4 Registry entry (content model)
| Field | Example | Notes |
|---|---|---|
| `bookId` | id from `data.json` | Book ids are stable |
| `slug` | `dune` | File name under `js/games/` |
| `title` | "Spice Run" | Original game title |
| `genre` | "top-down survival" | |
| `blurb` | one line | Own wording |
| `status` | `beta` / `released` | `beta` shows only with the switch on |

### 4.5 Timing
- All movement and timers use **elapsed time (delta time), never frame counts**. The reference phone has a high refresh-rate screen (up to 144 Hz); frame-based speed would make the game run faster there.
- The frame rate is capped at 60 fps (KAPLAY `maxFPS`) and the canvas pixel density at 2, to spare the battery on high refresh-rate screens.

### 4.6 Graphics and sound
- Graphics drawn in code: shapes, a small pixel palette, possibly emoji. No image files, no cover art, no character likenesses.
- **No sound in the pilot.** WebAudio-generated sound, off by default, may come later if the game sticks.

### 4.7 Offline and caching
- Rely on the existing service worker (network first, cache fallback for same-origin files): **a game works offline after it has been played once**.
- Add the engine and game files to the precache only if testing shows it is needed. Keeps the install size the same for people who never play.
- Known limit: each app update starts a new cache, so after an update the game must be played once online again before it works offline.
- Version bump with `python3 tools/bump.py` for every app change, as usual.

## 5. Content and rights

### 5.1 Plot source
- For each game, Claude reads the book's **Wikipedia plot section as a reference only**, while writing the game, never at runtime.
- Claude proposes the **genre** (with a one-line reason; the author decides) and **3 to 5 plot moments** written in Claude's own words, and says how complete the source was. Books without a usable Wikipedia plot are flagged; the author's corrections carry more weight there, or another book is chosen.
- The **author approves or corrects** the plot moments before anything is built. The author is the fact-checker; Claude does not invent plot details.

### 5.2 Copyright stance
- Original mechanics, original wording, art drawn in code.
- Allowed: the book title as a label, and generic in-world terms (for example spice, sandworm, ICE).
- Not allowed: character names, quotes from the books, cover art, and **no text copied word for word from Wikipedia** (its text is CC BY-SA), Goodreads or other plot summaries.

## 6. Pilot game: *Dune* (design sheet)

Plot moments for the intro and flavour text: to be drafted from Wikipedia and approved by the author (5.1) before PR 2.

- **Genre:** top-down survival, endless score run.
- **Goal:** collect as much spice as possible before being caught.
- **Core tension (greed vs noise):** moving fast makes noise, and noise draws the sandworm. Moving slowly is quiet and safe, but a storm (or timer) closes in, so you cannot just creep.
- **Controls (touch):** floating joystick. Put a thumb down anywhere and drag; how far you drag sets speed, and speed is noise. **Keyboard on desktop:** arrow keys or WASD, with a key (for example Shift) to switch between walking and running.
- **Lose:** the worm reaches you, or the storm catches you.
- **Score:** spice collected. Best score kept locally (section 7).
- **Difficulty:** rises over time (worm speed or sensitivity, storm pressure, spice spread). Exact curve tuned through playtests.
- **Feedback on screen:** a visible noise meter, and clear signs of where the worm is heading.
- **Art:** shapes on a sand palette in the spirit of the existing Dune theme, colour-blind safe (worm and danger must not rely on red vs green alone).
- **Reduced motion:** no screen shake.

## 7. Data and sync
- Pilot: **best score per game in local storage only.** Nothing written to `users/<uid>`; the Firestore document and the data-integrity checks are unchanged.
- Syncing results may be added later if the author cares about scores across devices.

## 8. Phone requirements and performance
- **Reference phone:** Motorola Edge 30 (installed Android PWA).
- **Frame rate:** target 60 fps, never below 30 fps on the reference phone.
- **Start time:** about 1 second from tapping Play. This is a soft target, not a hard requirement: report if it is far off, do not over-tune.
- Touch only on the phone; keyboard also works on desktop.
- Large touch targets for shell buttons.

## 9. Test plan and process

### 9.1 Automated (pytest-bdd + Playwright)
- New feature file **`tests/features/13-games.feature`** for the shared shell: beta switch shows and hides Play, Play launches the game, canvas appears, pause and resume, auto-pause on tab hidden, Back to book returns to the book page, best score is kept after a run.
- **Per-game smoke scenario** for *Dune* with a **fixed random seed**: loads, responds to input, can end a run, no console errors.
- Existing smoke scenarios keep gating merges via CI.

### 9.2 Manual playtest (author, on the phone)
Checklist for each playtest build:
- Starts quickly and plays smoothly.
- Joystick feels right (no drift, speed easy to control).
- The noise/worm rule is understandable without explanation.
- A run lasts 2 to 5 minutes.
- Pause, background and resume work; Back to book always reachable.
- Portrait and landscape both usable.
- Works offline after the first play.
- Would you play again?

Claude cannot judge fun or touch feel; that comes only from the author's playtests.

### 9.3 Scope rule while building
Nothing beyond the core loop (spice, noise, worm, storm, score) until the author has played it twice: no menus, levels, story screens or achievements.

### 9.4 Feedback
After playing, the author leaves short notes in a PR comment or in chat ("worm too fast", "joystick drifts"). Claude turns them into changes.

## 10. Milestones and PR plan
1. **PR 1 (this document):** spec with all decisions. Docs only.
2. **PR 2:** engine copied into the repo (size measured), shared shell, registry, beta switch on the About page, Play button on the book page, rough playable *Dune* in plain shapes, `13-games.feature` and the *Dune* smoke test. Merged to `main` hidden behind the beta switch, so the author can play it in the real installed app.
3. **PR 3 and later:** changes from phone playtests, until *Dune* passes or fails the success test (section 2).
4. **Then:** if it passes, pick the second game (genre and plot moments per section 5), at most 3 in total. Once a game is approved, its status becomes `released`; when all approved, the beta switch is removed.

GitHub Pages serves only `main`, so pull requests cannot be tried on the phone before merging; the beta switch is how unapproved games ship safely.

## 11. Later candidates (not committed)
- Other pilot ideas: *Neuromancer* (puzzle: route a signal through a grid of ICE nodes before a timer ends), *The Martian* (resource puzzle: plan potato plots and water on a small base grid), *The Forever War* (run and gun, time dilation changes the world between levels), *Hyperion* (quest with branching pilgrim stories).
- Cheap extras: data-only quiz modes, daily random book, "guess the book from three clues".
- Sound, synced scores, a Games tab, if games multiply.

## 12. Risks
| Risk | Mitigation |
|---|---|
| Wrong plot details | Wikipedia as reference, own wording, author approves before building (5.1) |
| Scope creep | Cap of 3 games, one at a time, core-loop-only rule (9.3), stop rule (2) |
| Not fun on a phone | Rough playable build early, author playtests, two rounds then stop |
| Performance or battery on the phone | Delta-time movement, frame cap, engine size limit, reference phone |
| Copyright | Original mechanics, wording and art; no names, quotes, covers or copied text (5.2) |
| Engine heavier than expected | Measure before committing; LittleJS fallback |
| Unfinished games visible to visitors | Beta switch, hidden by default |

## 13. Constraints from the existing app
- Static site on GitHub Pages, ES modules, no build step (`js/`, `css/`, `tools/bump.py` keeps the version consistent).
- Installable Android PWA with a service worker (network first for same-origin files, cache fallback).
- Tests: pytest-bdd with Playwright (`tests/`), smoke scenarios gate merges via CI.
- Version bump with `python3 tools/bump.py` for every app change. The script precaches only top-level `css/*.css` and `js/*.js`, so files under `js/games/` and `js/vendor/` stay out of the precache by default, which matches 4.7. Keep any game-related module that sits directly in `js/` small, since every install downloads it.
