# SPEC-935-R720 — Inventário autônomo dos prontos sem rede nem decisão nova

**Status:** `em implementação`
**Ciclo:** R720→R721
**Data:** 2026-10-07
**Base:** R719 (2 prontas pgmpy/prisma + sympy pendente; clones em /tmp/polymath_clones)

## 1. Problema

O caminho mais eficiente e autônomo não é decidir as 12 restantes nem re-pin
vivo: é extrair todo o valor local dos 2 prontos sem rede, sem subprocesso e
sem nova aprovação — inventário de artefatos com hashes, estrutura e sinais de
maturidade (README, LICENSE, tests, pyproject), cruzado com readiness e
scanner, em relatório único para a futura rotina R621.

## 2. Objetivo

Módulo `integrations/polymath_inventario.py` com `inventariar(clone_path)` e
`relatorio(destino_dir, intencoes_dir, clones_base)` 100% local e determinístico:
top arquivos por tamanho, contagens por extensão, presença de marcos
(`README, LICENSE, pyproject.toml, tests/, docs/`), `sha256` dos marcos,
cruzamento com `readiness.json` e `PolymathLabsScanner`, saída
`relatorio_autonomo.json`. Nenhuma rede, nenhum subprocesso, nenhuma escrita
fora do destino, nenhuma decisão nova.

## 3. Critérios de aceitação

- [ ] AC1 — `inventariar` caminha sem seguir links, ignora `.git`, limita a 5000 arquivos e 500KB por hash; retorna `total_arquivos, total_bytes, top10, extensoes, marcos{presente,bytes,sha256}, head`.
- [ ] AC2 — `relatorio` inclui apenas intenções `avaliado+pronto_para_R621`; pendentes viram seção `nao_prontos` sem falhar; inclui `scanner` com `pin_fresco` do readiness e `gerado_em`.
- [ ] AC3 — Determinístico: duas execuções seguidas geram mesmo `sha256_relatorio` excluindo `gerado_em`.
- [ ] AC4 — Testes herméticos `tests/test_r720_inventario.py`: clone sintético com marcos, extensão de rede proibida no módulo, relatório em tmp com schema.
- [ ] AC5 — Anti-overclaim: `pronto_para_analise_R621`, nunca `federado|verificado`; rótulo `candidato_a_inspecao`.
- [ ] AC6 — Eficiência: opera só nos prontos; sympy e 12 aguardando intactos.

## 4. Fora de escopo (declarado)

- Rede, subprocesso, clone novo, decisão humana, federação, execução de testes do lab.

## 5. Verificação

- `pytest tests/test_r720_inventario.py -q` verde.
- Relatório real em `/tmp/polymath_intencoes_piloto/relatorio_autonomo.json` com 2 prontas inventariadas.
- `doctor` sem novos falhos.
