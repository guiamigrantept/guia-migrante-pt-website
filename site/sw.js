
const CACHE = "guia-migrante-v13-auto-source-1";
const CORE = ["./", "./index.html", "./percursos.html", "./legalizacao.html", "./dia-a-dia.html", "./nacionalidade.html", "./ferramentas.html", "./contactos.html", "./faq.html", "./seguranca.html", "./atualizacoes.html", "./ux.css", "./brand.css", "./verify.css", "./v7.css", "./qa-v8.css", "./routes-v9.css", "./ux.js", "./ux-en.js", "./manifest.webmanifest", "./manifest-en.webmanifest", "./logo-guia-migrante-256.png", "./favicon.png", "./fora-de-portugal.html", "./ue-familiares.html", "./pais-terceiro.html", "./cplp.html", "./trabalho.html", "./independente-empreendedor.html", "./nomada-digital.html", "./altamente-qualificado.html", "./estudantes.html", "./rendimentos-proprios.html", "./familia.html", "./investimento.html", "./asilo.html", "./protecao-temporaria.html", "./longa-duracao.html", "./situacoes-especiais.html", "./integracao.html", "./en/index.html", "./en/percursos.html", "./en/legalizacao.html", "./en/dia-a-dia.html", "./en/nacionalidade.html", "./en/ferramentas.html", "./en/contactos.html", "./en/fora-de-portugal.html", "./en/ue-familiares.html", "./en/pais-terceiro.html", "./en/cplp.html", "./en/trabalho.html", "./en/independente-empreendedor.html", "./en/nomada-digital.html", "./en/altamente-qualificado.html", "./en/estudantes.html", "./en/rendimentos-proprios.html", "./en/familia.html", "./en/investimento.html", "./en/asilo.html", "./en/protecao-temporaria.html", "./en/longa-duracao.html", "./en/situacoes-especiais.html", "./en/integracao.html", "./viver-em-portugal.html", "./life-v10.css", "./trabalho-direitos.html", "./habitacao.html", "./escola-familias.html", "./carta-conducao.html", "./qualificacoes.html", "./impostos.html", "./apoios-sociais.html", "./portugues.html", "./discriminacao-apoio.html", "./en/viver-em-portugal.html", "./en/trabalho-direitos.html", "./en/habitacao.html", "./en/escola-familias.html", "./en/carta-conducao.html", "./en/qualificacoes.html", "./en/impostos.html", "./en/apoios-sociais.html", "./en/portugues.html", "./en/discriminacao-apoio.html", "./practical-v11.css", "./banco-pagamentos.html", "./servicos-casa.html", "./consumidor.html", "./saude-completa.html", "./registos-civis.html", "./mudanca-saida.html", "./situacoes-urgentes.html", "./en/banco-pagamentos.html", "./en/servicos-casa.html", "./en/consumidor.html", "./en/saude-completa.html", "./en/registos-civis.html", "./en/mudanca-saida.html", "./en/situacoes-urgentes.html", "./ops-v12.css", "./ops-v12.js", "./acessibilidade.html", "./estado-informacao.html", "./content-status.json", "./en/acessibilidade.html", "./en/estado-informacao.html", "./source-guard.css", "./source-guard.js", "./data/facts.json", "./data/source-status.json"];
self.addEventListener("install",event=>{
  event.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)));
  self.skipWaiting();
});
self.addEventListener("activate",event=>{
  event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch",event=>{
  if(event.request.method!=="GET") return;
  const url=new URL(event.request.url);
  if(url.origin!==location.origin) return;
  event.respondWith(
    fetch(event.request).then(resp=>{
      const clone=resp.clone();
      caches.open(CACHE).then(c=>c.put(event.request,clone));
      return resp;
    }).catch(()=>caches.match(event.request).then(r=>r||caches.match("./404.html")))
  );
});
