
(() => {
"use strict";
const isEN=document.documentElement.lang.toLowerCase().startsWith("en");
const main=document.querySelector("main");
if(main){
  if(!main.id) main.id=isEN?"content":"conteudo";
  if(!document.querySelector(".skip-link")){
    const a=document.createElement("a");
    a.className="skip-link";
    a.href="#"+main.id;
    a.textContent=isEN?"Skip to main content":"Saltar para o conteúdo principal";
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
    box.innerHTML=isEN
      ?"<strong>Review warning:</strong> this page has not been editorially verified for more than 90 days. Check the linked official source before acting."
      :"<strong>Aviso de revisão:</strong> esta página não é revista editorialmente há mais de 90 dias. Confirme a fonte oficial indicada antes de agir.";
    main.insertBefore(box,main.firstChild);
  }
}

/* Improve external-link announcement without changing visible text. */
document.querySelectorAll('a[target="_blank"]').forEach(a=>{
  if(!a.getAttribute("aria-label")){
    const text=(a.textContent||"").trim();
    a.setAttribute("aria-label",text+(isEN?" — opens in a new tab":" — abre num novo separador"));
  }
});
})();
