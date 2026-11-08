::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1574</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C058.png" alt=""> N1 · C058 · PHASE DAMPING</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1574" class="titulo">Phase damping — laboratório</h2>
<div class="corpo">

<p>Compare o efeito de dois ruídos no mesmo classificador.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">相位阻尼</span> <em>xiàng wèi zǔ ní</em> <span class="tom">· tons 4-4-3-2 · leitura shiang-uei-dzu-ni</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察相位阻尼。</span> <em>Guān chá xiàng wèi zǔ ní.</em> — Observe “Phase damping”.</span></p>

<table class="dados">
<tr><th>Condição</th><th>P(1) em 00</th><th>P(1) em 11</th></tr>
<tr><td>ideal</td><td>0,000</td><td>0,000</td></tr>
<tr><td>phase damping γ=0,05</td><td>0,037</td><td>0,037</td></tr>
<tr><td>depolarizing p=0,05</td><td>0,169</td><td>0,169</td></tr>
<tr><td>depolarizing p=0,20</td><td>0,422</td><td>0,422</td></tr>
</table>
<p class="mini">Phase damping não muda a população Z; depolarização reduz a margem até o limiar.</p>

<p><strong>Conclusão:</strong> phase damping não muda a população Z; depolarização reduz a margem. O tipo de ruído importa. <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> H-X-H deveria devolver |0⟩; P(0)=N₀/N.<br><strong>Conta:</strong> N₀=1016, N=1024: 1016/1024 = 0,9922.<br><strong>Resultado:</strong> P(0)=99,22% (ideal 100%).<br><em>Limite:</em> O ruído de fase não é visível na população Z; ele aparece na coerência.</span></p>

</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>Quatro pontos e 1024 tiros não generalizam. Ruído benéfico é hipótese, não garantia.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Um ruído invisível pode ser ignorado em uma auditoria?</p>
</div>

<div class="rodape">P06 · C058/100 · L1574/3000 · <a class="gab" href="#g-058">[G058]</a> · <a class="ficha-link" href="#f-058">[F058]</a></div>
:::
