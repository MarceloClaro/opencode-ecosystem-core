::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1414</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C042.png" alt=""> N1 · C042 · QUBIT FÍSICO</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1414" class="titulo">Qubit físico — laboratório</h2>
<div class="corpo">

<p><strong>Protocolo de bancada:</strong> escolha um exemplo de <em>qubit físico</em>, preveja o resultado e teste com um colega.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">物理量子比特</span> <em>wù lǐ liàng zǐ bǐ tè</em> <span class="tom">· tons 4-3-4-3-3-4 · leitura u-li-liang-dzi-bi-te</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察物理量子比特。</span> <em>Guān chá wù lǐ liàng zǐ bǐ tè.</em> — Observe “Qubit físico”.</span></p>
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
<p>Backends têm ruído, calibração e deriva. Fidelidade proxy não é prova de emaranhamento.</p>
<p class="prof"><strong>Para o professor:</strong> T1, T2, erro de leitura e ruído de porta são coisas distintas; não os trate como um número único.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Quem tem acesso ao hardware e quem só vê resultados?</p>
</div>

<div class="rodape">P05 · C042/100 · L1414/3000 · <a class="gab" href="#g-042">[G042]</a> · <a class="ficha-link" href="#f-042">[F042]</a></div>
:::
