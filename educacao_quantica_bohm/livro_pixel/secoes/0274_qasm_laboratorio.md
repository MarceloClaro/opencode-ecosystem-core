::: {.lauda .lente-laboratorio .nivel-0}
<div class="topo">
  <span class="cod">L0274</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C028.png" alt=""> N0 · C028 · QASM 2.0</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-0274" class="titulo">QASM 2.0 — laboratório</h2>
<div class="corpo">

<p>O experimento comparou a simulação com o backend. Veja os números abaixo.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">量子汇编</span> <em>liàng zǐ huì biān</em> <span class="tom">· tons 4-3-4-1 · leitura liang-dzi-ruei-bien</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察量子汇编。</span> <em>Guān chá liàng zǐ huì biān.</em> — Observe “QASM 2.0”.</span></p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> GHZ via QASM 2.0 — O mesmo GHZ carregado de um texto OpenQASM 2.0.</p>
<p><strong>Simulado:</strong> P(0000)+P(1111) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(0000)+P(1111) = 0,788 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 78,8% · <strong>task:</strong> —</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E15 · Guoji08 · <a href="#oficina-e15">oficina E15</a> · <a href="#codigo-e15">código E15</a></p>
</div>
<div class="dossie"><span class="rotulo-dossie">DOSSIÊ</span><p>A ficha F028 diz que a evidência é definição ou teste consolidado; o número não prova “QASM não é um algoritmo; é uma notação de circuito”.</p></div><div class="exercicio"><span class="rotulo-dossie">EXERCÍCIO</span><p>Explique com suas palavras por que o resultado não autoriza essa conclusão sobre QASM 2.0.</p></div>
</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>Circuito é um modelo; a ordem dos qubits importa.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue validar seu QASM no Qiskit localmente?</p>
</div>

<div class="rodape">P03 · C028/100 · L0274/3000 · <a class="gab" href="#g-028">[G028]</a> · <a class="ficha-link" href="#f-028">[F028]</a></div>
:::
