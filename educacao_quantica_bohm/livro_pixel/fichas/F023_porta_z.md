::: {.lauda .ficha}
<div class="topo">
  <span class="cod">F023</span>
  <span class="lente">FICHA DE EVIDÊNCIA</span>
  <span class="conc">C023 · PORTA Z</span>
</div>
<h2 id="f-023" class="titulo">Porta Z — o que a evidência mostra</h2>
<div class="corpo">
<p><strong>Em uma frase:</strong> Z troca o sinal da amplitude de |1⟩ sem mudar probabilidades isoladas.</p>
<p><strong>Fonte primária:</strong> NIELSEN, M. A.; CHUANG, I. L. <em>Quantum Computation and Quantum Information</em>. Cambridge University Press, 2010. DOI: <a href="https://doi.org/10.1017/CBO9780511976667">10.1017/CBO9780511976667</a>. <span class="mini">(DOI verificado via Crossref em 2026-11-07)</span></p>
<p><strong>O que foi medido:</strong> Z é diag(1,-1); a fase relativa é o recurso da interferência.</p>
<p><strong>O que não prova:</strong> Z não muda a probabilidade; ela muda o que acontece depois.</p>
<p><strong>Prática:</strong> Compare Z(H|0⟩) com H|0⟩ e depois aplique H.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Interferência H-Z-H — A fase Z inverte a interferência: o resultado vira |1⟩.</p>
<p><strong>Simulado:</strong> P(1) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(1) = 0,986 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 98,6% · <strong>task:</strong> 00a6d70a</p>
<p class="mini">Sobreposição = semelhança entre as distribuições; não é fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E04 · Guoji08 · oficina E04</p>
</div>

<div class="grau"><strong>Grau de evidência: A</strong> — Circuitos e algoritmos com tratamento textbook; implementação depende do backend.</div>
<p class="mini"><strong>Para citar:</strong> NIELSEN, M. A.; CHUANG, I. L. <em>Quantum Computation and Quantum Information</em>. Cambridge University Press, 2010. DOI: <a href="https://doi.org/10.1017/CBO9780511976667">10.1017/CBO9780511976667</a>.</p>
<p class="mini"><strong>Leitura complementar:</strong> QISKIT DEVELOPMENT TEAM. <em>Qiskit: An Open-Source Framework for Quantum Computing</em>. Zenodo, 2024. DOI: <a href="https://doi.org/10.5281/zenodo.2573505">10.5281/zenodo.2573505</a>.</p>
</div>
<div class="rodape">F023/100 · E04 · L2021–L2030</div>
:::
