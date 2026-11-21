# Ideas and roadmap

A scratchpad for features to add later. Move items to "Done" when they ship.

## Done
- Winners and finalists for seven awards, browsable and filterable
- Read marks, reading lists, list sorting
- Now reading row, star ratings, notes
- Back-to-top button
- Covers, descriptions and subjects on the book page (Open Library, optional)
- Per-book page (awards, your shelf, author's other books, same-year competitors)
- Themes: Nova (dark), Paper (light), Terminal, Dune and Auto, with a theme picker (synced with your account)

## Themes
- Per-theme accent colours, or a user-picked accent

## Reading life
- **Stats page**: books per year, yearly goal with progress bar, average rating, favourite authors and decades, awards covered
- **Reading log**: "Read in 2026" view sorted by finish date, with an editable date to backfill older books
- **Wishlist and owned**: mark books as "want to read" or "own"
- **Tags**: own labels such as audiobook, re-read, gift, usable as filters
- **Re-reads**: allow reading a book again and keep each read's date and rating

## Discovery
- **Covers on cards and lists**: small thumbnails in the library (needs lazy loading and care with request volume)
- **More like this**: suggestions based on awards, era or author
- **Series info**: group books by series and show what to read next
- **Series info** on the book page (Open Library has no reliable series field; may need another source)
- **Read-next picker**: choose from your lists, not only from the current filters

## Practical
- **Backup and restore**: export everything to a file and import it back
- **Share a list**: read-only link to one list (needs the multi-user setup)
- **Multi-user**: loosen the Firestore rules, either friends by email or any Google account, with a document size limit
- **Undo toast** after Start, Stop, Finish and Mark read
- **Home-screen shortcut** straight to Now reading
- **Award updates**: add new yearly results with `tools/` (see `tools/README.md`); consider more awards (e.g. Prometheus, Sturgeon, Kitschies, British Fantasy)

## Maybe
- Short stories and novellas as an optional second data set
- Notifications when a new award winner is announced
- Compare reading progress with a friend
