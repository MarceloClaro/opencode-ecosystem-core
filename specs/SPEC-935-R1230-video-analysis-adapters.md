---
spec_id: SPEC-935-R1230
title: Adaptadores de análise e cortes propostos para o editor de vídeo
component: integrations.video_analysis
status: specified
test_file: tests/test_r1230_video_analysis.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1230-TOOLS:
      - tests/test_r1230_video_analysis.py::test_diagnose_tools_reports_ffmpeg_ffprobe_versions_separately
      - tests/test_r1230_video_analysis.py::test_diagnose_tools_does_not_hide_missing_or_failed_binary
    R1230-SCENES:
      - tests/test_r1230_video_analysis.py::test_scene_markers_are_frame_aligned_hashed_and_review_only
      - tests/test_r1230_video_analysis.py::test_scene_markers_reject_symlink_vfr_and_bad_detector_output
    R1230-V1:
      - tests/test_r1230_video_analysis.py::test_auto_editor_v1_becomes_pending_cut_proposal_without_frame_drift
      - tests/test_r1230_video_analysis.py::test_auto_editor_parser_rejects_invalid_or_unmapped_chunks
      - tests/test_r1230_video_analysis.py::test_auto_editor_parser_rejects_vfr_and_non_frame_aligned_timebase
      - tests/test_r1230_video_analysis.py::test_auto_editor_parser_preserves_ntsc_rational_timebase_exactly
    R1230-RUNNER:
      - tests/test_r1230_video_analysis.py::test_auto_editor_runner_exports_only_v1_and_preserves_source
      - tests/test_r1230_video_analysis.py::test_auto_editor_runner_reports_timeout_and_missing_cli
    R1230-MCP:
      - tests/test_r1230_video_analysis.py::test_mcp_exposes_confined_analysis_and_review_proposal_tools
      - tests/test_r1230_video_analysis.py::test_mcp_status_reports_tool_versions_and_pending_artifact_counts
    R1230-CATALOG:
      - tests/test_r1230_video_analysis.py::test_registry_records_native_auto_editor_and_optional_longcat
    R1230-REQUIREMENTS:
      - tests/test_r1230_video_analysis.py::test_spec_declares_review_only_and_no_whisperx_install
depends_on:
  - SPEC-935-R1042
  - SPEC-935-R1043
  - SPEC-935-R1034
---

# SPEC-935-R1230 — análise de cenas e propostas de corte

## Objetivo

Ampliar o editor local, mantendo planos separados de execução, com:

1. diagnóstico executável de `ffmpeg` e `ffprobe` no ambiente atual;
2. marcadores de cena por PySceneDetect, sem alterar ou dividir o arquivo;
3. proposta de corte Auto-Editor convertida em segmentos revisáveis, sem render;
4. registro do LongCat-Video como gerador opcional de assets, sem baixar pesos;
5. preservação do Remotion como backend existente.
6. exposição das análises no MCP do editor, confinadas ao projeto e a fontes
   previamente registradas.

O pedido explícito de timestamps por palavra já é atendido no fluxo existente:
`integrations.video_cpu_pipeline.transcribe_cpu` chama faster-whisper com
`word_timestamps=True`, e os consumidores de timing/caption usam esses dados.
Portanto, esta entrega **não instala nem integra WhisperX**. Reavaliá-lo apenas
se uma medição em corpus PT-BR demonstrar falha de alinhamento no backend atual.

## Contrato e segurança

- O diagnóstico roda `-version` sem shell, apresenta caminho, versão, código de
  saída e erro de cada binário; ausência ou falha permanece explícita.
- A análise aceita somente mídia local regular, sem symlink, e calcula SHA-256
  da fonte. Não aceita URL, não envia arquivos e não faz upload/download.
- PySceneDetect retorna marcadores de início/fim em frames e timebase, com
  detector/parâmetros informados. O resultado é análise, não decisão editorial.
- Auto-Editor é invocado somente para exportar o formato de timeline v1, nunca
  para produzir arquivo final. O comando não usa shell; saída temporária é
  isolada e não sobrescreve arquivos do usuário; há timeout e limite de leitura.
- O parser v1 valida versão, timebase racional positiva, sequência contígua,
  intervalos half-open, valores finitos e velocidade suportada. Só converte
  limites para frames quando o mapeamento é exato; conversão ambígua/VFR bloqueia.
- O objeto resultante é `proposal` com `review_required=true` e
  `approval_state="pending"`; não é plano renderizável nem executa cortes.
- MCP recebe somente `project_id` e chave de fonte já existente no projeto;
  grava JSON content-addressed em `editor-analysis/` ou `editor-proposals/`,
  sem sobrescrever conteúdo diferente e sem caminho arbitrário no cliente.
- Nenhum subprocesso aceita argumentos livres do usuário. Falta de dependência
  gera erro acionável, não fallback silencioso.
- O inventário corrige Auto-Editor para CLI nativa/Nim, versionada, e registra
  LongCat-Video como `reference_only`, GPU/high-resource e sem adapter. Nenhum
  checkpoint ou modelo é instalado/baixado por esta entrega.
- Remotion, seu guard de licença/aprovação e o backend FFmpeg existentes não
  são substituídos nem relaxados.

## Critérios de aceitação verificáveis

1. Diagnóstico identifica `ffmpeg` e `ffprobe` separadamente, incluindo ausência,
   falha de execução e versão.
2. PySceneDetect gera marcadores corretos em clipe sintético de cortes conhecidos;
   entrada symlink, VFR não suportado e parâmetros inválidos são recusados.
3. Parser Auto-Editor v1 converte `timebase` para frames sem deriva; rejeita
   JSON inválido, chunks com lacunas/sobreposição, tempos não alinháveis e
   velocidades não suportadas.
4. Execução com runner falso demonstra argv fixo, sem shell, sem render, timeout,
   saída temporária e preservação do original; proposta fica pendente de revisão.
5. MCP rejeita fonte não registrada, symlink e project id inválido; artefatos
   ficam confinados, content-addressed e preservam propostas pendentes.
6. Smoke test Auto-Editor real gera timeline v1 para clipe sintético e a converte
   em proposta sem criar MP4 de saída.
7. `video_toolchain` registra Auto-Editor com runtime atual e LongCat-Video como
   gerador opcional não executável; WhisperX não é apresentado como requisito.
8. Testes focais, regressões de R1042/R1043 e doctor do `.venv` passam; limitações
   de execução e disponibilidade externa são registradas sem overclaim.

## Critérios de aceitação executáveis

- `R1230-TOOLS` — diagnóstico diferenciado de FFmpeg, ffprobe e Auto-Editor.
- `R1230-SCENES` — marcadores CFR íntegros, revisáveis e com rejeição de VFR/symlink.
- `R1230-V1` — conversão exata de timeline v1 e rejeição de dados ou timebases inválidos.
- `R1230-RUNNER` — exportação v1 sem shell/render, com temporário, timeout e fonte preservada.
- `R1230-MCP` — análise e propostas confinadas, content-addressed e pendentes de revisão.
- `R1230-CATALOG` — Auto-Editor nativo e LongCat-Video opcional/reference-only.
- `R1230-REQUIREMENTS` — WhisperX não é instalado quando timestamps por palavra já existem.

## Fora de escopo

- Instalar WhisperX, baixar modelos de ASR ou LongCat-Video, ou acessar token HF.
- Renderizar/editar mídia do usuário, aprovar cortes automaticamente ou criar
  animação generativa.
- Expor GUI/editor visual novo; Remotion continua um backend programático.
- Alegar qualidade narrativa, precisão geral dos detectores ou validação
  perceptual a partir de clipes sintéticos.
