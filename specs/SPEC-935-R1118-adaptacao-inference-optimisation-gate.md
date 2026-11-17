# SPEC-935-R1118 — Gate de Adaptação Metodológica de Otimização de Inferência

- **Status**: Aprovada para implementação local (após `doctor` estrutural sem falhas).
- **Data**: 2026-11-17.
- **Orquestrador**: `marceloclaro`.
- **Contrato textual antecedente**: `TSPEC-ac314fb5` (verificação apenas de critérios; sem entrega de software e sem validação externa).
- **Motivo do bloqueio resolvido**: `python3 -m marceloclaro.cli doctor` falhava com `ModuleNotFoundError: No module named 'whoosh'`; ambiente local recriado em `/tmp/opencode/rea-whoosh-venv` a partir de `requirements.txt`, com `Whoosh==2.7.4` e demais dependências de runtime. O `doctor` agora reporta `checks_failed: 0` (estado `degraded` apenas por avisos opcionais de CLI/LLM/provedores).

## 1. Contexto e proveniência

Três repositórios externos foram inventariados somente leitura:

| Repositório | ID GitHub | Árvore (commit de leitura) | Natureza observada |
|---|---:|---|---|
| `MarceloClaro/skills` | `1462012681` | `e4bb5d960d87126ff3b3a8af1a104b7db67560ba` | fork de `anthropics/skills`; README descreve Agent Skills; licenças por skill, não uniformes. |
| `MarceloClaro/paper-orchestra` | `1461999883` | `d9bae997e793a015ed38bb1605be9eb58c00284f` | fork; README/headers indicam Google Cloud AI Research e Apache-2.0; exige chaves externas e Conda. |
| `MarceloClaro/inference-optimisation-skill` | `1462014706` | `fda968e7fc1996aa23c67139c755fe541c9d4be0` | fork; README/PROMPT/SKILL descrevem hill-climb local, baseline, teto teórico, A/B, ledger e replay full-context. |

REA 6.8.0 foi usado como auxílio de custódia e delimitação:
- `status`: instalado, `verification: installation_only`.
- `catalog`: 229 ferramentas, hash `c8c839688eb6451fac62560f0904ca07bbc5e621a5d44cca418c27c68b779289`.
- `session`: hash `c000b78103433b921b64c0f318fbb92f260ab054e51114ebd08bdb226a98b25a`.
- `layers`: 18 camadas, 7 prontas; nenhuma camada pronta inspeciona ou corrige dependência Python de código-fonte. `native_ghidra` permanece indisponível (`GHIDRA_INSTALL_DIR`/`JAVA_HOME` ausentes).
- Observação MetaBus REA: `4baf8413-f1e5-4190-a606-2038bb931adc` (persistida, sem promoção de confiança).

## 2. Objetivo

Converter a **metodologia auditável** de `inference-optimisation` em um gate Core-native que:
1. exija proveniência explícita antes de qualquer adoção;
2. impeça cópia de código externo sem licença verificada;
3. exija baseline, métrica, orçamento, holdout e replay full-context;
4. produza relatório determinístico com limitações explícitas;
5. não execute otimização, benchmark, inferência de modelo, rede, instalação ou credenciais.

## 3. Escopo

### Incluído
- Módulo Python puro em `skills/tooling/inference_optimisation_gate.py`.
- Testes unitários em `tests/test_r1118_inference_optimisation_gate.py`.
- Constantes de proveniência com repositórios, IDs, hashes de árvore e natureza de fork.
- Função de avaliação de contrato e renderizador de relatório markdown.
- Guardas estáticos contra importação de rede, subprocess e leitura de variáveis de ambiente.

### Fora de escopo
- Copiar qualquer arquivo dos repositórios externos.
- Executar `paper_orchestra`, scripts Conda, Gemini/OpenAI/Semantic Scholar ou SMTP.
- Rodar hill-climb real, medir latência/throughput/custo ou gerar ledger de desempenho.
- Instalar bibliotecas novas além do ambiente local já criado para `requirements.txt`.
- Declararape, Qualis A1, validação externa, desempenho superior ou causalidade.

## 4. Critérios de aceitação

1. **Importabilidade**: `from skills.tooling.inference_optimisation_gate import ...` funciona no ambiente local.
2. **Proveniência**: constantes incluem os três repos, IDs GitHub, hashes de árvore e `external_code_copied: False`.
3. **Bloqueio de cópia**: contrato com `external_code_copied: True` resulta em `BLOCKED`.
4. **Proveniência incompleta**: ausência de `repo`, `commit` ou `retrieved_at` resulta em `BLOCKED`.
5. **Metodologia mínima**: ausência de `baseline`, `metric`, `budget` ou `holdout` resulta em `BLOCKED`.
6. **Replay integral**: `validation.full_context_replay != True` resulta em `BLOCKED`.
7. **Limitações obrigatórias**: `limitations` deve conter ao menos uma string não vazia e uma declaração de que o gate não comprova desempenho.
8. **Relatório determinístico**: duas chamadas com a mesma entrada produzem texto idêntico e contêm `SPEC-935-R1118`.
9. **Segurança estática**: o código-fonte do módulo não contém `requests`, `urllib`, `subprocess`, `socket`, `os.environ`, `OPENAI_API_KEY`, `GEMINI_API_KEY` nem chamadas de rede.
10. **Ciclo TDD**: testes escritos antes do módulo, executados em RED; implementação executada até GREEN; nenhum teste pulado.
11. **Doctor**: `doctor` permanece com `checks_failed: 0` após a entrega.

## 5. Desenho da interface

```python
SPEC_ID = "SPEC-935-R1118"
PROVENANCE = {...}

def evaluate_adaptation_contract(config: Mapping[str, Any]) -> dict: ...
def render_gate_report(result: Mapping[str, Any]) -> str: ...
```

O resultado de `evaluate_adaptation_contract` terá:
- `status`: `PASS` ou `BLOCKED`;
- `checks`: lista de `{criterion, status, evidence}` com `status` em `PASS`/`BLOCKED`;
- `summary`: contagens de aprovados/bloqueados;
- `spec_id`: `SPEC-935-R1118`.

## 6. Limitações

- A verificação é local, determinística e estática; não é auditoria externa nem revisão por pares.
- Licenças finais dos forks e o upstream exato de `inference-optimisation-skill` permanecem pendentes de confirmação.
- REA não possui camada pronta para código-fonte Python; seu papel aqui foi de custódia, não de reparo.
- O gate não mede desempenho de inferência e não substitui benchmark com dados reais.

## 7. Rastreabilidade

- TSPEC: `TSPEC-ac314fb5`.
- REA observation: `4baf8413-f1e5-4190-a606-2038bb931adc`.
- Ambiente de verificação: `/tmp/opencode/rea-whoosh-venv` (Python 3.12.3, Whoosh 2.7.4, requirements.txt completo).
- Comando de gate: `/tmp/opencode/rea-whoosh-venv/bin/python -m pytest tests/test_r1118_inference_optimisation_gate.py -q`.
- Comando de saúde: `/tmp/opencode/rea-whoosh-venv/bin/python -m marceloclaro.cli doctor`.
