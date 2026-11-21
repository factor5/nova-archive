# Data tools

`data.json` (the book list the app loads) is generated from `raw.txt` by `parse.py`.

## Update the data

1. Edit `tools/raw.txt`. Each award has a `#AWARD <exact award name>` header, followed by one line per year:

   `2026 | W: Title - Author | F: Finalist Title - Author; Another Title - Author`

   Ties: put several winners in `W:` separated by `;`.
2. Run `python3 tools/parse.py` from the repo root. It rewrites `data.json` and prints the number of books per award.
3. Commit `raw.txt` and `data.json`, then push. GitHub Pages republishes in a few minutes.

## Rules

- Keep the exact award names: Hugo Award, Nebula Award, Arthur C. Clarke Award, John W. Campbell Memorial Award, Locus Award (SF Novel), Philip K. Dick Award, BSFA Award.
- Book ids come from title + first author, so do not rename an existing title or author. Read marks, ratings, notes and lists are stored by id. If the same book appears under two spellings, add the variant to the `AUTH` or `TITLE` alias tables at the top of `parse.py` instead of editing the data.
- Sources used: Wikipedia award list pages, plus sfadb (Locus Awards, 2026).
