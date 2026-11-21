# Nova Archive

A personal web app for browsing science-fiction novel awards, tracking what you've read and keeping reading lists.

**Live:** https://factor5.github.io/nova-archive/ (installable as an app on Android via Chrome → "Install app")

## What it does

- Winners **and finalists** (novels only) for seven awards: Hugo, Nebula, Arthur C. Clarke, John W. Campbell Memorial, Locus (SF Novel), Philip K. Dick and BSFA. 1,329 books in total.
- Browse and filter by year, decade, award, author, winners only, or read status. Group and sort the results.
- Mark books as read, start reading them (shown in a "Now reading" row), rate them 1–5 stars and keep private notes.
- Build reading lists, reorder or sort them, and copy them as text.
- Links to Wikipedia, Goodreads and ISFDB for every book and author.
- Works offline once opened. Sign in with Google to sync your progress across devices.

## How it works

A static site, with no build step and no framework.

| File | Purpose |
|---|---|
| `index.html` | The whole app: markup, styles and JavaScript |
| `data.json` | The award data, one book per line |
| `firebase-config.js` | Firebase web config (public by design; access is limited by Firestore rules) |
| `sw.js`, `manifest.webmanifest`, `icons/` | Offline support and installability (PWA) |
| `tools/` | Source data and the script that generates `data.json` |

- **Hosting:** GitHub Pages, served from the `main` branch root.
- **Persistence:** Firebase Authentication (Google sign-in) and Cloud Firestore, one document per user at `users/<uid>`. Without signing in, progress is kept in the browser's local storage only.
- **Data:** award results come from Wikipedia list pages and sfadb (Locus Awards, 2026).

## Updating

- **App changes:** edit `index.html`, commit to `main`, and Pages redeploys in a few minutes. Increase the `VERSION` in `sw.js` so installed copies refresh.
- **New award results:** see [`tools/README.md`](tools/README.md). Edit `tools/raw.txt`, run `python3 tools/parse.py`, then commit `raw.txt` and `data.json`.
- **Book ids are stable.** Read marks, ratings, notes and lists are stored by id, so avoid renaming existing titles or authors in the data.

## Setting up your own copy

1. Create a Firebase project, enable Google sign-in under Authentication, and create a Firestore database.
2. Register a web app in the project and put its config values into `firebase-config.js`.
3. Add your GitHub Pages domain (for example `<username>.github.io`) under Authentication → Settings → Authorized domains.
4. Set Firestore rules so each user can only read and write their own `users/<uid>` document. Restrict it further to specific emails if the app is for private use.
5. Enable GitHub Pages: Settings → Pages → Deploy from a branch → `main` / root.

## License

Application code: your choice of license, none is set yet. Award names and results are public facts compiled from the sources above.
