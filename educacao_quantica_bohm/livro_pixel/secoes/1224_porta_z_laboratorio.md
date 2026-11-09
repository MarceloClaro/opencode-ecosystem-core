::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1224</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C023.png" alt=""> N1 · C023 · PORTA Z</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1224" class="titulo">Porta Z — laboratório</h2>
<div class="corpo">

<p>No notebook, o código mínimo é:</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">相位门</span> <em>xiàng wèi mén</em> <span class="tom">· tons 4-4-2 · leitura shiang-uei-men</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察相位门。</span> <em>Guān chá xiàng wèi mén.</em> — Observe “Porta Z”.</span></p>
<pre><code>qml.PauliZ(0) · cirq.Z(q0) · qc.z(0)</code></pre>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Interferência H-Z-H — A fase Z inverte a interferência: o resultado vira |1⟩.</p>
<p><strong>Simulado:</strong> P(1) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(1) = 0,986 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 98,6% · <strong>task:</strong> 00a6d70a</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E04 · Guoji08 · <a href="#oficina-e04">oficina E04</a> · <a href="#codigo-e04">código E04</a></p>
</div>

<p><strong>O que observar:</strong> confira a ordem dos qubits, o número de tiros e a diferença entre estado e amostra. <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> H-Z-H devolve |1⟩; P(1) = N₁/N.<br><strong>Conta:</strong> N₁=1010, N=1024: 1010/1024 = 0,9863.<br><strong>Resultado:</strong> P(1)=98,63% (ideal 100%); 14 tiros em 0.<br><em>Limite:</em> A fase Z foi aplicada; o desvio restante é ruído, não uma fase residual.</span></p>
<p>A ficha F023 declara o limite “Z não muda a probabilidade; ela muda o que acontece depois”; o número não prova essa conclusão sobre Porta Z.</p>
</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>Z é diag(1,-1); a fase relativa é o recurso da interferência.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue explicar H→Z→H?</p>
</div>

<div class="rodape">P03 · C023/100 · L1224/3000 · <a class="gab" href="#g-023">[G023]</a> · <a class="ficha-link" href="#f-023">[F023]</a></div>
:::
