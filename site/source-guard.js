(() => {
  "use strict";

  const rawLang=(document.documentElement.lang||"pt-PT").toLowerCase();
  const supported=["pt","en","fr","es","uk","ru","hi","bn"];
  const lang=supported.find(code=>rawLang===code||rawLang.startsWith(code+"-"))||"pt";
  const intlLocale={pt:"pt-PT",en:"en-GB",fr:"fr-FR",es:"es-ES",uk:"uk-UA",ru:"ru-RU",hi:"hi-IN",bn:"bn-BD"}[lang]||"pt-PT";
  const metaPolicy=document.querySelector('meta[name="source-policy"]');
  const pageIds=(document.querySelector('meta[name="official-source-ids"]')?.content||"").split(/\s+/).filter(Boolean);
  const pathname=location.pathname.replace(/^\/+/,"")||"index.html";
  const pageKey=pathname.endsWith("/")?pathname+"index.html":pathname;
  const sourcePage=pageKey.replace(/^(?:en|fr|es|uk|ru|hi|bn)\//,"");

  const copy={
    pt:{changed:"A fonte oficial foi alterada",on:"em",body:"A orientação potencialmente desatualizada desta página foi retirada automaticamente enquanto a alteração é validada. Consulte entretanto a fonte oficial.",source:"fonte oficial"},
    en:{changed:"Official source changed",on:"on",body:"Potentially outdated guidance on this page has been automatically withdrawn while the change is validated. Use the official source meanwhile.",source:"official source"},
    fr:{changed:"La source officielle a changé",on:"le",body:"Les informations potentiellement obsolètes de cette page ont été retirées automatiquement pendant la vérification du changement. Consultez entre-temps la source officielle.",source:"source officielle"},
    es:{changed:"La fuente oficial ha cambiado",on:"el",body:"La orientación potencialmente desactualizada de esta página se ha retirado automáticamente mientras se valida el cambio. Consulte mientras tanto la fuente oficial.",source:"fuente oficial"},
    uk:{changed:"Офіційне джерело змінилося",on:"",body:"Потенційно застарілу інформацію на цій сторінці автоматично вилучено на час перевірки зміни. Тим часом користуйтеся офіційним джерелом.",source:"офіційне джерело"},
    ru:{changed:"Официальный источник изменился",on:"",body:"Потенциально устаревшая информация на этой странице автоматически скрыта на время проверки изменений. Пока используйте официальный источник.",source:"официальный источник"},
    hi:{changed:"आधिकारिक स्रोत बदल गया है",on:"",body:"इस पृष्ठ की संभावित रूप से पुरानी जानकारी को बदलाव की पुष्टि होने तक स्वतः हटा दिया गया है। इस बीच आधिकारिक स्रोत देखें।",source:"आधिकारिक स्रोत"},
    bn:{changed:"সরকারি উৎস পরিবর্তিত হয়েছে",on:"",body:"পরিবর্তন যাচাই হওয়া পর্যন্ত এই পৃষ্ঠার সম্ভাব্য পুরোনো নির্দেশনা স্বয়ংক্রিয়ভাবে সরিয়ে রাখা হয়েছে। এর মধ্যে সরকারি উৎস দেখুন।",source:"সরকারি উৎস"}
  }[lang];

  function fmtFact(f){
    if(f.type==="date"){
      const [y,m,d]=String(f.value).split("-").map(Number);
      return new Intl.DateTimeFormat(intlLocale,{day:"numeric",month:"long",year:"numeric"}).format(new Date(Date.UTC(y,m-1,d)));
    }
    if(f.type==="integer") return String(f.value);
    if(f.type==="currency_eur") return new Intl.NumberFormat(intlLocale,{style:"currency",currency:"EUR",minimumFractionDigits:2}).format(Number(f.value));
    if(f.type==="time_range"){
      const [a,b]=String(f.value).split("-");
      return lang==="pt"?`${a.replace(":","h")}–${b.replace(":","h")}`:`${a}–${b}`;
    }
    return String(f.value);
  }

  function fmtDate(value){
    if(!value) return "";
    const raw=String(value).slice(0,10);
    const [y,m,d]=raw.split("-").map(Number);
    if(!y||!m||!d) return raw;
    return new Intl.DateTimeFormat(intlLocale,{day:"numeric",month:"long",year:"numeric"}).format(new Date(Date.UTC(y,m-1,d)));
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
    }catch(_){ /* static fallback values remain visible */ }
  }

  function blockedIdsFor(state){
    const blockedPages=state.blocked_pages||{};
    const candidates=[pageKey,pathname,sourcePage,`en/${sourcePage}`];
    const ids=[];
    for(const key of candidates){
      const found=blockedPages[key];
      if(Array.isArray(found)) ids.push(...found);
    }
    return [...new Set(ids)];
  }

  async function applySourceGuard(){
    if(!pageIds.length) return;
    try{
      const state=await loadJSON("/data/source-status.json?ts="+Date.now());
      const blocked=blockedIdsFor(state);
      if(!blocked.length) return;

      const sources=state.sources||{};
      const relevant=blocked.map(id=>sources[id]).filter(Boolean);
      const main=document.querySelector("main");
      if(!main) return;

      const box=document.createElement("div");
      box.className="source-change-banner";
      const changedAt=relevant.map(x=>x.changed_at).filter(Boolean).sort().slice(-1)[0]||"";
      const dateText=changedAt?fmtDate(changedAt):"";
      const dateSuffix=dateText?` ${copy.on?copy.on+" ":""}${dateText}`:"";
      const links=relevant.slice(0,3).map(x=>`<a href="${x.url}" target="_blank" rel="noopener">${x.domain||copy.source} ↗</a>`).join(" · ");
      box.innerHTML=`<strong>${copy.changed}${dateSuffix}.</strong> ${copy.body}${links?` ${links}`:""}`;

      const first=main.querySelector(":scope > section");
      if(first) first.insertAdjacentElement("afterend",box); else main.prepend(box);
      if((metaPolicy?.content||"warn")==="quarantine") document.body.classList.add("source-quarantine");
    }catch(_){ /* never hide content because the status file itself failed to load */ }
  }

  applyFacts();
  applySourceGuard();
})();
