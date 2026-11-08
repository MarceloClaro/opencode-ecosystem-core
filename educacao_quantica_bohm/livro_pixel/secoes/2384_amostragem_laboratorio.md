::: {.lauda .lente-laboratorio .nivel-2}
<div class="topo">
  <span class="cod">L2384</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C039.png" alt=""> N2 · C039 · AMOSTRAGEM</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2384" class="titulo">Amostragem — laboratório</h2>
<div class="corpo">

<p>No notebook, o código mínimo é:</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">采样</span> <em>cǎi yàng</em> <span class="tom">· tons 3-4 · leitura tsai-iang</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察采样。</span> <em>Guān chá cǎi yàng.</em> — Observe “Amostragem”.</span></p>
<pre><code>sample_counts(shots, qargs=[...])</code></pre>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Amostragem binomial — H + medição; o desvio de P(1) cai com o número de tiros.</p>
<p><strong>Simulado:</strong> P(1) = 0,483 (ideal 0,500)<br>
<strong>Backend:</strong> P(1) = 0,482 (ideal 0,500)<br>
<strong>Sobreposição:</strong> 99,9% · <strong>task:</strong> 54de9107</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E18 · Guoji08 · <a href="#oficina-e18">oficina E18</a> · <a href="#codigo-e18">código E18</a></p>
</div>

<p><strong>O que observar:</strong> confira a ordem dos qubits, o número de tiros e a diferença entre estado e amostra. <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> P(1)=N₁/N; EP=√(p(1−p)/N).<br><strong>Conta:</strong> N₁=494, N=1024: p=0,4824; EP=√(0,4824×0,5176/1024)=0,0156.<br><strong>Resultado:</strong> P(1)=48,24% ± 1,56% (1 EP).<br><em>Limite:</em> O desvio de 50% é compatível com amostragem; não prova viés do backend.</span></p>

</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>A amostra não é o estado; é uma sombra estatística.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue explicar por que a frequência flutua?</p>
</div>

<div class="rodape">P04 · C039/100 · L2384/3000 · <a class="gab" href="#g-039">[G039]</a> · <a class="ficha-link" href="#f-039">[F039]</a></div>
:::
