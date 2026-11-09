::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1434</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C044.png" alt=""> N1 · C044 · T1 E T2</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1434" class="titulo">T1 e T2 — laboratório</h2>
<div class="corpo">

<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">弛豫与相干</span> <em>chí yù yǔ xiāng gān</em> <span class="tom">· tons 2-4-3-1-1 · leitura tchi-yu-yu-shiang-gan</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察弛豫与相干。</span> <em>Guān chá chí yù yǔ xiāng gān.</em> — Observe “T1 e T2”.</span></p>
<div class="dossie"><span class="rotulo-dossie">DOSSIÊ</span><p>Grau B (evidência experimental ou metodológica com limites); o número não prova “Não há garantia de generalização para outros contextos” (conceito: T1 e T2).</p></div>
<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Ruído de fase — H-X-H deveria devolver P(0)=1; o backend perde coerência.</p>
<p><strong>Simulado:</strong> P(0) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(0) = 0,992 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 99,2% · <strong>task:</strong> aae54f46</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E14 · Guoji08 · <a href="#oficina-e14">oficina E14</a> · <a href="#codigo-e14">código E14</a> <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> H-X-H deveria devolver |0⟩; P(0)=N₀/N.<br><strong>Conta:</strong> N₀=1016, N=1024: 1016/1024 = 0,9922.<br><strong>Resultado:</strong> P(0)=99,22% (ideal 100%).<br><em>Limite:</em> O ruído de fase não é visível na população Z; ele aparece na coerência.</span></p>
</div>


</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>Backends têm ruído, calibração e deriva. Fidelidade proxy não é prova de emaranhamento.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Quem publica esses dados e com que frequência?</p>
</div>

<div class="rodape">P05 · C044/100 · L1434/3000 · <a class="gab" href="#g-044">[G044]</a> · <a class="ficha-link" href="#f-044">[F044]</a></div>
:::
