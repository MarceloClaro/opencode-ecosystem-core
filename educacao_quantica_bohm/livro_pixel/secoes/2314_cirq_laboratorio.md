::: {.lauda .lente-laboratorio .nivel-2}
<div class="topo">
  <span class="cod">L2314</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C032.png" alt=""> N2 · C032 · CIRQ</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2314" class="titulo">Cirq — laboratório</h2>
<div class="corpo">

<p>No notebook, o código mínimo é:</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">量子框架</span> <em>liàng zǐ kuàng jià</em> <span class="tom">· tons 4-3-4-4 · leitura liang-dzi-kuang-djia</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察量子框架。</span> <em>Guān chá liàng zǐ kuàng jià.</em> — Observe “Cirq”.</span></p>
<pre><code>q0,q1 = cirq.LineQubit.range(2); cirq.Circuit(cirq.H(q0), cirq.CNOT(q0,q1))</code></pre>
<figure class="fig"><img class="fig-pequena" src="../livro/figuras_geradas/fig06_cirq.svg" alt="Diagrama textual do circuito de Bell em Cirq."><figcaption>Diagrama textual do circuito de Bell em Cirq.</figcaption></figure>
<p><strong>O que observar:</strong> confira a ordem dos qubits, o número de tiros e a diferença entre estado e amostra. <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> P(1) = N₁/N; desvio = |P(1) − 1/2|.<br><strong>Conta:</strong> N₁=494, N=1024: 494/1024 = 0,4824; |0,4824−0,5| = 0,0176.<br><strong>Resultado:</strong> P(1)=48,24%, dentro de ≈1,1 erro padrão de 50%.<br><em>Limite:</em> Uma execução não prova que a moeda é justa; o intervalo de confiança é largo.</span></p>

</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>O diagrama textual é útil, mas não é uma figura de livro.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue ler o diagrama textual do Cirq?</p>
</div>

<div class="rodape">P04 · C032/100 · L2314/3000 · <a class="gab" href="#g-032">[G032]</a> · <a class="ficha-link" href="#f-032">[F032]</a></div>
:::
