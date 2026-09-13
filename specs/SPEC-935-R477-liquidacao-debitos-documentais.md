---
spec_id: SPEC-935-R477
title: Liquidação dos débitos documentais remanescentes (release R448 e storytelling MIRA)
component: documentação pública (README, MANUAL, ARCHITECTURE, installers, architecture_map)
test_file: tests/test_r448_documentation_reconciliation.py
status: green
estoque: rc
data: 2026-09-12
---

# SPEC-935-R477 — Liquidação dos débitos documentais remanescentes

## Objetivo
Eliminar os 24 débitos documentais pré-existentes que mantinham a suíte fora do verde desde a release R448, sem alterar contratos de runtime. Escopo: README.md, MANUAL.md, ARCHITECTURE.md, installer/README.md, installer/windows/README.md e docs/architecture_map.html.

## Não-objetivos
- Não alterar comportamento de código nem contratos de runtime (nenhuma mudança fora de documentação).
- Não reescrever a documentação legada nem remover storytelling/MIRA existentes.
- Não promover mérito externo: métricas internas permanecem rotuladas como observadas localmente e **não constituem certificação externa**.

## Invariantes
1. Os 5 DOC_PATHS (README, MANUAL, ARCHITECTURE, installer/README, installer/windows/README) contêm "19 checks", "6 MCPs" e "209 agentes".
2. Nenhum dos 5 DOC_PATHS contém "100%", "production ready" ou "superhuman"; o combined contém "não constituem certificação externa".
3. Instalação pública segue local e revisável: nenhum `curl|wget|irm|invoke-webrequest ... | bash|sh|zsh|iex|powershell|pwsh` nos 5 DOC_PATHS; procedência via ECOSYSTEM_VERSION/ECOSYSTEM_REF/SHA-256/`git checkout --detach`/CommonInstallerSha256.
4. README preserva os marcadores legados de storytelling MIRA: "Presentation On Storytelling", "Act I — A Ilha de Agentes", "R47–R127", "média móvel", "não gate", mínimo de 4 blocos mermaid e menção a "snapshot histórico".
5. README mantém validação observada e sem overclaim: "SPEC-935-R448", "18/18", "3.488 passed", "70 skipped", "execução local", "certificação externa", "WSL2", "não substituem revisão humana", "disponíveis na sua máquina.", sem "superhuman" nem "/home/".
6. MANUAL espelha a CLI canônica (1x `[10]`, sem "imobench", comandos reais); installers usam o venv após criá-lo.

## Critérios de aceitação
- CA1: `tests/test_r448_documentation_reconciliation.py` 6/6 verdes.
- CA2: `tests/test_r449_readme_release.py` verdes (validação observada + marcadores legados + sem pipe de rede).
- CA3: `tests/test_r455_readme_historico_operacional.py` verdes (Mapa v3.9.0, Diagrama Operacional Atual, MIRA, multiárea).
- CA4: `tests/test_r127_arch_docs_meticulous.py`, `test_r236_docs_diagrams_and_storytelling.py`, `test_r237_diagrams_repair.py` verdes (6 estágios, leigo/phd, markers de arquitetura, mermaid).
- CA5: `tests/test_r231_docs_and_storytelling_update.py` e `test_r438_caminho_100.py` verdes (storytelling + anti-overclaim de caminho).
- CA6: Suíte completa verde (0 failed); doctor 18/20 pass, 0 fail.
- CA7: Ciclo R477 registrado no EvolutionRegistry com score e lições; reflexão no MetaBus.

## Plano TDD
RED: 24 falhas documentais pré-existentes (R455 7, R449 5, R127 5, R448 3, R438/R237/R236/R231 1 cada) sobre specs R444–R455. GREEN: edições restritas a documentação — seção observada de validação, marcadores de storytelling legados (Presentation On Storytelling, Act I, R47–R127), remoção de "100%" da tabela de datasets, fluxo `setup.sh` local sem pipe. VERIFY: grupo documental 55/55, suíte completa 3792 passed / 0 failed, doctor limpo; ciclo registrado.