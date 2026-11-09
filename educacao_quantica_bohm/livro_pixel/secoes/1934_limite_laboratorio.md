::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1934</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C094.png" alt=""> N1 · C094 · LIMITE</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1934" class="titulo">Limite — laboratório</h2>
<div class="corpo">

<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">局限</span> <em>jú xiàn</em> <span class="tom">· tons 2-4 · leitura djyu-shien</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察局限。</span> <em>Guān chá jú xiàn.</em> — Observe “Limite”.</span></p>
<div class="dossie"><span class="rotulo-dossie">DOSSIÊ</span><p>Grau B (evidência experimental ou metodológica com limites); o número não prova “Não há garantia de generalização para outros contextos” (conceito: Limite).</p></div><div class="exercicio"><span class="rotulo-dossie">EXERCÍCIO</span><p>Explique por que o resultado não autoriza essa conclusão sobre Limite.</p></div>
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
<p>Todo projeto é um recorte. Declare limite, evidência e o que ficou fora.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Quem é prejudicado quando o limite é escondido?</p>
</div>

<div class="rodape">P10 · C094/100 · L1934/3000 · <a class="gab" href="#g-094">[G094]</a> · <a class="ficha-link" href="#f-094">[F094]</a></div>
:::
