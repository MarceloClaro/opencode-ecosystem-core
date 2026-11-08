::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1514</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C052.png" alt=""> N1 · C052 · VQC XOR</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1514" class="titulo">VQC XOR — laboratório</h2>
<div class="corpo">

<p>Um classificador de 2 qubits foi treinado no simulador e avaliado no <strong>Guoji08</strong>.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">变分分类器</span> <em>biàn fēn fēn lèi qì</em> <span class="tom">· tons 4-1-1-4-4 · leitura bien-fen-fen-lei-tchi</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察变分分类器。</span> <em>Guān chá biàn fēn fēn lèi qì.</em> — Observe “VQC XOR”.</span></p>

<table class="dados">
<tr><th>Entrada</th><th>Rótulo</th><th>Ideal P(1)</th><th>Backend P(1)</th><th>Acertou?</th></tr>
<tr><td>00</td><td>0</td><td>0,00</td><td>0,041</td><td>sim</td></tr>
<tr><td>01</td><td>1</td><td>1,00</td><td>0,967</td><td>sim</td></tr>
<tr><td>10</td><td>1</td><td>1,00</td><td>0,952</td><td>sim</td></tr>
<tr><td>11</td><td>0</td><td>0,00</td><td>0,043</td><td>sim</td></tr>
</table>
<p class="mini">4/4 acertos em 1024 tiros por entrada. Não é generalized accuracy: são quatro pontos e um teto de 100%. <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> Predição = 1 se P(1) ≥ 0,5; acurácia = acertos/4.<br><strong>Conta:</strong> P(1): 42/1024=0,041; 990/1024=0,967; 975/1024=0,952; 44/1024=0,043.<br><strong>Resultado:</strong> Predições 0,1,1,0; 4 acertos em 4.<br><em>Limite:</em> Quatro pontos não medem generalização; o teste é pequeno.</span></p>

<figure class="fig"><img class="fig-pequena" src="../livro/figuras_geradas/fig13_vqc_xor.png" alt="VQC XOR: ideal, phase damping, depolarização e backend."><figcaption>VQC XOR: ideal, phase damping, depolarização e backend.</figcaption></figure>

</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>Quatro pontos e 1024 tiros não generalizam. Ruído benéfico é hipótese, não garantia.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Um resultado de 100% em 4 pontos pode enganar uma política pública?</p>
</div>

<div class="rodape">P06 · C052/100 · L1514/3000 · <a class="gab" href="#g-052">[G052]</a> · <a class="ficha-link" href="#f-052">[F052]</a></div>
:::
