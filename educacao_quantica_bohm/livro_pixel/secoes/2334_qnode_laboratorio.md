::: {.lauda .lente-laboratorio .nivel-2}
<div class="topo">
  <span class="cod">L2334</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C034.png" alt=""> N2 · C034 · QNODE</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2334" class="titulo">QNode — laboratório</h2>
<div class="corpo">

<p>No notebook, o código mínimo é:</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">量子节点</span> <em>liàng zǐ jié diǎn</em> <span class="tom">· tons 4-3-2-3 · leitura liang-dzi-djie-dien</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察量子节点。</span> <em>Guān chá liàng zǐ jié diǎn.</em> — Observe “QNode”.</span></p>
<pre><code>@qml.qnode(dev) def circuito(): ...</code></pre>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Interferência de dois qubits — H, CZ e H concentram a distribuição em 00/11.</p>
<p><strong>Simulado:</strong> P(00) = 0,488 (ideal 0,500)<br>
<strong>Backend:</strong> P(00) = 0,474 (ideal 0,500)<br>
<strong>Sobreposição:</strong> 94,3% · <strong>task:</strong> a9be9213</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E11 · Guoji08 · <a href="#oficina-e11">oficina E11</a> · <a href="#codigo-e11">código E11</a></p>
</div>

<p><strong>O que observar:</strong> confira a ordem dos qubits, o número de tiros e a diferença entre estado e amostra. <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> P(00) = N₀₀/N.<br><strong>Conta:</strong> N₀₀=485, N=1024: 485/1024 = 0,4736.<br><strong>Resultado:</strong> P(00)=47,36% (ideal 50%).<br><em>Limite:</em> A interferência de dois qubits concentra a distribuição, mas o ruído espalha.</span></p>
<p>A ficha F034 declara o limite “O QNode não é o hardware; é a descrição executável”; o número não prova essa conclusão sobre QNode.</p>
</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>O QNode não é o hardware; é a descrição executável.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue explicar o papel do dispositivo no QNode?</p>
</div>

<div class="rodape">P04 · C034/100 · L2334/3000 · <a class="gab" href="#g-034">[G034]</a> · <a class="ficha-link" href="#f-034">[F034]</a></div>
:::
