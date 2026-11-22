"""Steps for 12-data-integrity.feature (no browser). Most checks live in tests/support/check_repo.py."""
import json, os, re, subprocess, sys
from pytest_bdd import given, parsers
from steps.common import step, _di

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FACTS = json.load(open(os.path.join(ROOT, 'tests', 'fixtures', 'facts.json')))


def make(t):
    def _s(repo_check): _di(repo_check, t)
    return _s


CHECKS = [
    (r'it is a JSON array of 1329 books', 'DI-01'),
    (r'every book has string "id", "title", "author" and a list "entries"', 'DI-01'),
    (r'no two books share an id', 'DI-02'),
    (r'every id equals the slug of the title and of the first author joined by "--"', 'DI-02'),
    (r'every entry has an "award" from the 7 known awards', 'DI-03'),
    (r'"year" is an integer between 1950 and the current year', 'DI-03'),
    (r'"result" is "winner" or "finalist"', 'DI-03'),
    (r'a book has at most one entry per award and year and result', 'DI-04'),
    (r'no book has an empty entries list', 'DI-05'),
    (r'the output is byte-identical to data\.json', 'DI-07'),
    (r'no title or author has leading or trailing spaces, double spaces or control characters', 'DI-08'),
    (r'the SHELL list in sw\.js names every css/\*\.css and js/\*\.js file and each listed file exists', 'DI-11'),
    (r'stylesheets, scripts, icons and the manifest link all resolve', 'DI-12'),
    (r'"node --check" passes for every js/\*\.js file', 'DI-13'),
    (r'every relative import points to an existing file', 'DI-13'),
    (r'LICENSE, README\.md, IDEAS\.md, tools/README\.md and tests/README\.md exist', 'DI-15'),
    (r'every Scenario in tests/features has exactly one id tag like @LIB-03', 'DI-16'),
    (r'no id is used twice', 'DI-16'),
    (r'the VERSION in sw\.js, every "\?v=" in index\.html and the app-version meta are the same number', 'DI-10'),
    (r'no file contains a private key block, a service-account JSON or an API secret', 'DI-14'),
    (r'firebase-config\.js holds only the public web config', 'DI-14'),
]

# registered at module level so pytest-bdd finds them (see tests/README.md)
for _pattern, _tag in CHECKS:
    step(_pattern)(make(_tag))


@given(parsers.parse('data.json'))
def _given_data(): pass




@step(r'I run "python3 tests/support/gen_facts\.py --check"')
def _run_facts(env_or=None):
    pass


@step(r'it exits 0, meaning tests/fixtures/facts\.json is current')
def _facts_current():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tests', 'support', 'gen_facts.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


@step(r'the facts agree with the scenarios: 296 books with a win and 629 authors')
def _facts_agree():
    d = json.load(open(os.path.join(ROOT, 'data.json')))
    assert sum(1 for b in d if any(e['result'] == 'winner' for e in b['entries'])) == 296
    assert len({b['author'] for b in d}) == 629


@step(r'I run "python3 tools/parse\.py" into a temporary file')
def _run_parse(): pass
