::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1354</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C036.png" alt=""> N1 · C036 · QUANTUMCIRCUIT</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1354" class="titulo">QuantumCircuit — laboratório</h2>
<div class="corpo">

<p>No notebook, o código mínimo é:</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">量子电路</span> <em>liàng zǐ diàn lù</em> <span class="tom">· tons 4-3-4-4 · leitura liang-dzi-dien-lu</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察量子电路。</span> <em>Guān chá liàng zǐ diàn lù.</em> — Observe “QuantumCircuit”.</span></p>
<pre><code>qc = QuantumCircuit(4, 4); qc.measure_all()</code></pre>

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
<p>O Qiskit separa circuito lógico e circuito transpilado.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue explicar a diferença entre qreg e creg?</p>
</div>

<div class="rodape">P04 · C036/100 · L1354/3000 · <a class="gab" href="#g-036">[G036]</a> · <a class="ficha-link" href="#f-036">[F036]</a></div>
:::
