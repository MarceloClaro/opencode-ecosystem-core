# SPEC-935-R262 — Suíte de agentes PhD para preparação Amazon KDP

## Objetivo

Adicionar ao **OpenCode Ecosystem Core** uma suíte dedicada de agentes especialistas em formatação, validação e entrega de livros para Amazon KDP, cobrindo miolo, capa, ePub, metadados, ISBN, PDF preflight e QA final.

## Escopo

Criar agentes no catálogo oficial do ecossistema (`agents/catalog/`) e regenerar a configuração do OpenCode (`opencode.json`) para que os agentes fiquem disponíveis em sessões futuras.

## Agentes esperados

1. `kdp-orchestrator-phd` — orquestrador editorial KDP end-to-end.
2. `kdp-interior-layout-phd` — especialista em miolo 6x9/trim, margens, sangria e LaTeX/PDF.
3. `kdp-cover-engineer-phd` — especialista em capa completa, lombada, wrap, bleed, barcode e template KDP.
4. `kdp-ebook-epub-phd` — especialista em ePub/KPF, sumário, metadados e navegação digital.
5. `kdp-preflight-auditor-phd` — auditor técnico de PDF: MediaBox, CropBox, fontes, imagens, links, anotações, texto fora de margens.
6. `kdp-metadata-isbn-phd` — especialista em ISBN, ficha catalográfica, copyright, metadados ONIX-like e consistência bibliográfica.
7. `kdp-final-qa-phd` — gate final, checklist de upload e pacote de entrega.

## Critérios de aceitação

1. Todos os arquivos de agentes existem em `agents/catalog/`.
2. Cada agente possui frontmatter válido com `name`, `description`, `model` e `tools`.
3. Cada agente tem instruções operacionais explícitas para Amazon KDP.
4. Cada agente inclui postura anti-overclaim: não prometer aprovação KDP sem validação externa; reportar riscos e evidências.
5. O orquestrador `kdp-orchestrator-phd` roteia tarefas entre os especialistas e exige SDD/TDD/preflight.
6. A regeneração `python3 -m integrations.opencode_cli` conclui sem erro.
7. `opencode.json` passa a conter os 7 novos agentes.
8. `python3 -m marceloclaro.cli doctor` continua sem falhas.
9. O ciclo R262 é registrado no EvolutionRegistry e no MetaBus.

## Fora do escopo

- Publicar automaticamente na Amazon.
- Garantir aprovação KDP sem validação do previewer/portal da Amazon.
- Alterar conteúdo literário do usuário sem instrução explícita.
