::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1564</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C057.png" alt=""> N1 · C057 · ACURÁCIA</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1564" class="titulo">Acurácia — laboratório</h2>
<div class="corpo">

<p><strong>Protocolo de bancada:</strong> escolha um exemplo de <em>acurácia</em>, preveja o resultado e teste com um colega.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">准确率</span> <em>zhǔn què lǜ</em> <span class="tom">· tons 3-4-4 · leitura djuen-tchyue-lyu</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察准确率。</span> <em>Guān chá zhǔn què lǜ.</em> — Observe “Acurácia”.</span></p>
<ol>
<li>Escreva a previsão em uma frase.</li>
<li>Execute ou observe o fenômeno.</li>
<li>Registre a diferença e uma possível explicação.</li>
</ol>
<p><strong>O que observar:</strong> não basta acertar; é preciso explicar por que acertou.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Classificador XOR (VQC) — Quatro entradas, quatro medições, uma acurácia.</p>
<p><strong>Simulado:</strong> Acurácia = 4/4<br>
<strong>Backend:</strong> Acurácia = 4/4<br>
<strong>Sobreposição:</strong> 95,9% · <strong>task:</strong> —</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E10 · Guoji08 · <a href="#oficina-e10">oficina E10</a> · <a href="#codigo-e10">código E10</a> <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> Predição = 1 se P(1) ≥ 0,5; acurácia = acertos/4.<br><strong>Conta:</strong> P(1): 42/1024=0,041; 990/1024=0,967; 975/1024=0,952; 44/1024=0,043.<br><strong>Resultado:</strong> Predições 0,1,1,0; 4 acertos em 4.<br><em>Limite:</em> Quatro pontos não medem generalização; o teste é pequeno.</span></p>
</div>


</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>Quatro pontos e 1024 tiros não generalizam. Ruído benéfico é hipótese, não garantia.</p>
<p class="prof"><strong>Para o professor:</strong> A acurácia de 4/4 não é generalized accuracy. Explique o teto e o tamanho da amostra.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Uma métrica única pode esconder desigualdades?</p>
</div>

<div class="rodape">P06 · C057/100 · L1564/3000 · <a class="gab" href="#g-057">[G057]</a> · <a class="ficha-link" href="#f-057">[F057]</a></div>
:::
