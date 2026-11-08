::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1644</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C065.png" alt=""> N1 · C065 · MATRIZ DENSIDADE</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1644" class="titulo">Matriz densidade — laboratório</h2>
<div class="corpo">

<p><strong>Protocolo de bancada:</strong> escolha um exemplo de <em>matriz densidade</em>, preveja o resultado e teste com um colega.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">密度矩阵</span> <em>mì dù jǔ zhèn</em> <span class="tom">· tons 4-4-3-4 · leitura mi-du-djyu-djen</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察密度矩阵。</span> <em>Guān chá mì dù jǔ zhèn.</em> — Observe “Matriz densidade”.</span></p>
<ol>
<li>Escreva a previsão em uma frase.</li>
<li>Execute ou observe o fenômeno.</li>
<li>Registre a diferença e uma possível explicação.</li>
</ol>
<p><strong>O que observar:</strong> não basta acertar; é preciso explicar por que acertou.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Estado de Bell — H + CNOT criam uma correlação 00/11.</p>
<p><strong>Simulado:</strong> P(00)+P(11) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(00)+P(11) = 0,941 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 94,1% · <strong>task:</strong> 705bf99c</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E05 · Guoji08 · <a href="#oficina-e05">oficina E05</a> · <a href="#codigo-e05">código E05</a> <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> Fidelidade proxy = (N₀₀ + N₁₁)/N.<br><strong>Conta:</strong> (484+480)/1024 = 964/1024 = 0,9414.<br><strong>Resultado:</strong> 94,14%; 60 tiros em 01/10.<br><em>Limite:</em> A proxy não mede fase nem pureza; é uma soma de populações.</span></p>
</div>


</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>A matemática é representação; não é o fenômeno. Não confunda o mapa com o território.</p>
<p class="prof"><strong>Para o professor:</strong> A fórmula deve vir depois da intuição; use exemplos numéricos pequenos.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Uma mistura estatística pode esconder responsabilidade?</p>
</div>

<div class="rodape">P07 · C065/100 · L1644/3000 · <a class="gab" href="#g-065">[G065]</a> · <a class="ficha-link" href="#f-065">[F065]</a></div>
:::
