::: {.lauda .lente-laboratorio .nivel-2}
<div class="topo">
  <span class="cod">L2284</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C029.png" alt=""> N2 · C029 · TRANSPILAÇÃO</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2284" class="titulo">Transpilação — laboratório</h2>
<div class="corpo">

<p>No notebook, o código mínimo é:</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">转译</span> <em>zhuǎn yì</em> <span class="tom">· tons 3-4 · leitura djuan-i</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察转译。</span> <em>Guān chá zhuǎn yì.</em> — Observe “Transpilação”.</span></p>
<pre><code>generate_preset_pass_manager(backend=backend).run(qc)</code></pre>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> GHZ via QASM 2.0 — O mesmo GHZ carregado de um texto OpenQASM 2.0.</p>
<p><strong>Simulado:</strong> P(0000)+P(1111) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(0000)+P(1111) = 0,788 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 78,8% · <strong>task:</strong> —</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E15 · Guoji08 · <a href="#oficina-e15">oficina E15</a> · <a href="#codigo-e15">código E15</a></p>
</div>

<p><strong>O que observar:</strong> confira a ordem dos qubits, o número de tiros e a diferença entre estado e amostra. <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> O QASM carrega o mesmo GHZ; a proxy é (N₀₀₀₀+N₁₁₁₁)/N.<br><strong>Conta:</strong> (418+389)/1024 = 807/1024 = 0,7881.<br><strong>Resultado:</strong> 78,81%, igual ao GHZ montado no console.<br><em>Limite:</em> O formato QASM não muda o circuito; o backend e a calibração mudam.</span></p>
<p>A ficha F029 declara o limite “A tradução pode aumentar a profundidade e o ruído”; o número não prova essa conclusão sobre Transpilação.</p>
</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>A tradução pode aumentar a profundidade e o ruído.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue explicar por que a profundidade aumentou?</p>
</div>

<div class="rodape">P03 · C029/100 · L2284/3000 · <a class="gab" href="#g-029">[G029]</a> · <a class="ficha-link" href="#f-029">[F029]</a></div>
:::
