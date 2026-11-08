::: {.lauda .lente-laboratorio .nivel-2}
<div class="topo">
  <span class="cod">L2074</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C008.png" alt=""> N2 · C008 · INTERFERÊNCIA</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2074" class="titulo">Interferência — laboratório</h2>
<div class="corpo">

<p><strong>Protocolo de bancada:</strong> escolha um exemplo de <em>interferência</em>, preveja o resultado e teste com um colega.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">干涉</span> <em>gān shè</em> <span class="tom">· tons 1-4 · leitura gan-she</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察干涉。</span> <em>Guān chá gān shè.</em> — Observe “Interferência”.</span></p>
<ol>
<li>Escreva a previsão em uma frase.</li>
<li>Execute ou observe o fenômeno.</li>
<li>Registre a diferença e uma possível explicação.</li>
</ol>
<p><strong>O que observar:</strong> não basta acertar; é preciso explicar por que acertou.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Interferência H-Z-H — A fase Z inverte a interferência: o resultado vira |1⟩.</p>
<p><strong>Simulado:</strong> P(1) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(1) = 0,986 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 98,6% · <strong>task:</strong> 00a6d70a</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E04 · Guoji08 · <a href="#oficina-e04">oficina E04</a> · <a href="#codigo-e04">código E04</a> <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> H-Z-H devolve |1⟩; P(1) = N₁/N.<br><strong>Conta:</strong> N₁=1010, N=1024: 1010/1024 = 0,9863.<br><strong>Resultado:</strong> P(1)=98,63% (ideal 100%); 14 tiros em 0.<br><em>Limite:</em> A fase Z foi aplicada; o desvio restante é ruído, não uma fase residual.</span></p>
</div>


</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>A amplitude quântica não é uma vibração material.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue explicar H→H e H→Z→H?</p>
</div>

<div class="rodape">P01 · C008/100 · L2074/3000 · <a class="gab" href="#g-008">[G008]</a> · <a class="ficha-link" href="#f-008">[F008]</a></div>
:::
