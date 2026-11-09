::: {.lauda .lente-laboratorio .nivel-0}
<div class="topo">
  <span class="cod">L0574</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C058.png" alt=""> N0 · C058 · PHASE DAMPING</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-0574" class="titulo">Phase damping — laboratório</h2>
<div class="corpo">

<p>O experimento comparou a simulação com o backend. Veja os números abaixo.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">相位阻尼</span> <em>xiàng wèi zǔ ní</em> <span class="tom">· tons 4-4-3-2 · leitura shiang-uei-dzu-ni</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察相位阻尼。</span> <em>Guān chá xiàng wèi zǔ ní.</em> — Observe “Phase damping”.</span></p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Ruído de fase — H-X-H deveria devolver P(0)=1; o backend perde coerência.</p>
<p><strong>Simulado:</strong> P(0) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(0) = 0,992 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 99,2% · <strong>task:</strong> aae54f46</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E14 · Guoji08 · <a href="#oficina-e14">oficina E14</a> · <a href="#codigo-e14">código E14</a></p>
</div>
<div class="dossie"><span class="rotulo-dossie">DOSSIÊ</span><p>A ficha F058 diz que a evidência é resultado exploratório ou interpretativo; o número não prova “Não há garantia de generalização para outros contextos” (conceito: Phase damping).</p></div><div class="exercicio"><span class="rotulo-dossie">EXERCÍCIO</span><p>Explique com suas palavras por que o resultado não autoriza essa conclusão sobre Phase damping.</p></div>
</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>Amostra pequena não generaliza; 4 pontos não são um artigo.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Um ruído invisível pode ser ignorado em uma auditoria?</p>
</div>

<div class="rodape">P06 · C058/100 · L0574/3000 · <a class="gab" href="#g-058">[G058]</a> · <a class="ficha-link" href="#f-058">[F058]</a></div>
:::
