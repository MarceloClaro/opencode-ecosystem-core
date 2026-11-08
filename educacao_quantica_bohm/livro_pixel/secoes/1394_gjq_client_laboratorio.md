::: {.lauda .lente-laboratorio .nivel-1}
<div class="topo">
  <span class="cod">L1394</span>
  <span class="lente"><img class="ico" src="sprites/laboratorio.png" alt=""> LABORATÓRIO</span>
  <span class="conc"><img class="ico-conceito" src="sprites_conceitos/C040.png" alt=""> N1 · C040 · GJQ-CLIENT</span>
</div>
<div class="xp"><span class=""></span><span class=""></span><span class=""></span><span class="on"></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span><span class=""></span></div>
<h2 id="l-1394" class="titulo">gjq-client — laboratório</h2>
<div class="corpo">

<p>No notebook, o código mínimo é:</p>
<p class="ponte"><strong>PONTE SONORA · 中文</strong> <span class="termo"><strong>Termo:</strong> <span class="hanzi">量子客户端</span> <em>liàng zǐ kè hù duān</em> <span class="tom">· tons 4-3-4-4-1 · leitura liang-dzi-ke-ru-duan</span>.</span> <span class="frase"><strong>Microfrase:</strong> <span class="hanzi">观察量子客户端。</span> <em>Guān chá liàng zǐ kè hù duān.</em> — Observe “gjq-client”.</span></p>
<pre><code>from gjq_client import GJQRuntimeService; service.list_backends()</code></pre>

<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> GHZ via QASM 2.0 — O mesmo GHZ carregado de um texto OpenQASM 2.0.</p>
<p><strong>Simulado:</strong> P(0000)+P(1111) = 1,000 (ideal 1,000)<br>
<strong>Backend:</strong> P(0000)+P(1111) = 0,788 (ideal 1,000)<br>
<strong>Sobreposição:</strong> 78,8% · <strong>task:</strong> —</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · E15 · Guoji08 · <a href="#oficina-e15">oficina E15</a> · <a href="#codigo-e15">código E15</a></p>
</div>

<p><strong>O que observar:</strong> confira a ordem dos qubits, o número de tiros e a diferença entre estado e amostra. <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br><strong>Fórmula:</strong> O QASM carrega o mesmo GHZ; a proxy é (N₀₀₀₀+N₁₁₁₁)/N.<br><strong>Conta:</strong> (418+389)/1024 = 807/1024 = 0,7881.<br><strong>Resultado:</strong> 78,81%, igual ao GHZ montado no console.<br><em>Limite:</em> O formato QASM não muda o circuito; o backend e a calibração mudam.</span></p>

</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>O SDK suporta Sampler, Estimator e Sessões; o servidor MCP gjq-runtime-mcp-server expõe sample_tool e estimate_tool para agentes.</p>
<p class="prof"><strong>Para o professor:</strong> Compare a mesma grandeza nas três bibliotecas; se divergir, verifique convenção antes de concluir erro.</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>Você consegue listar um backend sem executar um circuito?</p>
</div>

<div class="rodape">P04 · C040/100 · L1394/3000 · <a class="gab" href="#g-040">[G040]</a> · <a class="ficha-link" href="#f-040">[F040]</a></div>
:::
