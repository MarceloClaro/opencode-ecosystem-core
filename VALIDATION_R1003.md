# VALIDATION R1003 — Data Storytelling Auditável

**Data:** 2026-11-01  
**Spec:** `SPEC-935-R1003`  
**Teste:** `tests/test_r1003_data_storytelling.py`  
**Escopo:** gate local de software; não é validação externa, revisão por
pares ou atestado científico.

## Resultado do gate

| Item | Resultado |
|---|---|
| `SpecVerifier` | 8/8 critérios aprovados |
| `runtime_evidence_valid` | `true` |
| `evidence_contract_valid` | `true` |
| Status | `green` |
| RED | `tdd-55a083df5d284b5d9776879a2cb3f829` |
| GREEN | `tdd-7b523186cb7c4853806a74a06565bdcb` |
| RED counts | 44 testes, 43 falhas por asserção, 1 aprovação, 0 erros |
| GREEN counts | 44 testes, 44 aprovações, 0 falhas, 0 erros |

O RED foi reproduzido por stub de controle sem comportamento (43 falhas
por asserção), porque o primeiro RED real foi `ImportError` com coleta
vazia e o `TDDHistory` exige os mesmos 44 nodeids nas duas fases. O stub
não simula aprovação: ele falha no chamado de cada função; o único teste
que passa no RED é o formatador puro `pt-BR`, que não depende do motor.

## Hashes dos artefatos

| Arquivo | SHA-256 |
|---|---|
| `skills/data_storytelling/__init__.py` | `95d961625795204a67ca78fe0bb916b9a7ca2712a914f391f248e2283d5239b6` |
| `skills/data_storytelling/__main__.py` | `6879541cd7efa737963ffc6ffcdb3122aac525d23964e733d34d5827978a2604` |
| `skills/data_storytelling/util.py` | `88c721f8fa89c68d978155f057e4adcb2007dc8981522d8ba33c28bf475ed896` |
| `skills/data_storytelling/profiling.py` | `dd0ee895848ab7310e8355f7826b7f2cefdea15b6cba968e474381f42bbb26bc` |
| `skills/data_storytelling/rules.py` | `680f7481d50f637ad524fadec2f15b60cfd5f8968ee705d282b79f756ac2a7ba` |
| `skills/data_storytelling/captions.py` | `960794b74c51a6610315624189e470721da37d2ca660cc1aaae9fe0c3ed8c7c3` |
| `skills/data_storytelling/render.py` | `0de72d4d0684a54bf36c2547d71e8e6e7e991532b92c5811c52fe49cc5e05e27` |
| `skills/data_storytelling/manifest.py` | `94dc562ba06182f366aa6d0ebda83dd3cb1b33eb42e887e2a56d2650b71a45e7` |
| `tests/test_r1003_data_storytelling.py` | `1fe963dccd7d0967aa6be651e4a54befd3da8f45561af9b0656905d3df9a4cea` |
| `specs/SPEC-935-R1003-data-storytelling-auditavel.md` | `0c62708a1eaa2b206a078ceb7f4a63db7a8284243cb8b8beda83185604e4b314` |
| `.opencode/skills/data-storytelling-auditavel/SKILL.md` | `5808a88ce7aa02e33e8c35bccca03150b5d110c946b610fdf8a80a259277c5be` |

## Reprodução

```bash
python3 -m pytest tests/test_r1003_data_storytelling.py -q
python3 -m skills.data_storytelling demo --out /tmp/ds_demo
python3 -m skills.data_storytelling audit examples/spec.example.json
```

## Limites

- A aprovação cobre os critérios e os bytes listados; não cobre mérito
  científico, estética, adequação editorial ou causalidade.
- O render embutido cobre `bar` e `line`; os demais tipos exigem
  renderizador externo após a auditoria.
- Regras de legenda são heurísticas declaradas e exigem revisão humana.
