::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1374</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C038.png" alt=""> N1 · C038 · ESFERA DE BLOCH</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1374" class="titulo">Esfera de Bloch — laboratório</h2>
<div class="corpo">

<p>No notebook, o código mínimo é:</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">布洛赫球</span> <em>bù luò hè qiú</em> <span class="tom">· tons 4-4-4-2 · leitura bu-luo-re-tchiu</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察布洛赫球。</span> <em>Guān chá bù luò hè qiú.</em> — Observe “Esfera de Bloch”.</span></p>
<pre><code>plot_bloch_multivector(Statevector(qc))</code></pre>
<figure class="fig"><img class="fig-pequena" src="../livro/figuras_geradas/fig10_bloch.png" alt="Esfera de Bloch de H|0⟩, gerada com Qiskit."><figcaption>Esfera de Bloch de H|0⟩, gerada com Qiskit.</figcaption></figure>
<p><strong>O que observar:</strong> confira a ordem dos qubits, o número de tiros e a diferença entre estado e amostra. <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> ⟨Z⟩ = (N₀−N₁)/N; ⟨X⟩ = (N₀−N₁)/N na base X.<br><strong>Conta:</strong> Z: (530−494)/1024=0,0352; X: (1016−8)/1024=0,9844.<br><strong>Resultado:</strong> ⟨Z⟩=+0,035; ⟨X⟩=+0,984.<br><em>Limite:</em> O estado é aproximadamente |+⟩; a pequena componente Z é erro.</span></p>
<div class="dossie"><span class="rotulo-dossie">DOSSIÊ</span><p>Grau B (evidência experimental ou metodológica com limites); o número não prova “A esfera não mostra emaranhamento de dois qubits”.</p></div><div class="exercicio"><span class="rotulo-dossie">EXERCÍCIO</span><p>Explique por que o resultado não autoriza essa conclusão sobre Esfera de Bloch.</p></div>
</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>O interior da esfera não é acessível; a superfície é o estado puro.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue localizar |0⟩, |1⟩ e H|0⟩ na esfera?</p>
</div>

<div class="rodape">P04 · C038/100 · L1374/3000 · <a class="gab" href="#g-038">[G038]</a> · <a class="ficha-link" href="#f-038">[F038]</a></div>
:::
