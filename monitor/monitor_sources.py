#!/usr/bin/env python3
from __future__ import annotations
import difflib, hashlib, io, json, re, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urlunparse
import truststore; truststore.inject_into_ssl()
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SITE=Path('site'); SNAPS=Path('monitor/snapshots'); CANDS=Path('monitor/candidates')
SNAPS.mkdir(parents=True,exist_ok=True); CANDS.mkdir(parents=True,exist_ok=True)
UA='GuiaMigrantePT-OfficialSourceMonitor/1.2 (+https://guia-migrante-pt.pages.dev/)'
OFFICIAL={
'aima.gov.pt','contactenos.aima.gov.pt','portal-renovacoes.aima.gov.pt','services.aima.gov.pt',
'gov.pt','www.gov.pt','www2.gov.pt','justica.gov.pt','diariodarepublica.pt','info.portaldasfinancas.gov.pt',
'www.seg-social.pt','seg-social.pt','www.sns24.gov.pt','sns24.gov.pt','www.imt-ip.pt','imt-ip.pt',
'www.dges.gov.pt','dges.gov.pt','www.anacom.pt','anacom.pt','www.erse.pt','erse.pt',
'simuladorprecos.erse.pt','simuladorpotencia.erse.pt','www.portaldahabitacao.pt','portaldahabitacao.pt',
'clientebancario.bportugal.pt','www.livroreclamacoes.pt','livroreclamacoes.pt','www.parlamento.pt','parlamento.pt',
'www.cig.gov.pt','cig.gov.pt','www.cm-amadora.pt','cm-amadora.pt'}
HIGH={'aima.gov.pt','justica.gov.pt','diariodarepublica.pt','gov.pt','www.gov.pt','www2.gov.pt'}
INTERACTIVE={'contactenos.aima.gov.pt','portal-renovacoes.aima.gov.pt','services.aima.gov.pt','simuladorprecos.erse.pt','simuladorpotencia.erse.pt'}
STOP=set('a o os as de do da dos das e em no na nos nas por para com the of to and in for with official fonte source informação information acting agir antes before confirm confirme checked check'.split())
MONTHS={'janeiro':1,'fevereiro':2,'março':3,'marco':3,'abril':4,'maio':5,'junho':6,'julho':7,'agosto':8,'setembro':9,'outubro':10,'novembro':11,'dezembro':12}
class SourceRemovedError(RuntimeError): pass

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def norm(s): return re.sub(r'\s+',' ',s).strip()
def clean_url(u):
 p=urlparse(u); path=re.sub(r'/+$','',p.path) or '/'; q=p.query if any(x in p.query for x in ('contentId=','q=','canal=')) else ''
 return urlunparse((p.scheme or 'https',p.netloc.lower(),path,'',q,''))
def sid(u): return 'src_'+hashlib.sha1(u.encode()).hexdigest()[:12]
def is_pdf(u): return urlparse(u).path.lower().endswith('.pdf')
def required(host,u): return host in HIGH and host not in INTERACTIVE and not is_pdf(u)
def watch_terms(s):
 out=[]
 for x in re.findall(r'[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9.ºª-]{3,}',s.lower()):
  if x not in STOP and x not in out: out.append(x)
 return out[:18]

def registry():
 reg={}
 for p in SITE.rglob('*.html'):
  rel=str(p.relative_to(SITE)).replace('\\','/'); soup=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser'); main=soup.find('main')
  if not main: continue
  for a in main.find_all('a',href=True):
   h=a['href'].strip()
   if not h.startswith(('http://','https://')): continue
   u=clean_url(h); host=urlparse(u).netloc.lower()
   if host not in OFFICIAL: continue
   i=sid(u); e=reg.setdefault(i,{'id':i,'url':u,'domain':host,'pages':set(),'watch_terms':set(),'risk':'high' if host in HIGH else 'medium','required':required(host,u)})
   e['pages'].add(rel); ctx=a.get_text(' ',strip=True); parent=a.parent
   for _ in range(4):
    if not parent: break
    tag=parent.find(['h1','h2','h3'])
    if tag: ctx+=' '+tag.get_text(' ',strip=True); break
    parent=parent.parent
   e['watch_terms'].update(watch_terms(ctx))
 out=[]
 for e in reg.values(): e['pages']=sorted(e['pages']); e['watch_terms']=sorted(e['watch_terms'])[:18]; out.append(e)
 return sorted(out,key=lambda x:x['url'])

def html_text(content):
 soup=BeautifulSoup(content,'html.parser')
 for t in soup(['script','style','noscript','svg','form','nav','header','footer']): t.decompose()
 node=soup.find('main') or soup.find('article') or soup.body or soup
 return '\n'.join(x for x in (norm(v) for v in node.get_text('\n').splitlines()) if len(x)>1 and 'ERR_CERT_' not in x and 'Privacy error' not in x)
def pdf_text(content):
 r=PdfReader(io.BytesIO(content)); return '\n'.join(norm(x) for p in r.pages for x in (p.extract_text() or '').splitlines() if norm(x))
def make_session():
 s=requests.Session(); retry=Retry(total=1,connect=1,read=1,status=1,backoff_factor=.8,status_forcelist=(429,500,502,503,504),allowed_methods=frozenset({'GET','HEAD'})); a=HTTPAdapter(max_retries=retry); s.mount('https://',a); s.mount('http://',a); return s
def chrome():
 for n in ('google-chrome','google-chrome-stable','chromium','chromium-browser'):
  p=shutil.which(n)
  if p: return p
 return None
def browser_fetch(u):
 c=chrome()
 if not c: raise RuntimeError('browser fallback unavailable')
 p=subprocess.run([c,'--headless=new','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--disable-background-networking','--dump-dom',u],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=70)
 raw=p.stdout
 if p.returncode or not raw: raise RuntimeError(f'browser fallback failed ({p.returncode})')
 low=raw.lower()
 if b'err_cert_' in low or b'privacy error' in low or b'your connection is not private' in low: raise RuntimeError('browser rejected TLS certificate')
 txt=html_text(raw)
 if len(txt)<100: raise RuntimeError('browser-rendered source text too short')
 return txt,u,'browser'
def fetch(sess,u):
 err=None
 try:
  r=sess.get(u,timeout=(8,30),allow_redirects=True,headers={'User-Agent':UA,'Accept':'text/html,application/pdf;q=0.9,*/*;q=0.5'})
  if r.status_code in (404,410): raise SourceRemovedError(f'official source returned HTTP {r.status_code}')
  r.raise_for_status(); c=(r.headers.get('content-type') or '').lower()
  if len(r.content)>15_000_000: raise RuntimeError('source over 15MB')
  pdf='pdf' in c or r.url.lower().endswith('.pdf'); txt=pdf_text(r.content) if pdf else html_text(r.content)
  if len(txt)>=100: return txt,r.url,'requests'
  if pdf: raise RuntimeError('PDF text too short')
  err=RuntimeError('source text too short')
 except SourceRemovedError: raise
 except Exception as e: err=e
 if is_pdf(u): raise err or RuntimeError('PDF fetch failed')
 try: return browser_fetch(u)
 except Exception as b: raise RuntimeError(f'primary fetch failed: {err}; browser fallback failed: {b}') from b

def relevant(src,old,new):
 lines=[x for x in difflib.unified_diff(old.splitlines(),new.splitlines(),n=1) if x.startswith(('+','-')) and not x.startswith(('+++','---'))]; diff='\n'.join(lines)
 if not diff: return False,''
 low=diff.lower(); hit=any(t.lower() in low for t in src['watch_terms'] if len(t)>=4); ratio=abs(len(new)-len(old))/max(len(old),1); threshold=.08 if src['risk']=='high' else .20
 return hit or ratio>threshold,diff[:6000]
def pt_date(text):
 m=re.search(r'(\d{1,2})\s+de\s+([A-Za-zÀ-ÿ]+)\s+de\s+(\d{4})',text,re.I)
 if not m or m.group(2).lower() not in MONTHS: return None
 return f'{int(m.group(3)):04d}-{MONTHS[m.group(2).lower()]:02d}-{int(m.group(1)):02d}'
def set_fact(facts,changes,fid,val,url):
 if val is None or fid not in facts.get('facts',{}) or facts['facts'][fid].get('value')==val: return
 old=facts['facts'][fid].get('value'); facts['facts'][fid].update(value=val,updated_at=now()[:10],auto_updated=True); changes.append({'fact_id':fid,'old':old,'new':val,'url':url})
def update_facts(url,text,facts,changes):
 if 'protecao-temporaria-para-pessoas-deslocados-da-ucrania-prorrogada-ate-2027' in url:
  m=re.search(r'(?:até|ate)\s+(?:ao\s+dia\s+)?(\d{1,2}\s+de\s+[A-Za-zÀ-ÿ]+\s+de\s+\d{4})',text,re.I); set_fact(facts,changes,'temporary_protection_end',pt_date(m.group(1)) if m else None,url)
 if 'clientebancario.bportugal.pt/pt-pt/o-que-sao' in url:
  m=re.search(r'(?:máxim[oa]|não\s+podem\s+exceder|não\s+pode\s+ultrapassar|limite).*?(\d+[.,]\d{2})\s*€',text,re.I); v=float(m.group(1).replace(',','.')) if m else None
  if v is not None and 0<=v<=50: set_fact(facts,changes,'basic_banking_max_fee',round(v,2),url)
 if 'certificado-de-residencia-permanente-para-nacionais-ue' in url:
  m=re.search(r'(?:Telefone|Centro\s+de\s+Contacto).*?(\(\+351\)\s*\d{3}\s*\d{3}\s*\d{3})',text,re.I); set_fact(facts,changes,'aima_phone',norm(m.group(1)) if m else None,url)
  h=re.search(r'(?:Horário|horario).*?(\d{2})[h:](\d{2}).*?(\d{2})[h:](\d{2})',text,re.I); set_fact(facts,changes,'aima_hours',f'{h.group(1)}:{h.group(2)}-{h.group(3)}:{h.group(4)}' if h else None,url)
 if 'portal-de-renovacoes-certificados-e-cartoes' in url:
  m=re.search(r'(?:entre|de)\s+(\d{1,2}\s+de\s+[A-Za-zÀ-ÿ]+\s+de\s+\d{4})\s+(?:e|a)\s+(\d{1,2}\s+de\s+[A-Za-zÀ-ÿ]+\s+de\s+\d{4})',text,re.I)
  if m: set_fact(facts,changes,'renewal_start',pt_date(m.group(1)),url); set_fact(facts,changes,'renewal_end',pt_date(m.group(2)),url)
 if 'pedir-os-numeros-de-identificacao-fiscal-seguranca-social-e-nacional-de-utente' in url:
  m=re.search(r'(\d{1,3})\s+Espaços?\s+Cidad',text,re.I)
  if m and 1<=int(m.group(1))<=100: set_fact(facts,changes,'combined_id_locations',int(m.group(1)),url)
def write_snap(path,src,final,text,h,ts,method): path.write_text(json.dumps({'url':src['url'],'final_url':final,'sha256':h,'checked_at':ts,'fetch_method':method,'text':text},ensure_ascii=False),encoding='utf-8')

def main():
 sources=registry(); Path('monitor/sources.json').write_text(json.dumps({'version':4,'sources':sources},ensure_ascii=False,indent=2),encoding='utf-8')
 spath=SITE/'data/source-status.json'; fpath=SITE/'data/facts.json'; lpath=SITE/'data/change-log.json'
 status=json.loads(spath.read_text(encoding='utf-8')) if spath.exists() else {'version':4,'sources':{},'blocked_pages':{}}; facts=json.loads(fpath.read_text(encoding='utf-8')) if fpath.exists() else {'version':1,'facts':{}}; log=json.loads(lpath.read_text(encoding='utf-8')) if lpath.exists() else {'version':1,'changes':[]}
 sess=make_session(); changed=[]; errors=[]; fact_changes=[]; baseline=0
 for src in sources:
  i=src['id']; bp=SNAPS/f'{i}.json'; cp=CANDS/f'{i}.json'; old=json.loads(bp.read_text(encoding='utf-8')) if bp.exists() else None; prev=status.get('sources',{}).get(i,{})
  try:
   text,final,method=fetch(sess,src['url']); h=hashlib.sha256(text.encode()).hexdigest(); ts=now()
   if old is None:
    write_snap(bp,src,final,text,h,ts,method); cp.unlink(missing_ok=True); baseline+=1; update_facts(src['url'],text,facts,fact_changes); state='healthy'
    status.setdefault('sources',{})[i]={'url':src['url'],'domain':src['domain'],'state':state,'checked_at':ts,'changed_at':None,'pages':src['pages'],'required':src['required'],'fetch_method':method}; continue
   if old.get('sha256')==h:
    cp.unlink(missing_ok=True); status.setdefault('sources',{})[i]={'url':src['url'],'domain':src['domain'],'state':'healthy','checked_at':ts,'changed_at':None,'pages':src['pages'],'required':src['required'],'fetch_method':method}; continue
   is_rel,diff=relevant(src,old.get('text',''),text); update_facts(src['url'],text,facts,fact_changes)
   if is_rel:
    write_snap(cp,src,final,text,h,ts,method); changed.append(i); status.setdefault('sources',{})[i]={'url':src['url'],'domain':src['domain'],'state':'changed_pending_review','checked_at':ts,'changed_at':prev.get('changed_at') or ts,'pages':src['pages'],'required':src['required'],'fetch_method':method,'candidate_sha256':h,'diff_excerpt':diff}
    if prev.get('candidate_sha256')!=h: log['changes'].insert(0,{'time':ts,'source_id':i,'url':src['url'],'state':'changed_pending_review','pages':src['pages'],'candidate_sha256':h,'diff_excerpt':diff[:1200]})
   else:
    write_snap(bp,src,final,text,h,ts,method); cp.unlink(missing_ok=True); status.setdefault('sources',{})[i]={'url':src['url'],'domain':src['domain'],'state':'healthy','checked_at':ts,'changed_at':None,'pages':src['pages'],'required':src['required'],'fetch_method':method,'note':'non-relevant source change accepted automatically'}
  except SourceRemovedError as e:
   ts=now(); errors.append({'id':i,'url':src['url'],'domain':src['domain'],'risk':src['risk'],'required':src['required'],'had_baseline':old is not None,'kind':'removed','error':str(e)})
   if old is not None:
    changed.append(i); state='source_removed'; changed_at=prev.get('changed_at') or ts
   else: state='baseline_failed'; changed_at=None
   status.setdefault('sources',{})[i]={'url':src['url'],'domain':src['domain'],'state':state,'checked_at':ts,'changed_at':changed_at,'pages':src['pages'],'required':src['required'],'error':str(e)}
  except Exception as e:
   ts=now(); count=int(prev.get('failure_count',0))+1; errors.append({'id':i,'url':src['url'],'domain':src['domain'],'risk':src['risk'],'required':src['required'],'had_baseline':old is not None,'kind':'fetch_error','failure_count':count,'error':str(e)}); state='fetch_error' if old is not None else 'baseline_failed'
   status.setdefault('sources',{})[i]={'url':src['url'],'domain':src['domain'],'state':state,'checked_at':ts,'changed_at':None,'pages':src['pages'],'required':src['required'],'failure_count':count,'error':str(e)}
 blocked={}
 for src in sources:
  if status.get('sources',{}).get(src['id'],{}).get('state') in {'changed_pending_review','source_removed'}:
   for pg in src['pages']: blocked.setdefault(pg,[]).append(src['id'])
 req=[s for s in sources if s['required']]; missing=[s['id'] for s in req if not (SNAPS/f"{s['id']}.json").exists()]; complete=not missing; critical=[e for e in errors if e.get('required') and not e.get('had_baseline')]; coverage=complete and not critical
 status.update(version=4,blocked_pages={k:sorted(set(v)) for k,v in blocked.items()},generated_at=now(),baseline_complete=complete,coverage_ok=coverage,summary={'checked':len(sources),'required_sources':len(req),'new_baselines':baseline,'relevant_changes':len(set(changed)),'blocked_pages':len(blocked),'errors':len(errors),'critical_errors':len(critical),'missing_required':len(missing),'fact_updates':len(fact_changes),'browser_fallback_available':bool(chrome())})
 spath.write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8'); fpath.write_text(json.dumps(facts,ensure_ascii=False,indent=2),encoding='utf-8'); log['changes']=log.get('changes',[])[:300]; lpath.write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
 report={'generated_at':now(),'baseline_complete':complete,'coverage_ok':coverage,'browser_fallback_available':bool(chrome()),'required_sources':len(req),'missing_required':missing,'changed_sources':sorted(set(changed)),'blocked_pages':status['blocked_pages'],'errors':errors,'critical_errors':critical,'fact_updates':fact_changes}; Path('monitor/report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(status['summary'],ensure_ascii=False))
if __name__=='__main__': main()
