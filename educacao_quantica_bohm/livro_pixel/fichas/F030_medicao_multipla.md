::: {.lauda .ficha}
<div class="topo">
  <span class="cod">F030</span>
  <span class="lente">FICHA DE EVIDÊNCIA</span>
  <span class="conc">C030 · MEDIÇÃO MÚLTIPLA</span>
</div>
<h2 id="f-030" class="titulo">Medição múltipla — o que a evidência mostra</h2>
<div class="corpo">
<p><strong>Em uma frase:</strong> Medir vários qubits produz um bitstring e uma distribuição.</p>
<p><strong>Fonte primária:</strong> NIELSEN, M. A.; CHUANG, I. L. <em>Quantum Computation and Quantum Information</em>. Cambridge University Press, 2010. DOI: <a href="https://doi.org/10.1017/CBO9780511976667">10.1017/CBO9780511976667</a>. <span class="mini">(DOI verificado via Crossref em 2026-11-07)</span></p>
<p><strong>O que foi medido:</strong> A amostragem tem erro estatístico que diminui com o número de tiros.</p>
<p><strong>O que não prova:</strong> A distribuição não mostra o estado completo; mostra uma amostra.</p>
<p><strong>Prática:</strong> Meça 1000 vezes e compare as frequências com as probabilidades.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Amostragem binomial — H + medição; o desvio de P(1) cai com o número de tiros.</p>
<p><strong>Simulado:</strong> P(1) = 0,483 (ideal 0,500)<br>
<strong>Backend:</strong> P(1) = 0,482 (ideal 0,500)<br>
<strong>Sobreposição:</strong> 99,9% · <strong>task:</strong> 54de9107</p>
<p class="mini">Sobreposição = semelhança entre as distribuições; não é fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E18 · Guoji08 · oficina E18</p>
</div>

<div class="grau"><strong>Grau de evidência: A</strong> — Circuitos e algoritmos com tratamento textbook; implementação depende do backend.</div>
<p class="mini"><strong>Para citar:</strong> NIELSEN, M. A.; CHUANG, I. L. <em>Quantum Computation and Quantum Information</em>. Cambridge University Press, 2010. DOI: <a href="https://doi.org/10.1017/CBO9780511976667">10.1017/CBO9780511976667</a>.</p>
<p class="mini"><strong>Leitura complementar:</strong> QISKIT DEVELOPMENT TEAM. <em>Qiskit: An Open-Source Framework for Quantum Computing</em>. Zenodo, 2024. DOI: <a href="https://doi.org/10.5281/zenodo.2573505">10.5281/zenodo.2573505</a>.</p>
</div>
<div class="rodape">F030/100 · E18 · L2091–L2100</div>
:::
