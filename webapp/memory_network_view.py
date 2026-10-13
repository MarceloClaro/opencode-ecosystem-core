"""Canvas local sem dependências remotas; dados externos são texto inerte."""
import json


def build_network_html(snapshot, *, selected_id=None, motion=True):
    payload = json.dumps({'snapshot':snapshot,'selected':selected_id,'motion':bool(motion)},
                         ensure_ascii=True,allow_nan=False)
    payload = payload.replace('<',r'\u003c').replace('>',r'\u003e').replace('&',r'\u0026')
    return _HTML.replace('__PAYLOAD__',payload)


_HTML = r'''<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<style>
*{box-sizing:border-box}body{margin:0;background:#0c1421;color:#e5edf7;font:14px system-ui,sans-serif}
.shell{padding:18px;border:1px solid #26364a;border-radius:14px}.top{display:flex;justify-content:space-between;gap:12px;align-items:center}
h2{font-size:18px;margin:0 0 5px}.muted{color:#a1b0c4;font-size:12px}.badge{padding:6px 10px;border-radius:12px;background:#203447;font-size:11px}
.legend{display:flex;flex-wrap:wrap;gap:15px;padding:15px 0;font-size:12px}.legend span:before{content:'●';margin-right:6px;color:var(--color)}
.workspace{display:grid;grid-template-columns:minmax(0,3fr) minmax(190px,1fr);gap:16px}
.maps{display:grid;grid-template-columns:1fr 1fr;gap:12px}.mapbox{background:#101d2e;border-radius:12px;padding:8px}
.mapbox h4{margin:4px 2px 6px;font-size:12px;color:#a1b0c4;font-weight:600}
canvas{width:100%;height:420px;background:#0e1a2b;border-radius:8px}
aside{border-left:1px solid #29394e;padding-left:15px;overflow-wrap:anywhere}h3{font-size:14px;margin-top:0}pre{white-space:pre-wrap;font:12px system-ui;line-height:1.6}
.footer{display:flex;justify-content:space-between;gap:12px;margin-top:10px;font-size:12px;color:#a1b0c4}
.topactions{display:flex;gap:8px;align-items:center}
.fsbtn{cursor:pointer;border:1px solid #33475e;background:#182941;color:#e5edf7;border-radius:10px;padding:6px 10px;font-size:12px}
.fsbtn:hover{background:#20344c}.fsbtn:focus-visible{outline:2px solid #64aafc;outline-offset:2px}
.shell:fullscreen{background:#0c1421;overflow:auto;border-radius:0}
.shell.expanded{position:fixed;inset:0;z-index:9999;overflow:auto;background:#0c1421;border-radius:0}
.shell:fullscreen canvas,.shell.expanded canvas{height:min(62vh,640px)}
@media(max-width:900px){.maps{grid-template-columns:1fr}}
@media(max-width:650px){.workspace{grid-template-columns:1fr}aside{border-left:0;border-top:1px solid #29394e;padding:12px 0}canvas{height:400px}}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
</style>
<div class="shell" id="shell"><div class="top"><div><h2>Rede de memória e evidências</h2><div class="muted">Registros do Core · visão simultânea: topologia por tipo + mapa de vetores · selecione um nó em qualquer mapa</div></div><div class="topactions"><span id="mode" class="badge"></span><button id="fsbtn" class="fsbtn" type="button" aria-pressed="false" title="Alternar tela cheia (Esc sai)">⛶ Tela cheia</button></div></div>
<div id="legend" class="legend"></div><div class="workspace"><div class="maps"><div class="mapbox"><h4>Topologia por tipo</h4><canvas id="network" aria-label="Grafo de registros do Core"></canvas></div><div class="mapbox"><h4>Mapa de vetores — projeção hash, sem semântica</h4><canvas id="vectors" aria-label="Mapa de vetores por projeção determinística"></canvas><div class="muted">Posição por hash do ID; tamanho por relevância; sem valor semântico ou probatório.</div></div></div><aside><h3 id="node-title">Detalhes do nó</h3><pre id="details">Nenhum nó selecionado.</pre><div class="muted">Peso de relação e relevância não são probabilidades calibradas. Atividade indica evento recente, sem revelar atenção interna de um LLM.</div></aside></div>
<div class="footer"><span id="counts"></span><span id="activity"></span></div></div>
<script type="application/json" id="data">__PAYLOAD__</script>
<script>
'use strict';
const args=JSON.parse(document.getElementById('data').textContent), snap=args.snapshot;
const types=['consulta','memoria','contexto','agente','evidencia','resposta'];
const labels={consulta:'Consulta',memoria:'Memória',contexto:'Contexto',agente:'Agentes',evidencia:'Evidência',resposta:'Resposta'};
const colors={consulta:'#64aafc',memoria:'#66dab1',contexto:'#70d6e3',agente:'#efca70',evidencia:'#d5e2ff',resposta:'#c69bfa'};
const motion=args.motion&&!matchMedia('(prefers-reduced-motion: reduce)').matches;
const canvas=document.getElementById('network'),ctx=canvas.getContext('2d');
const vcanvas=document.getElementById('vectors'),vctx=vcanvas.getContext('2d');
let positions=new Map(), vpositions=new Map(), chosen=args.selected, start=performance.now();
document.getElementById('mode').textContent=snap.mode==='demonstration'?'DEMONSTRAÇÃO — DADOS SIMULADOS':'DADOS LOCAIS OBSERVADOS';
for(const type of types){const entry=document.createElement('span');entry.textContent=labels[type];entry.style.setProperty('--color',colors[type]);document.getElementById('legend').append(entry);}
let selected=snap.nodes.find(n=>n.id===chosen)||snap.nodes[0];
function details(node){if(!node)return;selected=node;document.getElementById('node-title').textContent=node.label;
document.getElementById('details').textContent='Tipo: '+labels[node.type]+'\nOrigem: '+node.source+'\nID original: '+node.original_id+'\nRelevância: '+(node.relevance===null?'não registrada':node.relevance+' (registrada)')+'\nMétrica calibrada: não\n'+JSON.stringify(node.metadata,null,2);}
details(selected);
const shell=document.getElementById('shell'),fsbtn=document.getElementById('fsbtn');
function fsLabel(){const on=document.fullscreenElement===shell||shell.classList.contains('expanded');fsbtn.textContent=on?'✕ Sair da tela cheia':'⛶ Tela cheia';fsbtn.setAttribute('aria-pressed',on?'true':'false');}
async function toggleFS(){try{if(document.fullscreenElement===shell){await document.exitFullscreen();}else if(shell.classList.contains('expanded')){shell.classList.remove('expanded');}else if(shell.requestFullscreen){await shell.requestFullscreen();}else{shell.classList.add('expanded');}}catch(e){shell.classList.toggle('expanded');}fsLabel();layout();}
fsbtn.addEventListener('click',toggleFS);
document.addEventListener('fullscreenchange',()=>{if(!document.fullscreenElement)shell.classList.remove('expanded');fsLabel();layout();});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){shell.classList.remove('expanded');fsLabel();}});
fsLabel();
function hash01(str,seed){let h=seed>>>0;for(let i=0;i<str.length;i++){h=Math.imul(h^str.charCodeAt(i),2654435761);h^=h>>>13;}h=Math.imul(h,2246822519);h^=h>>>16;return (h>>>0)/4294967295;}
const typeIdx={consulta:0,memoria:1,contexto:2,agente:3,evidencia:4,resposta:5};
function layout(){const ratio=Math.min(devicePixelRatio||1,2),width=Math.max(300,canvas.clientWidth),height=canvas.clientHeight;canvas.width=width*ratio;canvas.height=height*ratio;ctx.setTransform(ratio,0,0,ratio,0,0);positions=new Map();
for(let col=0;col<types.length;col++){let group=snap.nodes.filter(n=>n.type===types[col]);const current=group.find(n=>selected&&n.id===selected.id);group=group.slice(0,8);if(current&&!group.includes(current))group[group.length-1]=current;
group.forEach((node,row)=>positions.set(node.id,{x:(col+.5)*width/types.length,y:60+row*(height-105)/Math.max(7,group.length-1),node}));}
const vw=Math.max(300,vcanvas.clientWidth),vh=vcanvas.clientHeight;vcanvas.width=vw*ratio;vcanvas.height=vh*ratio;vctx.setTransform(ratio,0,0,ratio,0,0);vpositions=new Map();
const all=snap.nodes.slice(0,120);
for(const node of all){const ti=typeIdx[node.type]||0;const x=18+hash01(node.id+'#x'+node.type,5381+ti*101)*(vw-36);const y=30+hash01(node.id+'#y'+node.type,33+ti*997)*(vh-60);vpositions.set(node.id,{x,y,node});}}
layout();new ResizeObserver(layout).observe(canvas);new ResizeObserver(layout).observe(vcanvas);
function active(item,elapsed){return item.active&&item.timestamp!==null&&snap.generated_at+elapsed-item.timestamp<=snap.limits.activation_window_seconds;}
function draw(){const elapsed=(performance.now()-start)/1000,w=canvas.clientWidth,h=canvas.clientHeight;ctx.clearRect(0,0,Math.max(w,300),h);
ctx.font='bold 10px system-ui';ctx.textAlign='center';for(let col=0;col<types.length;col++){ctx.fillStyle=colors[types[col]];ctx.fillText(labels[types[col]],(col+.5)*Math.max(w,300)/types.length,24);}
let moving=0;
for(const edge of snap.edges){const a=positions.get(edge.source),b=positions.get(edge.target);if(!a||!b)continue;const on=active(edge,elapsed);if(on)moving++;ctx.strokeStyle=on?'#b0c7e7':'#314861';ctx.lineWidth=edge.weight===null?1:Math.min(4,Math.max(.5,edge.weight));ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
const angle=Math.atan2(b.y-a.y,b.x-a.x),tx=b.x-Math.cos(angle)*14,ty=b.y-Math.sin(angle)*14;ctx.fillStyle=ctx.strokeStyle;ctx.beginPath();ctx.moveTo(tx,ty);ctx.lineTo(tx-6*Math.cos(angle-.5),ty-6*Math.sin(angle-.5));ctx.lineTo(tx-6*Math.cos(angle+.5),ty-6*Math.sin(angle+.5));ctx.fill();
if(on&&motion){const phase=(elapsed*.45)%1;ctx.fillStyle='#e9f4ff';ctx.beginPath();ctx.arc(a.x+(b.x-a.x)*phase,a.y+(b.y-a.y)*phase,2.5,0,Math.PI*2);ctx.fill();}}
for(const {x,y,node} of positions.values()){const on=active(node,elapsed);ctx.shadowBlur=on&&motion?10+5*Math.sin(elapsed*4):0;ctx.shadowColor=colors[node.type];ctx.fillStyle=colors[node.type];ctx.globalAlpha=on?1:.7;ctx.beginPath();ctx.arc(x,y,on?10:7,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;ctx.shadowBlur=0;if(selected&&node.id===selected.id){ctx.strokeStyle='#f0f6ff';ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(x,y,14,0,Math.PI*2);ctx.stroke();}
ctx.fillStyle='#c9d6e7';ctx.font='10px system-ui';ctx.fillText(node.label.length>15?node.label.slice(0,13)+'…':node.label,x,y+23);}
// Mapa de vetores simultâneo
const vw=vcanvas.clientWidth,vh=vcanvas.clientHeight;vctx.clearRect(0,0,Math.max(vw,300),vh);
vctx.strokeStyle='#1d2f44';vctx.lineWidth=1;for(let g=1;g<4;g++){vctx.beginPath();vctx.moveTo(vw*g/4,0);vctx.lineTo(vw*g/4,vh);vctx.stroke();vctx.beginPath();vctx.moveTo(0,vh*g/4);vctx.lineTo(vw,vh*g/4);vctx.stroke();}
for(const edge of snap.edges){const a=vpositions.get(edge.source),b=vpositions.get(edge.target);if(!a||!b)continue;const on=active(edge,elapsed);vctx.strokeStyle=on?'rgba(176,199,231,.9)':'rgba(49,72,97,.55)';vctx.lineWidth=.8;vctx.beginPath();vctx.moveTo(a.x,a.y);vctx.lineTo(b.x,b.y);vctx.stroke();
if(on&&motion){const phase=(elapsed*.45)%1;vctx.fillStyle='#e9f4ff';vctx.beginPath();vctx.arc(a.x+(b.x-a.x)*phase,a.y+(b.y-a.y)*phase,2.2,0,Math.PI*2);vctx.fill();}}
for(const {x,y,node} of vpositions.values()){const on=active(node,elapsed);const base=node.relevance===null?4:4+Math.min(1,Math.max(0,node.relevance))*8;const r=on?base+2:base;vctx.shadowBlur=on&&motion?10+5*Math.sin(elapsed*4):0;vctx.shadowColor=colors[node.type];vctx.fillStyle=colors[node.type];vctx.globalAlpha=on?1:.75;vctx.beginPath();vctx.arc(x,y,r,0,Math.PI*2);vctx.fill();vctx.globalAlpha=1;vctx.shadowBlur=0;
if(selected&&node.id===selected.id){vctx.strokeStyle='#f0f6ff';vctx.lineWidth=1.5;vctx.beginPath();vctx.arc(x,y,r+5,0,Math.PI*2);vctx.stroke();}
if(on||(selected&&node.id===selected.id)){vctx.fillStyle='#c9d6e7';vctx.font='10px system-ui';vctx.textAlign='center';const lb=node.label.length>12?node.label.slice(0,11)+'…':node.label;vctx.fillText(lb,x,y+r+12);}}
document.getElementById('counts').textContent=positions.size+'/'+snap.nodes.length+' nós na topologia · '+vpositions.size+' pontos no mapa de vetores · '+snap.edges.length+' vetores registrados';
document.getElementById('activity').textContent=moving?moving+' vínculos com evento recente':'Sem ativação recente registrada';
if(motion&&(moving||[...positions.values()].some(p=>active(p.node,elapsed))))requestAnimationFrame(draw);else setTimeout(draw,1000);}
function pick(cv,map){const rect=cv.getBoundingClientRect(),x=event.clientX-rect.left,y=event.clientY-rect.top;let nearest,best=20;for(const p of map.values()){const d=Math.hypot(x-p.x,y-p.y);if(d<best){best=d;nearest=p.node;}}if(nearest)details(nearest);}
canvas.addEventListener('click',()=>pick(canvas,positions));
vcanvas.addEventListener('click',()=>pick(vcanvas,vpositions));
draw();
</script></html>'''
