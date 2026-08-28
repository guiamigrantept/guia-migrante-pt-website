
(() => {
"use strict";
const lang=(document.documentElement.lang||"pt-PT").toLowerCase();
const isEN=lang.startsWith("en");
const ui={
  pt:{skip:"Saltar para o conteúdo principal",stale:"<strong>Aviso de revisão:</strong> esta página não é revista editorialmente há mais de 90 dias. Confirme a fonte oficial indicada antes de agir.",newtab:" — abre num novo separador"},
  en:{skip:"Skip to main content",stale:"<strong>Review warning:</strong> this page has not been editorially verified for more than 90 days. Check the linked official source before acting.",newtab:" — opens in a new tab"},
  fr:{skip:"Aller au contenu principal",stale:"<strong>Avertissement de révision :</strong> cette page n’a pas été vérifiée éditorialement depuis plus de 90 dias. Vérifiez la source officielle indiquée avant d’agir.",newtab:" — s’ouvre dans un nouvel onglet"},
  es:{skip:"Saltar al contenido principal",stale:"<strong>Aviso de revisión:</strong> esta página no se ha verificado editorialmente en más de 90 días. Consulte la fuente oficial indicada antes de actuar.",newtab:" — se abre en una pestaña nueva"},
  uk:{skip:"Перейти до основного вмісту",stale:"<strong>Попередження про перевірку:</strong> цю сторінку редакційно не перевіряли понад 90 днів. Перед діями перевірте вказане офіційне джерело.",newtab:" — відкривається в новій вкладці"},
  ru:{skip:"Перейти к основному содержанию",stale:"<strong>Предупреждение о проверке:</strong> эта страница не проходила редакционную проверку более 90 дней. Перед действиями проверьте указанный официальный источник.",newtab:" — откроется в новой вкладке"},
  hi:{skip:"मुख्य सामग्री पर जाएँ",stale:"<strong>समीक्षा चेतावनी:</strong> इस पृष्ठ की 90 दिनों से अधिक समय से संपादकीय समीक्षा नहीं हुई है। कोई कदम उठाने से पहले दिए गए आधिकारिक स्रोत की जाँच करें।",newtab:" — नई टैब में खुलेगा"},
  bn:{skip:"মূল বিষয়বস্তুতে যান",stale:"<strong>পর্যালোচনা সতর্কতা:</strong> এই পৃষ্ঠাটি ৯০ দিনের বেশি সময় ধরে সম্পাদকীয়ভাবে যাচাই করা হয়নি। কোনো পদক্ষেপ নেওয়ার আগে উল্লেখিত সরকারি উৎস যাচাই করুন।",newtab:" — নতুন ট্যাবে খুলবে"}
};
const code=lang.startsWith("fr")?"fr":lang.startsWith("es")?"es":lang.startsWith("uk")?"uk":lang.startsWith("ru")?"ru":lang.startsWith("hi")?"hi":lang.startsWith("bn")?"bn":isEN?"en":"pt";
const copy=ui[code]||ui.pt;
const main=document.querySelector("main");
if(main){
  if(!main.id) main.id=isEN?"content":"conteudo";
  if(!document.querySelector(".skip-link")){
    const a=document.createElement("a");
    a.className="skip-link";
    a.href="#"+main.id;
    a.textContent=copy.skip;
    document.body.insertBefore(a,document.body.firstChild);
  }
}
document.querySelectorAll("main").forEach(m=>m.setAttribute("tabindex","-1"));

const obs=new MutationObserver(()=>{
  document.querySelectorAll(".ux-search-results").forEach(el=>{
    if(!el.hasAttribute("role")){el.setAttribute("role","status");el.setAttribute("aria-live","polite");}
  });
});
obs.observe(document.documentElement,{childList:true,subtree:true});

const meta=document.querySelector('meta[name="last-reviewed"]');
if(meta && main && !document.querySelector(".review-runtime")){
  const d=new Date(meta.content+"T00:00:00");
  const age=Math.floor((Date.now()-d.getTime())/86400000);
  if(Number.isFinite(age) && age>90){
    const box=document.createElement("div");
    box.className="review-status stale review-runtime";
    box.innerHTML=copy.stale;
    main.insertBefore(box,main.firstChild);
  }
}

document.querySelectorAll('a[target="_blank"]').forEach(a=>{
  if(!a.getAttribute("aria-label")){
    const text=(a.textContent||"").trim();
    a.setAttribute("aria-label",text+copy.newtab);
  }
});

/* Privacy-first first-party analytics.
   No cookies, persistent IDs, IP storage, user-agent storage or full referrer URLs.
   Only campaign labels may be kept in sessionStorage for the current browser session
   so a later contact conversion can still be attributed to its campaign. */
const analyticsBlocked=location.pathname.startsWith('/admin-')||location.pathname.startsWith('/api/')||navigator.globalPrivacyControl===true||navigator.doNotTrack==='1'||window.doNotTrack==='1';
const params=new URLSearchParams(location.search);
let referrerHost='';
try{if(document.referrer){const u=new URL(document.referrer);if(u.hostname!==location.hostname)referrerHost=u.hostname.toLowerCase();}}catch{}
let campaign={utmSource:'',utmMedium:'',utmCampaign:''};
if(!analyticsBlocked){
  const current={utmSource:(params.get('utm_source')||'').slice(0,120),utmMedium:(params.get('utm_medium')||'').slice(0,120),utmCampaign:(params.get('utm_campaign')||'').slice(0,160)};
  if(current.utmSource||current.utmMedium||current.utmCampaign){
    campaign=current;
    try{sessionStorage.setItem('gmpCampaign',JSON.stringify(current));}catch{}
  }else{
    try{
      const saved=JSON.parse(sessionStorage.getItem('gmpCampaign')||'{}');
      campaign={utmSource:String(saved.utmSource||'').slice(0,120),utmMedium:String(saved.utmMedium||'').slice(0,120),utmCampaign:String(saved.utmCampaign||'').slice(0,160)};
    }catch{}
  }
}
function track(event,targetHost=''){
  if(analyticsBlocked) return;
  const payload={event,path:location.pathname,locale:code,referrerHost,targetHost:String(targetHost||'').slice(0,180).toLowerCase(),...campaign};
  fetch('/api/analytics',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(payload),keepalive:true,credentials:'same-origin'}).catch(()=>{});
}
window.GMPAnalytics={track};
if(!analyticsBlocked) track('page_view');
window.addEventListener('gmp:contact-success',()=>track('contact_submit'));

const officialHosts=['gov.pt','www.gov.pt','aima.gov.pt','www.aima.gov.pt','seg-social.pt','www.seg-social.pt','sns24.gov.pt','www.sns24.gov.pt','justica.gov.pt','www.justica.gov.pt','dre.pt','www.dre.pt','irn.justica.gov.pt'];
document.addEventListener('click',event=>{
  const a=event.target?.closest?.('a[href]');
  if(!a) return;
  try{const u=new URL(a.href,location.href);if(officialHosts.includes(u.hostname.toLowerCase()))track('official_link_click',u.hostname);}catch{}
},{capture:true});

if("serviceWorker" in navigator && location.protocol==="https:"){
  navigator.serviceWorker.register("/sw.js",{scope:"/"}).catch(()=>{});
}

const pathParts=location.pathname.split('/').filter(Boolean);
const translated=['en','fr','es','uk','ru','hi','bn'].includes(pathParts[0]);
const prefix=translated?'../':'';
if(!document.querySelector('link[data-gm-language]')){
  const css=document.createElement('link');
  css.rel='stylesheet';
  css.href=prefix+'language-switcher.css';
  css.dataset.gmLanguage='style';
  document.head.appendChild(css);
}
if(!document.querySelector('script[data-gm-language]')){
  const script=document.createElement('script');
  script.src=prefix+'language-switcher.js';
  script.defer=true;
  script.dataset.gmLanguage='script';
  document.head.appendChild(script);
}
if(!document.querySelector('script[data-gm-official-updates]')){
  const script=document.createElement('script');
  script.src=prefix+'official-updates.js';
  script.defer=true;
  script.dataset.gmOfficialUpdates='script';
  document.head.appendChild(script);
}
})();
