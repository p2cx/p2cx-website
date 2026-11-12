"""Prüft alle internen Links der p2cx-Website (lokaler Server auf 8765) und die Sprache in Kopf/Fuß."""
import glob, html, os, re, sys, urllib.parse, urllib.request

ROOT = sys.argv[1]
BASIS = sys.argv[2] if len(sys.argv) > 2 else 'http://localhost:8765'
AUS = re.compile(r'/(skills|helpcenter|kurz|notizen|Test_LiveTabelle)/|/0\d-|AuszugBI|onepager')
FLAGGE = re.compile(r'aria-label="(Deutsch|English|Dansk)"')

seiten = []
for f in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True):
    rel = '/' + os.path.relpath(f, ROOT).replace(os.sep, '/')
    if not AUS.search(rel):
        seiten.append((f, rel))

cache, kaputt, sprache = {}, set(), set()

def status(u):
    if u not in cache:
        try:
            with urllib.request.urlopen(u, timeout=10) as r:
                cache[u] = r.status
        except urllib.error.HTTPError as e:
            cache[u] = e.code
        except Exception as e:
            cache[u] = type(e).__name__
    return cache[u]

for f, rel in seiten:
    teile = rel.split('/')
    lang = teile[1] if teile[1] in ('de', 'en', 'dk') else None
    s = open(f, encoding='utf-8').read()
    bereiche = [('seite', s)]
    if '</header>' in s:
        bereiche.append(('kopf', s[:s.find('</header>')]))
    if '<footer' in s:
        bereiche.append(('fuss', s[s.find('<footer'):]))
    for name, teil in bereiche:
        for m in re.finditer(r'<a\b[^>]*href="([^"]*)"[^>]*>', teil):
            h = html.unescape(m.group(1))
            if not h or h.startswith(('http', 'mailto:', 'tel:', 'javascript', '#')):
                continue
            u = urllib.parse.urljoin(BASIS + rel, h).split('#')[0]
            st = status(u)
            if st != 200:
                kaputt.add((rel, name, h, st))
            if name in ('kopf', 'fuss') and lang and not FLAGGE.search(m.group(0)):
                ziel = urllib.parse.urlparse(u).path.split('/')
                if len(ziel) > 1 and ziel[1] in ('de', 'en', 'dk') and ziel[1] != lang:
                    # Ausnahme: AGB/AVV gibt es nur auf Deutsch
                    if not re.search(r'/de/(agb|avv)/', urllib.parse.urlparse(u).path):
                        sprache.add((rel, name, h))

print('Seiten geprüft:', len(seiten), '| verschiedene Ziele:', len(cache))
print('KAPUTT:', len(kaputt))
for k in sorted(kaputt):
    print('  ', k)
print('FALSCHE SPRACHE in Kopf/Fuß:', len(sprache))
for k in sorted(sprache):
    print('  ', k)
