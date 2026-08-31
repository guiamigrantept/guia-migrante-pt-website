(() => {
  "use strict";
  const raw=(document.documentElement.lang||'pt-PT').toLowerCase();
  const code=['en','fr','es','uk','ru','hi','bn'].find(x=>raw===x||raw.startsWith(x+'-'))||'pt';
  const locale={pt:'pt-PT',en:'en-GB',fr:'fr-FR',es:'es-ES',uk:'uk-UA',ru:'ru-RU',hi:'hi-IN',bn:'bn-BD'}[code];
  const parts=location.pathname.split('/').filter(Boolean);
  const page=(['en','fr','es','uk','ru','hi','bn'].includes(parts[0])?parts.slice(1):parts).join('/')||'index.html';
  const pageName=page.endsWith('/')?page+'index.html':page;

  const pageFacts={
    'legalizacao.html':['renewal_start','renewal_end','aima_phone','aima_hours'],
    'cplp.html':['aima_phone','aima_hours'],
    'ue-familiares.html':['aima_phone','aima_hours'],
    'familia.html':['aima_phone'],
    'asilo.html':['aima_phone','aima_hours'],
    'protecao-temporaria.html':['temporary_protection_end'],
    'contactos.html':['aima_phone','aima_hours'],
    'nif.html':['combined_id_locations'],
    'niss.html':['combined_id_locations'],
    'sns.html':['combined_id_locations'],
    'banco-pagamentos.html':['basic_banking_max_fee']
  };
  const ids=pageFacts[pageName];
  if(!ids?.length) return;

  const T={
    pt:{title:'Dados oficiais atualizados automaticamente',note:'Estes dados objetivos são sincronizados com fontes oficiais. Alterações jurídicas ou ambíguas não são aplicadas sem validação.',labels:{renewal_start:'Renovações abrangidas desde',renewal_end:'Autorizações expiradas/a expirar até',aima_phone:'Telefone AIMA',aima_hours:'Horário AIMA',temporary_protection_end:'Proteção temporária até',combined_id_locations:'Locais do serviço conjunto NIF/NISS/SNS',basic_banking_max_fee:'Comissão máxima anual — serviços mínimos bancários'}},
    en:{title:'Automatically updated official data',note:'These objective facts are synchronized with official sources. Legal or ambiguous changes are not applied without validation.',labels:{renewal_start:'Renewals covered from',renewal_end:'Permits expired/expiring until',aima_phone:'AIMA phone',aima_hours:'AIMA hours',temporary_protection_end:'Temporary protection until',combined_id_locations:'Combined NIF/NISS/SNS service locations',basic_banking_max_fee:'Maximum annual fee — basic banking services'}},
    fr:{title:'Données officielles mises à jour automatiquement',note:'Ces données objectives sont synchronisées avec des sources officielles. Les changements juridiques ou ambigus ne sont pas appliqués sans validation.',labels:{renewal_start:'Renouvellements couverts depuis',renewal_end:'Titres expirés/expirant jusqu’au',aima_phone:'Téléphone AIMA',aima_hours:'Horaires AIMA',temporary_protection_end:'Protection temporaire jusqu’au',combined_id_locations:'Lieux du service conjoint NIF/NISS/SNS',basic_banking_max_fee:'Commission annuelle maximale — services bancaires de base'}},
    es:{title:'Datos oficiales actualizados automáticamente',note:'Estos datos objetivos se sincronizan con fuentes oficiales. Los cambios jurídicos o ambiguos no se aplican sin validación.',labels:{renewal_start:'Renovaciones cubiertas desde',renewal_end:'Autorizaciones vencidas/a vencer hasta',aima_phone:'Teléfono AIMA',aima_hours:'Horario AIMA',temporary_protection_end:'Protección temporal hasta',combined_id_locations:'Lugares del servicio conjunto NIF/NISS/SNS',basic_banking_max_fee:'Comisión anual máxima — servicios bancarios básicos'}},
    uk:{title:'Офіційні дані, що оновлюються автоматично',note:'Ці об’єктивні дані синхронізуються з офіційними джерелами. Юридичні або неоднозначні зміни не застосовуються без перевірки.',labels:{renewal_start:'Поновлення охоплено з',renewal_end:'Дозволи, що закінчилися/закінчуються до',aima_phone:'Телефон AIMA',aima_hours:'Години AIMA',temporary_protection_end:'Тимчасовий захист до',combined_id_locations:'Пункти спільної послуги NIF/NISS/SNS',basic_banking_max_fee:'Максимальна річна комісія — базові банківські послуги'}},
    ru:{title:'Официальные данные с автоматическим обновлением',note:'Эти объективные данные синхронизируются с официальными источниками. Юридические или неоднозначные изменения не применяются без проверки.',labels:{renewal_start:'Продления охватываются с',renewal_end:'Разрешения, истекшие/истекающие до',aima_phone:'Телефон AIMA',aima_hours:'Часы AIMA',temporary_protection_end:'Временная защита до',combined_id_locations:'Пункты совместной услуги NIF/NISS/SNS',basic_banking_max_fee:'Максимальная годовая комиссия — базовые банковские услуги'}},
    hi:{title:'स्वचालित रूप से अपडेट किए गए आधिकारिक डेटा',note:'ये वस्तुनिष्ठ तथ्य आधिकारिक स्रोतों से सिंक होते हैं। कानूनी या अस्पष्ट बदलाव बिना सत्यापन लागू नहीं किए जाते।',labels:{renewal_start:'नवीनीकरण इस तारीख से',renewal_end:'समाप्त/समाप्त होने वाले परमिट इस तारीख तक',aima_phone:'AIMA फ़ोन',aima_hours:'AIMA समय',temporary_protection_end:'अस्थायी संरक्षण इस तारीख तक',combined_id_locations:'संयुक्त NIF/NISS/SNS सेवा स्थान',basic_banking_max_fee:'अधिकतम वार्षिक शुल्क — बुनियादी बैंकिंग सेवाएँ'}},
    bn:{title:'স্বয়ংক্রিয়ভাবে হালনাগাদ সরকারি তথ্য',note:'এই বস্তুনিষ্ঠ তথ্য সরকারি উৎসের সঙ্গে সমন্বয় করা হয়। আইনি বা অস্পষ্ট পরিবর্তন যাচাই ছাড়া প্রয়োগ করা হয় না।',labels:{renewal_start:'নবায়ন কার্যকর শুরু',renewal_end:'মেয়াদোত্তীর্ণ/মেয়াদ শেষ হবে পর্যন্ত',aima_phone:'AIMA ফোন',aima_hours:'AIMA সময়সূচি',temporary_protection_end:'অস্থায়ী সুরক্ষা পর্যন্ত',combined_id_locations:'যৌথ NIF/NISS/SNS সেবাস্থল',basic_banking_max_fee:'সর্বোচ্চ বার্ষিক ফি — মৌলিক ব্যাংকিং সেবা'}}
  }[code];

  function fmt(f){
    if(!f) return '';
    if(f.type==='date'){
      const [y,m,d]=String(f.value).split('-').map(Number);
      return new Intl.DateTimeFormat(locale,{day:'numeric',month:'long',year:'numeric'}).format(new Date(Date.UTC(y,m-1,d)));
    }
    if(f.type==='currency_eur') return new Intl.NumberFormat(locale,{style:'currency',currency:'EUR',minimumFractionDigits:2}).format(Number(f.value));
    if(f.type==='time_range') return String(f.value).replace('-', '–');
    return String(f.value);
  }

  fetch('/data/facts.json?ts='+Date.now(),{cache:'no-store',headers:{Accept:'application/json'}})
    .then(r=>{if(!r.ok) throw new Error(String(r.status)); return r.json();})
    .then(data=>{
      const rows=ids.map(id=>({id,f:data.facts?.[id]})).filter(x=>x.f);
      if(!rows.length) return;
      const main=document.querySelector('main');
      if(!main || document.querySelector('.gmp-verified-facts')) return;
      const box=document.createElement('section');
      box.className='gmp-verified-facts';
      box.setAttribute('aria-label',T.title);
      box.style.cssText='margin:18px auto;padding:18px;border:1px solid #bbf7d0;border-radius:16px;background:#f0fdf4;box-shadow:0 8px 24px rgba(15,23,42,.05)';
      const items=rows.map(x=>`<div style="display:flex;justify-content:space-between;gap:18px;padding:7px 0;border-top:1px solid rgba(22,101,52,.12)"><span style="color:#475569">${T.labels[x.id]||x.id}</span><strong style="text-align:right;color:#14532d">${fmt(x.f)}</strong></div>`).join('');
      box.innerHTML=`<strong style="display:block;color:#14532d;margin-bottom:8px">✓ ${T.title}</strong>${items}<small style="display:block;margin-top:10px;color:#64748b">${T.note}</small>`;
      const first=main.querySelector(':scope > section');
      if(first) first.insertAdjacentElement('afterend',box); else main.prepend(box);
    })
    .catch(()=>{});
})();
