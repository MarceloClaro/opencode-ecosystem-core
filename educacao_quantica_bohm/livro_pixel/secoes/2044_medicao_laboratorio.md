::: {.lauda .lente-laboratorio .nivel-2}
<div class="topo">
  <span class="cod">L2044</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C005.png" alt=""> N2 · C005 · MEDIÇÃO</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2044" class="titulo">Medição — laboratório</h2>
<div class="corpo">

<p><strong>Protocolo de bancada:</strong> escolha um exemplo de <em>medição</em>, preveja o resultado e teste com um colega.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">测量</span> <em>cè liáng</em> <span class="tom">· tons 4-2 · leitura tse-liang</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察测量。</span> <em>Guān chá cè liáng.</em> — Observe “Medição”.</span></p>
<ol>
<li>Escreva a previsão em uma frase.</li>
<li>Execute ou observe o fenômeno.</li>
<li>Registre a diferença e uma possível explicação.</li>
</ol>
<p><strong>O que observar:</strong> não basta acertar; é preciso explicar por que acertou.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Base |1⟩ e leitura — Prepara |1⟩ e mede; a discrepância é erro de leitura.</p>
<p><strong>Simulado:</strong> P(1) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(1) = 0,986 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 98,6% · <strong>task:</strong> 6018c711</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E02 · Guoji08 · <a href="#oficina-e02">oficina E02</a> · <a href="#codigo-e02">código E02</a> <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> P(1) = N₁/N; erro de leitura ≈ N₀/N.<br><strong>Conta:</strong> N₁=1010, N₀=14, N=1024: 1010/1024 = 0,9863.<br><strong>Resultado:</strong> P(1)=98,63%; 14 leituras erradas = 1,37%.<br><em>Limite:</em> O erro de leitura é uma propriedade do dispositivo, não do estado preparado.</span></p>
</div>


</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>A caixa pode já ter um valor; o qubit não é assim.</p>
<p class="prof"><strong>Para pesquisa:</strong> repita com outra seed/backend.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue explicar por que a ordem das medições importa?</p>
</div>

<div class="rodape">P01 · C005/100 · L2044/3000 · <a class="gab" href="#g-005">[G005]</a> · <a class="ficha-link" href="#f-005">[F005]</a></div>
:::
