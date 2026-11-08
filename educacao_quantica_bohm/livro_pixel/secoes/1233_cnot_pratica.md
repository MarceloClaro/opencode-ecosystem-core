::: {.lauda .lente-pratica .nivel-1}
<div class="topo">
  <span class="cod">L1233</span>
  <span class="lente"><img class="ico" src="sprites/pratica.png" alt=""> MÃO NA MASSA</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C024.png" alt=""> N1 · C024 · CNOT</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1233" class="titulo">CNOT — mão na massa</h2>
<div class="corpo">

<p>Aplique H no controle, CNOT e meça os dois qubits.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">受控非门</span> <em>shòu kòng fēi mén</em> <span class="tom">· tons 4-4-1-2 · leitura shou-kong-fei-men</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">练习受控非门。</span> <em>Liàn xí shòu kòng fēi mén.</em> — Pratique “CNOT”.</span></p>
<ol>
<li>Faça a atividade sem pressa, em 5 minutos.</li>
<li>Anote o que esperava antes de começar.</li>
<li>Compare a previsão com o que observou.</li>
</ol>
<p><strong>O que observar:</strong> a diferença entre o que você esperava e o que aconteceu é o dado mais valioso.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Estado de Bell — H + CNOT criam uma correlação 00/11.</p>
<p><strong>Simulado:</strong> P(00)+P(11) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(00)+P(11) = 0,941 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 94,1% · <strong>task:</strong> 705bf99c</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E05 · Guoji08 · <a href="#oficina-e05">oficina E05</a> · <a href="#codigo-e05">código E05</a></p>
</div>


</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>CNOT é a porta de duas entradas que gera o estado de Bell.</p>
<p class="prof"><strong>Para o professor:</strong> Confira a ordem dos qubits e a diferença entre circuito lógico e transpilado.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue listar a tabela verdade do CNOT?</p>
</div>

<div class="rodape">P03 · C024/100 · L1233/3000 · <a class="gab" href="#g-024">[G024]</a> · <a class="ficha-link" href="#f-024">[F024]</a></div>
:::
