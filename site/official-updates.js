(() => {
  "use strict";

  if (location.pathname.startsWith('/admin-') || location.pathname.startsWith('/api/')) return;

  const rawLang=(document.documentElement.lang||'pt-PT').toLowerCase();
  const code=rawLang.startsWith('en')?'en':rawLang.startsWith('fr')?'fr':rawLang.startsWith('es')?'es':rawLang.startsWith('uk')?'uk':rawLang.startsWith('ru')?'ru':rawLang.startsWith('hi')?'hi':rawLang.startsWith('bn')?'bn':'pt';
  const locale={pt:'pt-PT',en:'en-GB',fr:'fr-FR',es:'es-ES',uk:'uk-UA',ru:'ru-RU',hi:'hi-IN',bn:'bn-BD'}[code]||'pt-PT';
  const copy={
    pt:{recent:'Atualização oficial recente',latest:'Últimas atualizações oficiais',source:'Fonte: AIMA',open:'Ver fonte oficial',note:'O Guia acompanha publicações oficiais e mantém alterações substantivas sob validação antes de substituir orientação sensível.'},
    en:{recent:'Recent official update',latest:'Latest official updates',source:'Source: AIMA',open:'Open official source',note:'The Guide follows official publications and keeps substantive changes under review before replacing sensitive guidance.'},
    fr:{recent:'Mise à jour officielle récente',latest:'Dernières mises à jour officielles',source:'Source : AIMA',open:'Voir la source officielle',note:'Le Guide suit les publications officielles et vérifie les changements importants avant de remplacer des informations sensibles.'},
    es:{recent:'Actualización oficial reciente',latest:'Últimas actualizaciones oficiales',source:'Fuente: AIMA',open:'Ver fuente oficial',note:'La Guía sigue las publicaciones oficiales y valida los cambios importantes antes de sustituir información sensible.'},
    uk:{recent:'Нове офіційне оновлення',latest:'Останні офіційні оновлення',source:'Джерело: AIMA',open:'Відкрити офіційне джерело',note:'Гід відстежує офіційні публікації та перевіряє суттєві зміни перед заміною чутливої інформації.'},
    ru:{recent:'Свежее официальное обновление',latest:'Последние официальные обновления',source:'Источник: AIMA',open:'Открыть официальный источник',note:'Гид отслеживает официальные публикации и проверяет существенные изменения перед заменой чувствительной информации.'},
    hi:{recent:'हाल की आधिकारिक जानकारी',latest:'नवीनतम आधिकारिक अपडेट',source:'स्रोत: AIMA',open:'आधिकारिक स्रोत खोलें',note:'गाइड आधिकारिक प्रकाशनों की निगरानी करता है और संवेदनशील जानकारी बदलने से पहले महत्वपूर्ण बदलावों की समीक्षा करता है।'},
    bn:{recent:'সাম্প্রতিক সরকারি আপডেট',latest:'সর্বশেষ সরকারি আপডেট',source:'উৎস: AIMA',open:'সরকারি উৎস খুলুন',note:'গাইড সরকারি প্রকাশনা অনুসরণ করে এবং সংবেদনশীল তথ্য বদলানোর আগে গুরুত্বপূর্ণ পরিবর্তন যাচাই করে।'}
  }[code];

  const parts=location.pathname.split('/').filter(Boolean);
  const localized=['en','fr','es','uk','ru','hi','bn'].includes(parts[0]);
  const page=(localized?parts.slice(1):parts).pop()||'index.html';

  function fmtDate(value){
    if(!value) return '';
    const m=String(value).match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if(!m) return String(value);
    return new Intl.DateTimeFormat(locale,{day:'numeric',month:'long',year:'numeric'}).format(new Date(Date.UTC(Number(m[1]),Number(m[2])-1,Number(m[3]))));
  }

  function recentEnough(value,days=90){
    if(!value) return true;
    const t=Date.parse(value+'T00:00:00Z');
    return Number.isFinite(t) && (Date.now()-t)<=days*86400000;
  }

  function safeOfficialUrl(raw){
    try{
      const u=new URL(raw,location.origin);
      return u.protocol==='https:' && u.hostname.toLowerCase()==='aima.gov.pt' ? u.href : '';
    }catch{return '';}
  }

  function style(el,css){Object.assign(el.style,css);return el;}

  function makeLink(item){
    const href=safeOfficialUrl(item.url);
    if(!href) return null;
    const a=document.createElement('a');
    a.href=href;
    a.target='_blank';
    a.rel='noopener';
    a.textContent=copy.open+' ↗';
    style(a,{display:'inline-flex',marginTop:'10px',fontWeight:'800',fontSize:'.82rem',color:'#1e3a8a',textDecoration:'none'});
    return a;
  }

  function makeCard(item,compact=false){
    const article=document.createElement('article');
    style(article,{background:'#fff',border:'1px solid #dbe4f0',borderRadius:'16px',padding:compact?'15px':'18px',boxShadow:'0 8px 24px rgba(15,23,42,.06)'});

    const meta=document.createElement('div');
    meta.textContent=[copy.source,fmtDate(item.date)].filter(Boolean).join(' · ');
    style(meta,{fontSize:'.72rem',fontWeight:'850',letterSpacing:'.03em',color:'#047857',textTransform:'uppercase'});

    const h=document.createElement(compact?'h3':'h2');
    h.textContent=item.title||'AIMA';
    style(h,{margin:'7px 0 0',fontSize:compact?'1rem':'1.2rem',lineHeight:'1.25',color:'#172554'});

    const p=document.createElement('p');
    const summary=code==='pt'?(item.summary_pt||''):(item.summary_en||item.summary_pt||'');
    p.textContent=summary;
    style(p,{margin:'7px 0 0',fontSize:'.86rem',lineHeight:'1.55',color:'#64748b'});

    article.append(meta,h);
    if(summary) article.append(p);
    const link=makeLink(item); if(link) article.append(link);
    return article;
  }

  async function run(){
    const main=document.querySelector('main');
    if(!main || document.querySelector('[data-official-updates-live]')) return;

    try{
      const response=await fetch('/data/official-updates.json?ts='+Date.now(),{cache:'no-store',headers:{Accept:'application/json'}});
      if(!response.ok) return;
      const data=await response.json();
      const updates=Array.isArray(data.updates)?data.updates:[];
      if(!updates.length) return;

      if(page==='atualizacoes.html'){
        const section=document.createElement('section');
        section.dataset.officialUpdatesLive='feed';
        style(section,{padding:'26px 0 10px'});
        const inner=document.createElement('div');
        inner.className='container';
        const title=document.createElement('h2');
        title.textContent=copy.latest;
        style(title,{margin:'0 0 6px',fontSize:'clamp(1.55rem,5vw,2.2rem)',color:'#172554',letterSpacing:'-.03em'});
        const note=document.createElement('p');
        note.textContent=copy.note;
        style(note,{margin:'0 0 16px',maxWidth:'760px',color:'#64748b',fontSize:'.88rem'});
        const grid=document.createElement('div');
        style(grid,{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(245px,1fr))',gap:'12px'});
        updates.slice(0,6).forEach(item=>grid.append(makeCard(item,true)));
        inner.append(title,note,grid); section.append(inner);
        const first=main.querySelector(':scope > section');
        if(first) first.insertAdjacentElement('afterend',section); else main.prepend(section);
        return;
      }

      const relevant=updates.filter(item=>Array.isArray(item.pages)&&item.pages.includes(page)&&page!=='atualizacoes.html'&&recentEnough(item.date,90));
      if(!relevant.length) return;
      const item=relevant[0];

      const wrap=document.createElement('div');
      wrap.dataset.officialUpdatesLive='banner';
      style(wrap,{width:'min(calc(100% - 24px),1180px)',margin:'18px auto',padding:'16px',border:'1px solid #bfdbfe',borderRadius:'16px',background:'#eff6ff',boxShadow:'0 8px 24px rgba(15,23,42,.05)'});
      const label=document.createElement('div');
      label.textContent=copy.recent+' · '+[copy.source,fmtDate(item.date)].filter(Boolean).join(' · ');
      style(label,{fontSize:'.72rem',fontWeight:'900',textTransform:'uppercase',letterSpacing:'.04em',color:'#047857'});
      const h=document.createElement('strong');
      h.textContent=item.title||'AIMA';
      style(h,{display:'block',marginTop:'5px',fontSize:'.98rem',color:'#172554'});
      const p=document.createElement('p');
      p.textContent=code==='pt'?(item.summary_pt||''):(item.summary_en||item.summary_pt||'');
      style(p,{margin:'5px 0 0',fontSize:'.84rem',lineHeight:'1.5',color:'#52647b'});
      wrap.append(label,h); if(p.textContent) wrap.append(p);
      const link=makeLink(item); if(link) wrap.append(link);
      const first=main.querySelector(':scope > section');
      if(first) first.insertAdjacentElement('afterend',wrap); else main.prepend(wrap);
    }catch(_){/* Last known static guidance remains available. */}
  }

  run();
})();
