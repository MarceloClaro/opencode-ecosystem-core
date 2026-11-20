---
name: pesquisador-universal-marcelo-claro
description: >
  Use para pesquisa científica rigorosa e auditável: busca/download open access,
  revisão sistemática e living review, Evidence Graph, meta-análise, GRADE,
  inferência causal, pesquisa NISQ/quântica, análise de lacunas, métodos híbridos,
  simulação, annealing, QCA, Agent Mesh, Mission Control, replicação federada e
  release reproduzível. MarceloClaro permanece o orquestrador primário do Core.
---

# Pesquisador Universal Marcelo Claro v4.1 — Core Native Bridge

Esta skill registra no OpenCode Ecosystem Core a supercamada científica v4.1.
O Core permanece o kernel/runtime; a supercamada não substitui MetaBus,
Blackboard, AttentionRouter ou SDD/TDD.

## Entrada nativa

```bash
python -m marceloclaro.scientific_lab doctor
python -m marceloclaro.scientific_lab research harvest "tema" --workspace .
python -m marceloclaro.scientific_lab review --help
python -m marceloclaro.scientific_lab synthesis --help
python -m marceloclaro.scientific_lab grade --help
python -m marceloclaro.scientific_lab causal --help
python -m marceloclaro.scientific_lab federation --help
python -m marceloclaro.scientific_lab production --help
python -m integrations.quantum_research catalog
python -m integrations.quantum_research plan  # JSON v1 por stdin
```

`plan` lê JSON v1 de stdin e retorna lacunas e protocolo de pesquisa. A entrada
nunca é executada; não há rede, autenticação, acesso a QPU ou instalação de
dependências.

## Discovery

A bridge procura a instalação completa nesta ordem:

1. `PESQUISADOR_UNIVERSAL_HOME`;
2. `PU_PREFIX/skill`;
3. `~/.local/share/pesquisador-universal/skill`.

A instalação completa continua sendo responsável pelos 88 schemas e 87 testes
da v4.1. A integração Core adiciona apenas a fachada e os testes de contrato da
ponte.

## Invariantes

- `marceloclaro` é o único orquestrador primário.
- ausência da supercamada instalada é reportada como `not_installed`, não sucesso.
- o commit `a5478054...` é baseline auditada, não HEAD obrigatório após merge.
- nenhum score, consenso computacional, GRADE ou estimativa causal possui
  autoridade epistêmica automática.
- `scihub-cli` não faz parte desta integração.

Veja `docs/SCIENTIFIC_LAB_V41.md` e `specs/SPEC-935-R468-pesquisador-universal-v41-core-integration.md`.

## Nota R470 — opt-in restrito desabilitado por omissão

O padrão é `open_science_only`; o resolvedor restrito nasce desligado
(fail-closed) e exige autorização, base legal e evidência com recibo auditável.
Sem opt-in explícito, toda tentativa é negada sem rede nem execução.

## Pesquisa NISQ/quântica e lacunas — R1247

Use `python -m integrations.quantum_research catalog` para consultar métodos e
rótulos; envie um contrato JSON versionado por stdin ao subcomando `plan`. O
planejador cobre baselines clássicos, métodos variacionais híbridos, simulação
clássica, annealing, autômatos celulares quânticos e mitigação de erros. Ele
aponta requisitos ausentes e oferece uma sequência experimental; não escolhe
automaticamente a técnica, não executa solver/simulador, não submete jobs e não
declara vantagem quântica.

### Protocolo obrigatório

1. Delimitar pergunta, classe do problema, objetivo, restrições, dados e
   proveniência; definir métricas, seeds, repetição e critério de parada.
2. Fixar baseline(s) clássicos e orçamento comparável antes de qualquer
   comparação híbrida/quântica. Registrar limites de qubits, shots, memória e
   tempo de simulação, custo de amostragem e fonte de ruído/calibração.
   O snapshot de backends fornecido pelo usuário em 20/11/2026 está listado em
   `docs/QUANTUM_NISQ_TIANGONG_AUDIT.md`; ele é não verificado e não é status live,
   prova de acesso/conta, autorização de job ou elegibilidade para submissão.
3. Para método híbrido, explicitar codificação, ansatz/profundidade,
   otimizador, observáveis, orçamento de medições e hipóteses de execução.
   Simulação statevector/MPS/tensor network deve declarar tamanho, memória,
   aproximação e erro; não confundir simulação com QPU.
4. Para annealing, validar QUBO/Ising e penalidades, conectividade/embedding,
   precisão, escala, cadeia e agenda. Para QCA, formalizar espaço de estados,
   regra local, contorno e validade da evolução; não vincular o rótulo `CA` a
   QCA sem evidência de fonte.
5. Para mitigação de erro, conservar observáveis/resultados crus e baseline não
   mitigado; declarar método, calibração/modelo de ruído, overhead, incerteza e
   condições em que a hipótese de mitigação pode falhar.
6. Tratar `VRP`, `WSA`, `HDR`, `QSS`, `OPC`, `PTO`, `CA`, `RSA`, `ECC` e `SDES`
   como rótulos fornecidos. Sem contrato confirmado, registrar semântica como
   desconhecida e não criar solver por domínio. Reutilizar somente as rotas
   locais existentes, com limites descritos em
   `docs/QUANTUM_NISQ_TIANGONG_AUDIT.md`.

### Roteamento e evidência

- Delegar pelo MarceloClaro aos perfis existentes `quantum-applicability-researcher`
  e `quantum-optimization-researcher`; não editar diretamente cartões gerenciados
  com `allow_edit: false` nem confundir cadastro/roteamento com inferência.
- Usar REA em modo autorizado, conservar Evidence, origem e hashes, separar
  observação estática, inferência e desconhecido. Um endpoint ou string de bundle
  não prova backend nem execução.
- A tentativa REA agregada R1247 excedeu o limite de resposta MCP de 10 MiB;
  não repita o mesmo alvo integral. Recomece por artefatos pequenos ou por view
  retida somente se a ferramenta/schema estiver disponível. Se navegador ou
  executor externo não produzir conteúdo, registrar bloqueio, não sucesso.
- O planejador atual não implementa solver para os rótulos desconhecidos. Cada
  solver posterior precisa de spec e testes próprios, contrato por fonte, baseline
  clássico, casos negativos e autorização separada para qualquer efeito remoto.

Veja `specs/SPEC-935-R1247-nisq-research-planner.md` e
`docs/QUANTUM_NISQ_TIANGONG_AUDIT.md`.
