::: {.lauda .lente-laboratorio .nivel-2}
<div class="topo">
  <span class="cod">L2054</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C006.png" alt=""> N2 · C006 · BASE</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2054" class="titulo">Base — laboratório</h2>
<div class="corpo">

<p><strong>Protocolo de bancada:</strong> escolha um exemplo de <em>base</em>, preveja o resultado e teste com um colega.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">基</span> <em>jī</em> <span class="tom">· tons 1 · leitura dji</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察基。</span> <em>Guān chá jī.</em> — Observe “Base”.</span></p>
<ol>
<li>Escreva a previsão em uma frase.</li>
<li>Execute ou observe o fenômeno.</li>
<li>Registre a diferença e uma possível explicação.</li>
</ol>
<p><strong>O que observar:</strong> não basta acertar; é preciso explicar por que acertou.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Esfera de Bloch — Mede Z e X do estado H|0⟩.</p>
<p><strong>Simulado:</strong> ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1)<br>
<strong>Backend:</strong> ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1)<br>
<strong>Sobreposição:</strong> 98,9% · <strong>task:</strong> 9da79d10</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E16 · Guoji08 · <a href="#oficina-e16">oficina E16</a> · <a href="#codigo-e16">código E16</a> <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> ⟨Z⟩ = (N₀−N₁)/N; ⟨X⟩ = (N₀−N₁)/N na base X.<br><strong>Conta:</strong> Z: (530−494)/1024=0,0352; X: (1016−8)/1024=0,9844.<br><strong>Resultado:</strong> ⟨Z⟩=+0,035; ⟨X⟩=+0,984.<br><em>Limite:</em> O estado é aproximadamente |+⟩; a pequena componente Z é erro.</span></p>
</div>


</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>Bases diferentes não são 'ângulos' da mesma foto; são perguntas diferentes.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue explicar por que medir na base errada dá ruído?</p>
</div>

<div class="rodape">P01 · C006/100 · L2054/3000 · <a class="gab" href="#g-006">[G006]</a> · <a class="ficha-link" href="#f-006">[F006]</a></div>
:::
