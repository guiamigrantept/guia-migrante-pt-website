const ADMIN_KEY_HASH='33c4e0fac8895bcff60ce878c938ee09171d669f6078be99f5a8be58517178e0';

function json(data,status=200){return new Response(JSON.stringify(data),{status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff','X-Robots-Tag':'noindex, nofollow'}})}
async function sha256(value){const bytes=new TextEncoder().encode(value);const digest=await crypto.subtle.digest('SHA-256',bytes);return [...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('')}
async function authorized(request){const h=request.headers.get('authorization')||'';if(!h.startsWith('Bearer '))return false;const token=h.slice(7).trim();if(token.length<32)return false;const got=await sha256(token);let diff=0;for(let i=0;i<ADMIN_KEY_HASH.length;i++)diff|=got.charCodeAt(i)^ADMIN_KEY_HASH.charCodeAt(i);return diff===0}

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
}

export async function onRequestGet({request,env}){
  if(!(await authorized(request))) return json({ok:false,code:'unauthorized'},401);
  if(!env.CONTACT_DB) return json({ok:false,code:'storage_unavailable'},503);
  try{
    await ensureSchema(env.CONTACT_DB);
    await env.CONTACT_DB.prepare("DELETE FROM analytics_events WHERE created_at < datetime('now','-90 days')").run();
    const url=new URL(request.url);
    const days=Math.min(Math.max(Number(url.searchParams.get('days')||30),1),90);
    const modifier=`-${days} days`;
    const totals=await env.CONTACT_DB.prepare("SELECT COUNT(*) AS total, SUM(CASE WHEN event_type='page_view' THEN 1 ELSE 0 END) AS page_views, SUM(CASE WHEN event_type='contact_submit' THEN 1 ELSE 0 END) AS contact_submits, SUM(CASE WHEN event_type='official_link_click' THEN 1 ELSE 0 END) AS official_clicks FROM analytics_events WHERE created_at >= datetime('now',?)").bind(modifier).first();
    const pages=await env.CONTACT_DB.prepare("SELECT path, COUNT(*) AS n FROM analytics_events WHERE event_type='page_view' AND created_at >= datetime('now',?) GROUP BY path ORDER BY n DESC LIMIT 20").bind(modifier).all();
    const locales=await env.CONTACT_DB.prepare("SELECT locale, COUNT(*) AS n FROM analytics_events WHERE event_type='page_view' AND created_at >= datetime('now',?) GROUP BY locale ORDER BY n DESC").bind(modifier).all();
    const campaigns=await env.CONTACT_DB.prepare("SELECT COALESCE(NULLIF(utm_source,''),'(sem UTM)') AS source, COALESCE(NULLIF(utm_medium,''),'') AS medium, COALESCE(NULLIF(utm_campaign,''),'') AS campaign, COUNT(*) AS n FROM analytics_events WHERE event_type='page_view' AND created_at >= datetime('now',?) GROUP BY source,medium,campaign ORDER BY n DESC LIMIT 20").bind(modifier).all();
    const referrers=await env.CONTACT_DB.prepare("SELECT COALESCE(NULLIF(referrer_host,''),'(direto/indisponível)') AS host, COUNT(*) AS n FROM analytics_events WHERE event_type='page_view' AND created_at >= datetime('now',?) GROUP BY host ORDER BY n DESC LIMIT 20").bind(modifier).all();
    const daily=await env.CONTACT_DB.prepare("SELECT substr(created_at,1,10) AS day, SUM(CASE WHEN event_type='page_view' THEN 1 ELSE 0 END) AS page_views, SUM(CASE WHEN event_type='contact_submit' THEN 1 ELSE 0 END) AS contact_submits, SUM(CASE WHEN event_type='official_link_click' THEN 1 ELSE 0 END) AS official_clicks FROM analytics_events WHERE created_at >= datetime('now',?) GROUP BY day ORDER BY day ASC").bind(modifier).all();
    return json({ok:true,days,totals:totals||{},pages:pages.results||[],locales:locales.results||[],campaigns:campaigns.results||[],referrers:referrers.results||[],daily:daily.results||[]});
  }catch(error){console.error('admin analytics read failed',error);return json({ok:false,code:'storage_unavailable'},503)}
}
