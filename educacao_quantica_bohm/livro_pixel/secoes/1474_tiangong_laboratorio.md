::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1474</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C048.png" alt=""> N1 · C048 · TIANGONG</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1474" class="titulo">Tiangong — laboratório</h2>
<div class="corpo">

<p><strong>Protocolo de bancada:</strong> escolha um exemplo de <em>tiangong</em>, preveja o resultado e teste com um colega.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">天宫</span> <em>tiān gōng</em> <span class="tom">· tons 1-1 · leitura tien-gong</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察天宫。</span> <em>Guān chá tiān gōng.</em> — Observe “Tiangong”.</span></p>
<ol>
<li>Escreva a previsão em uma frase.</li>
<li>Execute ou observe o fenômeno.</li>
<li>Registre a diferença e uma possível explicação.</li>
</ol>
<p><strong>O que observar:</strong> não basta acertar; é preciso explicar por que acertou.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> GHZ via QASM 2.0 — O mesmo GHZ carregado de um texto OpenQASM 2.0.</p>
<p><strong>Simulado:</strong> P(0000)+P(1111) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(0000)+P(1111) = 0,788 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 78,8% · <strong>task:</strong> —</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E15 · Guoji08 · <a href="#oficina-e15">oficina E15</a> · <a href="#codigo-e15">código E15</a> <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> O QASM carrega o mesmo GHZ; a proxy é (N₀₀₀₀+N₁₁₁₁)/N.<br><strong>Conta:</strong> (418+389)/1024 = 807/1024 = 0,7881.<br><strong>Resultado:</strong> 78,81%, igual ao GHZ montado no console.<br><em>Limite:</em> O formato QASM não muda o circuito; o backend e a calibração mudam.</span></p>
</div>


</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>Backends têm ruído, calibração e deriva. Fidelidade proxy não é prova de emaranhamento.</p>
<p class="prof"><strong>Para o professor:</strong> T1, T2, erro de leitura e ruído de porta são coisas distintas; não os trate como um número único.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Uma dependência externa pode comprometer a soberania de dados?</p>
</div>

<div class="rodape">P05 · C048/100 · L1474/3000 · <a class="gab" href="#g-048">[G048]</a> · <a class="ficha-link" href="#f-048">[F048]</a></div>
:::
