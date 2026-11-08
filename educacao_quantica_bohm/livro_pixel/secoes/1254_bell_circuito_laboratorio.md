::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1254</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C026.png" alt=""> N1 · C026 · CIRCUITO DE BELL</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1254" class="titulo">Circuito de Bell — laboratório</h2>
<div class="corpo">

<p>No notebook, o código mínimo é:</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">贝尔电路</span> <em>bèi ěr diàn lù</em> <span class="tom">· tons 4-3-4-4 · leitura bei-er-dien-lu</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察贝尔电路。</span> <em>Guān chá bèi ěr diàn lù.</em> — Observe “Circuito de Bell”.</span></p>
<pre><code>qc.h(0); qc.cx(0,1); qc.measure_all()</code></pre>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Estado de Bell — H + CNOT criam uma correlação 00/11.</p>
<p><strong>Simulado:</strong> P(00)+P(11) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(00)+P(11) = 0,941 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 94,1% · <strong>task:</strong> 705bf99c</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E05 · Guoji08 · <a href="#oficina-e05">oficina E05</a> · <a href="#codigo-e05">código E05</a></p>
</div>

<p><strong>O que observar:</strong> confira a ordem dos qubits, o número de tiros e a diferença entre estado e amostra. <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> Fidelidade proxy = (N₀₀ + N₁₁)/N.<br><strong>Conta:</strong> (484+480)/1024 = 964/1024 = 0,9414.<br><strong>Resultado:</strong> 94,14%; 60 tiros em 01/10.<br><em>Limite:</em> A proxy não mede fase nem pureza; é uma soma de populações.</span></p>

</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>O circuito de Bell é o 'olá, mundo' do emaranhamento.</p>
<p class="prof"><strong>Para o professor:</strong> Confira a ordem dos qubits e a diferença entre circuito lógico e transpilado.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue prever os quatro resultados possíveis?</p>
</div>

<div class="rodape">P03 · C026/100 · L1254/3000 · <a class="gab" href="#g-026">[G026]</a> · <a class="ficha-link" href="#f-026">[F026]</a></div>
:::
