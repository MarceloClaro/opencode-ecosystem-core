#!/usr/bin/env node
// R1056. Render local estrito; não instala nada e bloqueia HTTP do navegador.
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');

function modulesRoot() {
  if (process.env.MERMAID_NODE_MODULES) return path.resolve(process.env.MERMAID_NODE_MODULES);
  const cache = path.join(os.homedir(), '.npm', '_npx');
  const candidates = fs.existsSync(cache) ? fs.readdirSync(cache).sort().map(n => path.join(cache, n, 'node_modules')) : [];
  const found = candidates.find(p => fs.existsSync(path.join(p, 'mermaid/dist/mermaid.min.js')) && fs.existsSync(path.join(p, 'puppeteer/package.json')));
  if (!found) throw new Error('Defina MERMAID_NODE_MODULES para instalação existente de mermaid + puppeteer');
  return found;
}

async function main() {
  const request = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const root = modulesRoot();
  const puppeteer = require(path.join(root, 'puppeteer'));
  const mermaid = path.join(root, 'mermaid/dist/mermaid.min.js');
  const version = JSON.parse(fs.readFileSync(path.join(root, 'mermaid/package.json'))).version;
  let browser;
  try {
    const launch = {headless: true};
    if (process.env.CHROME_EXECUTABLE) launch.executablePath = process.env.CHROME_EXECUTABLE;
    // Respeita o sandbox padrão; bypass NÃO é ativado silenciosamente.
    browser = await puppeteer.launch(launch);
    const page = await browser.newPage();
    await page.setViewport({width: 1600, height: 1000, deviceScaleFactor: 1});
    await page.setRequestInterception(true);
    page.on('request', r => r.url().startsWith('http') ? r.abort() : r.continue());
    await page.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0;background:#0b1220"><main id="canvas"></main></body></html>');
    await page.addScriptTag({path: mermaid});
    for (const item of request.diagrams) {
      if (!/^diagram-[a-f0-9]{16}$/.test(item.id)) throw new Error('ID inválido');
      if (Buffer.byteLength(item.source) > 100000 || /%%\{|^\s*click\s|<\s*(script|iframe|img|image|foreignObject)\b|https?:\/\/|javascript:\S|data:\S/im.test(item.source)) throw new Error('Fonte não permitida');
      const output = await page.evaluate(async ({id, source}) => {
        const canvas = document.querySelector('#canvas');
        canvas.innerHTML = '';
        window.mermaid.initialize({startOnLoad: false, securityLevel: 'strict',
          deterministicIds: true, deterministicIDSeed: id, htmlLabels: false,
          maxEdges: 1000, maxTextSize: 100000, theme: 'base',
          fontFamily: 'DejaVu Sans',
          themeVariables: {background: '#0b1220', primaryColor: '#172a42',
            primaryTextColor: '#edf5ff', primaryBorderColor: '#5985ab',
            secondaryColor: '#16383e', tertiaryColor: '#142238',
            lineColor: '#8fb0cc', textColor: '#edf5ff', nodeTextColor: '#edf5ff',
            clusterBkg: '#101e30', clusterBorder: '#34516b',
            edgeLabelBackground: '#0b1220', fontSize: '18px'},
          flowchart: {htmlLabels: false, useMaxWidth: false, curve: 'basis', nodeSpacing: 42, rankSpacing: 64, wrappingWidth: 220},
          secure: ['securityLevel', 'startOnLoad', 'maxEdges', 'maxTextSize']});
        const {svg} = await window.mermaid.render(id, source);
        canvas.innerHTML = svg;
        const el = canvas.querySelector('svg');
        if (el.querySelector('script, foreignObject, image, a')) throw new Error('SVG ativo não permitido');
        const vb = el.viewBox.baseVal;
        const width = vb.width, height = vb.height, ox = vb.x, oy = vb.y;
        const nodes = [...el.querySelectorAll('g.node')].map(n => {
          const b = n.getBBox(), m = n.getCTM();
          const pt = new DOMPoint(b.x + b.width/2, b.y + b.height/2).matrixTransform(m);
          const label = [...n.querySelectorAll('tspan.text-outer-tspan')]
            .map(t => t.textContent.trim()).filter(Boolean).join(' ');
          return {id: n.id, label, x: pt.x, y: pt.y};
        });
        const labels = {};
        el.querySelectorAll('g.edgeLabel').forEach(g => {
          const inner = g.querySelector('.label[data-id]');
          if (inner) labels[inner.dataset.id] = g.textContent.replace(/\s+/g, ' ').trim();
        });
        // Calcular coordenadas usando matriz relativa ao SVG, antes de rasterizar.
        const inverse = el.getCTM().inverse();
        const map = (p, matrix) => {
          const q = new DOMPoint(p.x, p.y).matrixTransform(matrix).matrixTransform(inverse);
          return [q.x - ox, q.y - oy];
        };
        const normalizedNodes = nodes.map(n => {
          const pt = new DOMPoint(n.x, n.y).matrixTransform(inverse);
          return {...n, x: pt.x - ox, y: pt.y - oy};
        });
        const nearest = pt => [...normalizedNodes].sort((a,b) => Math.hypot(a.x-pt[0],a.y-pt[1])-Math.hypot(b.x-pt[0],b.y-pt[1]))[0]?.label || '';
        const edges = [...el.querySelectorAll('path.flowchart-link, .edgePath path.path')].map(p => {
          const length = p.getTotalLength(), matrix = p.getCTM();
          const points = Array.from({length: 61}, (_,i) => map(p.getPointAtLength(length*i/60), matrix));
          return {id: p.id, label: labels[p.id] || '', points,
                  from_label: nearest(points[0]), to_label: nearest(points[60])};
        });
        el.style.maxWidth = 'none';
        const scale = Math.min(1.5, 2400/width, 2400/height);
        el.setAttribute('width', String(Math.ceil(width*scale)));
        el.setAttribute('height', String(Math.ceil(height*scale)));
        return {svg: el.outerHTML, geometry: {width, height, nodes: normalizedNodes, edges}};
      }, {id: item.id, source: item.source});
      const stem = path.join(request.output, item.id);
      fs.writeFileSync(stem+'.svg', output.svg+'\n');
      const el = await page.$('#canvas svg');
      await el.screenshot({path: stem+'.render.png'});
      output.geometry.renderer = {mermaid: version,
        browser: await browser.version(),
        bundle_sha256: crypto.createHash('sha256').update(fs.readFileSync(mermaid)).digest('hex')};
      fs.writeFileSync(stem+'.geometry.json', JSON.stringify(output.geometry,null,2)+'\n');
      console.log(JSON.stringify({svg: item.id, nodes: output.geometry.nodes.length, edges: output.geometry.edges.length}));
    }
  } finally {
    if (browser) await browser.close();
  }
}
main().catch(e => {console.error(e.message); process.exitCode=1;});
