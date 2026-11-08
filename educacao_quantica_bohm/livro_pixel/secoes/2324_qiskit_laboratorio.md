::: {.lauda .lente-laboratorio .nivel-2}
<div class="topo">
  <span class="cod">L2324</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C033.png" alt=""> N2 · C033 · QISKIT</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2324" class="titulo">Qiskit — laboratório</h2>
<div class="corpo">

<p>No notebook, o código mínimo é:</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">量子开发包</span> <em>liàng zǐ kāi fā bāo</em> <span class="tom">· tons 4-3-1-1-1 · leitura liang-dzi-kai-fa-bau</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察量子开发包。</span> <em>Guān chá liàng zǐ kāi fā bāo.</em> — Observe “Qiskit”.</span></p>
<pre><code>from qiskit import QuantumCircuit; qc.h(0); qc.cx(0,1)</code></pre>
<figure class="fig"><img class="fig-pequena" src="../livro/figuras_geradas/fig07_qiskit.svg" alt="Circuito de Bell desenhado por Qiskit."><figcaption>Circuito de Bell desenhado por Qiskit.</figcaption></figure>
<p><strong>O que observar:</strong> confira a ordem dos qubits, o número de tiros e a diferença entre estado e amostra. <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> P(1) = N₁/N; desvio = |P(1) − 1/2|.<br><strong>Conta:</strong> N₁=494, N=1024: 494/1024 = 0,4824; |0,4824−0,5| = 0,0176.<br><strong>Resultado:</strong> P(1)=48,24%, dentro de ≈1,1 erro padrão de 50%.<br><em>Limite:</em> Uma execução não prova que a moeda é justa; o intervalo de confiança é largo.</span></p>

</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>O desenho do circuito não é o circuito físico; é uma representação.</p>
<p class="prof"><strong>Para pesquisa:</strong> repita com outra seed/backend.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue comparar o Bell de Qiskit com o de Cirq?</p>
</div>

<div class="rodape">P04 · C033/100 · L2324/3000 · <a class="gab" href="#g-033">[G033]</a> · <a class="ficha-link" href="#f-033">[F033]</a></div>
:::
