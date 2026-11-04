import json,re,sys,collections
f,rx,themes=sys.argv[1],sys.argv[2],sys.argv[3:]
P=[p for p in json.load(open(f))['posts'] if re.search(rx,(p.get('title') or '')+(p.get('content') or ''),re.I)]
print('N=',len(P))
for t in themes:
    k,v=t.split('=');s=[p for p in P if re.search(v,(p.get('content') or '')+(p.get('title') or ''),re.I)]
    print(f'## {k} {len(s)} ({len(s)*100//max(1,len(P))}%)')
    for p in sorted(s,key=lambda p:-(p.get('likes') or 0))[:4]:
        c=re.sub(r'\s+',' ',p.get('content') or '')[:150]
        print(f"  [{p['source']} {p.get('likes')}♥ {p['pageCreatedAt'][:10]}] {c} | {p['url']}")
