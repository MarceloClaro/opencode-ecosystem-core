::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1304</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C031.png" alt=""> N1 · C031 · PENNYLANE</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1304" class="titulo">PennyLane — laboratório</h2>
<div class="corpo">

<p>No notebook, o código mínimo é:</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">量子软件</span> <em>liàng zǐ ruǎn jiàn</em> <span class="tom">· tons 4-3-3-4 · leitura liang-dzi-juan-djien</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察量子软件。</span> <em>Guān chá liàng zǐ ruǎn jiàn.</em> — Observe “PennyLane”.</span></p>
<pre><code>import pennylane as qml; dev = qml.device('default.qubit', wires=2)</code></pre>
<figure class="fig"><img class="fig-pequena" src="../livro/figuras_geradas/fig05_pennylane.svg" alt="Circuito de Bell desenhado por PennyLane."><figcaption>Circuito de Bell desenhado por PennyLane.</figcaption></figure>
<p><strong>O que observar:</strong> confira a ordem dos qubits, o número de tiros e a diferença entre estado e amostra. <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> P(1) = N₁/N; desvio = |P(1) − 1/2|.<br><strong>Conta:</strong> N₁=494, N=1024: 494/1024 = 0,4824; |0,4824−0,5| = 0,0176.<br><strong>Resultado:</strong> P(1)=48,24%, dentro de ≈1,1 erro padrão de 50%.<br><em>Limite:</em> Uma execução não prova que a moeda é justa; o intervalo de confiança é largo.</span></p>
<div class="dossie"><span class="rotulo-dossie">DOSSIÊ</span><p>Grau B (evidência experimental ou metodológica com limites); o número não prova “A diferenciação automática não substitui a interpretação física”.</p></div><div class="exercicio"><span class="rotulo-dossie">EXERCÍCIO</span><p>Explique por que o resultado não autoriza essa conclusão sobre PennyLane.</p></div>
</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>PennyLane integra com simuladores e vários provedores.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue escrever um QNode de Bell?</p>
</div>

<div class="rodape">P04 · C031/100 · L1304/3000 · <a class="gab" href="#g-031">[G031]</a> · <a class="ficha-link" href="#f-031">[F031]</a></div>
:::
