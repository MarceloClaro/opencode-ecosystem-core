::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1094</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C010.png" alt=""> N1 · C010 · ESTADO DE BELL</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1094" class="titulo">Estado de Bell — laboratório</h2>
<div class="corpo">

<p>O estado de Bell é a base do teste CHSH. Quatro configurações foram enviadas ao <strong>Guoji08</strong> (hardware) e repetidas no <strong>FAS-GPU</strong> (simulador GJQ), com 1024 tiros cada.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">贝尔态</span> <em>bèi ěr tài</em> <span class="tom">· tons 4-3-4 · leitura bei-er-tai</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察贝尔态。</span> <em>Guān chá bèi ěr tài.</em> — Observe “Estado de Bell”.</span></p>

<table class="dados">
<tr><th>Configuração</th><th>E ideal</th><th>E Guoji08</th><th>E FAS-GPU</th></tr>
<tr><td>E00</td><td>+0,707</td><td>+0,574</td><td>+0,709</td></tr><tr><td>E01</td><td>+0,707</td><td>+0,576</td><td>+0,703</td></tr><tr><td>E10</td><td>+0,707</td><td>+0,566</td><td>+0,744</td></tr><tr><td>E11</td><td>-0,707</td><td>-0,666</td><td>-0,715</td></tr>
</table>
<p class="mini">S = E00 + E01 + E10 − E11. Guoji08 (hardware): <strong>2,383</strong>. No <strong>FAS-GPU</strong> (simulador GJQ), S = <strong>2,871 ± 0,044</strong>.
Limite clássico 2; ideal quântico 2√2 ≈ 2,828. S > 2 nos dois casos; 2,871 é consistente com 2√2 dentro de ~1 SE. <a href="#apendice-gjq">Apêndice GJQ</a>: contas, task IDs e reprodução. <span class="fn"><strong>NOTA DE CÁLCULO.</strong> E = (N₀₀+N₁₁−N₀₁−N₁₀)/N; S = E₀₀+E₀₁+E₁₀−E₁₁. Guoji08: 2,383. FAS-GPU: 2,871±0,044.</span></p>

<figure class="fig"><img class="fig-pequena fig-mini" src="../livro/figuras_geradas/fig15_chsh.png" alt="CHSH no Guoji08: S ≈ 2,38, acima do limite clássico 2 e abaixo do ideal 2√2."><figcaption>CHSH no Guoji08: S ≈ 2,38, acima do limite clássico 2 e abaixo do ideal 2√2.</figcaption></figure>

</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>O estado de Bell é usado em teleportação e criptografia.</p>
<p class="prof"><strong>Para o professor:</strong> Use a notação de ket apenas depois do concreto; verifique P(0)+P(1)=1.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue listar os quatro estados de Bell?</p>
</div>

<div class="rodape">P01 · C010/100 · L1094/3000 · <a class="gab" href="#g-010">[G010]</a> · <a class="ficha-link" href="#f-010">[F010]</a></div>
:::
