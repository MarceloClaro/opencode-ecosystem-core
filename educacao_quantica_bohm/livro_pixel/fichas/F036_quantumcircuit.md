::: {.lauda .ficha}
<div class="topo">
  <span class="cod">F036</span>
  <span class="lente">FICHA DE EVIDÊNCIA</span>
  <span class="conc">C036 · QUANTUMCIRCUIT</span>
</div>
<h2 id="f-036" class="titulo">QuantumCircuit — o que a evidência mostra</h2>
<div class="corpo">
<p><strong>Em uma frase:</strong> QuantumCircuit é a estrutura do Qiskit para portas e medições.</p>
<p><strong>Fonte primária:</strong> QISKIT DEVELOPMENT TEAM. <em>Qiskit: An Open-Source Framework for Quantum Computing</em>. Zenodo, 2024. DOI: <a href="https://doi.org/10.5281/zenodo.2573505">10.5281/zenodo.2573505</a>. <span class="mini">(DOI verificado via DataCite em 2026-11-07)</span></p>
<p><strong>O que foi medido:</strong> O Qiskit separa circuito lógico e circuito transpilado.</p>
<p><strong>O que não prova:</strong> O circuito lógico precisa ser transpilado para o hardware.</p>
<p><strong>Prática:</strong> Crie um circuito de 4 qubits e meça todos.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Estado de Bell — H + CNOT criam uma correlação 00/11.</p>
<p><strong>Simulado:</strong> P(00)+P(11) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(00)+P(11) = 0,941 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 94,1% · <strong>task:</strong> 705bf99c</p>
<p class="mini">Sobreposição = semelhança entre as distribuições; não é fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E05 · Guoji08 · oficina E05</p>
</div>

<div class="grau"><strong>Grau de evidência: B</strong> — Ferramentas documentadas; resultados variam com versão e convenção.</div>
<p class="mini"><strong>Para citar:</strong> QISKIT DEVELOPMENT TEAM. <em>Qiskit: An Open-Source Framework for Quantum Computing</em>. Zenodo, 2024. DOI: <a href="https://doi.org/10.5281/zenodo.2573505">10.5281/zenodo.2573505</a>.</p>
<p class="mini"><strong>Leitura complementar:</strong> BERGHOLM, V. et al. <em>PennyLane: Automatic differentiation of hybrid quantum-classical computations</em>. arXiv, 2018. Disponível em: <a href="https://arxiv.org/abs/1811.04968">https://arxiv.org/abs/1811.04968</a>. Acesso em: 7 nov. 2026.</p>
</div>
<div class="rodape">F036/100 · E05 · L3051–L3060</div>
:::
