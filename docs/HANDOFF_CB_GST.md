# Handoff — CB e GST após auditoria R1125

Data: 2026-11-09. Sem novos jobs de hardware nesta correção.
Spec: `specs/SPEC-935-R1125-cycle-benchmarking-identifiability.md`.

## Resultado que muda o próximo passo

**O desenho somente-CZ com profundidades pares tem posto 9 para 15 taxas.**
Não basta implementar o ajuste ou aumentar shots. A promessa anterior de
extrair 15 taxas dos 150 jobs foi corrigida antes da submissão. A qualificação
"somente-CZ" importa: a matriz completa tem posto 15, o aumento por outros
ciclos é discutido na R1126 e o limite fundamental de aprendibilidade (13/2)
está na R1128, abaixo.

Com L(ρ)=Σ_Q γ_Q(QρQ−ρ), temos

```
f_P = exp(−2 Σ_{Q anticomuta P} γ_Q)
E(P,m) = A_P [sqrt(f_P f_C(P))]^m       (m par; C(P)=CZ P CZ)
y_P = −log(f_eff,P)/2 = D_P γ
```

Há três órbitas unitárias {IZ}, {ZI}, {ZZ} e seis pares:
{IX,ZX}, {IY,ZY}, {XI,XZ}, {YI,YZ}, {XX,YY}, {XY,YX}.
O sinal de conjugação não altera o produto par. Como contraprova, geradores
com apenas γ_XI=a ou apenas γ_XZ=a produzem os mesmos decaimentos pares.
São dois modelos físicos distintos e não negativos. Pseudoinversa e NNLS
selecionariam uma solução por hipótese, não por identificação experimental.

### Aumento de posto (R1126)

A matriz de anticomutação completa tem **posto 15**; o posto 9 é específico da
média por órbitas do CZ. Sob a hipótese de que o **mesmo gerador** (ou um
conjugado por transformação conhecida) governa todos os ciclos, acrescentar um
Clifford adequado pode elevar o posto a 15. Exemplo determinístico: CZ + um
Clifford aleatório de semente 0 tem posto 15 e condição 15,45. A escolha
importa: a semente 1, nas mesmas condições, não passa do posto 9.

A hipótese é o elemento decisivo, não um detalhe. A identidade também dá posto
15, mas não é um ciclo físico comparável ao CZ. Se cada ciclo tiver seu próprio
gerador, há `15k` incógnitas e apenas `9k` combinações independentes: o défice
é `6k`, e nenhum número de ciclos resolve. Submodelos restritos são
identificáveis apenas sob hipótese adicional: taxas locais, posto 6; taxas de
dois qubits, posto 9; ambos exigem que as demais taxas sejam nulas.

Conclusão prática: acrescentar ciclos sem justificar fisicamente o gerador
compartilhado apenas desloca a suposição. O artefato está em
`harnesses/quantum-error-mitigation/resultados/r1126_rank_audit/`.

### Aprendibilidade (R1128) — correção do posto 9

Chen et al. (2023), *The learnability of Pauli noise* (Nat. Commun. 14, 52,
DOI `10.1038/s41467-022-35759-4`), provam que o espaço de funções aprendíveis
de um Clifford de 2 qubits é o **espaço de ciclos** do grafo de transferência
de padrões, e o não aprendível é o **espaço de cortes**. Para o CZ:

```
E = 15 arestas, V = 4 vértices, c = 2 componentes
aprendível = E − V + c = 13
não aprendível = V − c = 2
```

O posto 9 do desenho de médias de órbita **não é o limite fundamental**: é o
subespaço de 9 das 13 funções aprendíveis. Faltam 4 funções, que exigem
**Cliffords de 1 qubit intercalados** para mapear o Pauli de volta ao mesmo
padrão de peso (a Fig. 1(b) do artigo). As 2 funções de corte exigem hipótese
adicional (preparação perfeita, GST ou restrição física) e não são medidas pelo
CB padrão. Portanto, PEC 2q continua bloqueado, mas o próximo desenho tem um
alvo bem definido: 13 funções, não 15, e não 9.

Artefato: `harnesses/quantum-error-mitigation/resultados/r1128_learnability/`.
Dossiê: `docs/LITERATURA_APRENDIZABILIDADE_R1128.md`.

### Implementação R1129

O desenho com **7 ciclos individuais + 6 produtos de pares** foi implementado
em `quantum_mitigation/interleaved_cb.py`. A matriz 13×15 tem posto 13 e
nulidade 2; a simulação exata (ruído de Pauli antes do CZ, correções ideais)
recupera as 13 funções com erro máximo `3,33×10⁻¹⁶`. As 2 funções de corte não
são medidas.

Isso valida o desenho, não o hardware: não há twirl de Pauli, as correções de
1 qubit são ideais e o caminho GJQ atual aplica ruído depois do CZ. Artefato:
`harnesses/quantum-error-mitigation/resultados/r1129_interleaved/`; relatório:
`docs/RELATORIO_CB_R1129.md`.

### Twirl/frame, ruído e pré-registro (R1130)

`cycle_body_framed` registra os frames de twirl por CZ; `simulate_expectation`
aceita `twirl`, `seed` e `correction_rate`. A depolarização 1q após cada
correção degrada o erro: 0,005 → erro máximo `1,29×10⁻²`; 0,010 → `2,57×10⁻²`.
O ajuste ainda retorna 13/13, mas **13/13 ajustes não é 13/13 precisão**.

O pré-registro local planeja 325 jobs (13 funções × 5 profundidades × 5 seeds),
4.096 shots/job e 1.331.200 shots; `hardware_submission_allowed=False` e
`analysis_allowed=False`. Artefato:
`harnesses/quantum-error-mitigation/resultados/r1130_twirl_noise/`; relatório:
`docs/RELATORIO_R1130.md`.

### Contraprova Lean (R1131)

`lean/quantum-cb/QuantumCB.lean` formaliza em Lean 4 core: `D` (13×15) tem
inversa à direita `R` (15×13); `B` e `C` anulam `D`; as 2 linhas de corte são
independentes; `7+6=13`, `15−4+2=13`, `4−2=2`. Compila com `lean
QuantumCB.lean`. As identidades matriciais usam `native_decide` (axioma de
avaliação nativa); as contagens são livres de axiomas adicionais. O Lean não
prova o canal quântico, a simulação, o twirl ou o hardware. Relatório:
`docs/RELATORIO_LEAN_R1131.md`.

### Rotas de desbloqueio (R1132–R1134)

- **PEC 2q / 2 cortes:** a rota é GSPN/MLCB com gauge autoconsistente
  (Chen et al. 2026, DOI `10.1103/1pnv-t9px`; Calzona et al. 2026, DOI
  `10.1103/4hbl-hpl3`; Chen et al. 2026, DOI `10.1103/69wc-gzl6`). A auditoria
  `solution_audit.py` mostra que as 13 funções são invariantes ao corte,
  enquanto as 15 fidelidades mudam. Isso é gauge; não é PEC desbloqueado.
- **ZNE:** LRE (Russo & Mari 2024, DOI `10.1103/PhysRevA.110.062420`) substitui
  a escala global monotônica por escalas por camada. No modelo multilinear,
  recupera o zero-ruído com erro `< 1e-12`; não valida o Baihua.
- **Layouts:** desenho pareado randomizado, `n` por aproximação normal e r1
  como covariável. Pares diferentes sem randomização são bloqueados por
  confundimento.
- **Mathlib:** `MathlibCounterproof.lean` compilou com `lake env lean`,
  retorno 0. `rank_D` usa `Matrix.rank`; as identidades finitas usam
  `native_decide` (338 axiomas nativos em `D_mul_R`). A contraprova leve
  continua em Lean 4 core; nenhuma das duas prova o canal ou o hardware.

Relatório: `docs/SOLUCOES_BLOQUEIOS_R1132.md`.

### Compilação/layout e roteador (R1137–R1138)

O `gjq_client` envia o QASM original (`qasm2.dumps(circuit)`) e o serviço
compila; `measure-position` é removido para não-MPS. O layout físico não é
devolvido. `compilation_audit.py` pré-transpila com `initial_layout` explícito
e verifica `final_index_layout`, qubits ativos e QASM; identidade preserva
106/107 e uma troca é detectada por `identity_preserved=False`. O teste usa
backend genérico, não o Baihua. O teste controlado de `compile=False` (R1140)
foi pré-registrado com 1 job/4.096 shots, mas ficou **blocked** antes da
submissão por `Failed to fetch machine config for Baihua`; nenhum task ID foi
criado. Ver `docs/TESTE_COMPILE_FALSE_R1140.md`.

`gate_router.py --gate pec_2q|zne|layout|cuts` devolve rota, campos de
evidência e fontes; sem evidência, fail-closed. Relatório REA:
`docs/REA_COMPILACAO_R1137.md`.

## O que está implementado e testado localmente

- `quantum_mitigation/cycle_benchmarking.py`: circuitos pares, paridade,
  ajuste E=A f_eff^m, IC condicional de shots, teste de posto e inversão
  de espectro **completo**. Rejeita canal incompatível com gerador não negativo.
- `harnesses/quantum-error-mitigation/cb_protocol.py`: manifesto, simulação
  e análise offline, hashes de QASM, ordem por seed e arquivos sem sobrescrita.
- `tests/test_r1125_cycle_benchmarking.py`: contraprovas, oráculo independente
  por superoperador, indistinguibilidade XI/XZ, domínio e proveniência.
- `quantum_mitigation/cb_rank_bounds.py` e `tests/test_r1126_cb_rank_bounds.py`:
  posto da matriz completa, órbitas do CZ, aumento por ciclos, geradores
  separados e submodelos. Nada executa hardware.
- Artefatos em `harnesses/quantum-error-mitigation/resultados/r1125_simulation/`:
  são **sintéticos**, com taxas injetadas declaradas. Não são dados GJQ.
- `harnesses/quantum-error-mitigation/resultados/r1126_rank_audit/`: auditoria
  de posto, também sem dados de hardware.
- `quantum_mitigation/interleaved_cb.py` e
  `tests/test_r1129_interleaved_cb.py`: desenho de 13 funções com correções
  de 1 qubit; recuperação exata em simulação, sem hardware.
- `harnesses/quantum-error-mitigation/resultados/r1129_interleaved/`: auditoria
  do desenho e da recuperação exata.
- `tests/test_r1130_twirl_noise_prereg.py`: twirl/frame, ruído 1q e
  pré-registro.
- `lean/quantum-cb/QuantumCB.lean` e `tests/test_r1131_lean_counterproof.py`:
  contraprova finita em Lean 4 core.
- `lean/quantum-cb/MathlibCounterproof.lean` e
  `tests/test_r1136_mathlib_counterproof.py`: prova Mathlib dedicada,
  compilada com retorno 0; `rank_D` via `Matrix.rank`.
- `harnesses/quantum-error-mitigation/resultados/r1130_twirl_noise/`: ruído
  simulado e pré-registro.
- `quantum_mitigation/lre.py`, `layout_design.py` e `solution_audit.py`:
  rotas LRE, desenho pareado e gauge/GSPN; somente offline.
- `quantum_mitigation/compilation_audit.py` e
  `tests/test_r1137_compilation_audit.py`: auditoria local de `initial_layout`
  e qubits ativos.
- `harnesses/quantum-error-mitigation/gate_router.py` e
  `tests/test_r1138_gate_router.py`: roteamento fail-closed de gates.
- `harnesses/quantum-error-mitigation/solution_audit.py` e
  `tests/test_r1132_solutions.py`: reprodução das rotas.

O piloto usa 15 Paulis × 5 profundidades **0,2,4,8,16** × 2 conjuntos = 150
circuitos, com 4.096 shots sintéticos cada. É revisão do plano, não alteração
retroativa do pré-registro histórico [1,2,4,8,16]. Não constitui autorização
nem proposta suficiente para caracterizar todas as taxas no hardware.

## Limites que permanecem

- Portas locais ideais e canal Pauli estacionário são hipóteses do simulador.
- Sanduíches Pauli compensados não implementam toda a randomização de sinal
  nas fronteiras do protocolo de Erhard. Offsets SPAM podem invalidar A f^m.
- Duas seeds por observável/profundidade não garantem média sobre randomizações.
- ICs são pontuais e condicionais a shots; χ² é diagnóstico heurístico não
  calibrado. Não há certificação de cobertura, sobretudo em fronteiras.
- O ajuste conserva os pontos de cada conjunto; não faz média antes do ajuste.
  Ainda assim, não constitui controle experimental de drift.
- Hashes validam consistência de bytes, não autenticidade de task IDs ou counts.
- Barreiras não comprovam preservação pelo compilador GJQ: exigir circuito
  físico retornado/contrato de compilação antes de medir CZ repetidos.

## Próximo protocolo necessário

1. Definir o alvo: ruído do ciclo vestido ou CZ isolado. Não misturar os dois.
2. O desenho com **Cliffords de 1 qubit intercalados** está implementado
   (R1129), com twirl/frame e ruído simulado das correções (R1130) e
   pré-registro local. Falta auditar a compilação física, o ruído real das
   correções e a estabilidade temporal. As 2 de corte exigem GST, preparação
   perfeita ou restrição física. Se usar aumento por ciclos genéricos,
   justificar fisicamente o gerador compartilhado (ou conjugado) e validar o
   posto conjunto; sem isso, `9k < 15k`.
3. Alternativa: GST autoconsistente do par, respeitando liberdade de gauge.
   GST apenas de q1 não identifica o canal CZ 2q.
4. Pré-registrar randomizações, blocos temporais, offsets/SPAM, shots, poder
   e orçamento do novo desenho. Não dividir processos para contornar quotas.
5. Simular canal conhecido e contraprovas fora do modelo; conferir compilação.
6. Só então executar o desenho revisado com autorização e reavaliar PEC.

Restringir as taxas a erros locais pode tornar um submodelo identificável,
mas é hipótese adicional e não substitui o pedido de 15 taxas gerais.

## GST de q1 e do par

pyGSTi estava ausente na inspeção registrada; não foi instalado nesta rodada.
A receita anterior `StandardGST(target_model='TP')` era não verificada e foi
retirada: TP é parametrização, não substituto do objeto de modelo alvo.
O orçamento de ~100 circuitos também não foi validado e não deve orientar
submissões. Antes de instalar/executar:

- fixar versão/API, gate set, fiduciais, germs e comprimentos;
- verificar completude do desenho, conversão Qiskit e convenções de resultado;
- registrar gauge, alvo de referência, incerteza e solver para diamond norm;
- distinguir estimativa autoconsistente de identificação absoluta de SPAM;
- orçar o conjunto real de circuitos e validar em simulação.

Context7 não localizou pyGSTi nesta consulta e uma URL de API retornou 404;
não apresentar snippets de API como testados.

## Retificações dos resultados anteriores

- RC R1123 **foi executado**: 16 jobs. Sem ganho detectado; não prova equivalência
  nem explica causalmente o resultado. Δ observado = +0,00160156; +0,0018 é
  a média bootstrap legada, com IC [−0,0071,+0,0108], sem pareamento temporal.
- Leitura R1124: todos os três runs usaram calibração **00/11**. Os campos
  `mitigated_tvd_vs_ideal` nos dois novos arquivos não os tornam 4×4.
- As comparações de 4.096 shots ocorreram antes de cumprir os gates e não
  satisfazem R1120. Preservar os dados, classificar como exploratórios e não
  repetir esse desvio. Qubits diferentes são parte do efeito de mapeamento;
  não são motivo universal para proibir comparação.
- Rabi/tomografia não fornecem separação SPAM livre de hipóteses. Mitigação
  de leitura não altera o erro bruto de aquisição/preparação.

## Fontes efetivamente consultadas nesta correção

Erhard et al. (2019), DOI [10.1038/s41467-019-13068-7](https://www.nature.com/articles/s41467-019-13068-7):
texto principal, seção **The CB protocol**, passos 2/3b e equações 3–7.
Comprimentos devem compor a identidade; expectativa e sinal são relevantes;
ciclo vestido inclui ruído local. Discussão final deixa reconstrução geral de
modelo como questão adicional. Suplemento não foi lido nesta rodada.
A dedução posto 9 é local, com contraprova testada e revisão textual de agente;
não é revisão humana nem prova formal Lean.

Chen et al. (2023), DOI
[10.1038/s41467-022-35759-4](https://www.nature.com/articles/s41467-022-35759-4):
texto principal, Teoremas 1–2, Figs. 1–6 e seção de experimentos. Dá o limite
13/2, a noção de espaço de ciclos/cortes e a técnica de Cliffords de 1 qubit
intercalados. A derivação 13/2 foi reproduzida localmente no grafo do CZ.

van den Berg & Wocjan (2024), DOI
[10.22331/q-2024-12-10-1556](https://quantum-journal.org/papers/q-2024-12-10-1556/):
abstract e seções 1–5 (arXiv:2311.15408v4). Rotações Pauli com θ=π/2,
sequências de correção de 1 qubit, seleção de bases por coloração/covering
arrays e NNLS com posto coluna completo. Não foi executado.

Artigos de 2026 vistos apenas na lista de citações e **não lidos**:
`10.1103/69wc-gzl6` (Disambiguating Pauli Noise),
`10.1103/1pnv-t9px` (Self-Consistent Learning) e
`10.1103/4hbl-hpl3` (Multilayer CB). Ficam como leads.

## Gates que continuam fechados

| Etapa | Pendência |
|---|---|
| PEC 2q | modelo identificável, incerteza, validação fora do treino e overhead |
| ZNE | diagnóstico de escalas e extrapolação; monotonicidade não é garantia |
| Layouts | desenho pré-registrado, SPAM/leitura, efeito e drift |
| Superfície | capacidades de controle e decoder em tempo real confirmados |
