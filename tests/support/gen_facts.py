#!/usr/bin/env python3
"""Compute the data facts the scenarios rely on, straight from data.json.

    python3 tests/support/gen_facts.py            print the facts as JSON
    python3 tests/support/gen_facts.py --check    compare with tests/fixtures/facts.json (exit 1 on any difference)
    python3 tests/support/gen_facts.py --write    refresh tests/fixtures/facts.json

When the award data changes, run --write, then update the numbers in tests/features/*.feature that changed.
"""
import json, os, re, sys
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
B = json.load(open(os.path.join(root, 'data.json'), encoding='utf-8'))
AW = ['Hugo Award', 'Nebula Award', 'Arthur C. Clarke Award', 'John W. Campbell Memorial Award', 'Locus Award (SF Novel)', 'Philip K. Dick Award', 'BSFA Award']
for b in B:
    b['w'] = sum(e['result'] == 'winner' for e in b['entries']); b['n'] = len(b['entries'])
    b['first'] = min(e['year'] for e in b['entries']); b['last'] = max(e['year'] for e in b['entries'])
def decade(d, winners=False):
    return len([b for b in B if any(d <= e['year'] <= d + 9 and (not winners or e['result'] == 'winner') for e in b['entries'])])
def sur(a):
    p = re.sub(r' and .*$', '', re.sub(r'\s*&.*$', '', a)).split(' '); return p[-1].lower()
def find(t): return next(b for b in B if b['title'] == t)
facts = {
    'books_total': len(B),
    'books_with_a_win': len([b for b in B if b['w']]),
    'authors_total': len({b['author'] for b in B}),
    'ids_unique': len({b['id'] for b in B}) == len(B),
    'per_award': {a: {
        'books': len([b for b in B if any(e['award'] == a for e in b['entries'])]),
        'entries': sum(1 for b in B for e in b['entries'] if e['award'] == a),
        'winner_entries': sum(1 for b in B for e in b['entries'] if e['award'] == a and e['result'] == 'winner'),
        'books_with_win': len([b for b in B if any(e['award'] == a and e['result'] == 'winner' for e in b['entries'])]),
        'first_year': min(e['year'] for b in B for e in b['entries'] if e['award'] == a),
        'last_year': max(e['year'] for b in B for e in b['entries'] if e['award'] == a)} for a in AW},
    'hugo_or_nebula_books': len([b for b in B if any(e['award'] in ('Hugo Award', 'Nebula Award') for e in b['entries'])]),
    'decades': {str(d): {'books': decade(d), 'winners_only': decade(d, True)} for d in range(1950, 2030, 10)},
    'top_most_honoured': [b['title'] for b in sorted(B, key=lambda b: (-(3 * b['w'] + b['n']), -b['last']))[:3]],
    'top_most_wins': [b['title'] for b in sorted(B, key=lambda b: (-b['w'], -b['n']))[:2]],
    'oldest_first': sorted(B, key=lambda b: (b['first'], b['title']))[0]['title'],
    'author_az_first': sorted(B, key=lambda b: (sur(b['author']), b['title']))[0]['author'],
    'search': {q: len([b for b in B if q in (b['title'] + ' ' + b['author']).lower()]) for q in ['dune', 'leckie']},
    'author_counts': {a: len([b for b in B if b['author'] == a]) for a in ['Arthur C. Clarke', 'Ursula K. Le Guin', 'Charles Stross']},
    'books': {t: {'id': find(t)['id'], 'author': find(t)['author'], 'wins': find(t)['w'], 'nominations': find(t)['n'],
                  'entries': sorted((e['award'], e['year'], e['result']) for e in find(t)['entries'])}
              for t in ['Ancillary Justice', 'Rendezvous with Rama', 'The City & the City', "Neptune's Brood", 'Dune', 'Hyperion', 'The Left Hand of Darkness']},
    'hugo_2014': sorted((b['title'], e['result']) for b in B for e in b['entries'] if e['award'] == 'Hugo Award' and e['year'] == 2014),
}
out = json.dumps(facts, indent=2, ensure_ascii=False, sort_keys=True) + '\n'
path = os.path.join(root, 'tests', 'fixtures', 'facts.json')
if '--write' in sys.argv: open(path, 'w', encoding='utf-8').write(out); print('wrote', path)
elif '--check' in sys.argv:
    cur = open(path, encoding='utf-8').read()
    if cur != out: print('facts.json is out of date. Run: python3 tests/support/gen_facts.py --write and update the scenarios.'); sys.exit(1)
    print('facts are up to date')
else: print(out)
