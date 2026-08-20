(() => {
  'use strict';

  const LOCALE_SEGMENTS = ['en','fr','es','uk','ru','hi','bn'];
  const FALLBACK = [
    {code:'pt',native_name:'Português',status:'live'},
    {code:'en',native_name:'English',status:'live'},
    {code:'fr',native_name:'Français',status:'preparing'},
    {code:'es',native_name:'Español',status:'preparing'},
    {code:'uk',native_name:'Українська',status:'preparing'},
    {code:'ru',native_name:'Русский',status:'preparing'},
    {code:'hi',native_name:'हिन्दी',status:'preparing'},
    {code:'bn',native_name:'বাংলা',status:'preparing'}
  ];
  const COPY = {
    pt:{label:'Idioma',preparing:'Em tradução',note:'Os novos idiomas só ficam disponíveis depois de todas as páginas manterem o mesmo conteúdo e funcionalidades da versão principal.'},
    en:{label:'Language',preparing:'In translation',note:'New languages only become available after every page preserves the same content and functionality as the main version.'},
    fr:{label:'Langue',preparing:'Traduction en cours',note:'Les nouvelles langues ne deviennent disponibles qu’après vérification complète du contenu et des fonctionnalités.'},
    es:{label:'Idioma',preparing:'En traducción',note:'Los nuevos idiomas solo estarán disponibles tras verificar todo el contenido y las funciones.'},
    uk:{label:'Мова',preparing:'Перекладається',note:'Нові мови стануть доступними лише після повної перевірки змісту та функцій.'},
    ru:{label:'Язык',preparing:'Переводится',note:'Новые языки станут доступны только после полной проверки содержания и функций.'},
    hi:{label:'भाषा',preparing:'अनुवाद जारी',note:'नई भाषाएँ सभी सामग्री और सुविधाओं की पूरी जाँच के बाद ही उपलब्ध होंगी।'},
    bn:{label:'ভাষা',preparing:'অনুবাদ চলছে',note:'সব কনটেন্ট ও ফিচার সম্পূর্ণ যাচাইয়ের পরেই নতুন ভাষা চালু হবে।'}
  };

  function pathInfo(){
    const parts=location.pathname.split('/').filter(Boolean);
    const locale=parts.length && LOCALE_SEGMENTS.includes(parts[0]) ? parts[0] : 'pt';
    const page=(locale==='pt' ? parts[0] : parts[1]) || 'index.html';
    return {locale,page:page.endsWith('.html')?page:'index.html'};
  }

  function basePrefix(locale){ return locale==='pt' ? '' : '../'; }

  function hrefFor(code,page,current){
    if(code==='pt') return current==='pt' ? page : '../'+page;
    if(current==='pt') return code+'/'+page;
    return code===current ? page : '../'+code+'/'+page;
  }

  function globe(){
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/></svg>';
  }

  async function getLocales(prefix){
    try{
      const r=await fetch(prefix+'data/locales.json',{cache:'no-store'});
      if(!r.ok) throw new Error('locale config unavailable');
      const j=await r.json();
      return Array.isArray(j.locales)?j.locales:FALLBACK;
    }catch(_){ return FALLBACK; }
  }

  async function init(){
    const old=document.querySelector('.site-lang');
    const actions=document.querySelector('.header-actions');
    if(!old || !actions || document.querySelector('.gm-language')) return;

    const {locale,page}=pathInfo();
    const copy=COPY[locale]||COPY.en;
    const locales=await getLocales(basePrefix(locale));
    const current=locales.find(x=>x.code===locale)||locales[0];

    const wrap=document.createElement('div');
    wrap.className='gm-language';
    wrap.innerHTML=`<button class="gm-language-button" type="button" aria-haspopup="true" aria-expanded="false" aria-label="${copy.label}">${globe()}<span class="gm-current-code">${(current.code||locale).toUpperCase()}</span><span class="gm-chevron" aria-hidden="true">▾</span></button><div class="gm-language-menu" role="menu" aria-label="${copy.label}"></div>`;
    const menu=wrap.querySelector('.gm-language-menu');

    locales.forEach(item=>{
      const live=item.status==='live';
      const el=document.createElement(live?'a':'div');
      el.className='gm-language-option'+(live?'':' is-preparing');
      if(live){
        el.href=hrefFor(item.code,page,locale);
        el.setAttribute('role','menuitem');
        el.addEventListener('click',()=>{try{localStorage.setItem('guiaMigranteLocaleV1',item.code);}catch(_){}});
      }else{
        el.setAttribute('role','menuitem');
        el.setAttribute('aria-disabled','true');
        el.tabIndex=-1;
      }
      if(item.code===locale) el.setAttribute('aria-current','page');
      el.innerHTML=`<span class="gm-language-name"><span class="gm-language-code">${item.code.toUpperCase()}</span><span>${item.native_name||item.name||item.code}</span></span>${live?'':`<span class="gm-language-status">${copy.preparing}</span>`}`;
      menu.appendChild(el);
    });

    const note=document.createElement('div');
    note.className='gm-language-note';
    note.textContent=copy.note;
    menu.appendChild(note);

    const backdrop=document.createElement('div');
    backdrop.className='gm-language-backdrop';
    backdrop.setAttribute('aria-hidden','true');

    old.classList.add('gm-enhanced');
    old.insertAdjacentElement('afterend',wrap);
    wrap.insertAdjacentElement('afterend',backdrop);

    const button=wrap.querySelector('.gm-language-button');
    const close=()=>{wrap.classList.remove('open');button.setAttribute('aria-expanded','false');};
    button.addEventListener('click',()=>{
      const open=!wrap.classList.contains('open');
      wrap.classList.toggle('open',open);
      button.setAttribute('aria-expanded',String(open));
    });
    backdrop.addEventListener('click',close);
    document.addEventListener('keydown',e=>{if(e.key==='Escape') close();});
    document.addEventListener('click',e=>{if(wrap.classList.contains('open')&&!wrap.contains(e.target)&&e.target!==button) close();});
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
