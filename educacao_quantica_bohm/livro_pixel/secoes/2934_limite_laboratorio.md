::: {.lauda .lente-laboratorio .nivel-2}
<div class="topo">
  <span class="cod">L2934</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C094.png" alt=""> N2 · C094 · LIMITE</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2934" class="titulo">Limite — laboratório</h2>
<div class="corpo">

<p><strong>Protocolo de bancada:</strong> escolha um exemplo de <em>limite</em>, preveja o resultado e teste com um colega.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">局限</span> <em>jú xiàn</em> <span class="tom">· tons 2-4 · leitura djyu-shien</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察局限。</span> <em>Guān chá jú xiàn.</em> — Observe “Limite”.</span></p>
<ol>
<li>Escreva a previsão em uma frase.</li>
<li>Execute ou observe o fenômeno.</li>
<li>Registre a diferença e uma possível explicação.</li>
</ol>
<p><strong>O que observar:</strong> não basta acertar; é preciso explicar por que acertou.</p>

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
<p>O projeto não esgota o problema; escolhe um recorte.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Quem é prejudicado quando o limite é escondido?</p>
</div>

<div class="rodape">P10 · C094/100 · L2934/3000 · <a class="gab" href="#g-094">[G094]</a> · <a class="ficha-link" href="#f-094">[F094]</a></div>
:::
