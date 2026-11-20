# Planejamento NISQ/quântico e auditoria dos rótulos Tiangong

**Estado:** plano de pesquisa local; não é execução de circuito, benchmark ou
confirmação de semântica dos aplicativos.  **Spec:** `SPEC-935-R1247`.

## Evidência disponível e limites

- A aquisição REA R1089 existente contém capturas HTML de raiz para `HDR`,
  `RSIR` e `VRP`, além de bundles JavaScript estáticos. Os três HTML têm o mesmo
  SHA-256 (`8040aca9…73f342`) e 756 bytes; são capturas muito pequenas, não
  prova de que a interface completa foi renderizada.
- Evidência REA: `ev_d4fafa5023de258fbccba21eaec6f8845ddd4302d6467740bdc659f0018808ef`,
  raiz SHA-256 `bfddef3dce8945269bcadd62a18f83ddc11740260ac2f20420e8863f9ad79888`.
  O resumo local contém 28 candidatos de rota e nenhum browser window observado.
  Isso documenta inventário estático; não estabelece backend, comportamento em
  runtime, algoritmo executado ou resultado quântico.
- A reanálise REA mais recente do diretório inteiro não foi entregue pelo MCP:
  `resource_constraint`, pois a resposta excedeu o orçamento stdio de 10 MiB.
  Repetir o mesmo alvo não é plano de recuperação; dividir a investigação por
  artefatos pequenos ou usar exportação/view retida somente quando o transporte
  oferecer a ferramenta e o schema necessários.
- No ciclo atual, fetch direto às dez páginas parou em `robots.txt` HTTP 500 e a
  busca web respondeu HTTP 402. A chamada de browser Antigravity devolveu um
  identificador de tarefa e prompt, sem observação de página; não é evidência de
  execução. Provider de browser REA indisponível neste ambiente.

| Rótulo fornecido | Semântica da página | Captura/localidade hoje | Rota local existente | Decisão segura |
|---|---|---|---|---|
| `VRP` | Não revalidada no browser; manter rótulo sem extrapolar contrato | Captura estática parcial R1089 | `integrations.tiangong_mcp.vrp_handler`: baseline heurístico clássico CVRP | Reutilizar apenas como baseline clássico; sem alegar QAOA ou ótimo |
| `WSA` | Não verificada; não expandir sigla | Ausente do bundle R1089 conhecido | Nenhuma confirmada | Bloquear solver até fonte e contrato |
| `HDR` | Não revalidada no browser | Captura estática parcial R1089 | `integrations.tiangong_mcp.hdr_handler`: validação/pré-processamento; reconhecimento indisponível | Não fabricar classificação ou modelo QNN |
| `QSS` | Não verificada; não expandir sigla | Ausente do bundle R1089 conhecido | Nenhuma confirmada | Bloquear solver até fonte e contrato |
| `OPC` | Não verificada; não expandir sigla | Ausente do bundle R1089 conhecido | Nenhuma confirmada | Bloquear solver até fonte e contrato |
| `PTO` | Não verificada; não expandir sigla | Ausente do bundle R1089 conhecido | Nenhuma confirmada | Bloquear solver até fonte e contrato |
| `CA` | Não verificada; não presumir que signifique autômato celular | Ausente do bundle R1089 conhecido | Nenhuma confirmada | QCA é método candidato separado, não interpretação do rótulo `CA` |
| `RSA` | Não verificada; não expandir sigla | Ausente do bundle R1089 conhecido | Nenhuma confirmada | Não criar solver criptográfico sem contrato, escopo e avaliação de segurança |
| `ECC` | Não verificada; não expandir sigla | Ausente do bundle R1089 conhecido | Nenhuma confirmada | Não criar solver criptográfico sem contrato, escopo e avaliação de segurança |
| `SDES` | Não verificada; não expandir sigla | Ausente do bundle R1089 conhecido | Nenhuma confirmada | Não criar solver criptográfico sem contrato, escopo e avaliação de segurança |

O status “ausente” descreve a aquisição local revisada, não a inexistência de
página, endpoint ou função no serviço remoto. Strings de rota/API em bundle são
candidatos estáticos e não são contratos de execução.

## Métodos que o planejador passa a cobrir

`python -m integrations.quantum_research catalog` lista, sem rede:

1. baselines clássicos adequados à formulação e orçamento;
2. algoritmos variacionais híbridos como candidatos (por exemplo, famílias
   QAOA/VQE), exigindo codificação, otimizador, ruído, shots e comparação justa;
3. simulação clássica de circuito/dinâmica, separando statevector, MPS/redes de
   tensores e simulação ruidosa, com limites de memória/tempo e erro declarados;
4. annealing com validação QUBO/Ising, penalidades, conectividade/embedding,
   escala e agenda;
5. autômatos celulares quânticos como problema teórico independente, com espaço
   de estados, regra local, contorno, evolução e baseline formalizados;
6. mitigação de erro como hipóteses de experimento (calibração de leitura, ZNE,
   PEC ou dynamical decoupling) com dados brutos, overhead, incerteza e baseline
   não mitigado preservados.

O planejador retorna lacunas comuns e específicas de cada método. “Pré-requisito
completo” significa somente que os campos foram declarados pelo operador; não é
checagem independente nem prontidão para hardware. Não recomenda método
automaticamente, não otimiza parâmetros, não transforma lacunas em fatos e não
mede vantagem quântica.

## Rotas locais que já existem

- `integrations.quantum_optimization.qaoa_plan`: valida QUBO, gera representação
  Ising e IR QAOA e compara com enumeração clássica exata até 16 variáveis. IR e
  planejamento não executam circuito em simulador. A rotina remota existente
  continua sujeita a gate de autorização por chamada; este planejador não a chama.
- `integrations.tiangong_mcp.vrp_handler`: baseline clássico heurístico, com
  domínio e limite documentados no handler.
- `integrations.tiangong_mcp.hdr_handler`: validação/pré-processamento local;
  reconhecimento continua `unavailable` quando backend/modelo não observado.
- Não há aqui solver novo de QCA, annealing, WSA, QSS, OPC, PTO, CA, RSA, ECC ou
  SDES. O catálogo metodológico não deve ser confundido com implementação.

## Próxima sequência autorizada e gates

1. Obter evidência primária das páginas restantes por REA/browser com suporte real,
   chamadas de baixo volume e recibos separados. Não autenticar, submeter jobs,
   executar conteúdo do bundle ou repetir análise MCP que excede 10 MiB.
2. Para cada domínio, registrar fonte/hash/localizadores, entradas, saídas,
   objetivo, restrições, variante matemática, dados, casos negativos, baseline e
   critérios de segurança. Rótulo ou rota sozinho não satisfaz esse gate.
3. Abrir spec e testes próprios para cada solver; medir RED antes de código e
   comparar com baseline clássico. O solver deve ser local, determinístico e
   limitado quando a semântica o permitir.
4. Manter QPU, credenciais, instalação de SDKs e jobs remotos fora do escopo até
   consentimento específico por chamada. Declarar explicitamente qualquer
   indisponibilidade ou falha de executor.
