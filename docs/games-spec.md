# Book games: idea and draft spec

Status: **idea stage, not started.** This file records the original idea, the discussion so far and a first proposal. Expand it into a proper spec before building. Open points are marked **TBD**.

## 1. The idea (author's words, lightly edited)

Introduce some interactivity in the app: a simple game for each of the winner books, based on the book's plot.

Follow-up: a data-only quiz is not interactive enough. The author prefers real games: **puzzle, mapping, top-down RPG, run and gun, questing** and similar. Start with a few to see how it goes, using either an open-source light game engine or a handcrafted one. Spoilers are not a concern.

## 2. Questions and answers so far

**Q: What do you think of one game per winner book?**
A: Good idea, wrong scope. 296 of the 1,329 books have at least one win (data.json), and handcrafting that many games is not realistic. Plot details written by an AI can be wrong, and a wrong detail in a game looks bad. Better: a small engine plus content per book, starting with a handful of hand-picked games.

**Q: Is a data-only quiz enough?** (Proposed by Claude: guess the year, which book won, which author wrote these.)
A (author): No, not interactive enough. Prefer real game genres. The quiz idea may return later as a cheap extra, but it is not the goal.

**Q: Engine or handcrafted?**
A (Claude): Use a small open-source engine for the first games. Recommendation: **Kaplay** (successor to Kaboom). It covers sprites, collision, tilemaps, input, scenes and camera, is a plain JavaScript module (fits the no-build-step setup) and can be copied into the repo so the service worker caches it for offline use. Phaser is more powerful but heavier and slower to learn. LittleJS is tiny but less convenient. A fully handcrafted canvas game is fine for a single puzzle but repeats engine basics across genres. File sizes were stated from memory and must be measured before committing. **Decision: TBD** (author to confirm after a prototype).

**Q: Spoilers?**
A (author): Not a concern. Games may show plot events and endings. (Earlier idea of unlocking games only after marking a book read is dropped.)

## 3. Proposed approach (Claude's proposal, to be confirmed)

### 3.1 Structure
- One file per game: `js/games/<book-id-or-slug>.js`, loaded only when the player taps **Play** on the book page (dynamic `import()`), so the main app stays light.
- A small registry (JSON) maps book id to game file, title, genre and a one-line description. Books without a game show no Play button.
- The engine library is copied into the repo (for example `js/vendor/kaplay.mjs`), versioned, and added to the service worker precache or runtime cache.
- A shared helper provides: start screen, pause, restart, score, "Back to book", and an optional "Finished" record. **TBD:** whether results are stored (see 3.5).
- Graphics are drawn in code (shapes, emoji, small pixel palette). No image files, no licensing issues, small size. No cover art or character likenesses.
- Sound: optional, generated with WebAudio, off by default. **TBD.**

### 3.2 Phone first
The author uses the app mainly on a phone (installed Android PWA). Every game must:
- work with touch only (virtual joystick or tap-to-move, large buttons) and also with keyboard on desktop;
- fit portrait and landscape without scrolling;
- run acceptably on a mid-range phone (**TBD:** target frame rate and a reference device);
- not trap the user: there is always a visible way back to the book.

### 3.3 Pilot games (one genre each)
| Book | Genre | Sketch |
|---|---|---|
| *Dune* | Top-down survival run | Cross the dunes collecting spice. Sandworms track your footsteps, so you must keep changing pace. |
| *Neuromancer* | Puzzle | Route a signal through a grid of ICE nodes before a timer ends. |
| *The Martian* | Resource puzzle | Plan potato plots and water on a small Mars base grid. |

The author has not yet chosen the final three. Alternatives named: *The Forever War* (run and gun, time dilation changes the world between levels), *Hyperion* (quest with branching pilgrim stories). **TBD:** final pilot list.

### 3.4 Process
- Build one prototype first, then iterate. Each game ships in its own pull request so it can be tried on a phone before the next one is merged.
- Claude can build the games and automate smoke tests (loads, canvas appears, responds to input, no console errors, back button works). Claude cannot judge fun or touch feel; that needs the author playing on a phone and giving feedback.

### 3.5 Open questions (to resolve while writing the spec)
1. Engine: Kaplay, Phaser, LittleJS or handcrafted? Measure sizes and try one prototype.
2. Should game results (high score, "completed") be stored in the user's data and synced? If yes, where in the `users/<uid>` document and how does it affect the data-integrity checks?
3. Difficulty and length: each game a 2 to 5 minute session, or longer?
4. Content source: who writes the plot beats for each game (Claude drafts, author reviews)? How to avoid factual errors about the books?
5. Copyright stance: original mechanics and original wording only. Confirm no cover art, no quotes from the books, no text taken from Wikipedia or Goodreads plot sections.
6. Where do games appear: only on the book page, also as a "Play" filter or a Games tab in the library?
7. Accessibility: colour-blind safe palette, reduced motion option, pause on tab hidden.
8. Testing: how much of each game can be covered by BDD scenarios (see `tests/`)? Suggest a new feature file `13-games.feature` for the shared shell (Play button, launch, pause, back) and per-game smoke scenarios.
9. Offline: confirm games work offline after first load.
10. Cheap extras for later: data-only quiz modes, daily random book, "guess the book from three clues".

## 4. Constraints from the existing app
- Static site on GitHub Pages, ES modules, no build step (`js/`, `css/`, `tools/bump.py` keeps the version consistent).
- Installable Android PWA with a service worker (network first for same-origin files, cache fallback).
- Tests: pytest-bdd with Playwright (`tests/`), smoke scenarios gate merges via CI.
- Version bump with `python3 tools/bump.py` for every app change; new JS files must be listed in the precache (the script does this).

## 5. Spec skeleton (fill in)
1. Goals and non-goals
2. Player experience and navigation (entry points, back, pause, results)
3. Technical architecture (engine choice, game module interface, registry format, loading and caching)
4. Content model (per-game fields: book id, title, genre, description, difficulty, status)
5. Game design sheets, one per pilot game (goal, controls, rules, win and lose, levels, art and sound)
6. Phone requirements and performance budget
7. Data and sync (what, if anything, is stored)
8. Test plan (BDD scenarios, manual playtest checklist)
9. Milestones and PR plan
10. Risks (accuracy of plot details, scope creep, performance, copyright)
