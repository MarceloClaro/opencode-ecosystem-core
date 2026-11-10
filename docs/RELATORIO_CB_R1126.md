# R1126 — Posto do CB e aumento por ciclos

**Status:** análise linear local, sem hardware.
**Depende de:** R1125.
**Artefato:** `harnesses/quantum-error-mitigation/resultados/r1126_rank_audit/`.

## Resultado

| Desenho | Posto | Leitura |
|---|---:|---|
| Matriz de anticomutação completa | 15 | 15 taxas seriam recuperáveis se todas as fidelidades fossem medidas |
| Somente-CZ, profundidades pares | 9 | 9 combinações independentes; 15 taxas não identificadas |
| CZ + Clifford aleatório (semente 0) | 15 | possível sob gerador compartilhado/conjugado |
| CZ + Clifford aleatório (semente 1) | 9 | a escolha do ciclo importa |
| 3 ciclos com geradores separados | 27 | 45 incógnitas; défice 18; não identificável |
| Submodelo local (6 taxas) | 6 | identificável só se as outras 9 forem nulas |
| Submodelo de dois qubits (9 taxas) | 9 | identificável só se as outras 6 forem nulas |

O posto 9 não é um limite de toda a matriz; é a perda causada pela média nas
órbitas do CZ. Aumentar o desenho com outros Cliffords pode recuperar o posto
15, mas somente se o mesmo gerador (ou um conjugado conhecido) governar todos
os ciclos. A identidade também dá posto 15, o que mostra que a hipótese é o
elemento decisivo — e que ela não é fisicamente gratuita.

## Correção R1128 (ler antes de usar a tabela)

Chen et al. (2023), DOI `10.1038/s41467-022-35759-4`, mostram que o espaço
**aprendível com SPAM twirlado** para um Clifford de 2 qubits tem dimensão
**13**, com **2** graus não aprendíveis (espaço de ciclos vs espaço de cortes).
Para o CZ, o grafo de padrões dá `E=15, V=4, c=2`: 13 aprendíveis, 2 de corte.
O posto 9 é o subespaço medido pelo desenho de médias de órbita; faltam 4
funções, recuperáveis com **Cliffords de 1 qubit intercalados**, não com um
Clifford aleatório de 2 qubits.

As linhas de posto 15 da tabela são inversões matemáticas sob a hipótese de
**gerador compartilhado**; elas não são o espaço aprendível SPAM-robusto e não
autorizam declarar 15 taxas. As 2 funções de corte exigem hipótese adicional
(preparação perfeita, GST ou restrição física).

## Por que isso não libera PEC

- Ciclos aleatórios acrescentam portas e ruído próprio; a existência
  matemática do posto 15 não é um protocolo executado.
- Com um gerador por ciclo, o número de incógnitas cresce mais rápido que o
  número de equações: `9k < 15k`.
- Submodelos locais ou de dois qubits exigem que as demais taxas sejam nulas;
  essa é uma hipótese adicional, não uma medida.
- Nenhuma taxa foi medida; nenhum job foi submetido nesta rodada.

## Caminho prático

Para o espaço aprendível, gerar CB com correções de 1 qubit e validar as 13
funções; as 2 de corte exigem GST, preparação perfeita ou restrição física.
Para um submodelo local, declarar a hipótese e pré-registrar o desenho.
Acrescentar ciclos sem justificar o gerador compartilhado apenas desloca a
suposição. Ver `docs/LITERATURA_APRENDIZABILIDADE_R1128.md`.

## Reprodução

```bash
.venv-quantum/bin/python - <<'PY'
from quantum_mitigation.cb_rank_bounds import audit
import json
print(json.dumps(audit(), indent=2, ensure_ascii=False))
PY
```

Ou:

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/cb_protocol.py rank \
  --out /tmp/opencode/rank.json
```

Testes: `tests/test_r1126_cb_rank_bounds.py`.
