import re, json, sys, unicodedata
import os
HERE = os.path.dirname(os.path.abspath(__file__))
raw = open(os.path.join(HERE, 'raw.txt'), encoding='utf-8').read().splitlines()
AUTH = {'Liu Cixin':'Cixin Liu','Ursula Vernon':'T. Kingfisher','E.J. Swift':'E. J. Swift','Paul McAuley':'Paul J. McAuley',
        'Kate Wilhelm':'Kate Wilhelm','Arkady and Boris Strugatsky':'Arkady & Boris Strugatsky','Jon Courtenay Grimwood':'Jon Courtenay Grimwood'}
TITLE = {'The Speed of Dark':'Speed of Dark','Hyperion Cantos':'Hyperion','Europe In Autumn':'Europe in Autumn','Bold As Love':'Bold as Love'}
def norm(s): 
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+',' ',s).strip()
def slug(s): return norm(s).replace(' ','-')
books = {}; award=None; counts={}
for line in raw:
    if line.startswith('#AWARD '): award=line[7:].strip(); continue
    if not line.strip(): continue
    m = re.match(r'(\d{4}) \| W:(.*?) \| F:(.*)$', line)
    if not m: print('BAD', line[:80]); continue
    year=int(m.group(1))
    for res, blob in (('winner', m.group(2)), ('finalist', m.group(3))):
        for part in blob.split(';'):
            part=part.strip()
            if not part: continue
            part=re.sub(r'\s*\((tie|joint)\)\s*$','',part).strip()
            if ' - ' not in part: print('NODASH', part); continue
            title, author = part.rsplit(' - ',1)
            author=re.sub(r'\s*\(.*?\)\s*$','',author); author=re.sub(r',? eds?\.$','',author).strip()
            title=TITLE.get(title.strip(), title.strip()); author=AUTH.get(author, author)
            key = slug(title)+'|'+slug(author)
            b=books.setdefault(key, {'id':slug(title)+'--'+slug(author.split(',')[0].split(' and ')[0].split(' & ')[0]) ,'title':title,'author':author,'entries':[]})
            b['entries'].append({'award':award,'year':year,'result':res})
            counts[award]=counts.get(award,0)+1
# ensure unique ids
seen={}
for k,b in books.items():
    i=b['id']; 
    if i in seen: b['id']=i+'-'+str(len(seen)); 
    seen[b['id']]=1
out=sorted(books.values(), key=lambda b:(b['author'].split()[-1].lower(), b['title']))
with open(os.path.join(HERE, '..', 'data.json'),'w',encoding='utf-8') as f:
    f.write('[\n'+',\n'.join(json.dumps(b,ensure_ascii=False,separators=(',',':')) for b in out)+'\n]\n')
print(len(out),'books', counts)
