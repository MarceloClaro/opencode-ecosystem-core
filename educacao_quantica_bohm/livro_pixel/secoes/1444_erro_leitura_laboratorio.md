::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1444</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C045.png" alt=""> N1 · C045 · ERRO DE LEITURA</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1444" class="titulo">Erro de leitura — laboratório</h2>
<div class="corpo">

<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">读取错误</span> <em>dú qǔ cuò wù</em> <span class="tom">· tons 2-3-4-4 · leitura du-tchyu-tsuo-u</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察读取错误。</span> <em>Guān chá dú qǔ cuò wù.</em> — Observe “Erro de leitura”.</span></p>
<p>A ficha F045 declara o limite “Não há garantia de generalização para outros contextos” (conceito: Erro de leitura); o número não prova essa conclusão sobre Erro de leitura.</p>
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
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Um erro sistemático pode prejudicar um grupo específico?</p>
</div>

<div class="rodape">P05 · C045/100 · L1444/3000 · <a class="gab" href="#g-045">[G045]</a> · <a class="ficha-link" href="#f-045">[F045]</a></div>
:::
