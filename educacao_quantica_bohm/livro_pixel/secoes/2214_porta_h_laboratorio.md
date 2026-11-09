::: {.lauda .lente-laboratorio .nivel-2}
<div class="topo">
  <span class="cod">L2214</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C022.png" alt=""> N2 · C022 · PORTA H</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2214" class="titulo">Porta H — laboratório</h2>
<div class="corpo">

<p>No notebook, o código mínimo é:</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">哈达玛门</span> <em>hā dá mǎ mén</em> <span class="tom">· tons 1-2-3-2 · leitura ra-da-ma-men</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察哈达玛门。</span> <em>Guān chá hā dá mǎ mén.</em> — Observe “Porta H”.</span></p>
<pre><code>qml.Hadamard(0) · cirq.H(q0) · qc.h(0)</code></pre>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Superposição H|0⟩ — H cria uma superposição; a medição produz 0 ou 1.</p>
<p><strong>Simulado:</strong> P(1) = 0,496 (ideal 0,500)<br>
<strong>Backend:</strong> P(1) = 0,482 (ideal 0,500)<br>
<strong>Sobreposição:</strong> 98,6% · <strong>task:</strong> 268a67b7</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E03 · Guoji08 · <a href="#oficina-e03">oficina E03</a> · <a href="#codigo-e03">código E03</a></p>
</div>

<p><strong>O que observar:</strong> confira a ordem dos qubits, o número de tiros e a diferença entre estado e amostra. <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> P(1) = N₁/N; desvio = |P(1) − 1/2|.<br><strong>Conta:</strong> N₁=494, N=1024: 494/1024 = 0,4824; |0,4824−0,5| = 0,0176.<br><strong>Resultado:</strong> P(1)=48,24%, dentro de ≈1,1 erro padrão de 50%.<br><em>Limite:</em> Uma execução não prova que a moeda é justa; o intervalo de confiança é largo.</span></p>
<p>A ficha F022 declara o limite “H não é 'um pouco de 0 e um pouco de 1'; é uma transformação precisa”; o número não prova essa conclusão sobre Porta H.</p>
</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>H não é 'um pouco de 0 e um pouco de 1'; é uma transformação precisa.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue explicar por que H(H|0⟩)=|0⟩?</p>
</div>

<div class="rodape">P03 · C022/100 · L2214/3000 · <a class="gab" href="#g-022">[G022]</a> · <a class="ficha-link" href="#f-022">[F022]</a></div>
:::
