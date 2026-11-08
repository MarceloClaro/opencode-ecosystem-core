::: {.lauda .lente-laboratorio .nivel-2}
<div class="topo">
  <span class="cod">L2084</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C009.png" alt=""> N2 · C009 · EMARANHAMENTO</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2084" class="titulo">Emaranhamento — laboratório</h2>
<div class="corpo">

<p>O mesmo GHZ de 4 qubits foi enviado a dois backends supercondutores. Compare as populações: a fidelidade proxy muda com o backend, e mais qubits não garantem melhor resultado.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">纠缠</span> <em>jiū chán</em> <span class="tom">· tons 1-2 · leitura djiu-tchan</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察纠缠。</span> <em>Guān chá jiū chán.</em> — Observe “Emaranhamento”.</span></p>

<table class="dados">
<tr><th>Resultado</th><th>Guoji08 (20 q)</th><th>Baihua (156 q)</th></tr>
<tr><td>|0000⟩</td><td>418</td><td>437</td></tr><tr><td>|1111⟩</td><td>389</td><td>230</td></tr><tr><td>outros</td><td>217</td><td>357</td></tr>
<tr><td><strong>fidelidade proxy</strong></td><td><strong>78,8%</strong></td>
<td><strong>65,1%</strong></td></tr>
</table>
<p class="mini">Mais qubits não significa menos ruído: calibração, acoplamento e
mapeamento importam. O Baihua tem 156 qubits e fidelidade proxy menor que o
Guoji08, de 20 qubits. <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> Fidelidade proxy = (N₀₀ + N₁₁)/N.<br><strong>Conta:</strong> (484+480)/1024 = 964/1024 = 0,9414.<br><strong>Resultado:</strong> 94,14%; 60 tiros em 01/10.<br><em>Limite:</em> A proxy não mede fase nem pureza; é uma soma de populações.</span></p>

<figure class="fig"><img class="fig-pequena" src="../livro/figuras_geradas/fig16_backends.png" alt="GHZ de 4 qubits em dois backends: Guoji08 (20 q) e Baihua (156 q)."><figcaption>GHZ de 4 qubits em dois backends: Guoji08 (20 q) e Baihua (156 q).</figcaption></figure>

</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>As luvas têm valores escondidos; o emaranhamento não é explicado por variáveis locais.</p>
<p class="prof"><strong>Para pesquisa:</strong> repita com outra seed/backend.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue explicar por que a marginal de Bob é 50/50?</p>
</div>

<div class="rodape">P01 · C009/100 · L2084/3000 · <a class="gab" href="#g-009">[G009]</a> · <a class="ficha-link" href="#f-009">[F009]</a></div>
:::
