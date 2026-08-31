const EVENTS=new Set(['page_view','engaged_view','contact_submit','official_link_click']);
const LOCALES=new Set(['pt','en','fr','es','uk','ru','hi','bn']);

function json(data,status=200){return new Response(JSON.stringify(data),{status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}})}
function clean(value,max){return String(value??'').replace(/\u0000/g,'').trim().slice(0,max)}

async function ensureSchema(db){
  await db.prepare(`CREATE TABLE IF NOT EXISTS analytics_events (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,
    path TEXT NOT NULL,
    locale TEXT NOT NULL,
    referrer_host TEXT,
    target_host TEXT,
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT
  )`).run();
  await db.prepare('CREATE INDEX IF NOT EXISTS idx_analytics_created ON analytics_events(created_at DESC)').run();
  await db.prepare('CREATE INDEX IF NOT EXISTS idx_analytics_event ON analytics_events(event_type, created_at DESC)').run();
  await db.prepare('CREATE INDEX IF NOT EXISTS idx_analytics_path ON analytics_events(path, created_at DESC)').run();
}

export async function onRequestPost({request,env}){
  if(!env.CONTACT_DB) return json({ok:false,code:'storage_unavailable'},503);
  const type=(request.headers.get('content-type')||'').toLowerCase();
  if(!type.includes('application/json')) return json({ok:false,code:'invalid'},415);
  const length=Number(request.headers.get('content-length')||0);
  if(length>3000) return json({ok:false,code:'too_large'},413);

  const origin=request.headers.get('origin');
  if(origin){
    try{if(new URL(origin).origin!==new URL(request.url).origin)return json({ok:false,code:'forbidden'},403)}catch{return json({ok:false,code:'forbidden'},403)}
  }

  let body;try{body=await request.json()}catch{return json({ok:false,code:'invalid'},400)}
  const eventType=clean(body.event,40);
  const path=clean(body.path,250);
  const localeRaw=clean(body.locale,10);
  const locale=LOCALES.has(localeRaw)?localeRaw:'pt';
  const referrerHost=clean(body.referrerHost,180).toLowerCase();
  const targetHost=clean(body.targetHost,180).toLowerCase();
  const utmSource=clean(body.utmSource,120);
  const utmMedium=clean(body.utmMedium,120);
  const utmCampaign=clean(body.utmCampaign,160);
  if(!EVENTS.has(eventType)||!path||!path.startsWith('/')) return json({ok:false,code:'invalid'},422);

  try{
    await ensureSchema(env.CONTACT_DB);
    await env.CONTACT_DB.prepare("DELETE FROM analytics_events WHERE created_at < datetime('now','-90 days')").run();
    await env.CONTACT_DB.prepare('INSERT INTO analytics_events (id,event_type,path,locale,referrer_host,target_host,utm_source,utm_medium,utm_campaign) VALUES (?,?,?,?,?,?,?,?,?)')
      .bind(crypto.randomUUID(),eventType,path,locale,referrerHost||null,targetHost||null,utmSource||null,utmMedium||null,utmCampaign||null).run();
    return json({ok:true},201);
  }catch(error){
    console.error('analytics storage failed',error);
    return json({ok:false,code:'storage_unavailable'},503);
  }
}

export function onRequestGet(){return json({ok:true,service:'Guia Migrante PT privacy-first analytics'},200)}
