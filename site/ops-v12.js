
(() => {
"use strict";
const lang=(document.documentElement.lang||"pt-PT").toLowerCase();
const isEN=lang.startsWith("en");
const ui={
  pt:{skip:"Saltar para o conteúdo principal",stale:"<strong>Aviso de revisão:</strong> esta página não é revista editorialmente há mais de 90 dias. Confirme a fonte oficial indicada antes de agir.",newtab:" — abre num novo separador"},
  en:{skip:"Skip to main content",stale:"<strong>Review warning:</strong> this page has not been editorially verified for more than 90 days. Check the linked official source before acting.",newtab:" — opens in a new tab"},
  fr:{skip:"Aller au contenu principal",stale:"<strong>Avertissement de révision :</strong> cette page n’a pas été vérifiée éditorialement depuis plus de 90 jours. Vérifiez la source officielle indiquée avant d’agir.",newtab:" — s’ouvre dans un nouvel onglet"},
  es:{skip:"Saltar al contenido principal",stale:"<strong>Aviso de revisión:</strong> esta página no se ha verificado editorialmente en más de 90 días. Consulte la fuente oficial indicada antes de actuar.",newtab:" — se abre en una pestaña nueva"},
  uk:{skip:"Перейти до основного вмісту",stale:"<strong>Попередження про перевірку:</strong> цю сторінку редакційно не перевіряли понад 90 днів. Перед діями перевірте вказане офіційне джерело.",newtab:" — відкривається в новій вкладці"},
  ru:{skip:"Перейти к основному содержанию",stale:"<strong>Предупреждение о проверке:</strong> эта страница не проходила редакционную проверку более 90 дней. Перед действиями проверьте указанное официальное источник.",newtab:" — откроется в новой вкладке"},
  hi:{skip:"मुख्य सामग्री पर जाएँ",stale:"<strong>समीक्षा चेतावनी:</strong> इस पृष्ठ की 90 दिनों से अधिक समय से संपादकीय समीक्षा नहीं हुई है। कोई कदम उठाने से पहले दी गई आधिकारिक स्रोत की जाँच करें।",newtab:" — नई टैब में खुलेगा"},
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

/* Announce dynamic search result changes when the existing search UI is present. */
const obs=new MutationObserver(()=>{
  document.querySelectorAll(".ux-search-results").forEach(el=>{
    if(!el.hasAttribute("role")){el.setAttribute("role","status");el.setAttribute("aria-live","polite");}
  });
});
obs.observe(document.documentElement,{childList:true,subtree:true});

/* Staleness warning using the page's last-reviewed meta.
   No network request and no personal data transmission. */
const meta=document.querySelector('meta[name="last-reviewed"]');
if(meta && main && !document.querySelector(".review-runtime")){
  const d=new Date(meta.content+"T00:00:00");
  const age=Math.floor((Date.now()-d.getTime())/86400000);
  const limit=90;
  if(Number.isFinite(age) && age>limit){
    const box=document.createElement("div");
    box.className="review-status stale review-runtime";
    box.innerHTML=copy.stale;
    main.insertBefore(box,main.firstChild);
  }
}

/* Improve external-link announcement without changing visible text. */
document.querySelectorAll('a[target="_blank"]').forEach(a=>{
  if(!a.getAttribute("aria-label")){
    const text=(a.textContent||"").trim();
    a.setAttribute("aria-label",text+copy.newtab);
  }
});

/* Load the shared multilingual selector. PT is at root; translated versions live one level down. */
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
})();
