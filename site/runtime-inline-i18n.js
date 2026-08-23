(() => {
  "use strict";

  const raw=(document.documentElement.lang||"").toLowerCase();
  const locale=raw.startsWith("fr")?"fr":raw.startsWith("es")?"es":raw.startsWith("uk")?"uk":raw.startsWith("ru")?"ru":raw.startsWith("hi")?"hi":raw.startsWith("bn")?"bn":"";
  if(!locale) return;

  let exact=new Map();
  let pairs=[];
  let busy=false;

  function preserveOuter(original, translated){
    const leading=(original.match(/^\s*/)||[""])[0];
    const trailing=(original.match(/\s*$/)||[""])[0];
    return leading+translated.trim()+trailing;
  }

  function translate(value){
    if(typeof value!=="string"||!value.trim()) return value;
    const trimmed=value.trim();
    if(exact.has(trimmed)) return preserveOuter(value, exact.get(trimmed));
    let out=value;
    for(const [src,dst] of pairs){
      if(src.length<4||!out.includes(src)) continue;
      out=out.split(src).join(dst);
    }
    return out;
  }

  function skipTextNode(node){
    const p=node.parentElement;
    return !p||p.closest("script,style,noscript,code,pre,textarea");
  }

  function translateTextNode(node){
    if(skipTextNode(node)) return;
    const next=translate(node.nodeValue||"");
    if(next!==node.nodeValue) node.nodeValue=next;
  }

  function translateAttributes(el){
    if(!(el instanceof Element)) return;
    for(const attr of ["aria-label","placeholder","title"]){
      if(!el.hasAttribute(attr)) continue;
      const old=el.getAttribute(attr)||"";
      const next=translate(old);
      if(next!==old) el.setAttribute(attr,next);
    }
    if((el.matches('button,input[type="button"],input[type="submit"]'))&&el.hasAttribute("value")){
      const old=el.getAttribute("value")||"";
      const next=translate(old);
      if(next!==old) el.setAttribute("value",next);
    }
  }

  function translateTree(root){
    if(root.nodeType===Node.TEXT_NODE){translateTextNode(root);return;}
    if(!(root instanceof Element||root instanceof Document||root instanceof DocumentFragment)) return;
    if(root instanceof Element) translateAttributes(root);
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_ELEMENT|NodeFilter.SHOW_TEXT);
    let node;
    while((node=walker.nextNode())){
      if(node.nodeType===Node.TEXT_NODE) translateTextNode(node);
      else translateAttributes(node);
    }
  }

  function patchDialogs(){
    const originalAlert=window.alert.bind(window);
    const originalConfirm=window.confirm.bind(window);
    const originalPrompt=window.prompt.bind(window);
    window.alert=(message)=>originalAlert(translate(String(message)));
    window.confirm=(message)=>originalConfirm(translate(String(message)));
    window.prompt=(message,defaultValue)=>originalPrompt(translate(String(message)),defaultValue);
  }

  async function init(){
    try{
      const response=await fetch(`/data/inline-runtime-${locale}.json`,{cache:"no-store"});
      if(!response.ok) throw new Error(String(response.status));
      const data=await response.json();
      const entries=Object.entries(data.phrases||{}).filter(([src,dst])=>src&&dst&&src!==dst);
      exact=new Map(entries);
      pairs=entries.sort((a,b)=>b[0].length-a[0].length);
    }catch(error){
      console.warn("Guia Migrante inline i18n unavailable",error);
      return;
    }

    patchDialogs();
    busy=true;
    translateTree(document);
    busy=false;

    const observer=new MutationObserver(records=>{
      if(busy) return;
      busy=true;
      try{
        for(const record of records){
          if(record.type==="characterData") translateTextNode(record.target);
          else if(record.type==="attributes") translateAttributes(record.target);
          else for(const node of record.addedNodes) translateTree(node);
        }
      }finally{busy=false;}
    });
    observer.observe(document.documentElement,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:["aria-label","placeholder","title","value"]});
  }

  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",init,{once:true});
  else init();
})();
