::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1534</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C054.png" alt=""> N1 · C054 · ENCODING</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1534" class="titulo">Encoding — laboratório</h2>
<div class="corpo">

<p><strong>Protocolo de bancada:</strong> escolha um exemplo de <em>encoding</em>, preveja o resultado e teste com um colega.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">编码</span> <em>biān mǎ</em> <span class="tom">· tons 1-3 · leitura bien-ma</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察编码。</span> <em>Guān chá biān mǎ.</em> — Observe “Encoding”.</span></p>
<ol>
<li>Escreva a previsão em uma frase.</li>
<li>Execute ou observe o fenômeno.</li>
<li>Registre a diferença e uma possível explicação.</li>
</ol>
<p><strong>O que observar:</strong> não basta acertar; é preciso explicar por que acertou.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Codificação de amplitude — Ry(2π/3) prepara P(1)=0,75.</p>
<p><strong>Simulado:</strong> P(1) = 0,735 (ideal 0,750)<br>
<strong>Backend:</strong> P(1) = 0,743 (ideal 0,750)<br>
<strong>Sobreposição:</strong> 99,2% · <strong>task:</strong> 90f9f88a</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E09 · Guoji08 · <a href="#oficina-e09">oficina E09</a> · <a href="#codigo-e09">código E09</a> <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> Ry(2π/3)|0⟩ = cos(π/3)|0⟩ + sen(π/3)|1⟩; P(1)=sen²(π/3).<br><strong>Conta:</strong> sen²(π/3)=0,75. Medido: 761/1024 = 0,7432.<br><strong>Resultado:</strong> P(1)=74,32% (ideal 75%).<br><em>Limite:</em> A diferença de 0,68 ponto percentual é compatível com 1024 tiros.</span></p>
</div>


</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>Quatro pontos e 1024 tiros não generalizam. Ruído benéfico é hipótese, não garantia.</p>
<p class="prof"><strong>Para o professor:</strong> A acurácia de 4/4 não é generalized accuracy. Explique o teto e o tamanho da amostra.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Dados pessoais podem ser reconstruídos a partir do encoding?</p>
</div>

<div class="rodape">P06 · C054/100 · L1534/3000 · <a class="gab" href="#g-054">[G054]</a> · <a class="ficha-link" href="#f-054">[F054]</a></div>
:::
