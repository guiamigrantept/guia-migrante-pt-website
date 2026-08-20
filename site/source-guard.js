
(() => {
"use strict";
const lang=document.documentElement.lang.toLowerCase().startsWith("en")?"en":"pt";
const metaPolicy=document.querySelector('meta[name="source-policy"]');
const pageIds=(document.querySelector('meta[name="official-source-ids"]')?.content||"").split(/\s+/).filter(Boolean);
const pathname=location.pathname.replace(/^\/+/,"") || "index.html";
const pageKey=pathname.endsWith("/") ? pathname+"index.html" : pathname;

function fmtFact(f){
  const locale=lang==="en"?"en-GB":"pt-PT";
  if(f.type==="date"){
    const [y,m,d]=String(f.value).split("-").map(Number);
    return new Intl.DateTimeFormat(locale,{day:"numeric",month:"long",year:"numeric"}).format(new Date(Date.UTC(y,m-1,d)));
  }
  if(f.type==="integer") return String(f.value);
  if(f.type==="currency_eur"){
    return new Intl.NumberFormat(locale,{style:"currency",currency:"EUR",minimumFractionDigits:2}).format(Number(f.value));
  }
  if(f.type==="time_range"){
    const [a,b]=String(f.value).split("-");
    return lang==="en" ? `${a}–${b}` : `${a.replace(":","h")}–${b.replace(":","h")}`;
  }
  return String(f.value);
}

async function loadJSON(url){
  const r=await fetch(url,{cache:"no-store",headers:{"Accept":"application/json"}});
  if(!r.ok) throw new Error(`${r.status}`);
  return r.json();
}

async function applyFacts(){
  try{
    const data=await loadJSON("/data/facts.json?ts="+Date.now());
    for(const el of document.querySelectorAll("[data-fact]")){
      const f=data.facts?.[el.dataset.fact];
      if(f) el.textContent=fmtFact(f);
    }
  }catch(e){ /* static fallback values remain visible */ }
}

async function applySourceGuard(){
  if(!pageIds.length) return;
  try{
    const state=await loadJSON("/data/source-status.json?ts="+Date.now());
    const blocked=(state.blocked_pages||{})[pageKey] || (state.blocked_pages||{})[pathname] || [];
    if(!blocked.length) return;

    const sources=(state.sources||{});
    const relevant=blocked.map(id=>sources[id]).filter(Boolean);
    const main=document.querySelector("main");
    if(!main) return;

    const box=document.createElement("div");
    box.className="source-change-banner";
    const changedAt=relevant.map(x=>x.changed_at).filter(Boolean).sort().slice(-1)[0] || "";
    const links=relevant.slice(0,3).map(x=>`<a href="${x.url}" target="_blank" rel="noopener">${x.domain||"fonte oficial"} ↗</a>`).join(" · ");
    box.innerHTML = lang==="en"
      ? `<strong>Official source changed${changedAt?` on ${changedAt.slice(0,10)}`:""}.</strong> Potentially outdated guidance on this page has been automatically withdrawn while the change is validated. Use the official source meanwhile. ${links}`
      : `<strong>A fonte oficial foi alterada${changedAt?` em ${changedAt.slice(0,10)}`:""}.</strong> A orientação potencialmente desatualizada desta página foi retirada automaticamente enquanto a alteração é validada. Consulte entretanto a fonte oficial. ${links}`;

    const first=main.querySelector(":scope > section");
    if(first) first.insertAdjacentElement("afterend",box); else main.prepend(box);
    if((metaPolicy?.content||"warn")==="quarantine") document.body.classList.add("source-quarantine");
  }catch(e){ /* never hide content because the status file itself failed to load */ }
}

applyFacts();
applySourceGuard();
})();
