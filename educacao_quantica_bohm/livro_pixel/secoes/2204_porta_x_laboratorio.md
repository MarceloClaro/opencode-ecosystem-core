::: {.lauda .lente-laboratorio .nivel-2}
<div class="topo">
  <span class="cod">L2204</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C021.png" alt=""> N2 · C021 · PORTA X</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2204" class="titulo">Porta X — laboratório</h2>
<div class="corpo">

<p>No notebook, o código mínimo é:</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">翻转门</span> <em>fān zhuǎn mén</em> <span class="tom">· tons 1-3-2 · leitura fan-djuan-men</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察翻转门。</span> <em>Guān chá fān zhuǎn mén.</em> — Observe “Porta X”.</span></p>
<pre><code>qml.PauliX(0) · cirq.X(q0) · qc.x(0)</code></pre>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Base |1⟩ e leitura — Prepara |1⟩ e mede; a discrepância é erro de leitura.</p>
<p><strong>Simulado:</strong> P(1) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(1) = 0,986 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 98,6% · <strong>task:</strong> 6018c711</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E02 · Guoji08 · <a href="#oficina-e02">oficina E02</a> · <a href="#codigo-e02">código E02</a></p>
</div>

<p><strong>O que observar:</strong> confira a ordem dos qubits, o número de tiros e a diferença entre estado e amostra. <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> P(1) = N₁/N; erro de leitura ≈ N₀/N.<br><strong>Conta:</strong> N₁=1010, N₀=14, N=1024: 1010/1024 = 0,9863.<br><strong>Resultado:</strong> P(1)=98,63%; 14 leituras erradas = 1,37%.<br><em>Limite:</em> O erro de leitura é uma propriedade do dispositivo, não do estado preparado.</span></p>

</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>X não cria superposição; ela apenas troca os estados de base.</p>
<p class="prof"><strong>Para pesquisa:</strong> repita com outra seed/backend.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue prever X|0⟩ e X|1⟩?</p>
</div>

<div class="rodape">P03 · C021/100 · L2204/3000 · <a class="gab" href="#g-021">[G021]</a> · <a class="ficha-link" href="#f-021">[F021]</a></div>
:::
