
(() => {
"use strict";
const items=[
 {c:"NIF",t:"NIF — Tax Identification Number",d:"Who can request it, cost and official source.",u:"dia-a-dia.html#nif",k:"tax fiscal number"},
 {c:"NSS",t:"NISS — Social Security",d:"Online request and Social Security information.",u:"dia-a-dia.html#niss",k:"niss work employment social security"},
 {c:"SNS",t:"NHS/SNS user number",d:"Public-health user number and health-centre guidance.",u:"dia-a-dia.html#sns",k:"health healthcare user"},
 {c:"AR",t:"Residence permits / AIMA",d:"First grants, work, study, family and transitional routes.",u:"legalizacao.html",k:"residence aima permit legalisation"},
 {c:"REN",t:"Residence renewal",d:"Current Renewal Portal window and guidance.",u:"legalizacao.html#renewals",k:"renew renewal expired permit"},
 {c:"NAT",t:"Portuguese nationality",d:"Residence, descent, marriage and 2026 law change.",u:"nacionalidade.html",k:"nationality citizenship portuguese"},
 {c:"AIM",t:"AIMA contacts",d:"Phone, e-mail, Contact Form and selected shops.",u:"contactos.html#aima",k:"aima phone appointment contact"},
 {c:"CLM",t:"CLAIM support network",d:"Free local information, integration and referral.",u:"contactos.html#claim",k:"claim support integration"},
 {c:"TOO",t:"Free tools",d:"Route builder, checklist, expiry counter and glossary.",u:"ferramentas.html",k:"tools checklist route"},
 {c:"FAQ",t:"Frequently asked questions",d:"Plain answers to common migration questions.",u:"faq.html",k:"questions help"},
 {c:"SAFE",t:"Avoid scams",d:"Warning signs before paying or sharing documents.",u:"seguranca.html",k:"scam fraud safety"},
 {c:"NEW",t:"What changed?",d:"Verified 2026 updates.",u:"atualizacoes.html",k:"updates changes latest"},
 {c:"RTE",t:"All migration routes",d:"EU, CPLP, work, study, family, asylum, digital nomads, long-term and special situations.",u:"percursos.html",k:"routes profiles migrants"},
 {c:"LIFE",t:"Living in Portugal",d:"Work, housing, school, driving, qualifications, taxes, benefits, Portuguese and rights.",u:"viver-em-portugal.html",k:"living portugal work housing school driving qualifications taxes benefits language rights"},
 {c:"BANK",t:"Banking and payments",d:"Accounts, basic banking services and fees.",u:"banco-pagamentos.html",k:"bank account iban"},
 {c:"HOME",t:"Home services",d:"Electricity, water, gas, internet and telecoms.",u:"servicos-casa.html",k:"energy water gas internet"},
 {c:"REC",t:"Consumer rights",d:"Complaints Book, evidence and regulators.",u:"consumidor.html",k:"consumer complaint"},
 {c:"SNS+",t:"Complete healthcare guide",d:"Health centre, SNS 24, rights and care.",u:"saude-completa.html",k:"health sns doctor emergency"},
 {c:"CIV",t:"Civil registration",d:"Birth, marriage and registry events.",u:"registos-civis.html",k:"birth marriage registry"},
 {c:"ADDR",t:"Moving / leaving Portugal",d:"Tax, Social Security, AIMA and contracts.",u:"mudanca-saida.html",k:"address move leave"},
 {c:"SOS",t:"Urgent situations",d:"Danger, violence, exploitation and lost documents.",u:"situacoes-urgentes.html",k:"urgent violence exploitation"},
 {c:"A11Y",t:"Accessibility",d:"Keyboard, visible focus, contrast, larger text and reduced motion.",u:"acessibilidade.html",k:"accessibility keyboard contrast focus screen reader"},
 {c:"STAT",t:"Information status",d:"Verification dates and scheduled editorial reviews.",u:"estado-informacao.html",k:"status review updated verified"},
 {c:"EU",t:"EU/EEA/Swiss & family",d:"Free movement, municipal registration and family residence cards.",u:"ue-familiares.html",k:"eu eea swiss family"},
 {c:"CPLP",t:"CPLP route",d:"First grant, renewal and replacement.",u:"cplp.html",k:"cplp"},
 {c:"ASY",t:"Asylum / international protection",d:"International-protection request through AIMA/CNAR.",u:"asilo.html",k:"asylum refugee protection"},
 {c:"REM",t:"Digital nomad / remote work",d:"Remote work for outside Portugal.",u:"nomada-digital.html",k:"remote digital nomad"},
 {c:"5Y",t:"Long-term resident",d:"Specific long-term status after prolonged legal residence when conditions are met.",u:"longa-duracao.html",k:"long term five years permanent"}
];
const norm=s=>(s||"").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"").trim();
function svg(n){const p={home:'<path d="M3 10.8 12 3l9 7.8v9.2a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1v-9.2Z"/>',search:'<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',tools:'<path d="M14.7 6.3a4 4 0 0 0-5 5L3 18l3 3 6.7-6.7a4 4 0 0 0 5-5l-2.4 2.4-3-3 2.4-2.4Z"/>',help:'<circle cx="12" cy="12" r="9"/><path d="M9.7 9a2.5 2.5 0 1 1 4.3 1.7c-.9.8-2 1.2-2 2.8M12 17h.01"/>'};return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">${p[n]||""}</svg>`}
function build(){
 if(document.querySelector(".ux-bottom-nav"))return;
 const cur=location.pathname.split("/").pop()||"index.html";
 const nav=document.createElement("nav");nav.className="ux-bottom-nav";nav.innerHTML=`<a href="index.html" class="${cur==="index.html"?"active":""}">${svg("home")}<span>Home</span></a><button type="button" data-search>${svg("search")}<span>Search</span></button><a href="ferramentas.html" class="${cur==="ferramentas.html"?"active":""}">${svg("tools")}<span>Tools</span></a><a href="contactos.html">${svg("help")}<span>Help</span></a>`;document.body.appendChild(nav);nav.querySelector("[data-search]").addEventListener("click",open);
 const h=document.querySelector(".header-actions");if(h&&!h.querySelector(".ux-header-search")){const b=document.createElement("button");b.className="ux-header-search";b.type="button";b.setAttribute("aria-label","Search");b.innerHTML=svg("search");b.onclick=open;h.insertBefore(b,h.firstChild)}
}
function overlay(){
 if(document.getElementById("enSearch"))return;
 const o=document.createElement("div");o.id="enSearch";o.className="ux-overlay";o.innerHTML=`<section class="ux-dialog" role="dialog" aria-modal="true"><div class="ux-dialog-head"><strong>Search Guia Migrante</strong><button class="ux-close" type="button">×</button></div><label class="ux-search-box">${svg("search")}<input type="search" placeholder="NIF, AIMA, renewal, nationality..."></label><div class="ux-search-results"></div></section>`;document.body.appendChild(o);
 const input=o.querySelector("input"),res=o.querySelector(".ux-search-results");function render(){const q=norm(input.value);const m=q?items.filter(x=>norm(x.t+" "+x.d+" "+x.k).includes(q)):items.slice(0,8);res.innerHTML=m.length?m.map(x=>`<a class="ux-result" href="${x.u}"><span class="ux-result-icon">${x.c}</span><span><strong>${x.t}</strong><span>${x.d}</span></span><span class="ux-result-arrow">›</span></a>`).join(""):`<div class="ux-no-results">No direct match. Try “AIMA”, “NISS”, “renewal” or “nationality”.</div>`}input.oninput=render;render();o.querySelector(".ux-close").onclick=close;o.onclick=e=>{if(e.target===o)close()}
}
function open(){overlay();document.getElementById("enSearch").classList.add("open");document.body.classList.add("ux-lock");setTimeout(()=>document.querySelector("#enSearch input").focus(),30)}
function close(){const o=document.getElementById("enSearch");if(o)o.classList.remove("open");document.body.classList.remove("ux-lock")}
document.addEventListener("keydown",e=>{if(e.key==="Escape")close()});
if("serviceWorker" in navigator&&location.protocol==="https:")navigator.serviceWorker.register("../sw.js").catch(()=>{});
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",build);else build();
})();
