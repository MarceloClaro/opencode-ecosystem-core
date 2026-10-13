---
spec_id: SPEC-935-R862
title: Recusar identidade ambígua no registro de especificações
component: sdd.spec_engine
status: implemented
test_file: tests/test_r862_spec_identity.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    identidade:
    - tests/test_r862_spec_identity.py::test_identidade_duplicada_no_mesmo_diretorio_nao_seleciona_ultima
    - tests/test_r862_spec_identity.py::test_identidade_duplicada_entre_diretorios_nao_sobrescreve
    continuidade:
    - tests/test_r862_spec_identity.py::test_mesmo_arquivo_pode_ser_recarregado
    - tests/test_r862_spec_identity.py::test_remover_duplicata_reabilita_definicao_unica
    - tests/test_r862_spec_identity.py::test_especificacao_dinamica_nao_e_removida
    repositorio:
    - tests/test_r862_spec_identity.py::test_repositorio_nao_tem_ids_formais_duplicados
---

# R862 — Identidade não ambígua de especificações

O registro sobrescrevia silenciosamente specs de mesmo ID. A execução R853
selecionou a reprodução RX em vez do aceite REA e foi rejeitada por erro de
coleção. R852 também colidia com uma spec JEB; R440 tinha duas definições
históricas. Os arquivos próprios foram realocados para R860/R861, preservando
os recibos antigos. R440 recebe IDs completos derivados dos nomes existentes;
o corpo histórico de cada documento permanece intacto.

## Critérios de Aceitação Executáveis

- `identidade` — dois caminhos formais com mesmo ID tornam esse ID indisponível,
  inclusive entre cargas de diretórios diferentes; não há escolha pela ordenação.
- `continuidade` — reler o mesmo caminho atualiza sua definição; remover uma
  duplicata permite reabilitar a definição única; specs dinâmicas são preservadas.
- `repositorio` — o checkout atual não contém IDs formais duplicados. O registro
  publica quais caminhos conflitam para permitir correção explícita.

O guard trata identidade de contrato, não qualidade do conteúdo da spec.
Manifests e eventos antigos não são editados ou retrodatados. Execução e
aceitação local pelo primário são separadas de validação humana/externa.
