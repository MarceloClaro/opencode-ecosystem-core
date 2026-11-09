::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1504</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C051.png" alt=""> N1 · C051 · GHZ REAL</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1504" class="titulo">GHZ real — laboratório</h2>
<div class="corpo">

<p>O GHZ de 4 qubits foi enviado ao Guoji08 com 1024 tiros.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">实验多体态</span> <em>shí yàn duō tǐ tài</em> <span class="tom">· tons 2-4-1-3-4 · leitura shi-ien-duo-ti-tai</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察实验多体态。</span> <em>Guān chá shí yàn duō tǐ tài.</em> — Observe “GHZ real”.</span></p>

<table class="dados">
<tr><th>Resultado</th><th>Ideal</th><th>Guoji08</th></tr>
<tr><td>|0000⟩</td><td>512</td><td>418</td></tr>
<tr><td>|1111⟩</td><td>512</td><td>389</td></tr>
<tr><td>outros</td><td>0</td><td>217</td></tr>
<tr><td><strong>fidelidade proxy</strong></td><td>100%</td><td><strong>78,8%</strong></td></tr>
</table>

<figure class="fig"><img class="fig-pequena" src="../livro/figuras_geradas/fig12_ghz4_resultados.png" alt="GHZ de 4 qubits no Guoji08: 78,8% de fidelidade proxy; 0000 e 1111 dominam, mas 21,2% ficam fora do ideal."><figcaption>GHZ de 4 qubits no Guoji08: 78,8% de fidelidade proxy; 0000 e 1111 dominam, mas 21,2% ficam fora do ideal.</figcaption></figure>
<p><strong>Baihua (156 q):</strong> 0000=437, 1111=230, outros=357; fidelidade 65,1%. <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> Fidelidade proxy = (N₀₀₀₀ + N₁₁₁₁)/N.<br><strong>Conta:</strong> (418+389)/1024 = 807/1024 = 0,7881.<br><strong>Resultado:</strong> 78,81%; 217 tiros fora de 0000/1111.<br><em>Limite:</em> O GHZ é frágil; a proxy cai rápido com o número de qubits.</span></p>
<p>A ficha F051 declara o limite “Não há garantia de generalização para outros contextos” (conceito: GHZ real); o número não prova essa conclusão sobre GHZ real.</p>
</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>Quatro pontos e 1024 tiros não generalizam. Ruído benéfico é hipótese, não garantia.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Quem deve saber que o resultado tem 21% de erro?</p>
</div>

<div class="rodape">P06 · C051/100 · L1504/3000 · <a class="gab" href="#g-051">[G051]</a> · <a class="ficha-link" href="#f-051">[F051]</a></div>
:::
