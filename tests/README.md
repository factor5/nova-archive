# Tests

Behaviour-driven scenarios for Nova Archive. They are written in Gherkin (Given / When / Then) so that the same files can be:

1. **Run by hand** by a person following the steps in a browser.
2. **Run by an AI** that drives a browser (for example with Playwright) and checks each step.
3. **Automated later** in CI on every pull request (see "Roadmap to CI").

Nothing here changes the app. The scenarios describe what the app does at version 17 and later; when behaviour changes, change the scenario in the same pull request.

## Layout

```
tests/
  README.md                 this file
  features/                 the scenarios, one file per area
    01-library-browsing.feature
    02-reading-status.feature
    03-ratings-and-notes.feature
    04-reading-lists.feature
    05-book-page.feature
    06-my-books.feature
    07-open-library.feature
    08-themes.feature
    09-persistence-and-sync.feature
    10-offline-and-updates.feature
    11-navigation-and-accessibility.feature
    12-data-integrity.feature
  fixtures/facts.json       numbers and example books taken from data.json (generated)
  support/
    gen_facts.py            regenerates / verifies fixtures/facts.json
    mocks/                  test doubles for Firebase and Open Library
```

## Determinism rules

The scenarios are written so that two runs give the same result.

- **Start clean.** Every scenario starts from an empty browser profile: no local storage, no service worker (unless the scenario is tagged `@sw`), no cookies. "Given a fresh browser profile" means exactly that.
- **No real network services.** The app talks to three outside services. In tests they are always replaced:
  - Firebase (`www.gstatic.com/firebasejs/*` and `firebase-config.js`) by the files in `support/mocks/`. Without the mock `firebase-config.js` the app runs in "local only" mode, which is the default for most scenarios.
  - Open Library (`openlibrary.org`, `covers.openlibrary.org`) by canned answers from `support/mocks/openlibrary.json`.
  - Google Fonts (`fonts.googleapis.com`, `fonts.gstatic.com`): block them. Layout checks must not depend on the web font.
- **No clocks and no randomness in assertions.** Dates are asserted as "today" or relative days, never as fixed timestamps, unless the scenario sets the browser clock first (`Given the browser clock is set to ...`). The "Surprise me" button is random, so its scenarios assert properties (unread, matches filters) and not a specific book.
- **The data is real and fixed.** Scenarios use `data.json` as shipped. The numbers in the scenarios (for example 361 Hugo books) come from `fixtures/facts.json`. When the award data changes, regenerate the facts, then fix the scenarios. CI runs `python3 tests/support/gen_facts.py --check` so a data change cannot slip through without updating the tests.
- **Viewport.** Scenarios tagged `@mobile` use 390 x 844 (a phone). Scenarios tagged `@desktop` use 1280 x 800. Untagged scenarios must pass in both.
- **Reduced motion.** Run with `prefers-reduced-motion: reduce` so animations and smooth scrolling do not make assertions flaky.

## Tags

| Tag | Meaning |
|---|---|
| `@smoke` | Fast, essential. Run on every pull request. About a third of all scenarios. |
| `@regression` | Everything else. Run before merging to main (and nightly). |
| `@mobile`, `@desktop` | Needs that viewport. |
| `@firebase-mock` | Needs the Firebase mocks routed in. |
| `@ol-mock` | Needs the Open Library mocks routed in. |
| `@sw` | Needs the service worker enabled (not blocked). |
| `@manual` | Cannot be automated against mocks. Needs a real device, real Firebase or a human eye. |
| `@area-id` such as `@LIB-03` | Stable scenario id for reports and traceability. Never reuse an id. |

## Test hooks (selectors)

Scenarios talk about things a user sees. Automation maps them to these stable hooks.

| Thing | Hook |
|---|---|
| Header: read counter, total, progress bar | `#hudRead`, `#hudTotal`, `#hudBar` |
| Sync status (text is its accessible name) | `#sync`, `#syncTxt` |
| Theme button, sign-in/out button, back-to-top | `#themeBtn`, `#authBtn`, `#toTop` |
| Toast message | `#toastRoot .toast` |
| Tabs | `nav.tabs a[data-tab="library" \| "lists" \| "about"]`, count in `#listCount` |
| Now reading row and cards | `#nowReading`, `#nowReading .ncard` |
| Library filters | `#q`, `#result`, `#read`, `#decade`, `#source`, `#group`, `#sort`, `#awardPills .pill[data-aw]` |
| Result count, cards, group headings | `#count`, `#results .card`, `.group h2` |
| Card parts | `.card[data-id]`, `h3 a`, `.author`, `.badges .b`, `.rate .st` |
| Actions (buttons) | `[data-act="read"]`, `start`, `stop`, `finish`, `note`, `addlist`, `more`, `reset`, `surprise`, `addall`, `addbook`, `clearauthor` |
| Modal | `#ovRoot .modal` |
| Lists page | `#newListName`, `[data-act="newlist"]`, `.litem`, `#listName`, `#lsort`, `.item`, `[data-act="up" \| "down" \| "rm" \| "copylist" \| "dellist"]` |
| Book page | `.bpage`, `.bhead h2`, `#bookInfo`, `#pageNote`, `#pageFin`, `table.aw tbody tr`, `.sy`, `#cbT`, `#cbA`, `#cbY`, `#cbSave`, `#cbDel` |
| Add-a-book dialog | `#abQ`, `#abRes`, `#abT`, `#abA`, `#abY`, `#abMsg`, `[data-act="absave"]` |
| Theme in effect | attribute `data-theme` on `<html>`; saved choice in local storage key `nova-theme` |
| Saved user data (local copy) | local storage key `nova-archive-v1` (JSON) |
| Fake cloud / fake sign-in | local storage keys `fake-fs`, `fake-auth` (only with the mocks) |

## Step glossary

Automation implements these once; features reuse them. Steps are written in plain language on purpose.

**Setup**
- `Given a fresh browser profile` : empty storage, service worker blocked, outside services blocked.
- `Given the app is open on the <tab> tab` : load `/#library`, `/#lists` or `/#about` and wait for the cards or the page.
- `Given Firebase is configured with the test double` : route the mock `firebase-config.js` and SDK files.
- `Given I am signed in as "<email>"` : set `fake-auth`, then load the app.
- `Given the cloud holds <something> for my account` : seed `fake-fs` for `users/u1`.
- `Given Open Library answers with "<fixture>"` : route the canned response.
- `Given the browser is offline` : switch the browser context offline.
- `Given the viewport is a phone` / `a desktop`.

**Actions** use the visible label: `When I tap "Mark read" on "Dune"`, `When I choose "Hugo" in the award filter`, `When I type "dune" in the search box`, `When I open the book page for "Dune"`.

**Assertions** use what is visible: `Then the result count is 361`, `Then "Dune" shows a "✓ Read" button`, `Then the sync status reads "Cloud synced"`, `Then the saved data contains ...` (reads the local copy or the fake cloud document).

## How to run

**By hand.** Serve the repository folder (for example `python3 -m http.server 8000`), open `http://localhost:8000/` in Chrome, and follow a scenario. For scenarios tagged `@firebase-mock` or `@ol-mock`, use the real services if you prefer, or skip them. Scenarios tagged `@manual` are meant for a person.

**By an AI with Playwright.** Give it this README and a feature file. It should serve the folder, create a fresh browser context per scenario, route the mocks as described, implement the glossary steps, and report pass or fail per scenario id.

## Automated runner

The scenarios run with `pytest-bdd` and Playwright (Chromium). The step code is in `tests/steps/common.py`,
the browser, mocks and local web server in `tests/conftest.py`.

```
pip install -r tests/requirements.txt
python -m playwright install chromium
python -m pytest tests -m "smoke and not manual" -n 4      # what CI runs
python -m pytest tests -k "LIB-01 or dune"                  # a single scenario or topic
```

**Status.** All `@smoke` scenarios, all of `08-themes`, `09-persistence-and-sync`, `12-data-integrity`, `01-library-browsing`, `02-reading-status`, `03-ratings-and-notes`, `04-reading-lists`, `10-offline-and-updates` and `11-navigation-and-accessibility` have step definitions and pass (`@manual` and `@wip` scenarios are skipped). The remaining scenarios are
written but their steps are not implemented yet; running them fails with "Step definition is not found".
Run one feature file with its number: `python -m pytest tests -m f09`.
That is intentional: they are the backlog. To automate one, add the missing steps to `steps/common.py`
(reuse the existing ones where the wording matches) and, when it passes reliably, nothing else is needed:
CI selects by tag. Next planned step is to run `regression` on merges to `main` once most of them pass.

CI (`.github/workflows/tests.yml`) runs on every pull request and every push to `main`:
facts check, repository checks, then the smoke scenarios. To make it a gate, enable branch protection on
`main` and require the **tests / smoke** check.

Later: Firestore rules tests with the Firebase emulator (`@SY-30`) and visual snapshots per theme.

## Writing new scenarios

- One behaviour per scenario. Give it an id tag, and `@smoke` only if it is essential.
- Describe what a user sees, not how the code works.
- Prefer a `Scenario Outline` with an `Examples` table over copy and paste.
- If a number comes from the data, put it in `gen_facts.py` first.
- When a bug is fixed, add the scenario that would have caught it.

## Browser-free checks

`python3 tests/support/check_repo.py` implements the scenarios in `12-data-integrity.feature`
(plus the version/precache consistency in `10-offline-and-updates.feature` PW-11).
`python3 tests/support/gen_facts.py --check` confirms `tests/fixtures/facts.json` matches `data.json`.
Both exit non-zero on failure and need no browser, so they are the first CI step.
