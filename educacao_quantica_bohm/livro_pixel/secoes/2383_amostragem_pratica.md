::: {.lauda .lente-pratica .nivel-2}
<div class="topo">
  <span class="cod">L2383</span>
  <span class="lente"><img class="ico" src="sprites/pratica.png" alt=""> MÃO NA MASSA</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C039.png" alt=""> N2 · C039 · AMOSTRAGEM</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2383" class="titulo">Amostragem — mão na massa</h2>
<div class="corpo">

<p>Rode 100, 1000 e 10000 tiros e compare a flutuação.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">采样</span> <em>cǎi yàng</em> <span class="tom">· tons 3-4 · leitura tsai-iang</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">练习采样。</span> <em>Liàn xí cǎi yàng.</em> — Pratique “Amostragem”.</span></p>
<p><strong>Protocolo:</strong> varie um parâmetro, repita com outra seed e compare.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Amostragem binomial — H + medição; o desvio de P(1) cai com o número de tiros.</p>
<p><strong>Simulado:</strong> P(1) = 0,483 (ideal 0,500)<br>
<strong>Backend:</strong> P(1) = 0,482 (ideal 0,500)<br>
<strong>Sobreposição:</strong> 99,9% · <strong>task:</strong> 54de9107</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E18 · Guoji08 · <a href="#oficina-e18">oficina E18</a> · <a href="#codigo-e18">código E18</a></p>
</div>


</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>A amostra não é o estado; é uma sombra estatística.</p>
<p class="prof"><strong>Para pesquisa:</strong> repita com outra seed/backend.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue explicar por que a frequência flutua?</p>
</div>

<div class="rodape">P04 · C039/100 · L2383/3000 · <a class="gab" href="#g-039">[G039]</a> · <a class="ficha-link" href="#f-039">[F039]</a></div>
:::
