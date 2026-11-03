---
spec_id: SPEC-935-R1024
title: Plano de edição de vídeo auditável e verificação de render
component: integrations.video_edit_plan
status: implemented
test_file: tests/test_r1024_video_edit_plan.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1024-1:
      - "tests/test_r1024_video_edit_plan.py::test_valid_plan_is_accepted"
      - "tests/test_r1024_video_edit_plan.py::test_unknown_field_is_rejected"
      - "tests/test_r1024_video_edit_plan.py::test_duplicate_ids_are_rejected"
      - "tests/test_r1024_video_edit_plan.py::test_unknown_source_is_rejected"
      - "tests/test_r1024_video_edit_plan.py::test_load_rejects_symlink"
      - "tests/test_r1024_video_edit_plan.py::test_load_rejects_oversized_plan"
      - "tests/test_r1024_video_edit_plan.py::test_load_rejects_duplicate_json_keys"
    R1024-2:
      - "tests/test_r1024_video_edit_plan.py::test_source_bounds_are_enforced"
      - "tests/test_r1024_video_edit_plan.py::test_timeline_overlap_is_rejected"
      - "tests/test_r1024_video_edit_plan.py::test_timeline_gap_is_a_warning"
      - "tests/test_r1024_video_edit_plan.py::test_frame_math_is_exact"
    R1024-3:
      - "tests/test_r1024_video_edit_plan.py::test_caption_reading_speed_is_enforced"
      - "tests/test_r1024_video_edit_plan.py::test_caption_overlap_is_rejected"
      - "tests/test_r1024_video_edit_plan.py::test_caption_beyond_timeline_is_rejected"
      - "tests/test_r1024_video_edit_plan.py::test_crop_outside_source_is_rejected"
      - "tests/test_r1024_video_edit_plan.py::test_aspect_mismatch_is_a_warning"
    R1024-4:
      - "tests/test_r1024_video_edit_plan.py::test_output_cannot_overwrite_source"
      - "tests/test_r1024_video_edit_plan.py::test_extension_and_codec_compatibility"
      - "tests/test_r1024_video_edit_plan.py::test_rights_must_be_resolved"
      - "tests/test_r1024_video_edit_plan.py::test_hash_and_loudness_are_validated"
      - "tests/test_r1024_video_edit_plan.py::test_unsafe_paths_are_rejected"
    R1024-5:
      - "tests/test_r1024_video_edit_plan.py::test_plan_is_deterministic_and_not_mutated"
      - "tests/test_r1024_video_edit_plan.py::test_render_metadata_match"
      - "tests/test_r1024_video_edit_plan.py::test_render_mismatch_and_alias_handling"
      - "tests/test_r1024_video_edit_plan.py::test_render_requires_valid_plan"
      - "tests/test_r1024_video_edit_plan.py::test_render_never_claims_visual_quality"
      - "tests/test_r1024_video_edit_plan.py::test_cli_validate_compile_and_error"
      - "tests/test_r1024_video_edit_plan.py::test_no_network_or_execution_imports"
      - "tests/test_r1024_video_edit_plan.py::test_source_manifest_is_pinned_and_scoped"
      - "tests/test_r1024_video_edit_plan.py::test_skills_reference_the_validator"
---

# SPEC-935-R1024 — Plano de edição auditável

## Solicitação

«prossiga na melhora use que melhorar a edição de vídeo busque soluções e
complemento no github». A resposta é uma contribuição local e verificável:
validar o **plano** antes de renderizar, com foco nos erros que mais custam
retrabalho — corte fora da origem, sobreposição de faixas, legenda ilegível,
crop inválido, codec incompatível, destino sobrescrito e ausência de direitos.

## Fontes triadas no GitHub

`federation/video-editing-sources-r1024.json` registra 11 projetos com commit
fixo, licença e decisão. Nenhum foi clonado, instalado ou executado.

Conceitos aproveitados: linha de tempo/EDL (OpenTimelineIO), primeiro passe de
silêncio (auto-editor), detecção de cena (PySceneDetect), timestamp por palavra
(WhisperX, stable-ts), sincronização de legenda (ffsubsync), qualidade
perceptual (VMAF), metadados de mídia (FFmpeg/ffprobe), render programático
(Remotion), linha de tempo interativa (OpenCut, Diffusion Studio Core).

Licenças que impedem cópia silenciosa: Remotion usa a **Remotion License**, não
uma licença OSI, e exige licença comercial para empresas acima do limite.
VMAF usa BSD-2-Clause-Patent. FFmpeg é LGPL-2.1+ por padrão, com partes GPL
opcionais. O Core não incorpora código desses projetos nesta rodada.

## Entregáveis

- `integrations/video_edit_plan.py`: carga segura, validação, compilação
  canônica e verificação de metadados de render; sem rede e sem executar mídia.
- `tests/test_r1024_video_edit_plan.py`: contrato determinístico.
- `docs/EDICAO_VIDEO_AUDITAVEL_R1024.md`: formato, uso e limites.
- Referências nas skills `cp-direcao-de-edicao`,
  `meia-legendas-e-enquadramento` e `meia-revisao-economia`.

## Critérios de aceitação executáveis (RED → GREEN → REFACTOR)

- `R1024-1` — Carga e schema: plano válido, campo desconhecido, IDs duplicados,
  origem inexistente, symlink, tamanho acima de 2 MiB e JSON com chave duplicada.
- `R1024-2` — Tempo: limites de origem, sobreposição de faixa, lacuna como
  aviso e aritmética exata de frames/segundos.
- `R1024-3` — Legenda e composição: CPS máximo, sobreposição, legenda após o
  fim, crop fora da origem e aviso de proporção divergente.
- `R1024-4` — Destino e direitos: não sobrescrever origem, extensão/contêiner,
  codec compatível, direitos resolvidos, hash, loudness e caminhos inseguros.
- `R1024-5` — Determinismo e render: plano não mutado, digest estável, metadados
  de render conferidos, aliases de codec, plano inválido bloqueado, ausência de
  alegação de qualidade visual, CLI e imports sem rede/execução, manifesto de
  fontes fixado e skills apontando para o validador.

## Contrato

1. O plano é JSON estrito, arquivo regular local, não symlink, até 2 MiB.
2. Frames são inteiros; a linha de tempo usa frames e converte para segundos
   pela taxa declarada, sem arredondar silenciosamente.
3. Faixas de vídeo não podem se sobrepor na mesma lane. Lacunas são avisos,
   não erros: pausa pode ser intencional.
4. Legenda usa CPS de caracteres não vazios por segundo; o limite é declarado
   por legenda e o padrão é 17.
5. Crop precisa caber na origem; escala precisa ser positiva. Divergência de
   proporção em relação à saída gera aviso, não correção automática.
6. Direitos da origem precisam ser declarados. `unknown` bloqueia.
7. O destino não pode ser igual a nenhuma origem; extensão e codec precisam ser
   compatíveis com o contêiner.
8. `verify` compara **metadados** de um relatório produzido pelo usuário com o
   plano. Não abre o vídeo, não executa ffprobe e não mede qualidade visual.
9. Nenhuma função acessa rede, baixa, instala, renderiza ou executa mídia.

## Limites

O validador não prova que o vídeo ficou bom, que a legenda está sincronizada
com a fala real, que o crop preserva o rosto, que o loudness foi medido ou que
o render existe. Ele reduz erros de plano. A conferência visual, a escuta e a
aprovação humana continuam obrigatórias.
