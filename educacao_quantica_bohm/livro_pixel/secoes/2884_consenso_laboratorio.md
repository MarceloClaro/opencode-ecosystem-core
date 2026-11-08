::: {.lauda .lente-laboratorio .nivel-2}
<div class="topo">
  <span class="cod">L2884</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C089.png" alt=""> N2 · C089 · CONSENSO</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2884" class="titulo">Consenso — laboratório</h2>
<div class="corpo">

<p><strong>Protocolo de bancada:</strong> escolha um exemplo de <em>consenso</em>, preveja o resultado e teste com um colega.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">共识</span> <em>gòng shí</em> <span class="tom">· tons 4-2 · leitura gong-shi</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察共识。</span> <em>Guān chá gòng shí.</em> — Observe “Consenso”.</span></p>
<ol>
<li>Escreva a previsão em uma frase.</li>
<li>Execute ou observe o fenômeno.</li>
<li>Registre a diferença e uma possível explicação.</li>
</ol>
<p><strong>O que observar:</strong> não basta acertar; é preciso explicar por que acertou.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> GHZ de 4 qubits — Quatro qubits compartilham 0000/1111.</p>
<p><strong>Simulado:</strong> P(0000)+P(1111) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(0000)+P(1111) = 0,788 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 78,8% · <strong>task:</strong> —</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E06 · Guoji08 · <a href="#oficina-e06">oficina E06</a> · <a href="#codigo-e06">código E06</a> <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> Fidelidade proxy = (N₀₀₀₀ + N₁₁₁₁)/N.<br><strong>Conta:</strong> (418+389)/1024 = 807/1024 = 0,7881.<br><strong>Resultado:</strong> 78,81%; 217 tiros fora de 0000/1111.<br><em>Limite:</em> O GHZ é frágil; a proxy cai rápido com o número de qubits.</span></p>
</div>


</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>Não há consenso moral automático; há trade-offs.</p>
<p class="prof"><strong>Para pesquisa:</strong> repita com outra seed/backend.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Quem tem poder para encerrar a conversa?</p>
</div>

<div class="rodape">P09 · C089/100 · L2884/3000 · <a class="gab" href="#g-089">[G089]</a> · <a class="ficha-link" href="#f-089">[F089]</a></div>
:::
