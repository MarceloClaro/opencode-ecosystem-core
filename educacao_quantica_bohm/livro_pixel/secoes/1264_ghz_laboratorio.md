::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1264</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C027.png" alt=""> N1 · C027 · GHZ</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1264" class="titulo">GHZ — laboratório</h2>
<div class="corpo">

<p>No notebook, o código mínimo é:</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">多体纠缠态</span> <em>duō tǐ jiū chán tài</em> <span class="tom">· tons 1-3-1-2-4 · leitura duo-ti-djiu-tchan-tai</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察多体纠缠态。</span> <em>Guān chá duō tǐ jiū chán tài.</em> — Observe “GHZ”.</span></p>
<pre><code>qc.h(0); qc.cx(0,1); qc.cx(0,2); qc.cx(0,3)</code></pre>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> GHZ de 4 qubits — Quatro qubits compartilham 0000/1111.</p>
<p><strong>Simulado:</strong> P(0000)+P(1111) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(0000)+P(1111) = 0,788 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 78,8% · <strong>task:</strong> —</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E06 · Guoji08 · <a href="#oficina-e06">oficina E06</a> · <a href="#codigo-e06">código E06</a></p>
</div>

<p><strong>O que observar:</strong> confira a ordem dos qubits, o número de tiros e a diferença entre estado e amostra. <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> Fidelidade proxy = (N₀₀₀₀ + N₁₁₁₁)/N.<br><strong>Conta:</strong> (418+389)/1024 = 807/1024 = 0,7881.<br><strong>Resultado:</strong> 78,81%; 217 tiros fora de 0000/1111.<br><em>Limite:</em> O GHZ é frágil; a proxy cai rápido com o número de qubits.</span></p>

</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>O GHZ é usado em metrologia e testes de não localidade.</p>
<p class="prof"><strong>Para o professor:</strong> Confira a ordem dos qubits e a diferença entre circuito lógico e transpilado.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue escrever o QASM 2.0 do GHZ de 4 qubits?</p>
</div>

<div class="rodape">P03 · C027/100 · L1264/3000 · <a class="gab" href="#g-027">[G027]</a> · <a class="ficha-link" href="#f-027">[F027]</a></div>
:::
