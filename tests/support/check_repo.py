#!/usr/bin/env python3
"""Browser-free checks for 12-data-integrity.feature (DI-01..16). Exit 1 on any failure."""
import glob, json, os, re, subprocess, sys, tempfile
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
P = lambda *a: os.path.join(R, *a)
bad = []
def ok(c, m):
    if not c: bad.append(m)

AW = {'Hugo Award','Nebula Award','Arthur C. Clarke Award','John W. Campbell Memorial Award','Locus Award','Philip K. Dick Award','BSFA Award'}
d = json.load(open(P('data.json')))
ok(isinstance(d, list) and len(d) == 1329, 'DI-01 expected 1329 books, got %d' % len(d))
ids = [b.get('id') for b in d]
ok(len(set(ids)) == len(ids), 'DI-02 duplicate ids')
import unicodedata
def slug(t):
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')
for b in d:
    first = re.split(r'\s+(?:&|and)\s+', b['author'])[0]
    ok(b['id'] == slug(b['title']) + '--' + slug(first), 'DI-02 id %s does not match title and first author' % b['id'])
for b in d:
    ok(all(isinstance(b.get(k), str) and b[k] for k in ('id','title','author')) and isinstance(b.get('entries'), list), 'DI-01 shape %s' % b.get('id'))
    ok(b.get('entries'), 'DI-05 empty entries %s' % b.get('id'))
    seen = set()
    for e in b.get('entries', []):
        ok(isinstance(e.get('year'), int) and 1950 <= e['year'] <= 2100, 'DI-03 year %s' % b['id'])
        ok(e.get('result') in ('winner','finalist'), 'DI-03 result %s' % b['id'])
        k = (e.get('award'), e.get('year'), e.get('result'))
        ok(k not in seen, 'DI-04 duplicate entry %s %s' % (b['id'], k)); seen.add(k)
    for f in ('title','author'):
        v = b[f]; ok(v == v.strip() and '  ' not in v and not re.search(r'[\x00-\x1f]', v), 'DI-08 text %s' % b['id'])
awards = {e['award'] for b in d for e in b['entries']}
ok(len(awards) == 7, 'DI-03 expected 7 awards, found %s' % sorted(awards))

sw = open(P('sw.js')).read(); html = open(P('index.html')).read()
v = re.search(r"VERSION = 'nova-v(\d+)'", sw).group(1)
vs = set(re.findall(r'\?v=(\d+)', html)) | set(re.findall(r'name="app-version" content="(\d+)"', html))
ok(vs == {v}, 'DI-10 versions disagree: sw=%s html=%s' % (v, vs))
shell = re.search(r"const SHELL = \[(.*?)\];", sw, re.S).group(1)
listed = re.findall(r"'([^']+)'", shell)
for f in glob.glob(P('css','*.css')) + glob.glob(P('js','*.js')):
    ok(os.path.relpath(f, R).replace(os.sep,'/') in listed, 'DI-11 not precached: %s' % f)
for f in listed:
    ok(f == './' or os.path.exists(P(f)), 'DI-11 missing file %s' % f)
for ref in re.findall(r'(?:href|src)="([^"#:]+?)(?:\?[^"]*)?"', html):
    ok(os.path.exists(P(ref)), 'DI-12 missing %s' % ref)
mf = json.load(open(P('manifest.webmanifest')))
for i in mf.get('icons', []): ok(os.path.exists(P(i['src'])), 'DI-12 icon %s' % i['src'])
for f in glob.glob(P('js','*.js')):
    src = open(f).read()
    for imp in re.findall(r"from\s+'(\.[^']+)'", src):
        ok(os.path.exists(os.path.normpath(os.path.join(os.path.dirname(f), imp))), 'DI-13 import %s in %s' % (imp, f))
    if subprocess.run(['node','--check',f], capture_output=True).returncode: bad.append('DI-13 syntax %s' % f)
for f in glob.glob(P('**','*'), recursive=True):
    if os.path.isfile(f) and '.git' not in f and not f.endswith('check_repo.py') and f.endswith(('.js','.json','.html','.py','.md','.webmanifest')):
        t = open(f, errors='ignore').read()
        ok('PRIVATE KEY-----' not in t and '"private_key"' not in t, 'DI-14 secret in %s' % f)
for f in ('LICENSE','README.md','IDEAS.md','tools/README.md','tests/README.md'): ok(os.path.exists(P(f)), 'DI-15 missing %s' % f)
tags = {}
for f in sorted(glob.glob(P('tests','features','*.feature'))):
    lines = open(f).read().splitlines()
    for i, l in enumerate(lines):
        if re.match(r'\s*Scenario', l):
            j = i - 1; t = []
            while j >= 0 and lines[j].strip().startswith('@'): t += lines[j].split(); j -= 1
            ids_ = [x for x in t if re.fullmatch(r'@[A-Z]{2,3}-\d+', x)]
            ok(len(ids_) == 1, 'DI-16 %s:%d needs exactly one id tag, has %s' % (os.path.basename(f), i+1, ids_))
            for x in ids_:
                ok(x not in tags, 'DI-16 duplicate %s' % x); tags[x] = 1
# DI-07: parse.py must reproduce data.json byte for byte. Run it on a copy so the real file is never rewritten
# (browser tests read data.json at the same time).
import shutil
with tempfile.TemporaryDirectory() as tmp:
    shutil.copytree(P('tools'), os.path.join(tmp, 'tools'))
    subprocess.run(['python3', os.path.join(tmp, 'tools', 'parse.py')], capture_output=True, cwd=tmp)
    out = os.path.join(tmp, 'data.json')
    ok(os.path.exists(out) and open(out, 'rb').read() == open(P('data.json'), 'rb').read(), 'DI-07 parse.py output differs from data.json')
print('scenarios with id tags: %d' % len(tags))
print('FAIL' if bad else 'OK'); [print(' -', m) for m in bad[:50]]
sys.exit(1 if bad else 0)
