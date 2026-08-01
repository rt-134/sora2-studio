# -*- coding: utf-8 -*-
"""
VETREX STUDIO — Sora-2
ملف واحد فقط — التشغيل: python app.py
"""
import os
import uuid
import requests
import logging
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# ─── نفس إعدادات الاتصال الأصلية ───
VETREX_API = "https://vetrex.site/v1"
MODEL = "sora-2"
UPLOAD_DIR = "uploads"
REQUEST_TIMEOUT = 60  # زيادة المهلة إلى 60 ثانية

# تفعيل logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024
os.makedirs(UPLOAD_DIR, exist_ok=True)


def public_url(path):
    scheme = request.headers.get("X-Forwarded-Proto", request.scheme)
    host = request.headers.get("X-Forwarded-Host", request.host)
    return f"{scheme}://{host}{path}"


# ──────────────────────── HTML PAGE ────────────────────────

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VETREX STUDIO — Sora-2</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@700;800;900&family=Readex+Pro:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --ink:#090c11; --panel:#121722; --panel2:#0d1119; --line:#222c3d;
  --text:#e9edf4; --dim:#7f8ba0;
  --amber:#ffb02e; --amber-deep:#ff7a00; --rec:#ff4d4d; --cyan:#4fe3c1; --blue:#62a8ff;
  --mono:'IBM Plex Mono',monospace; --disp:'Cairo',sans-serif; --body:'Readex Pro',sans-serif;
}
body{background:var(--ink);color:var(--text);font-family:var(--body);min-height:100vh;overflow-x:hidden}
::selection{background:rgba(255,176,46,.3)}
::-webkit-scrollbar{width:8px;height:8px}
::-webkit-scrollbar-thumb{background:#232c3d;border-radius:4px}
::-webkit-scrollbar-thumb:hover{background:#31405a}
.glow{position:fixed;border-radius:50%;filter:blur(120px);pointer-events:none;z-index:0}
.glow-warm{width:520px;height:520px;background:rgba(255,140,20,.13);top:-160px;left:-120px;animation:breathe 9s ease-in-out infinite}
.glow-cool{width:620px;height:620px;background:rgba(60,190,170,.10);bottom:-220px;right:-160px;animation:breathe 11s ease-in-out infinite reverse}
@keyframes breathe{50%{transform:scale(1.18);opacity:.75}}
.grid-layer{position:fixed;inset:0;z-index:0;pointer-events:none;background-image:linear-gradient(rgba(120,140,180,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(120,140,180,.05) 1px,transparent 1px);background-size:44px 44px;-webkit-mask-image:radial-gradient(ellipse at 50% 0%,#000 30%,transparent 75%);mask-image:radial-gradient(ellipse at 50% 0%,#000 30%,transparent 75%)}
.grain{position:fixed;inset:-100%;z-index:2;pointer-events:none;opacity:.055;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)'/%3E%3C/svg%3E");animation:grain 7s steps(8) infinite}
@keyframes grain{0%,100%{transform:translate(0,0)}25%{transform:translate(-2%,3%)}50%{transform:translate(3%,-2%)}75%{transform:translate(-3%,-3%)}}
.scanline{position:fixed;left:0;right:0;height:120px;z-index:2;pointer-events:none;background:linear-gradient(180deg,transparent,rgba(140,180,255,.045),transparent);animation:scan 12s linear infinite}
@keyframes scan{from{top:-15%}to{top:110%}}
header{position:relative;z-index:5;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;padding:16px 28px;border-bottom:1px solid var(--line);background:rgba(10,13,18,.75);backdrop-filter:blur(8px)}
.brand{display:flex;align-items:center;gap:14px;color:var(--amber)}
.brand svg{width:38px;height:38px;animation:spin 24s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.brand-txt strong{font-family:var(--disp);font-weight:900;font-size:1.25rem;letter-spacing:.5px;color:var(--text);display:block}
.brand-txt strong span{color:var(--amber)}
.brand-txt small{font-family:var(--mono);font-size:.66rem;color:var(--dim);letter-spacing:2px;text-transform:uppercase}
.head-status{display:flex;align-items:center;gap:14px;font-family:var(--mono);font-size:.74rem}
.led{width:9px;height:9px;border-radius:50%;background:var(--cyan);box-shadow:0 0 10px var(--cyan);animation:pulse 2s infinite}
.led.busy{background:var(--amber);box-shadow:0 0 10px var(--amber)}
@keyframes pulse{50%{opacity:.35}}
.clock{color:var(--dim);letter-spacing:1px;border:1px solid var(--line);padding:5px 10px;border-radius:4px}
.ticker{position:relative;z-index:5;overflow:hidden;border-bottom:1px solid var(--line);direction:ltr;background:linear-gradient(90deg,rgba(255,176,46,.06),transparent 40%,rgba(79,227,193,.05));padding:8px 0}
.ticker-track{display:flex;gap:34px;width:max-content;animation:tick 26s linear infinite;font-family:var(--mono);font-size:.72rem;letter-spacing:2px;color:var(--dim);white-space:nowrap}
.ticker-track i{color:var(--amber);font-style:normal}
@keyframes tick{to{transform:translateX(-50%)}}
main{position:relative;z-index:5;display:grid;grid-template-columns:420px 1fr;gap:22px;padding:26px 28px;max-width:1280px;margin:0 auto}
@media(max-width:960px){main{grid-template-columns:1fr}}
.panel{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:10px;position:relative}
.panel::before{content:"";position:absolute;top:-1px;right:-1px;width:34px;height:34px;border-top:2px solid var(--amber);border-right:2px solid var(--amber);border-radius:0 10px 0 0;opacity:.7;pointer-events:none}
.panel-head{display:flex;justify-content:space-between;align-items:center;padding:15px 20px;border-bottom:1px solid var(--line)}
.panel-head h2{font-family:var(--disp);font-weight:800;font-size:1.05rem}
.tag{font-family:var(--mono);font-size:.62rem;letter-spacing:2px;color:var(--amber);border:1px solid rgba(255,176,46,.35);padding:3px 8px;border-radius:3px;background:rgba(255,176,46,.07)}
.body{padding:20px;display:flex;flex-direction:column;gap:16px}
.tabs{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.tab{font-family:var(--disp);font-weight:700;font-size:.9rem;padding:12px;border:1px solid var(--line);background:transparent;color:var(--dim);border-radius:7px;cursor:pointer;transition:.25s}
.tab:hover{border-color:var(--amber);color:var(--text);transform:translateY(-2px)}
.tab.active{background:linear-gradient(135deg,rgba(255,176,46,.16),rgba(255,122,0,.07));border-color:var(--amber);color:var(--amber);box-shadow:inset 0 0 18px rgba(255,176,46,.12)}
.dropzone{border:1.5px dashed var(--line);border-radius:8px;padding:18px;text-align:center;color:var(--dim);cursor:pointer;transition:.25s;position:relative;font-size:.85rem}
.dropzone:hover,.dropzone.drag{border-color:var(--cyan);background:rgba(79,227,193,.05);color:var(--text)}
.dropzone small{display:block;margin-top:6px;font-family:var(--mono);font-size:.64rem;letter-spacing:1px}
#dzPreview img{max-height:130px;border-radius:6px;border:1px solid var(--line)}
#removeImg{position:absolute;top:8px;right:8px;background:var(--rec);border:0;color:#fff;width:24px;height:24px;border-radius:50%;cursor:pointer;font-size:.7rem;transition:.2s}
#removeImg:hover{transform:scale(1.15)}
.field-label{font-family:var(--disp);font-weight:700;font-size:.85rem}
textarea{width:100%;min-height:120px;resize:vertical;background:var(--panel2);border:1px solid var(--line);border-radius:8px;color:var(--text);font-family:var(--body);font-size:.95rem;padding:14px;line-height:1.8;transition:.25s}
textarea:focus{outline:none;border-color:var(--amber);box-shadow:0 0 0 3px rgba(255,176,46,.12)}
textarea::placeholder{color:#5a6578}
.row-between{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px}
.ratios{display:flex;gap:8px}
.chip{font-family:var(--mono);font-size:.72rem;padding:7px 13px;border:1px solid var(--line);background:transparent;color:var(--dim);border-radius:5px;cursor:pointer;transition:.2s;letter-spacing:1px}
.chip:hover{border-color:var(--blue);color:var(--blue)}
.chip.active{border-color:var(--blue);color:var(--blue);background:rgba(98,168,255,.1)}
.counter{font-family:var(--mono);font-size:.68rem;color:var(--dim)}
.generate{font-family:var(--disp);font-weight:900;font-size:1.05rem;padding:16px;border:0;border-radius:8px;cursor:pointer;color:#1a1206;background:linear-gradient(135deg,var(--amber),var(--amber-deep));display:flex;align-items:center;justify-content:center;gap:10px;transition:.25s;box-shadow:0 6px 24px rgba(255,150,20,.25)}
.generate:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 10px 34px rgba(255,150,20,.4)}
.generate:active:not(:disabled){transform:translateY(0)}
.generate:disabled{cursor:wait;filter:saturate(.6) brightness(.85)}
.rec-dot{width:11px;height:11px;border-radius:50%;background:#7a1010;border:2px solid rgba(0,0,0,.35);transition:.3s}
.generate.working .rec-dot{background:var(--rec);animation:recpulse 1s infinite}
@keyframes recpulse{50%{box-shadow:0 0 0 6px rgba(255,77,77,.25)}}
.stage{position:relative;aspect-ratio:16/9;background:#05070b;border:1px solid var(--line);border-radius:8px;overflow:hidden;display:flex;align-items:center;justify-content:center}
.corner{position:absolute;width:22px;height:22px;border:2px solid var(--amber);opacity:.85;z-index:3;transition:.3s}
.c1{top:10px;right:10px;border-bottom:0;border-left:0}
.c2{top:10px;left:10px;border-bottom:0;border-right:0}
.c3{bottom:10px;right:10px;border-top:0;border-left:0}
.c4{bottom:10px;left:10px;border-top:0;border-right:0}
.stage.working .corner{animation:cornerpulse 1.4s infinite}
@keyframes cornerpulse{50%{opacity:.2}}
.standby{color:var(--dim);text-align:center}
.standby svg{width:64px;height:64px;color:#2c3648;animation:spin 30s linear infinite}
.standby p{margin-top:12px;font-size:.85rem}
#player{width:100%;height:100%;object-fit:contain;background:#000}
.render-overlay{position:absolute;inset:0;z-index:4;background:rgba(5,7,11,.85);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px}
.elapsed{font-family:var(--mono);font-size:2.2rem;font-weight:600;color:var(--amber);letter-spacing:3px;text-shadow:0 0 20px rgba(255,176,46,.4)}
.render-label{color:var(--text);font-size:.9rem;display:flex;align-items:center;gap:8px}
.render-label::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--rec);animation:recpulse 1s infinite}
.shimmer-bar{width:min(320px,70%);height:4px;background:#1a2130;border-radius:2px;overflow:hidden}
.shimmer-bar i{display:block;height:100%;width:40%;border-radius:2px;background:linear-gradient(90deg,var(--amber-deep),var(--amber),var(--amber-deep));animation:shimmer 1.4s ease-in-out infinite}
@keyframes shimmer{from{transform:translateX(260%)}to{transform:translateX(-120%)}}
.console{background:#05070b;border:1px solid var(--line);border-radius:8px;padding:14px 16px;font-family:var(--mono);font-size:.74rem;line-height:2;direction:ltr;text-align:left;max-height:170px;overflow-y:auto}
.console .line{animation:linein .3s ease both}
@keyframes linein{from{opacity:0;transform:translateY(4px)}}
.console .dim{color:#5a6578}
.console .info{color:var(--blue)}
.console .ok{color:var(--cyan)}
.console .warn{color:var(--amber)}
.console .err{color:var(--rec)}
.console .caret::after{content:"▊";color:var(--cyan);animation:blink 1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
.archive{position:relative;z-index:5;max-width:1280px;margin:0 auto;padding:0 28px 30px}
.archive-row{display:flex;gap:14px;overflow-x:auto;padding:16px 4px}
.empty-hint{color:#4d586c;font-size:.8rem;font-family:var(--mono);padding:20px}
.shot{flex:0 0 240px;background:var(--panel2);border:1px solid var(--line);border-radius:8px;overflow:hidden;cursor:pointer;transition:.25s;position:relative}
.shot:hover{transform:translateY(-4px);border-color:var(--amber);box-shadow:0 12px 30px rgba(0,0,0,.5)}
.shot video{width:100%;aspect-ratio:16/9;object-fit:cover;background:#000;display:block}
.shot .meta{padding:10px 12px}
.shot .meta p{font-size:.72rem;color:var(--dim);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.shot .meta small{font-family:var(--mono);font-size:.6rem;color:#4d586c;letter-spacing:1px}
.mode-badge{position:absolute;top:8px;right:8px;z-index:2;font-family:var(--mono);font-size:.58rem;background:rgba(5,7,11,.85);color:var(--amber);padding:3px 7px;border-radius:3px;border:1px solid rgba(255,176,46,.3)}
footer{position:relative;z-index:5;border-top:1px solid var(--line);padding:18px 28px;display:flex;gap:22px;align-items:center;justify-content:center;flex-wrap:wrap;font-family:var(--mono);font-size:.72rem;color:var(--dim)}
footer a{color:var(--amber);text-decoration:none;transition:.2s}
footer a:hover{color:var(--text);text-shadow:0 0 12px rgba(255,176,46,.6)}
</style>
</head>
<body>
<div class="glow glow-warm"></div>
<div class="glow glow-cool"></div>
<div class="grid-layer"></div>
<div class="grain"></div>
<div class="scanline"></div>
<header>
  <div class="brand">
    <svg viewBox="0 0 32 32" fill="none" stroke="currentColor"><circle cx="16" cy="16" r="13" stroke-width="2"/><circle cx="16" cy="16" r="5" stroke-width="2"/><path d="M16 3v6M16 23v6M3 16h6M23 16h6" stroke-width="2"/></svg>
    <div class="brand-txt">
      <strong>VETREX <span>STUDIO</span></strong>
      <small>Sora-2 Video Engine</small>
    </div>
  </div>
  <div class="head-status">
    <span class="led" id="led"></span><span id="ledText">متصل</span>
    <span class="clock" id="clock">00:00:00</span>
  </div>
</header>
<div class="ticker"><div class="ticker-track">
  <span>TEXT → VIDEO</span><i>✦</i><span>IMAGE → MOTION</span><i>✦</i><span>SORA-2 MODEL</span><i>✦</i><span>VETREX AI ENGINE</span><i>✦</i><span>CINEMATIC OUTPUT</span><i>✦</i><span>PROMPT → SCENE</span><i>✦</i>
  <span>TEXT → VIDEO</span><i>✦</i><span>IMAGE → MOTION</span><i>✦</i><span>SORA-2 MODEL</span><i>✦</i><span>VETREX AI ENGINE</span><i>✦</i><span>CINEMATIC OUTPUT</span><i>✦</i><span>PROMPT → SCENE</span><i>✦</i>
</div></div>
<main>
  <section class="panel">
    <div class="panel-head"><h2>كونسول المخرج</h2><span class="tag">INPUT</span></div>
    <div class="body">
      <div class="tabs">
        <button class="tab active" data-mode="create">🎬 إنشاء فيديو</button>
        <button class="tab" data-mode="edit">🖼️ تحريك صورة</button>
      </div>
      <div class="dropzone" id="dropzone" hidden>
        <input type="file" id="fileInput" accept="image/*" hidden>
        <div id="dzEmpty">اسحب صورة هنا أو <b>اضغط للاختيار</b><small>صورة واحدة — JPG / PNG</small></div>
        <div id="dzPreview" hidden><img id="previewImg" alt=""><button id="removeImg" title="إزالة">✕</button></div>
      </div>
      <label class="field-label" id="promptLabel">وصف المشهد</label>
      <textarea id="prompt" placeholder="مثال: لقطة سينمائية لمدينة مضاءة بالنيون تحت المطر، حركة كاميرا بطيئة..."></textarea>
      <div class="row-between">
        <div class="ratios">
          <button class="chip active" data-r="16:9">16:9</button>
          <button class="chip" data-r="9:16">9:16</button>
          <button class="chip" data-r="1:1">1:1</button>
        </div>
        <span class="counter"><span id="count">0</span> حرف</span>
      </div>
      <button class="generate" id="generateBtn"><span class="rec-dot"></span> بدء التوليد</button>
    </div>
  </section>
  <section class="panel">
    <div class="panel-head"><h2>غرفة العرض</h2><span class="tag" id="stageTag">STANDBY</span></div>
    <div class="body">
      <div class="stage" id="stage">
        <span class="corner c1"></span><span class="corner c2"></span><span class="corner c3"></span><span class="corner c4"></span>
        <div class="standby" id="standby">
          <svg viewBox="0 0 32 32" fill="none" stroke="currentColor"><circle cx="16" cy="16" r="13" stroke-width="1.5"/><circle cx="16" cy="16" r="5" stroke-width="1.5"/><path d="M16 3v6M16 23v6M3 16h6M23 16h6" stroke-width="1.5"/></svg>
          <p>بانتظار أول مشهد...</p>
        </div>
        <video id="player" controls hidden></video>
        <div class="render-overlay" id="renderOverlay" hidden>
          <div class="elapsed" id="elapsed">00:00</div>
          <div class="render-label">جاري توليد المشهد...</div>
          <div class="shimmer-bar"><i></i></div>
        </div>
      </div>
      <div class="console" id="console"></div>
    </div>
  </section>
</main>
<section class="archive">
  <div class="panel-head" style="border:1px solid var(--line);border-radius:10px 10px 0 0;background:var(--panel)">
    <h2>أرشيف اللقطات</h2><span class="tag">SESSION</span>
  </div>
  <div class="archive-row" id="archiveRow"></div>
</section>
<footer>
  <a href="https://t.me/VETREX_AI" target="_blank">• القناة •</a>
  <a href="https://t.me/VETREX_3" target="_blank">• المطور •</a>
  <span>Powered by VETREX AI — Sora-2</span>
</footer>
<script>
const $ = id => document.getElementById(id);
let mode='create', ratio='16:9', uploadedUrl=null, busy=false, elapsedTimer=null, history=[];
setInterval(()=>{ $('clock').textContent=new Date().toLocaleTimeString('en-GB'); },1000);
function log(msg, cls='dim'){
  const c=$('console'), t=new Date().toLocaleTimeString('en-GB');
  c.querySelectorAll('.caret').forEach(e=>e.classList.remove('caret'));
  const div=document.createElement('div');
  div.className='line '+cls;
  div.textContent=`[${t}] ${msg}`;
  div.classList.add('caret');
  c.appendChild(div);
  c.scrollTop=c.scrollHeight;
}
document.querySelectorAll('.tab').forEach(t=>t.addEventListener('click',()=>{
  if(busy) return;
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  t.classList.add('active');
  mode=t.dataset.mode;
  $('dropzone').hidden = mode!=='edit';
  $('promptLabel').textContent = mode==='create' ? 'وصف المشهد' : 'وصف الحركة';
  $('prompt').placeholder = mode==='create'
    ? 'مثال: لقطة سينمائية لمدينة مضاءة بالنيون تحت المطر، حركة كاميرا بطيئة...'
    : 'مثال: الشخص في الصورة يدير رأسه ببطء مع رياح خفيفة...';
  log('Mode → '+(mode==='create'?'CREATE VIDEO':'ANIMATE IMAGE'),'info');
}));
document.querySelectorAll('.chip').forEach(ch=>ch.addEventListener('click',()=>{
  document.querySelectorAll('.chip').forEach(x=>x.classList.remove('active'));
  ch.classList.add('active'); ratio=ch.dataset.r;
}));
$('prompt').addEventListener('input',e=>$('count').textContent=e.target.value.length);
const dz=$('dropzone'), fi=$('fileInput');
dz.addEventListener('click',()=>fi.click());
['dragover','dragenter'].forEach(ev=>dz.addEventListener(ev,e=>{e.preventDefault();dz.classList.add('drag');}));
['dragleave','drop'].forEach(ev=>dz.addEventListener(ev,e=>{e.preventDefault();dz.classList.remove('drag');}));
dz.addEventListener('drop',e=>{ if(e.dataTransfer.files.length) uploadImage(e.dataTransfer.files[0]); });
fi.addEventListener('change',()=>{ if(fi.files.length) uploadImage(fi.files[0]); });
$('removeImg').addEventListener('click',e=>{
  e.stopPropagation(); uploadedUrl=null;
  $('dzPreview').hidden=true; $('dzEmpty').hidden=false; fi.value='';
  log('Image removed','warn');
});
async function uploadImage(file){
  if(!file.type.startsWith('image/')){ log('ERROR: not an image file','err'); return; }
  log('Uploading image...','warn');
  const fd=new FormData(); fd.append('image',file);
  try{
    const r=await fetch('/api/upload',{method:'POST',body:fd});
    const j=await r.json();
    uploadedUrl=j.url;
    $('previewImg').src=URL.createObjectURL(file);
    $('dzEmpty').hidden=true; $('dzPreview').hidden=false;
    log('Image uploaded ✓ — أرسل وصف الحركة الآن','ok');
  }catch(e){ log('Upload failed: '+e,'err'); }
}
$('generateBtn').addEventListener('click', async ()=>{
  if(busy) return;
  const prompt=$('prompt').value.trim();
  if(!prompt){ log('أدخل وصفاً أولاً','warn'); $('prompt').focus(); return; }
  if(mode==='edit' && !uploadedUrl){ log('ارفع صورة أولاً','warn'); return; }
  setBusy(true);
  $('generateBtn').innerHTML='<span class="rec-dot"></span> جاري التوليد...';
  $('stageTag').textContent='RENDERING'; $('stageTag').style.color='var(--rec)';
  const endpoint = mode==='create' ? '/api/generate' : '/api/edit';
  const body = mode==='create'
    ? {prompt, aspect_ratio:ratio}
    : {prompt, aspect_ratio:ratio, images:[uploadedUrl]};
  log(`POST ${endpoint}  (sora-2, ${ratio})`,'info');
  try{
    const res=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    const post=await res.json();
    if(post.status==='pending'){
      log('Task accepted ✓  task_id = '+post.task_id,'ok');
      startElapsed();
      poll(post.task_id, prompt, mode);
    } else {
      log('Could not start task: '+JSON.stringify(post),'err');
      resetBusy();
    }
  }catch(e){
    if(e instanceof TypeError){
      log('ERR: cannot reach the server','err');
      log('→ run: python app.py  then open http://localhost:5000','warn');
    } else {
      log('Server connection error: '+e,'err');
    }
    resetBusy();
  }
});
async function poll(taskId, prompt, mode){
  log('Rendering on VETREX servers... (check every 10s)','warn');
  while(true){
    await new Promise(r=>setTimeout(r,10000));
    try{
      const res=await fetch('/api/results/'+taskId);
      const g=await res.json();
      if(g.status==='completed'){
        const url=g.data[0].url;
        stopElapsed();
        log('RENDER COMPLETE ✓ — video ready','ok');
        showVideo(url);
        addToHistory({url,prompt,mode,date:Date.now()});
        resetBusy();
        return;
      } else if(g.status==='failed'){
        stopElapsed();
        log('FAILED: '+(g.python_error||'Unknown video generation error'),'err');
        resetBusy();
        return;
      } else {
        log('Still rendering... status='+(g.status||'pending'),'warn');
      }
    }catch(e){
      log('Result check error: '+e,'err');
      resetBusy();
      return;
    }
  }
}
function showVideo(url){
  $('standby').hidden=true;
  const p=$('player');
  p.hidden=false; p.src=url; p.play().catch(()=>{});
}
function setBusy(b){
  busy=b;
  const btn=$('generateBtn');
  btn.disabled=b; btn.classList.toggle('working',b);
  $('led').classList.toggle('busy',b);
  $('ledText').textContent=b?'مشغول':'متصل';
  $('stage').classList.toggle('working',b);
  $('renderOverlay').hidden=!b;
}
function resetBusy(){
  setBusy(false);
  $('generateBtn').innerHTML='<span class="rec-dot"></span> بدء التوليد';
  $('stageTag').textContent='LIVE'; $('stageTag').style.color='';
}
let secs=0;
function startElapsed(){
  secs=0; $('elapsed').textContent='00:00';
  elapsedTimer=setInterval(()=>{
    secs++;
    $('elapsed').textContent=String(Math.floor(secs/60)).padStart(2,'0')+':'+String(secs%60).padStart(2,'0');
  },1000);
}
function stopElapsed(){ clearInterval(elapsedTimer); }
function loadHistory(){
  try{ history=JSON.parse(localStorage.getItem('vetrex_shots')||'[]'); }catch(e){ history=[]; }
  renderHistory();
}
function addToHistory(item){
  history.unshift(item); history=history.slice(0,12);
  localStorage.setItem('vetrex_shots',JSON.stringify(history));
  renderHistory();
}
function escapeHtml(s){ return s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function renderHistory(){
  const row=$('archiveRow'); row.innerHTML='';
  if(!history.length){ row.innerHTML='<div class="empty-hint">الفيديوهات المولّدة ستظهر هنا — أرشيف الجلسة</div>'; return; }
  history.forEach(h=>{
    const d=document.createElement('div');
    d.className='shot';
    d.innerHTML=`<span class="mode-badge">${h.mode==='create'?'CREATE':'ANIMATE'}</span>
      <video src="${h.url}" muted loop preload="metadata"></video>
      <div class="meta"><p>${escapeHtml(h.prompt)}</p><small>${new Date(h.date).toLocaleString('en-GB')}</small></div>`;
    d.addEventListener('mouseenter',()=>d.querySelector('video').play().catch(()=>{}));
    d.addEventListener('mouseleave',()=>d.querySelector('video').pause());
    d.addEventListener('click',()=>{ showVideo(h.url); log('Playing from archive','info'); window.scrollTo({top:0,behavior:'smooth'}); });
    row.appendChild(d);
  });
}
loadHistory();
log('VETREX Console v2.0 — Ready','dim');
log('Connected to VETREX API ✓','ok');
log('Sora-2 engine ready — اختر الوضع وابدأ الإخراج','dim');
</script>
</body>
</html>"""

# ──────────────────────── ROUTES ────────────────────────

@app.route("/")
def index():
    return HTML_PAGE


@app.post("/api/upload")
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No image"}), 400
    f = request.files["image"]
    name = f"{uuid.uuid4().hex}_{secure_filename(f.filename)}"
    f.save(os.path.join(UPLOAD_DIR, name))
    return jsonify({"url": public_url(f"/uploads/{name}")})


@app.route("/uploads/<path:name>")
def serve_upload(name):
    return send_from_directory(UPLOAD_DIR, name)


@app.post("/api/generate")
def generate():
    data = request.get_json()
    payload = {
        "prompt": data.get("prompt", ""),
        "model": MODEL,
        "aspect_ratio": data.get("aspect_ratio", "16:9"),
    }
    try:
        logger.info(f"🎬 Sending to {VETREX_API}/videos/generations: {payload}")
        res = requests.post(f"{VETREX_API}/videos/generations",
                            json=payload, timeout=REQUEST_TIMEOUT)
        logger.info(f"📥 Response Status: {res.status_code}")
        logger.info(f"📥 Response Text: {res.text[:500]}")
        
        if res.status_code != 200:
            return jsonify({"status": "error", "python_error": f"API returned {res.status_code}: {res.text}"}), 502
        
        try:
            json_response = res.json()
            logger.info(f"✅ JSON Response: {json_response}")
            return jsonify(json_response)
        except Exception as json_error:
            logger.error(f"❌ JSON Parse Error: {json_error}")
            return jsonify({"status": "error", "python_error": f"Invalid JSON response: {res.text}"}), 502
            
    except requests.exceptions.Timeout:
        logger.error("⏱️ Request Timeout")
        return jsonify({"status": "error", "python_error": "Request timeout - API is slow"}), 502
    except Exception as e:
        logger.error(f"❌ Exception: {str(e)}")
        return jsonify({"status": "error", "python_error": str(e)}), 502


@app.post("/api/edit")
def edit_video():
    data = request.get_json()
    payload = {
        "prompt": data.get("prompt", ""),
        "model": MODEL,
        "aspect_ratio": data.get("aspect_ratio", "16:9"),
        "images": data.get("images", []),
    }
    try:
        logger.info(f"🎨 Sending to {VETREX_API}/videos/edits: {payload}")
        res = requests.post(f"{VETREX_API}/videos/edits",
                            json=payload, timeout=REQUEST_TIMEOUT)
        logger.info(f"📥 Response Status: {res.status_code}")
        logger.info(f"📥 Response Text: {res.text[:500]}")
        
        if res.status_code != 200:
            return jsonify({"status": "error", "python_error": f"API returned {res.status_code}: {res.text}"}), 502
        
        try:
            json_response = res.json()
            logger.info(f"✅ JSON Response: {json_response}")
            return jsonify(json_response)
        except Exception as json_error:
            logger.error(f"❌ JSON Parse Error: {json_error}")
            return jsonify({"status": "error", "python_error": f"Invalid JSON response: {res.text}"}), 502
            
    except requests.exceptions.Timeout:
        logger.error("⏱️ Request Timeout")
        return jsonify({"status": "error", "python_error": "Request timeout - API is slow"}), 502
    except Exception as e:
        logger.error(f"❌ Exception: {str(e)}")
        return jsonify({"status": "error", "python_error": str(e)}), 502


@app.get("/api/results/<task_id>")
def task_result(task_id):
    try:
        logger.info(f"🔍 Fetching results for {task_id}")
        res = requests.get(f"{VETREX_API}/videos/results/{task_id}",
                           timeout=REQUEST_TIMEOUT)
        logger.info(f"📥 Response Status: {res.status_code}")
        logger.info(f"📥 Response Text: {res.text[:500]}")
        
        if res.status_code != 200:
            return jsonify({"status": "error", "python_error": f"API returned {res.status_code}: {res.text}"}), 502
        
        try:
            json_response = res.json()
            logger.info(f"✅ JSON Response: {json_response}")
            return jsonify(json_response)
        except Exception as json_error:
            logger.error(f"❌ JSON Parse Error: {json_error}")
            return jsonify({"status": "error", "python_error": f"Invalid JSON response: {res.text}"}), 502
            
    except requests.exceptions.Timeout:
        logger.error("⏱️ Request Timeout")
        return jsonify({"status": "error", "python_error": "Request timeout - API is slow"}), 502
    except Exception as e:
        logger.error(f"❌ Exception: {str(e)}")
        return jsonify({"status": "error", "python_error": str(e)}), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 44)
    print("   VETREX STUDIO — Sora-2")
    print(f"   http://localhost:{port}")
    print("=" * 44)
    app.run(host="0.0.0.0", port=port, debug=False)
