::: {.lauda .lente-laboratorio .nivel-2}
<div class="topo">
  <span class="cod">L2734</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C074.png" alt=""> N2 · C074 · CHECKPOINT</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2734" class="titulo">Checkpoint — laboratório</h2>
<div class="corpo">

<p><strong>Protocolo de bancada:</strong> escolha um exemplo de <em>checkpoint</em>, preveja o resultado e teste com um colega.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">检查点</span> <em>jiǎn chá diǎn</em> <span class="tom">· tons 3-2-3 · leitura djien-tcha-dien</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察检查点。</span> <em>Guān chá jiǎn chá diǎn.</em> — Observe “Checkpoint”.</span></p>
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
<p>A técnica não funciona igual para todos os estudantes.</p>
<p class="prof"><strong>Para pesquisa:</strong> repita com outra seed/backend.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Um checkpoint pode ser usado para excluir em vez de ensinar?</p>
</div>

<div class="rodape">P08 · C074/100 · L2734/3000 · <a class="gab" href="#g-074">[G074]</a> · <a class="ficha-link" href="#f-074">[F074]</a></div>
:::
