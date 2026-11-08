::: {.lauda .lente-laboratorio .nivel-2}
<div class="topo">
  <span class="cod">L2544</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C055.png" alt=""> N2 · C055 · ANSATZ</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2544" class="titulo">Ansatz — laboratório</h2>
<div class="corpo">

<p><strong>Protocolo de bancada:</strong> escolha um exemplo de <em>ansatz</em>, preveja o resultado e teste com um colega.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">拟设</span> <em>nǐ shè</em> <span class="tom">· tons 3-4 · leitura ni-she</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察拟设。</span> <em>Guān chá nǐ shè.</em> — Observe “Ansatz”.</span></p>
<ol>
<li>Escreva a previsão em uma frase.</li>
<li>Execute ou observe o fenômeno.</li>
<li>Registre a diferença e uma possível explicação.</li>
</ol>
<p><strong>O que observar:</strong> não basta acertar; é preciso explicar por que acertou.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Interferência de dois qubits — H, CZ e H concentram a distribuição em 00/11.</p>
<p><strong>Simulado:</strong> P(00) = 0,488 (ideal 0,500)<br>
<strong>Backend:</strong> P(00) = 0,474 (ideal 0,500)<br>
<strong>Sobreposição:</strong> 94,3% · <strong>task:</strong> a9be9213</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E11 · Guoji08 · <a href="#oficina-e11">oficina E11</a> · <a href="#codigo-e11">código E11</a> <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> P(00) = N₀₀/N.<br><strong>Conta:</strong> N₀₀=485, N=1024: 485/1024 = 0,4736.<br><strong>Resultado:</strong> P(00)=47,36% (ideal 50%).<br><em>Limite:</em> A interferência de dois qubits concentra a distribuição, mas o ruído espalha.</span></p>
</div>


</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>O teste é pequeno; não generaliza para outros dados ou modelos.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Quem decide a arquitetura e com base em quê?</p>
</div>

<div class="rodape">P06 · C055/100 · L2544/3000 · <a class="gab" href="#g-055">[G055]</a> · <a class="ficha-link" href="#f-055">[F055]</a></div>
:::
