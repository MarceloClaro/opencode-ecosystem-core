::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1604</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C061.png" alt=""> N1 · C061 · VETOR</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1604" class="titulo">Vetor — laboratório</h2>
<div class="corpo">

<p><strong>Protocolo de bancada:</strong> escolha um exemplo de <em>vetor</em>, preveja o resultado e teste com um colega.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">向量</span> <em>xiàng liàng</em> <span class="tom">· tons 4-4 · leitura shiang-liang</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察向量。</span> <em>Guān chá xiàng liàng.</em> — Observe “Vetor”.</span></p>
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
<p>A matemática é representação; não é o fenômeno. Não confunda o mapa com o território.</p>
<p class="prof"><strong>Para o professor:</strong> A fórmula deve vir depois da intuição; use exemplos numéricos pequenos.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Quem pode visualizar um vetor de 50 qubits?</p>
</div>

<div class="rodape">P07 · C061/100 · L1604/3000 · <a class="gab" href="#g-061">[G061]</a> · <a class="ficha-link" href="#f-061">[F061]</a></div>
:::
