::: {.lauda .ficha}
<div class="topo">
  <span class="cod">F040</span>
  <span class="lente">FICHA DE EVIDÊNCIA</span>
  <span class="conc">C040 · GJQ-CLIENT</span>
</div>
<h2 id="f-040" class="titulo">gjq-client — o que a evidência mostra</h2>
<div class="corpo">
<p><strong>Em uma frase:</strong> gjq-client é o cliente Python da plataforma quântica Guoji/Tiangong.</p>
<p><strong>Fonte primária:</strong> QISKIT DEVELOPMENT TEAM. <em>Qiskit: An Open-Source Framework for Quantum Computing</em>. Zenodo, 2024. DOI: <a href="https://doi.org/10.5281/zenodo.2573505">10.5281/zenodo.2573505</a>. <span class="mini">(DOI verificado via DataCite em 2026-11-07)</span></p>
<p><strong>O que foi medido:</strong> O SDK suporta Sampler, Estimator e Sessões; o servidor MCP gjq-runtime-mcp-server expõe sample_tool e estimate_tool para agentes.</p>
<p><strong>O que não prova:</strong> O cliente não garante acesso; depende de conta, fila e backend.</p>
<p><strong>Prática:</strong> Liste os backends e veja quais são hardware real.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> GHZ via QASM 2.0 — O mesmo GHZ carregado de um texto OpenQASM 2.0.</p>
<p><strong>Simulado:</strong> P(0000)+P(1111) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(0000)+P(1111) = 0,788 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 78,8% · <strong>task:</strong> —</p>
<p class="mini">Sobreposição = semelhança entre as distribuições; não é fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E15 · Guoji08 · oficina E15</p>
</div>

<div class="grau"><strong>Grau de evidência: B</strong> — Ferramentas documentadas; resultados variam com versão e convenção.</div>
<p class="mini"><strong>Para citar:</strong> QISKIT DEVELOPMENT TEAM. <em>Qiskit: An Open-Source Framework for Quantum Computing</em>. Zenodo, 2024. DOI: <a href="https://doi.org/10.5281/zenodo.2573505">10.5281/zenodo.2573505</a>.</p>
<p class="mini"><strong>Leitura complementar:</strong> BERGHOLM, V. et al. <em>PennyLane: Automatic differentiation of hybrid quantum-classical computations</em>. arXiv, 2018. Disponível em: <a href="https://arxiv.org/abs/1811.04968">https://arxiv.org/abs/1811.04968</a>. Acesso em: 7 nov. 2026.</p>
</div>
<div class="rodape">F040/100 · E15 · L3091–L3100</div>
:::
