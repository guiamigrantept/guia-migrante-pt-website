const ADMIN_KEY_HASH='33c4e0fac8895bcff60ce878c938ee09171d669f6078be99f5a8be58517178e0';
const STATUSES=new Set(['new','read','closed']);

function json(data,status=200){return new Response(JSON.stringify(data),{status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff','X-Robots-Tag':'noindex, nofollow'}})}
async function sha256(value){const bytes=new TextEncoder().encode(value);const digest=await crypto.subtle.digest('SHA-256',bytes);return [...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('')}
async function authorized(request){const h=request.headers.get('authorization')||'';if(!h.startsWith('Bearer '))return false;const token=h.slice(7).trim();if(token.length<32)return false;const got=await sha256(token);let diff=0;for(let i=0;i<ADMIN_KEY_HASH.length;i++)diff|=got.charCodeAt(i)^ADMIN_KEY_HASH.charCodeAt(i);return diff===0}

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
}

export async function onRequestGet({request,env}){
  if(!(await authorized(request))) return json({ok:false,code:'unauthorized'},401);
  if(!env.CONTACT_DB) return json({ok:false,code:'storage_unavailable'},503);
  try{
    await ensureSchema(env.CONTACT_DB);
    const url=new URL(request.url);
    const status=url.searchParams.get('status')||'all';
    const limit=Math.min(Math.max(Number(url.searchParams.get('limit')||50),1),100);
    let result;
    if(status==='all') result=await env.CONTACT_DB.prepare('SELECT id,created_at,locale,name,email,topic,message,source_path,status FROM contact_messages ORDER BY created_at DESC LIMIT ?').bind(limit).all();
    else if(STATUSES.has(status)) result=await env.CONTACT_DB.prepare('SELECT id,created_at,locale,name,email,topic,message,source_path,status FROM contact_messages WHERE status=? ORDER BY created_at DESC LIMIT ?').bind(status,limit).all();
    else return json({ok:false,code:'invalid_status'},400);
    const counts=await env.CONTACT_DB.prepare("SELECT status, COUNT(*) AS n FROM contact_messages GROUP BY status").all();
    return json({ok:true,messages:result.results||[],counts:counts.results||[]});
  }catch(error){console.error('admin messages read failed',error);return json({ok:false,code:'storage_unavailable'},503)}
}

export async function onRequestPatch({request,env}){
  if(!(await authorized(request))) return json({ok:false,code:'unauthorized'},401);
  if(!env.CONTACT_DB) return json({ok:false,code:'storage_unavailable'},503);
  let body;try{body=await request.json()}catch{return json({ok:false,code:'invalid'},400)}
  const id=String(body.id||'').trim();const status=String(body.status||'').trim();
  if(!id||!STATUSES.has(status)) return json({ok:false,code:'invalid'},422);
  try{
    await ensureSchema(env.CONTACT_DB);
    const r=await env.CONTACT_DB.prepare('UPDATE contact_messages SET status=? WHERE id=?').bind(status,id).run();
    return json({ok:true,changed:Number(r.meta?.changes||0)});
  }catch(error){console.error('admin messages update failed',error);return json({ok:false,code:'storage_unavailable'},503)}
}
