const TOPICS=new Set(['site_error','suggestion','technical','partnership','other']);
const LOCALES=new Set(['pt','en','fr','es','uk','ru','hi','bn']);

function json(data,status=200){return new Response(JSON.stringify(data),{status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}})}
function clean(value,max){return String(value??'').replace(/\u0000/g,'').trim().slice(0,max)}
function validEmail(value){return !value||/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)}
async function sha256(value){const bytes=new TextEncoder().encode(value);const digest=await crypto.subtle.digest('SHA-256',bytes);return [...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('')}

async function ensureSchema(db){
  await db.prepare(`CREATE TABLE IF NOT EXISTS contact_messages (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    locale TEXT NOT NULL,
    name TEXT,
    email TEXT,
    topic TEXT NOT NULL,
    message TEXT NOT NULL,
    source_path TEXT,
    status TEXT NOT NULL DEFAULT 'new',
    fingerprint TEXT NOT NULL
  )`).run();
  await db.prepare('CREATE INDEX IF NOT EXISTS idx_contact_created ON contact_messages(created_at DESC)').run();
  await db.prepare('CREATE INDEX IF NOT EXISTS idx_contact_status ON contact_messages(status, created_at DESC)').run();
  await db.prepare('CREATE INDEX IF NOT EXISTS idx_contact_fingerprint ON contact_messages(fingerprint, created_at DESC)').run();
}

export async function onRequestPost(context){
  const {request,env}=context;
  if(!env.CONTACT_DB) return json({ok:false,code:'storage_unavailable'},503);
  const type=request.headers.get('content-type')||'';
  if(!type.toLowerCase().includes('application/json')) return json({ok:false,code:'invalid'},415);
  const length=Number(request.headers.get('content-length')||0);
  if(length>12000) return json({ok:false,code:'too_large'},413);

  let body;
  try{body=await request.json()}catch{return json({ok:false,code:'invalid'},400)}

  if(clean(body.website,200)) return json({ok:true});
  const startedAt=Number(body.startedAt||0);
  if(!Number.isFinite(startedAt)||Date.now()-startedAt<2500) return json({ok:false,code:'too_fast'},429);
  if(body.consent!==true) return json({ok:false,code:'invalid'},422);

  const name=clean(body.name,100);
  const email=clean(body.email,180).toLowerCase();
  const topic=clean(body.topic,40);
  const message=clean(body.message,4000);
  const locale=LOCALES.has(clean(body.locale,10))?clean(body.locale,10):'pt';
  const sourcePath=clean(body.page,250);
  if(!TOPICS.has(topic)||message.length<10||!validEmail(email)) return json({ok:false,code:'invalid'},422);

  try{
    await ensureSchema(env.CONTACT_DB);
    await env.CONTACT_DB.prepare("DELETE FROM contact_messages WHERE created_at < datetime('now','-180 days')").run();

    const fingerprint=await sha256(`${email}\n${topic}\n${message.replace(/\s+/g,' ').toLowerCase()}`);
    const duplicate=await env.CONTACT_DB.prepare("SELECT id FROM contact_messages WHERE fingerprint=? AND created_at >= datetime('now','-10 minutes') LIMIT 1").bind(fingerprint).first();
    if(duplicate) return json({ok:false,code:'duplicate'},429);

    if(email){
      const recent=await env.CONTACT_DB.prepare("SELECT COUNT(*) AS n FROM contact_messages WHERE email=? AND created_at >= datetime('now','-1 hour')").bind(email).first();
      if(Number(recent?.n||0)>=5) return json({ok:false,code:'rate_limit'},429);
    }

    const id=crypto.randomUUID();
    await env.CONTACT_DB.prepare('INSERT INTO contact_messages (id,locale,name,email,topic,message,source_path,status,fingerprint) VALUES (?,?,?,?,?,?,?,?,?)')
      .bind(id,locale,name||null,email||null,topic,message,sourcePath||null,'new',fingerprint).run();
    return json({ok:true,id},201);
  }catch(error){
    console.error('contact message storage failed',error);
    return json({ok:false,code:'storage_unavailable'},503);
  }
}

export function onRequestGet(){return json({ok:true,service:'Guia Migrante PT contact channel'},200)}
