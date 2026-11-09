::: {.lauda .lente-laboratorio .nivel-2}
<div class="topo">
  <span class="cod">L2454</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C046.png" alt=""> N2 · C046 · RUÍDO</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2454" class="titulo">Ruído — laboratório</h2>
<div class="corpo">

<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">噪声</span> <em>zào shēng</em> <span class="tom">· tons 4-1 · leitura dzau-sheng</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察噪声。</span> <em>Guān chá zào shēng.</em> — Observe “Ruído”.</span></p>
<div class="dossie"><span class="rotulo-dossie">DOSSIÊ</span><p>Grau B (evidência experimental ou metodológica com limites); o número não prova “Não há garantia de generalização para outros contextos” (conceito: Ruído). Fonte do protocolo: <a href="https://doi.org/10.22331/q-2018-08-06-79">10.22331/q-2018-08-06-79</a>.</p></div>
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
<p>O resultado de hoje não garante o de amanhã; calibração muda.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Quem decide o nível de ruído aceitável em um serviço público?</p>
</div>

<div class="rodape">P05 · C046/100 · L2454/3000 · <a class="gab" href="#g-046">[G046]</a> · <a class="ficha-link" href="#f-046">[F046]</a></div>
:::
