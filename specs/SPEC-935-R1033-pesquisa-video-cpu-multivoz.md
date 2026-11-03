---
spec_id: SPEC-935-R1033
title: Pesquisa auditável de vídeo CPU e dublagem multivoz PT-BR
component: reports/r1033-video-cpu
status: planned
test_file: tests/test_r1033_video_cpu_research.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    fontes:
      - tests/test_r1033_video_cpu_research.py::test_sources_have_saved_receipts_and_hashes
    licencas:
      - tests/test_r1033_video_cpu_research.py::test_candidate_limits_and_separate_licenses
    escopo:
      - tests/test_r1033_video_cpu_research.py::test_scope_and_playlist_uncertainties
    estrategia:
      - tests/test_r1033_video_cpu_research.py::test_strategy_addresses_required_pipeline_and_human_gate
    inventario:
      - tests/test_r1033_video_cpu_research.py::test_candidate_sources_exist_and_local_files_unchanged
    revisao:
      - tests/test_r1033_video_cpu_research.py::test_review_findings_are_reconciled_without_runtime_claims
---

# SPEC-935-R1033 — pesquisa, não produção da playlist

## Escopo autorizado

Pesquisar documentação pública/GitHub e os materiais pertinentes em
`biblioteca ai`, em leitura, para propor animação explicativa em CPU,
dublagem longa multivoz PT-BR e legendas sincronizadas. Consultar apenas
metadados públicos da playlist PL2dcm-6042EC788TGxgH3qWF7MjpoJIv9.
Não instalar, executar instaladores locais, renderizar, baixar vídeos,
clonar vozes novas ou publicar. Consentimento anterior não cobre a playlist.

## Aceites documentais (não equivalem a qualidade audiovisual)

1. Relatório com candidatos, fontes oficiais, licença de código distinta da
   licença dos pesos/vozes e limites reais de CPU. Evidência remota armazenada
   com URL, data de coleta e SHA-256; consultas que falharem registradas.
2. Inventário seletivo local com caminhos/hashes. ZIPs lidos sem extração nem
   execução; PDFs alheios ao tema e documentos pessoais não examinados.
3. Playlist identificada somente quando houver recibo público. Desconhecidos
   (locutores, direitos, duração total) permanecem explícitos.
4. Estratégia inclui diarização, identidade persistente dos locutores,
   falas sobrepostas, tradução contextual, ajuste de duração sem cortar fala,
   trilha de música/efeitos, alinhamento do áudio PT-BR final e SRT/VTT/ASS.
5. CPU: priorizar animação determinística/2D e dublagem; lip sync seletivo,
   não prometer tempo real, todas as vozes clonadas ou qualidade profissional.
   Não usar zoom/drift nem diferença de frames como prova de sincronia.
6. Piloto futuro depende de direitos de uso, consentimento individual para
   clonagem, finalidade e aprovação de trecho. Nenhuma renderização nesta fase.
7. Testes de integridade do dossiê e revisão independente; resultados e
   limitações registrados. Sem alegar RED de implementação audiovisual.

## Verificação e falhas já observadas

Doctor prévio: 22/22 estrutural; não certifica ferramentas audiovisuais.
Busca web integrada retornou HTTP 402; usar fontes oficiais diretas, sem
contornar autenticação ou cotas. Erro 413 anterior: respostas compactas,
evidências completas locais, sem anexar mídia pesada ao contexto.

## Entregáveis

`reports/r1033-video-cpu/README.md`, `evidence.json`, recibos e testes.
Consulta/revisão via orquestrador com origem preservada. Sem alterar masters
R1032 ou configurações preexistentes.

## Critérios de aceitação executáveis

- `fontes`: recibos remotos presentes e hashes correspondentes.
- `licencas`: cada candidato separa código, modelo e benchmark não realizado.
- `escopo`: não execução audiovisual, playlist parcial e consentimento pendente.
- `estrategia`: etapas essenciais e revisão humana explícitas no texto.
- `inventario`: referências resolvíveis e materiais locais inalterados.
- `revisao`: achados da revisão textual reconciliados, sem transformar
  compatibilidade presumida em runtime aprovado.

## Cronologia de revisão

Os cinco testes documentais iniciais falharam por artefatos ausentes antes da
coleta e passaram após o primeiro dossiê. Esse RED foi observado no terminal,
mas não selado pelo TDDHistory. Após revisão externa textual, o sexto teste
formaliza as lacunas específicas antes de suas correções. A tentativa de
selagem TDDHistory atingiu timeout durante o snapshot, sem recibo aceito.
RED/GREEN foi observado por pytest normal, não selado. O gate final tem escopo
documental/criteria-only; não se atribui retroativamente selo à produção
audiovisual ou à primeira elaboração do dossiê.
