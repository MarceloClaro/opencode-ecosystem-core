::: {.lauda .ficha}
<div class="topo">
  <span class="cod">F039</span>
  <span class="lente">FICHA DE EVIDÊNCIA</span>
  <span class="conc">C039 · AMOSTRAGEM</span>
</div>
<h2 id="f-039" class="titulo">Amostragem — o que a evidência mostra</h2>
<div class="corpo">
<p><strong>Em uma frase:</strong> Amostrar é repetir preparo e medição para estimar probabilidades.</p>
<p><strong>Fonte primária:</strong> QISKIT DEVELOPMENT TEAM. <em>Qiskit: An Open-Source Framework for Quantum Computing</em>. Zenodo, 2024. DOI: <a href="https://doi.org/10.5281/zenodo.2573505">10.5281/zenodo.2573505</a>. <span class="mini">(DOI verificado via DataCite em 2026-11-07)</span></p>
<p><strong>O que foi medido:</strong> O erro padrão cai com a raiz do número de tiros.</p>
<p><strong>O que não prova:</strong> A amostra não é o estado; é uma sombra estatística.</p>
<p><strong>Prática:</strong> Rode 100, 1000 e 10000 tiros e compare a flutuação.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Amostragem binomial — H + medição; o desvio de P(1) cai com o número de tiros.</p>
<p><strong>Simulado:</strong> P(1) = 0,483 (ideal 0,500)<br>
<strong>Backend:</strong> P(1) = 0,482 (ideal 0,500)<br>
<strong>Sobreposição:</strong> 99,9% · <strong>task:</strong> 54de9107</p>
<p class="mini">Sobreposição = semelhança entre as distribuições; não é fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E18 · Guoji08 · oficina E18</p>
</div>

<div class="grau"><strong>Grau de evidência: B</strong> — Ferramentas documentadas; resultados variam com versão e convenção.</div>
<p class="mini"><strong>Para citar:</strong> QISKIT DEVELOPMENT TEAM. <em>Qiskit: An Open-Source Framework for Quantum Computing</em>. Zenodo, 2024. DOI: <a href="https://doi.org/10.5281/zenodo.2573505">10.5281/zenodo.2573505</a>.</p>
<p class="mini"><strong>Leitura complementar:</strong> BERGHOLM, V. et al. <em>PennyLane: Automatic differentiation of hybrid quantum-classical computations</em>. arXiv, 2018. Disponível em: <a href="https://arxiv.org/abs/1811.04968">https://arxiv.org/abs/1811.04968</a>. Acesso em: 7 nov. 2026.</p>
</div>
<div class="rodape">F039/100 · E18 · L3081–L3090</div>
:::
