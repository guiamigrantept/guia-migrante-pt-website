(() => {
  'use strict';

  const path=(location.pathname||'/').replace(/\/+$/,'');
  const current=(path.split('/').filter(Boolean).pop()||'index.html').toLowerCase();
  if(current!=='contactos.html'&&current!=='contactos') return;

  const raw=(document.documentElement.lang||'pt').toLowerCase();
  const locale=raw.startsWith('fr')?'fr':raw.startsWith('es')?'es':raw.startsWith('uk')?'uk':raw.startsWith('ru')?'ru':raw.startsWith('hi')?'hi':raw.startsWith('bn')?'bn':raw.startsWith('en')?'en':'pt';
  const startedAt=Date.now();
  const fallback={
    title:'Contact the Guide',kicker:'Message to the administration',
    lead:'Send a message to the Guia Migrante PT administration without exposing an email address publicly.',
    not_official:'This channel belongs to Guia Migrante PT. It does not replace any public authority.',
    privacy:'Do not send passports, tax numbers, residence cards, case numbers or other sensitive personal data.',
    name:'Name',name_optional:'optional',email:'Reply email',email_optional:'optional',topic:'Subject',message:'Message',
    message_placeholder:'Briefly explain what you want to tell the Guide.',
    consent:'I confirm that I am not sending documents or sensitive personal data.',submit:'Send message',sending:'Sending...',
    success:'Message sent successfully.',error:'The message could not be sent. Please try again later.',
    unavailable:'The message channel is temporarily unavailable.',too_fast:'Please wait a few seconds before sending.',
    duplicate:'This message appears to have been sent recently.',invalid:'Please review the required fields.',
    topics:[{value:'site_error',label:'Error or incorrect information on the site'},{value:'suggestion',label:'Suggestion'},{value:'technical',label:'Technical problem'},{value:'partnership',label:'Partnership or collaboration'},{value:'other',label:'Other'}]
  };

  const esc=value=>String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));

  function ensureStyles(){
    if(document.querySelector('link[href^="/contact-form.css"]')) return;
    const link=document.createElement('link');
    link.rel='stylesheet';
    link.href='/contact-form.css?v=20260824-2';
    document.head.appendChild(link);
  }

  async function getCopy(){
    try{
      const r=await fetch(`/data/contact-copy-${locale}.json?v=20260824-2`,{cache:'no-store'});
      if(!r.ok) throw new Error(String(r.status));
      return await r.json();
    }catch{return fallback;}
  }

  function render(copy){
    if(document.getElementById('fale-com-o-guia')) return;
    const main=document.querySelector('main');
    if(!main) return;
    ensureStyles();

    const section=document.createElement('section');
    section.id='fale-com-o-guia';
    section.className='gmp-contact-channel';
    section.innerHTML=`
      <div class="container gmp-contact-wrap">
        <div class="gmp-contact-intro">
          <span class="gmp-contact-kicker">${esc(copy.kicker)}</span>
          <h2>${esc(copy.title)}</h2>
          <p>${esc(copy.lead)}</p>
          <div class="gmp-contact-notice" role="note"><strong>${esc(copy.not_official)}</strong><span>${esc(copy.privacy)}</span></div>
        </div>
        <form class="gmp-contact-form" id="gmpContactForm" novalidate>
          <div class="gmp-field-grid">
            <label><span>${esc(copy.name)} <small>${esc(copy.name_optional)}</small></span><input name="name" type="text" autocomplete="name" maxlength="100"></label>
            <label><span>${esc(copy.email)} <small>${esc(copy.email_optional)}</small></span><input name="email" type="email" autocomplete="email" maxlength="180"></label>
          </div>
          <label><span>${esc(copy.topic)}</span><select name="topic" required>${(copy.topics||fallback.topics).map(x=>`<option value="${esc(x.value)}">${esc(x.label)}</option>`).join('')}</select></label>
          <label><span>${esc(copy.message)}</span><textarea name="message" required minlength="10" maxlength="4000" rows="7" placeholder="${esc(copy.message_placeholder)}"></textarea></label>
          <label class="gmp-honeypot" aria-hidden="true">Website<input name="website" type="text" tabindex="-1" autocomplete="off"></label>
          <label class="gmp-consent"><input name="consent" type="checkbox" required><span>${esc(copy.consent)}</span></label>
          <div class="gmp-contact-actions"><button type="submit" class="gmp-contact-submit">${esc(copy.submit)}</button><div class="gmp-contact-status" role="status" aria-live="polite"></div></div>
        </form>
      </div>`;
    main.appendChild(section);

    const heroActions=document.querySelector('.hero-actions');
    if(heroActions&&!heroActions.querySelector('[href="#fale-com-o-guia"]')){
      const a=document.createElement('a');
      a.href='#fale-com-o-guia';a.className='btn-secondary';a.textContent=copy.submit;
      heroActions.appendChild(a);
    }

    const form=section.querySelector('#gmpContactForm');
    const submit=form.querySelector('button[type="submit"]');
    const status=form.querySelector('.gmp-contact-status');

    form.addEventListener('submit',async e=>{
      e.preventDefault();
      status.className='gmp-contact-status';
      if(!form.reportValidity()){
        status.textContent=copy.invalid;status.classList.add('error');return;
      }
      submit.disabled=true;submit.textContent=copy.sending;status.textContent='';
      const fd=new FormData(form);
      const payload={
        name:String(fd.get('name')||'').trim(),email:String(fd.get('email')||'').trim(),topic:String(fd.get('topic')||'other'),
        message:String(fd.get('message')||'').trim(),website:String(fd.get('website')||''),consent:fd.get('consent')==='on',
        locale,page:location.pathname,startedAt
      };
      try{
        const r=await fetch('/api/contact',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(payload)});
        const data=await r.json().catch(()=>({}));
        if(r.ok){
          form.reset();status.textContent=copy.success;status.classList.add('success');
        }else if(r.status===429&&data.code==='duplicate'){
          status.textContent=copy.duplicate;status.classList.add('error');
        }else if(r.status===429||data.code==='too_fast'){
          status.textContent=copy.too_fast;status.classList.add('error');
        }else if(r.status===503){
          status.textContent=copy.unavailable;status.classList.add('error');
        }else if(r.status===400||r.status===422){
          status.textContent=copy.invalid;status.classList.add('error');
        }else{
          status.textContent=copy.error;status.classList.add('error');
        }
      }catch{
        status.textContent=copy.error;status.classList.add('error');
      }finally{
        submit.disabled=false;submit.textContent=copy.submit;
      }
    });
  }

  getCopy().then(render);
})();
