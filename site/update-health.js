(() => {
  "use strict";
  if (location.pathname.startsWith('/admin-') || location.pathname.startsWith('/api/')) return;

  const raw=(document.documentElement.lang||'pt-PT').toLowerCase();
  const code=['en','fr','es','uk','ru','hi','bn'].find(x=>raw===x||raw.startsWith(x+'-'))||'pt';
  const copy={
    pt:{stale:'A verificação automática das fontes oficiais está temporariamente atrasada. Confirme a fonte oficial indicada antes de agir.',critical:'O sistema detetou um problema na verificação automática de fontes oficiais. A orientação sensível deve ser confirmada diretamente na fonte oficial.'},
    en:{stale:'Automatic verification of official sources is temporarily delayed. Check the linked official source before acting.',critical:'The system detected a problem while verifying official sources. Sensitive guidance should be checked directly against the official source.'},
    fr:{stale:'La vérification automatique des sources officielles est temporairement retardée. Vérifiez la source officielle indiquée avant d’agir.',critical:'Le système a détecté un problème lors de la vérification des sources officielles. Vérifiez directement les informations sensibles auprès de la source officielle.'},
    es:{stale:'La verificación automática de las fuentes oficiales está temporalmente retrasada. Consulte la fuente oficial indicada antes de actuar.',critical:'El sistema detectó un problema al verificar las fuentes oficiales. Confirme directamente la información sensible en la fuente oficial.'},
    uk:{stale:'Автоматична перевірка офіційних джерел тимчасово затримується. Перед діями перевірте вказане офіційне джерело.',critical:'Система виявила проблему під час перевірки офіційних джерел. Чутливу інформацію слід підтвердити безпосередньо в офіційному джерелі.'},
    ru:{stale:'Автоматическая проверка официальных источников временно задерживается. Перед действиями проверьте указанную официальную источник.',critical:'Система обнаружила проблему при проверке официальных источников. Важную информацию следует подтвердить непосредственно в официальном источнике.'},
    hi:{stale:'आधिकारिक स्रोतों की स्वचालित जाँच अस्थायी रूप से विलंबित है। कोई कदम उठाने से पहले दिए गए आधिकारिक स्रोत की पुष्टि करें।',critical:'आधिकारिक स्रोतों की जाँच में समस्या मिली है। संवेदनशील जानकारी को सीधे आधिकारिक स्रोत से सत्यापित करें।'},
    bn:{stale:'সরকারি উৎসের স্বয়ংক্রিয় যাচাই সাময়িকভাবে বিলম্বিত হচ্ছে। কোনো পদক্ষেপ নেওয়ার আগে উল্লেখিত সরকারি উৎস যাচাই করুন।',critical:'সরকারি উৎস যাচাই করার সময় সিস্টেম একটি সমস্যা শনাক্ত করেছে। সংবেদনশীল তথ্য সরাসরি সরকারি উৎসে নিশ্চিত করুন।'}
  }[code];

  function show(message){
    const main=document.querySelector('main');
    if(!main || document.querySelector('.gmp-monitor-health-warning')) return;
    const box=document.createElement('div');
    box.className='review-status stale review-runtime gmp-monitor-health-warning';
    box.setAttribute('role','status');
    box.textContent=message;
    main.insertBefore(box,main.firstChild);
  }

  fetch('/data/monitor-health.json?ts='+Date.now(),{cache:'no-store',headers:{Accept:'application/json'}})
    .then(r=>{if(!r.ok) throw new Error(String(r.status)); return r.json();})
    .then(h=>{
      const t=Date.parse(h.generated_at||'');
      const age=Number.isFinite(t)?(Date.now()-t)/3600000:Infinity;
      const warnAfter=Number(h.warning_after_hours||6);
      if(h.state==='critical') show(copy.critical);
      else if(age>warnAfter) show(copy.stale);
    })
    .catch(()=>show(copy.stale));
})();
