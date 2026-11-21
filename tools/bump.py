#!/usr/bin/env python3
"""Bump the app version everywhere it must change together.

Run from anywhere:  python3 tools/bump.py        (next number)
                    python3 tools/bump.py 25     (explicit number)

Updates: the ?v=N on CSS/JS URLs and the app-version meta tag in index.html, VERSION in sw.js.
Also lists every css/*.css and js/*.js file in the service worker's precache list.
"""
import glob, os, re, sys
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
def path(*p): return os.path.join(root, *p)

sw = open(path('sw.js')).read()
cur = int(re.search(r"VERSION = 'nova-v(\d+)'", sw).group(1))
new = int(sys.argv[1]) if len(sys.argv) > 1 else cur + 1

files = sorted(glob.glob(path('css', '*.css'))) + sorted(glob.glob(path('js', '*.js')))
rel = [os.path.relpath(f, root).replace(os.sep, '/') for f in files]
shell = "const SHELL = ['./', 'index.html', " + ', '.join("'%s'" % f for f in rel) + ", 'data.json', 'firebase-config.js', 'manifest.webmanifest',\n  'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png'];"
sw = re.sub(r"VERSION = 'nova-v\d+'", "VERSION = 'nova-v%d'" % new, sw)
sw = re.sub(r"const SHELL = \[.*?\];", lambda m: shell, sw, flags=re.S)
open(path('sw.js'), 'w').write(sw)

h = open(path('index.html')).read()
h = re.sub(r'((?:css|js)/[\w.-]+\.(?:css|js)|firebase-config\.js)\?v=\d+', r'\1?v=%d' % new, h)
h = re.sub(r'(<meta name="app-version" content=")\d+(")', r'\g<1>%d\2' % new, h)
open(path('index.html'), 'w').write(h)
print('version %d -> %d' % (cur, new))
