::: {.lauda .lente-laboratorio .nivel-2}
<div class="topo">
  <span class="cod">L2364</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C037.png" alt=""> N2 · C037 · STATEVECTOR</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2364" class="titulo">Statevector — laboratório</h2>
<div class="corpo">

<p>No notebook, o código mínimo é:</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">态矢量</span> <em>tài shǐ liàng</em> <span class="tom">· tons 4-3-4 · leitura tai-shi-liang</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察态矢量。</span> <em>Guān chá tài shǐ liàng.</em> — Observe “Statevector”.</span></p>
<pre><code>Statevector(qc).data</code></pre>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Esfera de Bloch — Mede Z e X do estado H|0⟩.</p>
<p><strong>Simulado:</strong> ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1)<br>
<strong>Backend:</strong> ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1)<br>
<strong>Sobreposição:</strong> 98,9% · <strong>task:</strong> 9da79d10</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E16 · Guoji08 · <a href="#oficina-e16">oficina E16</a> · <a href="#codigo-e16">código E16</a></p>
</div>

<p><strong>O que observar:</strong> confira a ordem dos qubits, o número de tiros e a diferença entre estado e amostra. <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> ⟨Z⟩ = (N₀−N₁)/N; ⟨X⟩ = (N₀−N₁)/N na base X.<br><strong>Conta:</strong> Z: (530−494)/1024=0,0352; X: (1016−8)/1024=0,9844.<br><strong>Resultado:</strong> ⟨Z⟩=+0,035; ⟨X⟩=+0,984.<br><em>Limite:</em> O estado é aproximadamente |+⟩; a pequena componente Z é erro.</span></p>
<p>A ficha F037 declara o limite “O vetor cresce como 2^n; não é acessível por medição única”; o número não prova essa conclusão sobre Statevector.</p>
</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>O vetor cresce como 2^n; não é acessível por medição única.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue calcular as probabilidades a partir do vetor?</p>
</div>

<div class="rodape">P04 · C037/100 · L2364/3000 · <a class="gab" href="#g-037">[G037]</a> · <a class="ficha-link" href="#f-037">[F037]</a></div>
:::
