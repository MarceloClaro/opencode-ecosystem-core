# Recibo local de validação — SPEC-935-R455

## Escopo

Este recibo registra a atualização documental que separa, no `README.md`, o
**snapshot histórico** do ecossistema e o **diagrama operacional atual**, além
de restaurar a riqueza informativa multiárea sem converter a documentação em
certificação externa ou inventário absoluto do runtime.

## Ambiente registrado

| Campo | Valor observado |
|---|---|
| Base Git (`git rev-parse HEAD`) | `f3bc7fa` |
| Estado do checkout | working tree com ajustes documentais locais ainda não commitados. |
| Runtime | Python 3.14.4 |
| Plataforma | Linux 6.18.33.2-microsoft-standard-WSL2 |
| Doctor | 17 checks `pass` e 2 `warn` (`scihub-cli` opcional ausente e `litert_lm` indisponível no momento da consulta). |

## Evidência observada

```text
24 passed in 0.77s
```

Os testes documentais validaram que:

- o mapa histórico foi preservado como snapshot documental;
- um diagrama operacional atual separado foi adicionado;
- `README.md` e `ARCHITECTURE.md` seguem consistentes em alto nível;
- a riqueza multiárea do ecossistema voltou a aparecer no `README.md`;
- a redação permaneceu conservadora quanto a limites e validação externa.

## Comandos executados

```bash
python3 -m marceloclaro.cli doctor
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_r455_readme_historico_operacional.py \
  tests/test_r449_readme_release.py \
  tests/test_r127_arch_docs_meticulous.py
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ruff check --select E4,E7,E9,F \
  tests/test_r455_readme_historico_operacional.py
```

## Limites conhecidos

- a documentação continua sendo uma visão técnica de alto nível, não um
  inventário exaustivo de todos os arquivos e fluxos do repositório;
- a presença de um subsistema no diagrama não garante disponibilidade de suas
  dependências externas em qualquer máquina;
- o `doctor` desta rodada ainda reportou avisos para `scihub-cli` opcional e
  indisponibilidade momentânea do supervisor LiteRT-LM.
