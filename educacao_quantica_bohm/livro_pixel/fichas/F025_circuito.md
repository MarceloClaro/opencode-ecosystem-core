::: {.lauda .ficha}
<div class="topo">
  <span class="cod">F025</span>
  <span class="lente">FICHA DE EVIDÊNCIA</span>
  <span class="conc">C025 · CIRCUITO</span>
</div>
<h2 id="f-025" class="titulo">Circuito — o que a evidência mostra</h2>
<div class="corpo">
<p><strong>Em uma frase:</strong> Um circuito é uma sequência de portas e medições sobre qubits.</p>
<p><strong>Fonte primária:</strong> NIELSEN, M. A.; CHUANG, I. L. <em>Quantum Computation and Quantum Information</em>. Cambridge University Press, 2010. DOI: <a href="https://doi.org/10.1017/CBO9780511976667">10.1017/CBO9780511976667</a>. <span class="mini">(DOI verificado via Crossref em 2026-11-07)</span></p>
<p><strong>O que foi medido:</strong> A profundidade do circuito mede o número de camadas.</p>
<p><strong>O que não prova:</strong> A ordem importa; matrizes não comutam em geral.</p>
<p><strong>Prática:</strong> Desenhe H, CNOT e medição em um papel quadriculado.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Interferência de dois qubits — H, CZ e H concentram a distribuição em 00/11.</p>
<p><strong>Simulado:</strong> P(00) = 0,488 (ideal 0,500)<br>
<strong>Backend:</strong> P(00) = 0,474 (ideal 0,500)<br>
<strong>Sobreposição:</strong> 94,3% · <strong>task:</strong> a9be9213</p>
<p class="mini">Sobreposição = semelhança entre as distribuições; não é fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E11 · Guoji08 · oficina E11</p>
</div>

<div class="grau"><strong>Grau de evidência: A</strong> — Circuitos e algoritmos com tratamento textbook; implementação depende do backend.</div>
<p class="mini"><strong>Para citar:</strong> NIELSEN, M. A.; CHUANG, I. L. <em>Quantum Computation and Quantum Information</em>. Cambridge University Press, 2010. DOI: <a href="https://doi.org/10.1017/CBO9780511976667">10.1017/CBO9780511976667</a>.</p>
<p class="mini"><strong>Leitura complementar:</strong> QISKIT DEVELOPMENT TEAM. <em>Qiskit: An Open-Source Framework for Quantum Computing</em>. Zenodo, 2024. DOI: <a href="https://doi.org/10.5281/zenodo.2573505">10.5281/zenodo.2573505</a>.</p>
</div>
<div class="rodape">F025/100 · E11 · L2041–L2050</div>
:::
