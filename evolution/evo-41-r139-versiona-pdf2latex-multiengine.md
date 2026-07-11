# R139 — Versionamento do pdf2latex multi-engine + multi-renderer (SPEC-1000)

## Objetivo

Fechar e versionar a frente SPEC-1000 (arquitetura modular do pdf2latex:
engines de extração intercambiáveis + renderizadores LaTeX), que estava
implementada na árvore de trabalho mas **sem testes** — bloqueada pela
disciplina do projeto até ganhar cobertura TDD.

## Contexto

O pipeline PDF→LaTeX evoluiu de monolítico (pdfminer + LaTeXGenerator) para
um sistema com adapters: engines (`builtin`/`docling`/`mineru`) e renderers
(`builtin`/`pandoc`), com registro singleton, auto-seleção e fallback. A
implementação existia mas nenhum teste a cobria — versioná-la sem testes
violaria o SDD/TDD do repositório.

## Mudanças Entregues

1. **`tests/test_r139_pdf2latex_multi_engine.py`** (novo, 15 testes): trava
   os critérios de aceitação da SPEC-1000 na superfície offline e
   determinística — registro/auto-seleção/fallback de engines, dataclasses
   de contrato (`ConversionResult`, `RenderInput`), interfaces abstratas
   (`BaseEngine`/`BaseRenderer` não instanciáveis), engine/renderer builtin
   sempre disponíveis, presença dos templates Pandoc e dos `.bst` ABNT,
   e o CLI `--list-engines`.
2. **`pdf2latex/engine_registry.py`** (novo): registro singleton de engines
   (`register`/`get`/`list`/`best`, `convert_with_best`).
3. **`pdf2latex/engines/`** (novo): `base.py` (`BaseEngine`,
   `ConversionResult`), `builtin.py` (pdfminer + pdftotext + OCR),
   `docling_engine.py` (adapter opcional).
4. **`pdf2latex/renderers/`** (novo): `base.py` (`BaseRenderer`,
   `RenderInput`), `builtin_renderer.py`, `pandoc_renderer.py`.
5. **`pdf2latex/pandoc-templates/`** (novo): `default`/`abntex2`/`ieee`
   `.template` + `.lua` + `abnt.csl`.
6. **`pdf2latex/__init__.py` / `cli.py`**: orquestrador `PDF2LaTeX` com
   seleção de engine/renderer + fallback; flags `--engine`/`--renderer`/
   `--list-engines`.
7. **`pdf2latex/template_integrator.py`**: mapeamento de `bibliographystyle`
   + suporte a `.bst`/`.bib`; **`templates/abntex2/*.bst`+`.bib`** (arquivos
   CTAN do abntex2, licença LPPL — redistribuição aberta).
8. **`specs/SPEC-1000`**: status → "Implementado e versionado (R139)" com
   referência ao arquivo de testes.

## Verificação

- `python3 -m pytest tests/test_r139_pdf2latex_multi_engine.py -q` → 15 passed.
- `python3 -m pytest tests/ -q` completo (zero regressões).

## Lições

1. **Testes de caracterização são honestos para código legado não commitado.**
   A implementação já existia; os 15 testes passam de imediato. Isso não é
   TDD puro (vermelho→verde), mas trava o contrato antes de versionar —
   melhor que versionar sem rede de segurança. O evo declara isso
   explicitamente em vez de fingir um ciclo vermelho→verde.
2. **Testar só a superfície determinística evita flakiness.** docling,
   mineru, pandoc e latexmk são opcionais e variam por ambiente; os testes
   afirmam apenas `is_available() -> bool` e que o builtin (sempre presente)
   funciona, sem hard-assert em dependências externas.
3. **Procedência dos `.bst`:** ao contrário dos scripts cloud externos, os
   `.bst`/`.bib` do abntex2 são arquivos CTAN de licença aberta (LPPL) —
   versioná-los é padrão para repositórios de templates LaTeX.

## Score

**8.1/10**

- Fecha uma frente ampla com cobertura de contrato real e sem flakiness.
- Cobertura é de superfície (registro/contrato/CLI), não de conversão E2E
  de um PDF real — a extração de ponta a ponta permanece não testada aqui.
- Herda os "Próximos Passos" da SPEC-1000 (MinerU/Docling funcionais,
  `--compile`, mais templates) como trabalho futuro.
