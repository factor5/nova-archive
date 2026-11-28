# Nova Archive

A personal web app for browsing science-fiction novel awards, tracking what you've read and keeping reading lists.

**Live:** https://factor5.github.io/nova-archive/ (installable as an app on Android via Chrome → "Install app")

## What it does

- Winners **and finalists** (novels only) for seven awards: Hugo, Nebula, Arthur C. Clarke, John W. Campbell Memorial, Locus (SF Novel), Philip K. Dick and BSFA. 1,329 books in total.
- Browse and filter by year, decade, award, author, winners only, or read status. Group and sort the results.
- Add your own books that aren't in the award lists (manually, or by searching Open Library and filling the form), then treat them like any other book: lists, reading status, ratings, notes. A "Source" filter shows award books, your books, or both.
- Mark books as read, start reading them (shown in a "Now reading" row), rate them 1–5 stars and keep private notes.
- Build reading lists, reorder or sort them, and copy them as text.
- A page for every book (tap its title): all awards, your rating, notes and finish date, other books by the author, and the books it competed against.
- Book pages can show a cover, description and subjects from Open Library (only when a page is opened, cached in the browser, can be switched off on the About page).
- Links to Wikipedia, Goodreads and ISFDB for every book and author.
- Four themes (Nova dark, Paper light, Terminal, Dune) plus Auto, which follows the phone's light or dark setting.
- Works offline once opened. Sign in with Google to sync your progress across devices.

## How it works

A static site, with no build step and no framework.

| Path | Purpose |
|---|---|
| `index.html` | Page markup only |
| `css/base.css` | Layout and components (colours come from theme tokens) |
| `css/theme-*.css` | One file per theme (Nova, Paper, Terminal, Dune): design tokens and overrides |
| `js/main.js` | Entry point (ES module): loads data, wires the page, starts sync |
| `js/*.js` | Modules: `config`, `util`, `state`, `theme`, `sync` (Firebase), `data` (filtering and sorting), `cards`, `overlay`, `views`, `bookpage`, `enrich` (Open Library lookup), `addbook` (your own books), `actions` |
| `data.json` | The award data, one book per line |
| `firebase-config.js` | Firebase web config (public by design; access is limited by Firestore rules) |
| `js/games.js`, `js/games/`, `css/games/`, `js/vendor/` | Book games (beta, see [`docs/games/`](docs/games/README.md)): registry and beta switch, the game shell, the games and their decorative frames (loaded only on Play), and the KAPLAY engine |
| `sw.js`, `manifest.webmanifest`, `icons/` | Offline support and installability (PWA) |
| `tools/` | Source data, the script that generates `data.json`, and the version bump script |

- **Hosting:** GitHub Pages, served from the `main` branch root.
- **Persistence:** Firebase Authentication (Google sign-in) and Cloud Firestore, one document per user at `users/<uid>`. Without signing in, progress is kept in the browser's local storage only.
- **Your own books:** stored in the `custom` list of your Firestore document with the rest of your data (ids start with `my--`); `data.json` is never modified.
- **Open Library:** cover, description and subjects are fetched in the browser from `openlibrary.org` / `covers.openlibrary.org` when a book page opens. Nothing is stored in Firebase, and a failed lookup simply hides the section.
- **Data:** award results come from Wikipedia list pages and sfadb (Locus Awards, 2026).

## Updating

- **App changes:** edit the files under `css/` or `js/`, run `python3 tools/bump.py` (it raises the version in `sw.js`, the `?v=` URLs and the About page together), commit to `main`, and Pages redeploys in a few minutes. Installed copies refresh on the next open.
- **New theme:** add `css/theme-<name>.css` overriding the tokens in `theme-nova.css`, link it in `index.html`, and add it to `THEMES` in `js/config.js` (the theme picker, browser-bar colour and saved choice follow from that list).
- **New award results:** see [`tools/README.md`](tools/README.md). Edit `tools/raw.txt`, run `python3 tools/parse.py`, then commit `raw.txt` and `data.json`.
- **Book ids are stable.** Read marks, ratings, notes and lists are stored by id, so avoid renaming existing titles or authors in the data.

## Setting up your own copy

1. Create a Firebase project, enable Google sign-in under Authentication, and create a Firestore database.
2. Register a web app in the project and put its config values into `firebase-config.js`.
3. Add your GitHub Pages domain (for example `<username>.github.io`) under Authentication → Settings → Authorized domains.
4. Set Firestore rules so each user can only read and write their own `users/<uid>` document. Restrict it further to specific emails if the app is for private use.
5. Enable GitHub Pages: Settings → Pages → Deploy from a branch → `main` / root.

## Ideas

See [`IDEAS.md`](IDEAS.md) for planned and possible features.

## License

[MIT](LICENSE) for the application code. Award names and results are public facts compiled from the sources above.
