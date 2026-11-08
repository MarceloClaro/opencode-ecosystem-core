::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1014</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C002.png" alt=""> N1 · C002 · QUBIT</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1014" class="titulo">Qubit — laboratório</h2>
<div class="corpo">

<p><strong>Protocolo de bancada:</strong> escolha um exemplo de <em>qubit</em>, preveja o resultado e teste com um colega.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">量子比特</span> <em>liàng zǐ bǐ tè</em> <span class="tom">· tons 4-3-3-4 · leitura liang-dzi-bi-te</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察量子比特。</span> <em>Guān chá liàng zǐ bǐ tè.</em> — Observe “Qubit”.</span></p>
<ol>
<li>Escreva a previsão em uma frase.</li>
<li>Execute ou observe o fenômeno.</li>
<li>Registre a diferença e uma possível explicação.</li>
</ol>
<p><strong>O que observar:</strong> não basta acertar; é preciso explicar por que acertou.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Superposição H|0⟩ — H cria uma superposição; a medição produz 0 ou 1.</p>
<p><strong>Simulado:</strong> P(1) = 0,496 (ideal 0,500)<br>
<strong>Backend:</strong> P(1) = 0,482 (ideal 0,500)<br>
<strong>Sobreposição:</strong> 98,6% · <strong>task:</strong> 268a67b7</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E03 · Guoji08 · <a href="#oficina-e03">oficina E03</a> · <a href="#codigo-e03">código E03</a> <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> P(1) = N₁/N; desvio = |P(1) − 1/2|.<br><strong>Conta:</strong> N₁=494, N=1024: 494/1024 = 0,4824; |0,4824−0,5| = 0,0176.<br><strong>Resultado:</strong> P(1)=48,24%, dentro de ≈1,1 erro padrão de 50%.<br><em>Limite:</em> Uma execução não prova que a moeda é justa; o intervalo de confiança é largo.</span></p>
</div>


</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>A esfera de Bloch representa um qubit; o interior não é acessível.</p>
<p class="prof"><strong>Para o professor:</strong> Use a notação de ket apenas depois do concreto; verifique P(0)+P(1)=1.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue calcular P(0) para α=0,6?</p>
</div>

<div class="rodape">P01 · C002/100 · L1014/3000 · <a class="gab" href="#g-002">[G002]</a> · <a class="ficha-link" href="#f-002">[F002]</a></div>
:::
