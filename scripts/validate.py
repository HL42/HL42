#!/usr/bin/env python3
"""Offline checks for the Profile source, snapshots, SVGs, and safe update invariants."""
from pathlib import Path
from html.parser import HTMLParser
import json,re,sys,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.images=[];self.headings=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a':self.links.append(a.get('href',''))
        if tag=='img':self.images.append(a)
        if tag in ('h1','h2'):self.headings.append(tag)
text=(root/'README.md').read_text();p=Links();p.feed(text)
assert p.headings==['h1']+['h2']*5,'Expected semantic heading structure'
expected=['https://github.com/HL42/Repowiki','https://ciravo.app/','https://github.com/HL42/Enterprise-Multi-Source-RAG-Agent','https://github.com/HL42/SaveWise','https://save-wise-theta.vercel.app/']
assert all(u in p.links for u in expected),'Missing clickable project entry'
for image in p.images:assert image.get('alt'),'Missing alt'
assets=set(re.findall(r'(?:src|srcset)="(assets/[^" ]+)"',text))
assert len(assets)==12,'Expected desktop + mobile versions for six panels'
for asset in assets:
    path=root/asset;svg=ET.parse(path).getroot()
    assert svg.get('viewBox') and svg.find('{http://www.w3.org/2000/svg}title') is not None
    assert not re.search(r'<(?:script|foreignObject|image)\b|https?://(?!www.w3.org/2000/svg)',path.read_text()),'External or executable SVG content'
    if 'hero' in asset:
        assert 'prefers-reduced-motion' in path.read_text(),'Motion preference missing'
        assert 'infinite' not in path.read_text(),'Animation must be restrained'
from activity import select_events,render,update
raw=[{'id':'1','type':'PushEvent','created_at':'2026-11-05T17:57:43Z','actor':{'login':'HL42'},'repo':{'name':'HL42/SaveWise'},'payload':{}}, {'id':'2','type':'CreateEvent','created_at':'2026-11-23T04:04:04Z','actor':{'login':'HL42'},'repo':{'name':'HL42/personal-web'},'payload':{'ref_type':'branch','ref':'<script>alert(1)</script>'}}]
events=select_events(raw)
assert events[0]['id']=='2' and events[1]['id']=='1','Events must sort chronologically'
assert 'unavailable' in events[1]['label'],'Do not invent missing commit hashes'
assert '<script>' not in render(events,'2026-11-24 00:00 UTC'),'Escape untrusted labels'
assert len(select_events(raw+raw))==2,'Deduplicate events'
assert not select_events([{**raw[0],'repo':{'name':'other/project'}},{**raw[0],'repo':{'name':'HL42/HL42'}}]),'Respect owner scope and omit profile maintenance'
try:select_events({'message':'rate limit'})
except ValueError:pass
else:raise AssertionError('API errors must not erase the snapshot')
import tempfile
with tempfile.TemporaryDirectory() as tmp:
    r=Path(tmp);(r/'README.md').write_text('missing markers')
    try:update(r,raw,'test')
    except ValueError:pass
    else:raise AssertionError('Missing markers must fail closed')
    assert (r/'README.md').read_text()=='missing markers'
snapshot=json.loads((root/'activity.json').read_text())
assert snapshot['events']==sorted(snapshot['events'],key=lambda e:(e['sort'],e['id']),reverse=True)
for e in snapshot['events']:assert e['url'] in p.links,'Snapshot events must have clickable links'
print(f'Validated {len(assets)} SVGs, native project links, heading structure, activity snapshot, and update invariants.')
