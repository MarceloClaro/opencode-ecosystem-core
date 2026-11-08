::: {.lauda .lente-laboratorio .nivel-2}
<div class="topo">
  <span class="cod">L2844</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C085.png" alt=""> N2 · C085 · CUSTO</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-2844" class="titulo">Custo — laboratório</h2>
<div class="corpo">

<p><strong>Protocolo de bancada:</strong> escolha um exemplo de <em>custo</em>, preveja o resultado e teste com um colega.</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">成本</span> <em>chéng běn</em> <span class="tom">· tons 2-3 · leitura tcheng-ben</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察成本。</span> <em>Guān chá chéng běn.</em> — Observe “Custo”.</span></p>
<ol>
<li>Escreva a previsão em uma frase.</li>
<li>Execute ou observe o fenômeno.</li>
<li>Registre a diferença e uma possível explicação.</li>
</ol>
<p><strong>O que observar:</strong> não basta acertar; é preciso explicar por que acertou.</p>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> Amostragem binomial — H + medição; o desvio de P(1) cai com o número de tiros.</p>
<p><strong>Simulado:</strong> P(1) = 0,483 (ideal 0,500)<br>
<strong>Backend:</strong> P(1) = 0,482 (ideal 0,500)<br>
<strong>Sobreposição:</strong> 99,9% · <strong>task:</strong> 54de9107</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E18 · Guoji08 · <a href="#oficina-e18">oficina E18</a> · <a href="#codigo-e18">código E18</a> <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> P(1)=N₁/N; EP=√(p(1−p)/N).<br><strong>Conta:</strong> N₁=494, N=1024: p=0,4824; EP=√(0,4824×0,5176/1024)=0,0156.<br><strong>Resultado:</strong> P(1)=48,24% ± 1,56% (1 EP).<br><em>Limite:</em> O desvio de 50% é compatível com amostragem; não prova viés do backend.</span></p>
</div>


</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>Não há consenso moral automático; há trade-offs.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Um recurso caro deve ser reservado a que tipo de pergunta?</p>
</div>

<div class="rodape">P09 · C085/100 · L2844/3000 · <a class="gab" href="#g-085">[G085]</a> · <a class="ficha-link" href="#f-085">[F085]</a></div>
:::
