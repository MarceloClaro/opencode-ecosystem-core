::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1694</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C070.png" alt=""> N1 · C070 · FOURIER QUÂNTICO</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1694" class="titulo">Fourier quântico — laboratório</h2>
<div class="corpo">

<p><strong>Protocolo de bancada:</strong> escolha um exemplo de <em>fourier quântico</em>, preveja o resultado e teste com um colega.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">量子傅里叶</span> <em>liàng zǐ fù lǐ yè</em> <span class="tom">· tons 4-3-4-3-4 · leitura liang-dzi-fu-li-ie</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察量子傅里叶。</span> <em>Guān chá liàng zǐ fù lǐ yè.</em> — Observe “Fourier quântico”.</span></p>
<ol>
<li>Escreva a previsão em uma frase.</li>
<li>Execute ou observe o fenômeno.</li>
<li>Registre a diferença e uma possível explicação.</li>
</ol>
<p><strong>O que observar:</strong> não basta acertar; é preciso explicar por que acertou.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> QFT de 3 qubits — A transformada de Fourier quântica uniformiza a saída.</p>
<p><strong>Simulado:</strong> P(000) = 0,117 (ideal 0,125)<br>
<strong>Backend:</strong> P(000) = 0,120 (ideal 0,125)<br>
<strong>Sobreposição:</strong> 95,7% · <strong>task:</strong> 2e281bbe</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E12 · Guoji08 · <a href="#oficina-e12">oficina E12</a> · <a href="#codigo-e12">código E12</a> <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> P(000) = N₀₀₀/N; ideal 1/8 = 0,125.<br><strong>Conta:</strong> N₀₀₀=123, N=1024: 123/1024 = 0,1201.<br><strong>Resultado:</strong> P(000)=12,01% (ideal 12,5%).<br><em>Limite:</em> A QFT uniformiza as probabilidades; a fase não é medida aqui.</span></p>
</div>


</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>A matemática é representação; não é o fenômeno. Não confunda o mapa com o território.</p>
<p class="prof"><strong>Para o professor:</strong> A fórmula deve vir depois da intuição; use exemplos numéricos pequenos.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Algoritmos de fatoração podem ameaçar a privacidade?</p>
</div>

<div class="rodape">P07 · C070/100 · L1694/3000 · <a class="gab" href="#g-070">[G070]</a> · <a class="ficha-link" href="#f-070">[F070]</a></div>
:::
