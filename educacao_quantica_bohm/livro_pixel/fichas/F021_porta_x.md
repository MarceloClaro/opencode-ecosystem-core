::: {.lauda .ficha}
<div class="topo">
  <span class="cod">F021</span>
  <span class="lente">FICHA DE EVIDÊNCIA</span>
  <span class="conc">C021 · PORTA X</span>
</div>
<h2 id="f-021" class="titulo">Porta X — o que a evidência mostra</h2>
<div class="corpo">
<p><strong>Em uma frase:</strong> A porta X inverte 0 e 1, como um NOT quântico.</p>
<p><strong>Fonte primária:</strong> NIELSEN, M. A.; CHUANG, I. L. <em>Quantum Computation and Quantum Information</em>. Cambridge University Press, 2010. DOI: <a href="https://doi.org/10.1017/CBO9780511976667">10.1017/CBO9780511976667</a>. <span class="mini">(DOI verificado via Crossref em 2026-11-07)</span></p>
<p><strong>O que foi medido:</strong> X é a matriz [[0,1],[1,0]]; X² = I.</p>
<p><strong>O que não prova:</strong> X não cria superposição; ela apenas troca os estados de base.</p>
<p><strong>Prática:</strong> Aplique X em |0⟩ e em |1⟩ e desenhe as amplitudes.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Base |1⟩ e leitura — Prepara |1⟩ e mede; a discrepância é erro de leitura.</p>
<p><strong>Simulado:</strong> P(1) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(1) = 0,986 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 98,6% · <strong>task:</strong> 6018c711</p>
<p class="mini">Sobreposição = semelhança entre as distribuições; não é fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E02 · Guoji08 · oficina E02</p>
</div>

<div class="grau"><strong>Grau de evidência: A</strong> — Circuitos e algoritmos com tratamento textbook; implementação depende do backend.</div>
<p class="mini"><strong>Para citar:</strong> NIELSEN, M. A.; CHUANG, I. L. <em>Quantum Computation and Quantum Information</em>. Cambridge University Press, 2010. DOI: <a href="https://doi.org/10.1017/CBO9780511976667">10.1017/CBO9780511976667</a>.</p>
<p class="mini"><strong>Leitura complementar:</strong> QISKIT DEVELOPMENT TEAM. <em>Qiskit: An Open-Source Framework for Quantum Computing</em>. Zenodo, 2024. DOI: <a href="https://doi.org/10.5281/zenodo.2573505">10.5281/zenodo.2573505</a>.</p>
</div>
<div class="rodape">F021/100 · E02 · L2001–L2010</div>
:::
