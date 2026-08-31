(() => {
  "use strict";
  if (location.pathname.startsWith('/admin-') || location.pathname.startsWith('/api/')) return;

  const raw=(document.documentElement.lang||'pt-PT').toLowerCase();
  const code=['en','fr','es','uk','ru','hi','bn'].find(x=>raw===x||raw.startsWith(x+'-'))||'pt';
  const locale={pt:'pt-PT',en:'en-GB',fr:'fr-FR',es:'es-ES',uk:'uk-UA',ru:'ru-RU',hi:'hi-IN',bn:'bn-BD'}[code]||'pt-PT';
  const copy={
    pt:{stale:'A verificação automática das fontes oficiais está temporariamente atrasada. Confirme a fonte oficial indicada antes de agir.',critical:'O sistema detetou um problema na verificação automática de fontes oficiais. A orientação sensível deve ser confirmada diretamente na fonte oficial.',top:d=>`Informação independente · Fontes oficiais monitorizadas automaticamente · Última verificação: ${d}`,badge:d=>`Fontes oficiais verificadas automaticamente em ${d}`},
    en:{stale:'Automatic verification of official sources is temporarily delayed. Check the linked official source before acting.',critical:'The system detected a problem while verifying official sources. Sensitive guidance should be checked directly against the official source.',top:d=>`Independent information · Official sources monitored automatically · Last check: ${d}`,badge:d=>`Official sources automatically checked on ${d}`},
    fr:{stale:'La vérification automatique des sources officielles est temporairement retardée. Vérifiez la source officielle indiquée avant d’agir.',critical:'Le système a détecté un problème lors de la vérification des sources officielles. Vérifiez directement les informations sensibles auprès de la source officielle.',top:d=>`Information indépendante · Sources officielles surveillées automatiquement · Dernière vérification : ${d}`,badge:d=>`Sources officielles vérifiées automatiquement le ${d}`},
    es:{stale:'La verificación automática de las fuentes oficiales está temporalmente retrasada. Consulte la fuente oficial indicada antes de actuar.',critical:'El sistema detectó un problema al verificar las fuentes oficiales. Confirme directamente la información sensible en la fuente oficial.',top:d=>`Información independiente · Fuentes oficiales supervisadas automáticamente · Última verificación: ${d}`,badge:d=>`Fuentes oficiales verificadas automáticamente el ${d}`},
    uk:{stale:'Автоматична перевірка офіційних джерел тимчасово затримується. Перед діями перевірте вказане офіційне джерело.',critical:'Система виявила проблему під час перевірки офіційних джерел. Чутливу інформацію слід підтвердити безпосередньо в офіційному джерелі.',top:d=>`Незалежна інформація · Офіційні джерела перевіряються автоматично · Остання перевірка: ${d}`,badge:d=>`Офіційні джерела автоматично перевірено ${d}`},
    ru:{stale:'Автоматическая проверка официальных источников временно задерживается. Перед действиями проверьте указанный официальный источник.',critical:'Система обнаружила проблему при проверке официальных источников. Важную информацию следует подтвердить непосредственно в официальном источнике.',top:d=>`Независимая информация · Официальные источники проверяются автоматически · Последняя проверка: ${d}`,badge:d=>`Официальные источники автоматически проверены ${d}`},
    hi:{stale:'आधिकारिक स्रोतों की स्वचालित जाँच अस्थायी रूप से विलंबित है। कोई कदम उठाने से पहले दिए गए आधिकारिक स्रोत की पुष्टि करें।',critical:'आधिकारिक स्रोतों की जाँच में समस्या मिली है। संवेदनशील जानकारी को सीधे आधिकारिक स्रोत से सत्यापित करें।',top:d=>`स्वतंत्र जानकारी · आधिकारिक स्रोतों की स्वचालित निगरानी · अंतिम जाँच: ${d}`,badge:d=>`आधिकारिक स्रोतों की स्वचालित जाँच ${d} को हुई`},
    bn:{stale:'সরকারি উৎসের স্বয়ংক্রিয় যাচাই সাময়িকভাবে বিলম্বিত হচ্ছে। কোনো পদক্ষেপ নেওয়ার আগে উল্লেখিত সরকারি উৎস যাচাই করুন।',critical:'সরকারি উৎস যাচাই করার সময় সিস্টেম একটি সমস্যা শনাক্ত করেছে। সংবেদনশীল তথ্য সরাসরি সরকারি উৎসে নিশ্চিত করুন।',top:d=>`স্বাধীন তথ্য · সরকারি উৎস স্বয়ংক্রিয়ভাবে পর্যবেক্ষিত · সর্বশেষ যাচাই: ${d}`,badge:d=>`সরকারি উৎস স্বয়ংক্রিয়ভাবে যাচাই করা হয়েছে ${d}`}
  }[code];

  function clearWarning(){ document.querySelectorAll('.gmp-monitor-health-warning').forEach(el=>el.remove()); }
  function show(message){
    const main=document.querySelector('main');
    if(!main || document.querySelector('.gmp-monitor-health-warning')) return;
    const box=document.createElement('div');
    box.className='review-status stale review-runtime gmp-monitor-health-warning';
    box.setAttribute('role','status');
    box.textContent=message;
    main.insertBefore(box,main.firstChild);
  }
  function displayDate(iso){
    const d=new Date(iso);
    if(!Number.isFinite(d.getTime())) return '';
    return new Intl.DateTimeFormat(locale,{day:'2-digit',month:'2-digit',year:'numeric',timeZone:'Europe/Lisbon'}).format(d);
  }
  function updateVerificationLabels(h){
    const d=displayDate(h.generated_at||'');
    if(!d) return;
    const top=document.querySelector('.topbar .topbar-inner span:last-child');
    if(top) top.textContent=copy.top(d);
    document.querySelectorAll('.verified-badge').forEach(el=>{ el.textContent=copy.badge(d); });
  }
  async function loadHealth(attempt=0){
    const url='/data/monitor-health.json?health='+Date.now()+'-'+attempt;
    try{
      const r=await fetch(url,{cache:'no-store',headers:{Accept:'application/json','Cache-Control':'no-cache'}});
      if(!r.ok) throw new Error(String(r.status));
      return await r.json();
    }catch(err){
      if(attempt<1){ await new Promise(resolve=>setTimeout(resolve,900)); return loadHealth(attempt+1); }
      throw err;
    }
  }

  loadHealth()
    .then(h=>{
      updateVerificationLabels(h);
      const t=Date.parse(h.generated_at||'');
      const age=Number.isFinite(t)?Math.max(0,(Date.now()-t)/3600000):Infinity;
      const warnAfter=Number(h.warning_after_hours||6);
      if(h.state==='critical') show(copy.critical);
      else if(age>warnAfter) show(copy.stale);
      else clearWarning();
    })
    .catch(()=>{
      // A transient client/CDN read failure must not falsely claim that monitoring is stale.
      // The next page load retries; genuine stale/critical states are driven by the health payload itself.
      clearWarning();
    });
})();
