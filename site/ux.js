
(() => {
  "use strict";

  const UX = {
    checklistKey: "guiaMigranteChecklistV1",
    settingsKey: "guiaMigranteUxSettingsV3",
    routeKey: "guiaMigranteRouteV3",
    installPrompt: null
  };

  const searchIndex = [
    {code:"NIF", title:"NIF — identificação fiscal", text:"Como pedir, documentos, custo e canais das Finanças.", url:"dia-a-dia.html#nif", keys:"nif finanças fiscal contribuinte banco contratos"},
    {code:"NSS", title:"NISS — Segurança Social", text:"Pedido online, documentos e trabalho.", url:"dia-a-dia.html#niss", keys:"niss segurança social trabalho emprego contribuições"},
    {code:"SNS", title:"SNS e número de utente", text:"Número de utente, centro de saúde e acesso ao SNS.", url:"dia-a-dia.html#sns", keys:"sns saúde utente centro hospital médico"},
    {code:"3×", title:"NIF + NISS + Utente", text:"Serviço conjunto nos Espaços Cidadão aderentes para quem cumpre os critérios.", url:"dia-a-dia.html#servico-unificado", keys:"pedido conjunto unificado espaço cidadão nif niss utente"},
    {code:"AR", title:"Autorização de residência", text:"Vias de residência, concessão e documentos comuns.", url:"legalizacao.html#vias", keys:"aima residência autorização legalização concessão visto"},
    {code:"MI", title:"Manifestação de Interesse", text:"O que foi revogado e como funcionam processos anteriores e regime transitório.", url:"legalizacao.html#manifestacao-interesse", keys:"manifestação interesse artigo 88 89 regime transitório"},
    {code:"REN", title:"Renovação de residência", text:"Portal de Renovações e diferença entre renovação e primeira concessão.", url:"legalizacao.html#renovacoes", keys:"renovar renovação título residência portal"},
    {code:"AIM", title:"Contactar a AIMA", text:"Telefone, formulário, lojas e canais oficiais.", url:"contactos.html#aima", keys:"aima telefone email formulário agendamento"},
    {code:"LOJ", title:"Lojas AIMA", text:"Pesquisar balcões por cidade e região.", url:"contactos.html#lojas", keys:"loja aima lisboa porto faro cacem queluz odivelas"},
    {code:"CLM", title:"Rede CLAIM", text:"Apoio local gratuito, integração e encaminhamento.", url:"contactos.html#claim", keys:"claim apoio local integração migrante"},
    {code:"CON", title:"Consulados e embaixadas", text:"Diretório oficial para documentos do seu país.", url:"contactos.html#consulados", keys:"consulado embaixada passaporte país documentos estrangeiros"},
    {code:"NAC", title:"Nacionalidade por residência", text:"Regras de 2026, residência legal e requisitos.", url:"nacionalidade.html#residencia", keys:"nacionalidade cidadania residência 7 anos 10 anos"},
    {code:"FIL", title:"Filho, neto ou bisneto de português", text:"Vias de nacionalidade por descendência.", url:"nacionalidade.html#situacoes", keys:"filho neto bisneto português descendente nacionalidade"},
    {code:"CAS", title:"Casamento / união com português", text:"Via própria de nacionalidade e condições.", url:"nacionalidade.html#situacoes", keys:"casamento união facto português nacionalidade"},
    {code:"TOO", title:"Ferramentas gratuitas", text:"Roteiro, checklist, validade, documentos e glossário.", url:"ferramentas.html", keys:"ferramentas checklist roteiro validade glossário documentos"},
    {code:"DOC", title:"Checklist de documentos", text:"Crie uma lista base para NIF, NISS, SNS, residência ou nacionalidade.", url:"ferramentas.html#documentos", keys:"documentos checklist imprimir pdf"},
    {code:"EMG", title:"Emergência e linhas úteis", text:"112, SNS 24, emergência social e Segurança Social.", url:"contactos.html#emergencia", keys:"emergência 112 sns 24 144 ajuda urgente"},
    {code:"FAQ", title:"Perguntas frequentes", text:"Respostas rápidas sobre residência, documentos, nacionalidade, contactos e ferramentas.", url:"faq.html", keys:"faq perguntas dúvidas respostas"},
    {code:"SAFE", title:"Evite burlas", text:"Sinais de alerta antes de pagar, enviar documentos ou seguir instruções.", url:"seguranca.html", keys:"burla fraude segurança pagamento vaga falsa"},
    {code:"PRV", title:"Política de Privacidade", text:"O que fica no dispositivo e como funcionam os dados na versão pública do Guia.", url:"privacidade.html", keys:"privacidade dados localstorage cookies"},
    {code:"TER", title:"Termos e Condições", text:"Natureza independente do portal e limites das ferramentas de orientação.", url:"termos.html", keys:"termos condições responsabilidade independente"},
    {code:"NEW", title:"O que mudou?", text:"Atualizações verificadas sobre AIMA, renovações, nacionalidade, NIF, NISS e SNS.", url:"atualizacoes.html", keys:"novidades atualizações mudanças 2026 verificado"},
    {code:"ROT", title:"Todos os percursos", text:"UE, CPLP, trabalho, estudo, família, asilo, nómadas digitais, longa duração e situações especiais.", url:"percursos.html", keys:"percursos perfis tipos imigrantes ue cplp estudante trabalho asilo nomada"},
    {code:"VIDA", title:"Viver em Portugal", text:"Trabalho, casa, escola, carta de condução, diplomas, impostos, apoios, português e direitos.", url:"viver-em-portugal.html", keys:"viver portugal trabalho habitação escola carta condução qualificações impostos apoios português discriminação"},
    {code:"BANK", title:"Banco e pagamentos", text:"Conta bancária, serviços mínimos e comissões.", url:"banco-pagamentos.html", keys:"banco conta iban pagamentos"},
    {code:"CASA", title:"Serviços da casa", text:"Eletricidade, água, gás, internet e telecomunicações.", url:"servicos-casa.html", keys:"energia água gás internet telecom"},
    {code:"REC", title:"Consumidor e reclamações", text:"Livro de Reclamações, provas e reguladores.", url:"consumidor.html", keys:"consumidor reclamação"},
    {code:"SNS+", title:"Saúde completa", text:"Centro de saúde, SNS 24, direitos e cuidados.", url:"saude-completa.html", keys:"saúde sns médico urgência"},
    {code:"IRN", title:"Registos civis", text:"Nascimento, casamento e registos.", url:"registos-civis.html", keys:"nascimento casamento registo"},
    {code:"MOR", title:"Mudar morada / sair de Portugal", text:"Finanças, Segurança Social, AIMA e contratos.", url:"mudanca-saida.html", keys:"morada sair portugal fiscal"},
    {code:"SOS", title:"Situações urgentes", text:"Perigo, violência, exploração e perda de documentos.", url:"situacoes-urgentes.html", keys:"urgente violência exploração emergência"},
    {code:"A11Y", title:"Acessibilidade", text:"Teclado, foco visível, contraste, texto maior e movimento reduzido.", url:"acessibilidade.html", keys:"acessibilidade teclado contraste foco leitor ecrã"},
    {code:"STAT", title:"Estado da informação", text:"Datas de verificação e próximas revisões editoriais.", url:"estado-informacao.html", keys:"estado informação revisão atualizado verificado"},
    {code:"UE", title:"UE/EEE/Suíça e familiares", text:"Livre circulação, certificado municipal, cartões de familiares e residência permanente.", url:"ue-familiares.html", keys:"ue união europeia familiar eea swiss"},
    {code:"CPLP", title:"Percurso CPLP", text:"Concessão, renovação e substituição da autorização CPLP.", url:"cplp.html", keys:"cplp"},
    {code:"ASY", title:"Asilo e proteção internacional", text:"Pedido de proteção internacional perante AIMA/CNAR.", url:"asilo.html", keys:"asilo refugio proteção internacional"},
    {code:"REM", title:"Nómada digital / trabalho remoto", text:"Trabalho remoto para entidade ou cliente fora de Portugal.", url:"nomada-digital.html", keys:"nomada digital remoto remote"},
    {code:"5Y", title:"Residente de longa duração", text:"Estatuto próprio depois de residência legal prolongada quando os requisitos se verificam.", url:"longa-duracao.html", keys:"longa duração cinco anos permanente"}
  ];

  const guideSteps = [
    {
      q:"Onde está neste momento?",
      help:"Isto serve apenas para ordenar os conteúdos.",
      choices:[
        ["portugal","Já estou em Portugal"],
        ["outside","Ainda estou fora de Portugal"]
      ]
    },
    {
      q:"Qual é o seu principal objetivo agora?",
      help:"Escolha o assunto mais urgente.",
      choices:[
        ["start","Organizar os primeiros passos"],
        ["residence","Tratar da residência / AIMA"],
        ["renew","Renovar o meu título"],
        ["work","Trabalhar / Segurança Social"],
        ["health","Saúde / número de utente"],
        ["nationality","Nacionalidade portuguesa"],
        ["family","Família / filhos"],
        ["help","Preciso de apoio presencial"]
      ]
    },
    {
      q:"Já tem alguns documentos essenciais?",
      help:"Selecione a opção que melhor descreve a sua situação.",
      choices:[
        ["none","Ainda não tenho NIF, NISS nem número de utente"],
        ["some","Já tenho pelo menos um deles"],
        ["most","Já tenho os documentos essenciais"]
      ]
    }
  ];

  function normalize(s){
    return (s||"").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"").trim();
  }

  function toast(message){
    let el = document.querySelector(".ux-toast");
    if(!el){
      el = document.createElement("div");
      el.className = "ux-toast";
      el.setAttribute("role","status");
      el.setAttribute("aria-live","polite");
      document.body.appendChild(el);
    }
    el.textContent = message;
    el.classList.add("show");
    clearTimeout(el._timer);
    el._timer = setTimeout(()=>el.classList.remove("show"),2600);
  }

  function icon(name){
    const icons = {
      home:'<path d="M3 10.8 12 3l9 7.8v9.2a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1v-9.2Z"/>',
      search:'<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
      tools:'<path d="M14.7 6.3a4 4 0 0 0-5 5L3 18l3 3 6.7-6.7a4 4 0 0 0 5-5l-2.4 2.4-3-3 2.4-2.4Z"/>',
      help:'<circle cx="12" cy="12" r="9"/><path d="M9.7 9a2.5 2.5 0 1 1 4.3 1.7c-.9.8-2 1.2-2 2.8M12 17h.01"/>',
      share:'<circle cx="18" cy="5" r="2"/><circle cx="6" cy="12" r="2"/><circle cx="18" cy="19" r="2"/><path d="m8 11 8-5M8 13l8 5"/>',
      close:'<path d="m6 6 12 12M18 6 6 18"/>'
    };
    return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name]||""}</svg>`;
  }

  function addHeaderSearch(){
    const actions = document.querySelector(".header-actions");
    if(!actions || actions.querySelector(".ux-header-search")) return;
    const b = document.createElement("button");
    b.className = "ux-header-search";
    b.type = "button";
    b.setAttribute("aria-label","Pesquisar no Guia");
    b.innerHTML = icon("search");
    b.addEventListener("click", openSearch);
    actions.insertBefore(b, actions.firstChild);
  }

  function addBottomNav(){
    if(document.querySelector(".ux-bottom-nav")) return;
    const current = location.pathname.split("/").pop() || "index.html";
    const nav = document.createElement("nav");
    nav.className = "ux-bottom-nav";
    nav.setAttribute("aria-label","Navegação rápida");
    nav.innerHTML = `
      <a href="index.html" class="${current==="index.html"||current===""?"active":""}">${icon("home")}<span>Início</span></a>
      <button type="button" data-ux-search>${icon("search")}<span>Pesquisar</span></button>
      <a href="ferramentas.html" class="${current==="ferramentas.html"?"active":""}">${icon("tools")}<span>Ferramentas</span></a>
      <a href="contactos.html">${icon("help")}<span>Ajuda</span></a>`;
    document.body.appendChild(nav);
    nav.querySelector("[data-ux-search]").addEventListener("click",openSearch);
  }

  function buildSearch(){
    if(document.getElementById("uxSearchOverlay")) return;
    const overlay = document.createElement("div");
    overlay.id = "uxSearchOverlay";
    overlay.className = "ux-overlay";
    overlay.innerHTML = `
      <section class="ux-dialog" role="dialog" aria-modal="true" aria-labelledby="uxSearchTitle">
        <div class="ux-dialog-head">
          <strong id="uxSearchTitle">Pesquisar no Guia</strong>
          <button class="ux-close" type="button" aria-label="Fechar">×</button>
        </div>
        <label class="ux-search-box">
          ${icon("search")}
          <span class="sr-only">O que procura?</span>
          <input type="search" id="uxGlobalSearch" autocomplete="off" placeholder="Ex.: renovar residência, NIF, nacionalidade...">
        </label>
        <div class="ux-search-hints">
          <button type="button">NIF</button><button type="button">Renovação</button>
          <button type="button">AIMA</button><button type="button">Nacionalidade</button>
          <button type="button">CLAIM</button>
        </div>
        <div class="ux-tools-row">
          <button class="ux-mini-action" type="button" data-ux-font>A+ Aumentar texto</button>
          <button class="ux-mini-action" type="button" data-ux-contrast>◐ Alto contraste</button>
        </div>
        <div class="ux-search-results" id="uxSearchResults"></div>
      </section>`;
    document.body.appendChild(overlay);

    const input = overlay.querySelector("#uxGlobalSearch");
    const results = overlay.querySelector("#uxSearchResults");
    overlay.querySelector(".ux-close").addEventListener("click",closeSearch);
    overlay.addEventListener("click",e=>{if(e.target===overlay) closeSearch();});
    document.addEventListener("keydown",e=>{if(e.key==="Escape" && overlay.classList.contains("open")) closeSearch();});

    function render(q){
      const nq = normalize(q);
      let matches = searchIndex;
      if(nq){
        matches = searchIndex.filter(item =>
          normalize(item.title+" "+item.text+" "+item.keys).includes(nq)
        );
      } else {
        matches = searchIndex.slice(0,7);
      }
      results.innerHTML = matches.length ? matches.slice(0,10).map(item=>`
        <a class="ux-result" href="${item.url}">
          <span class="ux-result-icon">${item.code}</span>
          <span><strong>${item.title}</strong><span>${item.text}</span></span>
          <span class="ux-result-arrow">›</span>
        </a>`).join("") :
        `<div class="ux-no-results">Não encontrámos uma correspondência direta.<br>Experimente “AIMA”, “NISS”, “renovação” ou “nacionalidade”.</div>`;
    }
    input.addEventListener("input",()=>render(input.value));
    overlay.querySelectorAll(".ux-search-hints button").forEach(b=>b.addEventListener("click",()=>{
      input.value=b.textContent;render(input.value);input.focus();
    }));

    overlay.querySelector("[data-ux-font]").addEventListener("click",()=>{
      document.body.classList.toggle("ux-large-text"); saveSettings(); toast(document.body.classList.contains("ux-large-text")?"Texto aumentado.":"Tamanho de texto normal.");
    });
    overlay.querySelector("[data-ux-contrast]").addEventListener("click",()=>{
      document.body.classList.toggle("ux-high-contrast"); saveSettings(); toast(document.body.classList.contains("ux-high-contrast")?"Alto contraste ativado.":"Contraste normal.");
    });
    render("");
  }

  function openSearch(){
    buildSearch();
    const overlay = document.getElementById("uxSearchOverlay");
    overlay.classList.add("open");
    document.body.classList.add("ux-lock");
    setTimeout(()=>overlay.querySelector("#uxGlobalSearch").focus(),50);
  }
  function closeSearch(){
    const overlay = document.getElementById("uxSearchOverlay");
    if(overlay) overlay.classList.remove("open");
    document.body.classList.remove("ux-lock");
  }

  function saveSettings(){
    localStorage.setItem(UX.settingsKey,JSON.stringify({
      large:document.body.classList.contains("ux-large-text"),
      contrast:document.body.classList.contains("ux-high-contrast")
    }));
  }
  function loadSettings(){
    try{
      const s=JSON.parse(localStorage.getItem(UX.settingsKey)||"{}");
      if(s.large) document.body.classList.add("ux-large-text");
      if(s.contrast) document.body.classList.add("ux-high-contrast");
    }catch{}
  }

  function addShare(){
    if(document.querySelector(".ux-share")) return;
    const b=document.createElement("button");
    b.className="ux-share";
    b.type="button";
    b.setAttribute("aria-label","Partilhar esta página");
    b.innerHTML=icon("share");
    b.addEventListener("click", async ()=>{
      const data={title:document.title,text:"Veja esta informação no Guia Migrante PT",url:location.href};
      try{
        if(navigator.share) await navigator.share(data);
        else{
          await navigator.clipboard.writeText(location.href);
          toast("Link copiado.");
        }
      }catch{}
    });
    document.body.appendChild(b);
  }

  function checklistProgress(){
    try{
      const data=JSON.parse(localStorage.getItem(UX.checklistKey)||"{}");
      const keys=["nif","niss","sns","residence","bank","address","school","officials"];
      const done=keys.filter(k=>data[k]).length;
      return {done,total:keys.length,pct:Math.round(done/keys.length*100)};
    }catch{return {done:0,total:8,pct:0}}
  }

  function addHomeProgress(){
    if(!/index\.html$/.test(location.pathname) && location.pathname!=="/") return;
    const heroCopy=document.querySelector(".hero-grid>div");
    if(!heroCopy || document.querySelector(".ux-progress-card")) return;
    const p=checklistProgress();
    if(p.done===0) return;
    const box=document.createElement("div");
    box.className="ux-progress-card show";
    box.innerHTML=`
      <div class="ux-progress-top"><strong>Continuar de onde ficou</strong><a href="ferramentas.html#checklist">Abrir checklist →</a></div>
      <div class="ux-progress-track"><div class="ux-progress-fill" style="width:${p.pct}%"></div></div>
      <div class="ux-progress-copy">${p.done} de ${p.total} passos marcados como concluídos · ${p.pct}%</div>`;
    heroCopy.appendChild(box);
  }

  function addHomeIntents(){
    if(!/index\.html$/.test(location.pathname) && location.pathname!=="/") return;
    if(document.querySelector(".ux-intent-section")) return;
    const hero=document.querySelector(".hero");
    if(!hero) return;
    const sec=document.createElement("section");
    sec.className="ux-intent-section";
    sec.innerHTML=`
      <div class="container">
        <div class="ux-intent-head">
          <span class="ux-kicker">Comece pelo seu problema, não pela entidade</span>
          <h2>O que precisa de resolver agora?</h2>
          <p>Não precisa de saber se deve procurar AIMA, IRN ou Segurança Social. Escolha a situação e nós encaminhamos para o conteúdo certo.</p>
        </div>
        <div class="ux-intent-grid">
          ${[
            ["🧭","Cheguei agora","Quero organizar os primeiros passos","start"],
            ["🪪","Residência","Preciso de tratar da AIMA ou do meu título","residence"],
            ["↻","Renovar","O meu título está a expirar ou expirou","renew"],
            ["💼","Trabalho","NISS, Segurança Social e documentação","work"],
            ["✚","Saúde","Número de utente e centro de saúde","health"],
            ["PT","Nacionalidade","Quero perceber qual via se aplica","nationality"],
            ["?","Não sei","Quero responder a 3 perguntas rápidas","guide"]
          ].map(x=>`
            <button class="ux-intent-card" type="button" data-intent="${x[3]}">
              <span class="ux-intent-icon">${x[0]}</span>
              <span><strong>${x[1]}</strong><span>${x[2]}</span></span>
              <span class="arrow">›</span>
            </button>`).join("")}
        </div>
        <div class="ux-install-card" id="uxInstallCard">
          <div><strong>Adicionar o Guia ao ecrã inicial</strong><span>Abra como uma app e tenha acesso mais rápido às páginas principais.</span></div>
          <button type="button" data-install>Instalar</button>
        </div>
      </div>`;
    hero.insertAdjacentElement("afterend",sec);
    sec.querySelectorAll("[data-intent]").forEach(b=>b.addEventListener("click",()=>{
      const v=b.dataset.intent;
      if(v==="guide"||v==="start") openGuide(v==="start"?"start":null);
      else {
        const links={
          residence:"legalizacao.html",renew:"legalizacao.html#renovacoes",
          work:"dia-a-dia.html#niss",health:"dia-a-dia.html#sns",
          nationality:"nacionalidade.html"
        };
        location.href=links[v];
      }
    }));
  }

  let guideState={step:0,answers:{}};
  function buildGuide(){
    if(document.getElementById("uxGuideOverlay")) return;
    const overlay=document.createElement("div");
    overlay.id="uxGuideOverlay";
    overlay.className="ux-overlay";
    overlay.innerHTML=`
      <section class="ux-dialog" role="dialog" aria-modal="true" aria-labelledby="uxGuideTitle">
        <div class="ux-dialog-head">
          <strong id="uxGuideTitle">Roteiro rápido</strong>
          <button class="ux-close" type="button" aria-label="Fechar">×</button>
        </div>
        <div class="ux-guide-progress"><i></i><i></i><i></i></div>
        <div class="ux-guide-body" id="uxGuideBody"></div>
        <div class="ux-guide-actions">
          <button type="button" data-back>← Voltar</button>
          <button type="button" class="primary" data-next>Continuar →</button>
        </div>
      </section>`;
    document.body.appendChild(overlay);
    overlay.querySelector(".ux-close").addEventListener("click",closeGuide);
    overlay.addEventListener("click",e=>{if(e.target===overlay) closeGuide();});
    overlay.querySelector("[data-back]").addEventListener("click",()=>{
      if(guideState.step>0){guideState.step--;renderGuide();}
      else closeGuide();
    });
    overlay.querySelector("[data-next]").addEventListener("click",()=>{
      if(guideState.step>=guideSteps.length){closeGuide();return;}
      const selected=overlay.querySelector(".ux-guide-choice.selected");
      if(!selected){toast("Escolha uma opção para continuar.");return;}
      guideState.answers[guideState.step]=selected.dataset.value;
      guideState.step++;
      renderGuide();
    });
  }
  function openGuide(prefill){
    buildGuide();
    guideState={step:0,answers:{}};
    if(prefill==="start") guideState.answers.prefill="start";
    const o=document.getElementById("uxGuideOverlay");
    o.classList.add("open");document.body.classList.add("ux-lock");renderGuide();
  }
  function closeGuide(){
    const o=document.getElementById("uxGuideOverlay");
    if(o)o.classList.remove("open");
    document.body.classList.remove("ux-lock");
  }
  function renderGuide(){
    const overlay=document.getElementById("uxGuideOverlay");
    const body=overlay.querySelector("#uxGuideBody");
    const dots=[...overlay.querySelectorAll(".ux-guide-progress i")];
    dots.forEach((d,i)=>d.classList.toggle("done",i<guideState.step+1));
    const back=overlay.querySelector("[data-back]");
    const next=overlay.querySelector("[data-next]");

    if(guideState.step<guideSteps.length){
      const s=guideSteps[guideState.step];
      body.innerHTML=`<h2>${s.q}</h2><p>${s.help}</p><div class="ux-guide-choices">${s.choices.map(c=>`<button class="ux-guide-choice" type="button" data-value="${c[0]}">${c[1]}</button>`).join("")}</div>`;
      body.querySelectorAll(".ux-guide-choice").forEach(b=>b.addEventListener("click",()=>{
        body.querySelectorAll(".ux-guide-choice").forEach(x=>x.classList.remove("selected"));
        b.classList.add("selected");
      }));
      next.textContent="Continuar →";
      back.textContent=guideState.step?"← Voltar":"Cancelar";
    }else{
      const result=guideResult(guideState.answers);
      localStorage.setItem(UX.routeKey,JSON.stringify({answers:guideState.answers,createdAt:Date.now()}));
      body.innerHTML=`<h2>O seu ponto de partida</h2><p>Não é uma decisão jurídica. É uma ordem de conteúdos para saber onde começar.</p><div class="ux-guide-result">${result.map((r,i)=>`<div class="ux-guide-step"><b>${i+1}</b><div><strong>${r[0]}</strong><span>${r[1]} <a href="${r[2]}">Abrir →</a></span></div></div>`).join("")}</div>`;
      next.textContent="Concluir";
      back.textContent="← Rever";
    }
  }
  function guideResult(a){
    const locationState=a[0], need=a[1]||a.prefill||"start", docs=a[2];
    const out=[];
    if(locationState==="outside"){
      out.push(["Confirme primeiro a via de entrada adequada","Vistos e condições de entrada dependem do objetivo e da nacionalidade.","legalizacao.html#vias"]);
    }
    if(docs==="none"){
      out.push(["Organize os identificadores essenciais","Comece por NIF e veja se o serviço conjunto NIF + NISS + Utente se aplica.","dia-a-dia.html"]);
    } else if(docs==="some"){
      out.push(["Complete os documentos essenciais em falta","Use a checklist gratuita para ver o que já tem.","ferramentas.html#checklist"]);
    }
    const needs={
      start:["Siga o roteiro dos primeiros 30 dias","Use uma ordem prática e confirme cada passo nas fontes oficiais.","index.html#roteiro"],
      residence:["Confirme a sua via de residência","Primeira concessão, renovação e regime transitório são procedimentos diferentes.","legalizacao.html"],
      renew:["Veja as regras atuais de renovação","Confirme se o seu título/data estão abrangidos pelo portal atual.","legalizacao.html#renovacoes"],
      work:["Organize NISS e situação profissional","Depois confirme a via de residência correspondente ao seu caso.","dia-a-dia.html#niss"],
      health:["Trate do SNS / número de utente","Veja atribuição do número e inscrição no centro de saúde.","dia-a-dia.html#sns"],
      nationality:["Identifique a sua via de nacionalidade","Residência, casamento e descendência têm requisitos diferentes.","nacionalidade.html"],
      family:["Veja família, residência e serviços do dia a dia","Comece pelos documentos e pelo fundamento familiar aplicável.","legalizacao.html#vias"],
      help:["Procure apoio presencial adequado","CLAIM pode orientar e encaminhar localmente; AIMA trata processos migratórios.","contactos.html"]
    };
    if(needs[need]) out.unshift(needs[need]);
    if(locationState==="portugal") out.push(["Encontre o contacto certo perto de si","Use Lojas AIMA, CLAIM e outros canais apenas quando correspondem ao assunto.","contactos.html"]);
    out.push(["Guarde o seu progresso sem conta","A checklist fica apenas neste dispositivo.","ferramentas.html#checklist"]);
    return out.slice(0,4);
  }

  function registerSW(){
    if("serviceWorker" in navigator && location.protocol==="https:"){
      navigator.serviceWorker.register("sw.js").catch(()=>{});
    }
    window.addEventListener("beforeinstallprompt",e=>{
      e.preventDefault();UX.installPrompt=e;
      const card=document.getElementById("uxInstallCard");
      if(card) card.classList.add("show");
    });
    document.addEventListener("click",async e=>{
      if(!e.target.matches("[data-install]")||!UX.installPrompt)return;
      UX.installPrompt.prompt();
      try{await UX.installPrompt.userChoice}catch{}
      UX.installPrompt=null;
      const card=document.getElementById("uxInstallCard");if(card)card.classList.remove("show");
    });
  }

  function init(){
    loadSettings();
    addHeaderSearch();
    addBottomNav();
    addShare();
    addHomeIntents();
    addHomeProgress();
    buildSearch();
    registerSW();
  }

  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",init);
  else init();
})();
