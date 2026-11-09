::: {.lauda .lente-pratica .nivel-1}
<div class="topo">
  <span class="cod">L1573</span>
  <span class="lente"><img class="ico" src="sprites/pratica.png" alt=""> MÃO NA MASSA</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C058.png" alt=""> N1 · C058 · PHASE DAMPING</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1573" class="titulo">Phase damping — mão na massa</h2>
<div class="corpo">

<p>Ele não afeta uma medição Z de um estado já diagonal.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">相位阻尼</span> <em>xiàng wèi zǔ ní</em> <span class="tom">· tons 4-4-3-2 · leitura shiang-uei-dzu-ni</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">练习相位阻尼。</span> <em>Liàn xí xiàng wèi zǔ ní.</em> — Pratique “Phase damping”.</span></p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Ruído de fase — H-X-H deveria devolver P(0)=1; o backend perde coerência.</p>
<p><strong>Simulado:</strong> P(0) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(0) = 0,992 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 99,2% · <strong>task:</strong> aae54f46</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E14 · Guoji08 · <a href="#oficina-e14">oficina E14</a> · <a href="#codigo-e14">código E14</a></p>
</div>
<div class="dossie"><span class="rotulo-dossie">DOSSIÊ</span><p>A ficha F058 registra como medido “A fonte discute o conceito e suas consequências” (conceito: Phase damping).</p></div><div class="exercicio"><span class="rotulo-dossie">EXERCÍCIO</span><p>Repita a prática e explique por que o número não prova “Não há garantia de generalização para outros contextos” (conceito: Phase damping).</p></div>
</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>Quatro pontos e 1024 tiros não generalizam. Ruído benéfico é hipótese, não garantia.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Um ruído invisível pode ser ignorado em uma auditoria?</p>
</div>

<div class="rodape">P06 · C058/100 · L1573/3000 · <a class="gab" href="#g-058">[G058]</a> · <a class="ficha-link" href="#f-058">[F058]</a></div>
:::
