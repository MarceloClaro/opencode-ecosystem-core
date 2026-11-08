::: {.lauda .ficha}
<div class="topo">
  <span class="cod">F024</span>
  <span class="lente">FICHA DE EVIDÊNCIA</span>
  <span class="conc">C024 · CNOT</span>
</div>
<h2 id="f-024" class="titulo">CNOT — o que a evidência mostra</h2>
<div class="corpo">
<p><strong>Em uma frase:</strong> CNOT inverte o alvo quando o controle é 1.</p>
<p><strong>Fonte primária:</strong> NIELSEN, M. A.; CHUANG, I. L. <em>Quantum Computation and Quantum Information</em>. Cambridge University Press, 2010. DOI: <a href="https://doi.org/10.1017/CBO9780511976667">10.1017/CBO9780511976667</a>. <span class="mini">(DOI verificado via Crossref em 2026-11-07)</span></p>
<p><strong>O que foi medido:</strong> CNOT é a porta de duas entradas que gera o estado de Bell.</p>
<p><strong>O que não prova:</strong> CNOT não copia um estado quântico arbitrário; ela cria correlação.</p>
<p><strong>Prática:</strong> Aplique H no controle, CNOT e meça os dois qubits.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Estado de Bell — H + CNOT criam uma correlação 00/11.</p>
<p><strong>Simulado:</strong> P(00)+P(11) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(00)+P(11) = 0,941 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 94,1% · <strong>task:</strong> 705bf99c</p>
<p class="mini">Sobreposição = semelhança entre as distribuições; não é fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E05 · Guoji08 · oficina E05</p>
</div>

<div class="grau"><strong>Grau de evidência: A</strong> — Circuitos e algoritmos com tratamento textbook; implementação depende do backend.</div>
<p class="mini"><strong>Para citar:</strong> NIELSEN, M. A.; CHUANG, I. L. <em>Quantum Computation and Quantum Information</em>. Cambridge University Press, 2010. DOI: <a href="https://doi.org/10.1017/CBO9780511976667">10.1017/CBO9780511976667</a>.</p>
<p class="mini"><strong>Leitura complementar:</strong> QISKIT DEVELOPMENT TEAM. <em>Qiskit: An Open-Source Framework for Quantum Computing</em>. Zenodo, 2024. DOI: <a href="https://doi.org/10.5281/zenodo.2573505">10.5281/zenodo.2573505</a>.</p>
</div>
<div class="rodape">F024/100 · E05 · L2031–L2040</div>
:::
