"""Rebuild a candidate queue, not a person-identity matcher. Input: pdftotext -layout output."""
import argparse,csv,re,unicodedata,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('register_text');a=p.parse_args()
root=Path(__file__).resolve().parent
queries={
'gelis_variants':r'\b(?:gelis|botheler|botelhier|botelher|bouteiller)\b',
'calmelles':r'\bcalmelles\b','camelle':r'\bcamel(?:le|ie)\b','melonier':r'\bmelonier\b',
'loubens':r'\bloubens\b','durfort':r'\bdurfort\b','monesple':r'\bmonesple\b',
'battegay':r'\bbattegay\b','arignac':r'\barignac\b','pons_bru':r'\bpons bru\b',
'pons_malet':r'\bpons malet\b','belfag':r'\bbelfag\b','carpin':r'\bcarpin\b',
'fle chier'.replace(' ',''):r'\bflechier\b','santa_fe':r'\bsanta[- ]fe\b'}
def norm(s):return re.sub(r'\s+',' ',s).strip()
def fold(s):return ''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn').lower()
rows=[]
for num,raw in enumerate(Path(a.register_text).read_text().split('\f'),1):
 s=norm(raw); t=fold(s)
 for q,pattern in queries.items():
  for m in re.finditer(pattern,t):
   rows.append(dict(hit_id=f'hit{len(rows)+1:04}',query_id=q,pdf_page=num,page_header_raw=norm(raw[:180]),match_normalized=m.group(),snippet_ocr=s[max(0,m.start()-100):m.end()+160],review_status='candidate_only_not_a_confirmed_identity_or_relation',page_text_sha256=hashlib.sha256(raw.encode()).hexdigest()))
with (root/'search_hits.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
with (root/'search_queries.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['query_id','regex_accent_folded','limitations']);w.writerows((k,v,'OCR、空格、异拼会漏检；正文、注释、索引尚未自动区分') for k,v in queries.items())
print('candidate hits:',len(rows))
