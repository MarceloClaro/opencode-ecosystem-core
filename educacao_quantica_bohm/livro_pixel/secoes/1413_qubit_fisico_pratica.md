::: {.lauda .lente-pratica .nivel-1}
<div class="topo">
  <span class="cod">L1413</span>
  <span class="lente"><img class="ico" src="sprites/pratica.png" alt=""> MÃO NA MASSA</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C042.png" alt=""> N1 · C042 · QUBIT FÍSICO</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1413" class="titulo">Qubit físico — mão na massa</h2>
<div class="corpo">

<p>Qubits físicos não são ideais; vários formam um qubit lógico.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">物理量子比特</span> <em>wù lǐ liàng zǐ bǐ tè</em> <span class="tom">· tons 4-3-4-3-3-4 · leitura u-li-liang-dzi-bi-te</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">练习物理量子比特。</span> <em>Liàn xí wù lǐ liàng zǐ bǐ tè.</em> — Pratique “Qubit físico”.</span></p>
<ol>
<li>Faça a atividade sem pressa, em 5 minutos.</li>
<li>Anote o que esperava antes de começar.</li>
<li>Compare a previsão com o que observou.</li>
</ol>
<p><strong>O que observar:</strong> a diferença entre o que você esperava e o que aconteceu é o dado mais valioso.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Base |1⟩ e leitura — Prepara |1⟩ e mede; a discrepância é erro de leitura.</p>
<p><strong>Simulado:</strong> P(1) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(1) = 0,986 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 98,6% · <strong>task:</strong> 6018c711</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E02 · Guoji08 · <a href="#oficina-e02">oficina E02</a> · <a href="#codigo-e02">código E02</a></p>
</div>


</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>Backends têm ruído, calibração e deriva. Fidelidade proxy não é prova de emaranhamento.</p>
<p class="prof"><strong>Para o professor:</strong> T1, T2, erro de leitura e ruído de porta são coisas distintas; não os trate como um número único.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Quem tem acesso ao hardware e quem só vê resultados?</p>
</div>

<div class="rodape">P05 · C042/100 · L1413/3000 · <a class="gab" href="#g-042">[G042]</a> · <a class="ficha-link" href="#f-042">[F042]</a></div>
:::
