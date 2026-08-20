#!/usr/bin/env python3
from __future__ import annotations
import difflib, hashlib, io, json, re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

SITE=Path('site')
SNAPS=Path('monitor/snapshots')
SNAPS.mkdir(parents=True,exist_ok=True)
UA='GuiaMigrantePT-OfficialSourceMonitor/1.0 (+https://guia-migrante-pt.pages.dev/)'
OFFICIAL={
'aima.gov.pt','contactenos.aima.gov.pt','portal-renovacoes.aima.gov.pt','services.aima.gov.pt',
'gov.pt','www.gov.pt','www2.gov.pt','justica.gov.pt','diariodarepublica.pt','info.portaldasfinancas.gov.pt',
'www.seg-social.pt','seg-social.pt','www.sns24.gov.pt','sns24.gov.pt','www.imt-ip.pt','imt-ip.pt',
'www.dges.gov.pt','dges.gov.pt','www.anacom.pt','anacom.pt','www.erse.pt','erse.pt',
'simuladorprecos.erse.pt','simuladorpotencia.erse.pt','www.portaldahabitacao.pt','portaldahabitacao.pt',
'clientebancario.bportugal.pt','www.livroreclamacoes.pt','livroreclamacoes.pt','www.parlamento.pt','parlamento.pt',
'www.cig.gov.pt','cig.gov.pt'}

HIGH_RISK={'aima.gov.pt','justica.gov.pt','diariodarepublica.pt','gov.pt','www.gov.pt','www2.gov.pt'}
STOP={'a','o','os','as','de','do','da','dos','das','e','em','no','na','nos','nas','por','para','com','the','of','to','and','in','for','with','official','fonte','source'}

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def clean_url(u):
    p=urlparse(u); path=re.sub(r'/+$','',p.path) or '/'; q=p.query if ('contentId=' in p.query or 'q=' in p.query or 'canal=' in p.query) else ''
    return urlunparse((p.scheme or 'https',p.netloc.lower(),path,'',q,''))
def sid(u): return 'src_'+hashlib.sha1(u.encode()).hexdigest()[:12]
def norm(s): return re.sub(r'\s+',' ',s).strip()
def terms(s):
    out=[]
    for x in re.findall(r'[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9.ºª-]{3,}',s.lower()):
        if x not in STOP and x not in out: out.append(x)
    return out[:18]

def registry():
    reg={}
    for p in SITE.rglob('*.html'):
        rel=str(p.relative_to(SITE)).replace('\\','/')
        soup=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
        main=soup.find('main')
        if not main: continue
        for a in main.find_all('a',href=True):
            h=a['href'].strip()
            if not h.startswith(('http://','https://')): continue
            u=clean_url(h); host=urlparse(u).netloc.lower()
            if host not in OFFICIAL: continue
            i=sid(u)
            e=reg.setdefault(i,{'id':i,'url':u,'domain':host,'pages':set(),'watch_terms':set(),'risk':'high' if host in HIGH_RISK else 'medium'})
            e['pages'].add(rel)
            ctx=a.get_text(' ',strip=True)
            parent=a.parent
            for _ in range(4):
                if not parent: break
                htag=parent.find(['h1','h2','h3'])
                if htag: ctx+=' '+htag.get_text(' ',strip=True); break
                parent=parent.parent
            e['watch_terms'].update(terms(ctx))
    out=[]
    for e in reg.values():
        e['pages']=sorted(e['pages']); e['watch_terms']=sorted(e['watch_terms'])[:18]; out.append(e)
    return sorted(out,key=lambda x:x['url'])

def html_text(content):
    soup=BeautifulSoup(content,'html.parser')
    for t in soup(['script','style','noscript','svg','form','nav','header','footer']): t.decompose()
    node=soup.find('main') or soup.find('article') or soup.body or soup
    return '\n'.join(norm(x) for x in node.get_text('\n').splitlines() if len(norm(x))>1)
def pdf_text(content):
    r=PdfReader(io.BytesIO(content)); parts=[]
    for p in r.pages: parts.extend(norm(x) for x in (p.extract_text() or '').splitlines() if norm(x))
    return '\n'.join(parts)
def fetch(sess,u):
    r=sess.get(u,timeout=(10,35),allow_redirects=True,headers={'User-Agent':UA,'Accept':'text/html,application/pdf;q=0.9,*/*;q=0.5'})
    r.raise_for_status(); c=(r.headers.get('content-type') or '').lower()
    if len(r.content)>15_000_000: raise RuntimeError('source over 15MB')
    txt=pdf_text(r.content) if ('pdf' in c or r.url.lower().endswith('.pdf')) else html_text(r.content)
    if len(txt)<100: raise RuntimeError('source text too short')
    return txt,r.url

def relevant(src,old,new):
    diff='\n'.join(x for x in difflib.unified_diff(old.splitlines(),new.splitlines(),n=1) if x.startswith(('+','-')) and not x.startswith(('+++','---')))
    low=diff.lower(); hit=any(t.lower() in low for t in src['watch_terms'] if len(t)>=4)
    ratio=abs(len(new)-len(old))/max(len(old),1)
    return hit or ratio>.30 or src['risk']=='high',diff[:6000]

def update_simple_facts(source_url,text,facts,changes):
    # deterministic values only; complex legal text is quarantined instead
    rules=[]
    if 'protecao-temporaria-para-pessoas-deslocados-da-ucrania-prorrogada-ate-2027' in source_url:
        rules.append(('temporary_protection_end',r'(?:até|ate)\s+(\d{1,2})\s+de\s+(março|marco)\s+de\s+(\d{4})',lambda m:f'{m.group(3)}-03-{int(m.group(1)):02d}'))
    if 'clientebancario.bportugal.pt/pt-pt/o-que-sao' in source_url:
        rules.append(('basic_banking_max_fee',r'(\d+[.,]\d{2})\s*€',lambda m:float(m.group(1).replace(',','.'))))
    if 'certificado-de-residencia-permanente-para-nacionais-ue' in source_url:
        rules.append(('aima_phone',r'(\(\+351\)\s*\d{3}\s*\d{3}\s*\d{3})',lambda m:norm(m.group(1))))
    for fid,pat,fn in rules:
        m=re.search(pat,text,re.I)
        if not m or fid not in facts.get('facts',{}): continue
        val=fn(m); old=facts['facts'][fid].get('value')
        if val!=old:
            facts['facts'][fid]['value']=val; facts['facts'][fid]['updated_at']=now()[:10]; facts['facts'][fid]['auto_updated']=True
            changes.append({'fact_id':fid,'old':old,'new':val,'url':source_url})

def main():
    sources=registry(); Path('monitor/sources.json').write_text(json.dumps({'version':2,'sources':sources},ensure_ascii=False,indent=2),encoding='utf-8')
    status_path=SITE/'data/source-status.json'; facts_path=SITE/'data/facts.json'; log_path=SITE/'data/change-log.json'
    status=json.loads(status_path.read_text(encoding='utf-8')) if status_path.exists() else {'version':2,'sources':{},'blocked_pages':{}}
    facts=json.loads(facts_path.read_text(encoding='utf-8')) if facts_path.exists() else {'version':1,'facts':{}}
    log=json.loads(log_path.read_text(encoding='utf-8')) if log_path.exists() else {'version':1,'changes':[]}
    sess=requests.Session(); changed=[]; errors=[]; fact_changes=[]; baseline=0
    for src in sources:
        i=src['id']; sp=SNAPS/f'{i}.json'; old=json.loads(sp.read_text(encoding='utf-8')) if sp.exists() else None
        try:
            text,final=fetch(sess,src['url']); h=hashlib.sha256(text.encode()).hexdigest(); ts=now()
            if old is None:
                sp.write_text(json.dumps({'url':src['url'],'final_url':final,'sha256':h,'checked_at':ts,'text':text},ensure_ascii=False),encoding='utf-8'); baseline+=1
                status['sources'][i]={'url':src['url'],'domain':src['domain'],'state':'healthy','checked_at':ts,'changed_at':None,'pages':src['pages']}; continue
            if old.get('sha256')==h:
                status['sources'][i]={'url':src['url'],'domain':src['domain'],'state':'healthy','checked_at':ts,'changed_at':None,'pages':src['pages']}; continue
            is_rel,diff=relevant(src,old.get('text',''),text)
            sp.write_text(json.dumps({'url':src['url'],'final_url':final,'sha256':h,'checked_at':ts,'text':text},ensure_ascii=False),encoding='utf-8')
            update_simple_facts(src['url'],text,facts,fact_changes)
            if is_rel:
                changed.append(i); status['sources'][i]={'url':src['url'],'domain':src['domain'],'state':'changed_pending_review','checked_at':ts,'changed_at':ts,'pages':src['pages'],'diff_excerpt':diff}
                log['changes'].insert(0,{'time':ts,'source_id':i,'url':src['url'],'state':'changed_pending_review','pages':src['pages'],'diff_excerpt':diff[:1200]})
            else:
                status['sources'][i]={'url':src['url'],'domain':src['domain'],'state':'healthy','checked_at':ts,'changed_at':None,'pages':src['pages']}
        except Exception as e:
            ts=now(); errors.append({'id':i,'url':src['url'],'error':str(e)})
            state='source_unavailable' if old else 'baseline_failed'
            status['sources'][i]={'url':src['url'],'domain':src['domain'],'state':state,'checked_at':ts,'changed_at':ts if old else None,'pages':src['pages'],'error':str(e)}
            if old: changed.append(i)
    blocked={}
    for src in sources:
        st=status['sources'].get(src['id'],{})
        if st.get('state') in {'changed_pending_review','source_unavailable'}:
            for pg in src['pages']: blocked.setdefault(pg,[]).append(src['id'])
    status['blocked_pages']={k:sorted(set(v)) for k,v in blocked.items()}; status['generated_at']=now(); status['baseline_complete']=all((SNAPS/f"{s['id']}.json").exists() for s in sources)
    status['summary']={'checked':len(sources),'new_baselines':baseline,'relevant_changes':len(set(changed)),'errors':len(errors),'fact_updates':len(fact_changes)}
    status_path.write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8'); facts_path.write_text(json.dumps(facts,ensure_ascii=False,indent=2),encoding='utf-8')
    log['changes']=log['changes'][:300]; log_path.write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
    Path('monitor/report.json').write_text(json.dumps({'generated_at':now(),'changed_sources':sorted(set(changed)),'blocked_pages':status['blocked_pages'],'errors':errors,'fact_updates':fact_changes},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(status['summary'],ensure_ascii=False))

if __name__=='__main__': main()
