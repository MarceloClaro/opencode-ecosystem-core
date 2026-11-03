---
spec_id: SPEC-935-R1034
title: Implementação incremental CPU multivoz com timeline única
component: integrations.video_cpu_pipeline
status: planned
test_file: tests/test_r1034_video_cpu_pipeline.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    consentimento:
      - tests/test_r1034_video_cpu_pipeline.py::test_consent_required
      - tests/test_r1034_video_cpu_pipeline.py::test_unknown_speaker_rejected
    tempo:
      - tests/test_r1034_video_cpu_pipeline.py::test_overlapping_speakers_are_preserved
      - tests/test_r1034_video_cpu_pipeline.py::test_same_speaker_overlap_is_not_silent
      - tests/test_r1034_video_cpu_pipeline.py::test_bool_time_invalid
    audio:
      - tests/test_r1034_video_cpu_pipeline.py::test_final_audio_binding
      - tests/test_r1034_video_cpu_pipeline.py::test_alignment_type_and_real_duration
    legendas:
      - tests/test_r1034_video_cpu_pipeline.py::test_caption_formats_and_speaker_separation
      - tests/test_r1034_video_cpu_pipeline.py::test_caption_word_wrapping
      - tests/test_r1034_video_cpu_pipeline.py::test_caption_direct_input_cannot_add_blocks
      - tests/test_r1034_video_cpu_pipeline.py::test_reject_cue_lost_in_ass_rounding
      - tests/test_r1034_video_cpu_pipeline.py::test_caption_cli_with_real_wav_and_no_overwrite
    cache:
      - tests/test_r1034_video_cpu_pipeline.py::test_resume_checks_input_output_and_params
      - tests/test_r1034_video_cpu_pipeline.py::test_resume_rejects_changed_input
      - tests/test_r1034_video_cpu_pipeline.py::test_write_new_does_not_follow_existing_symlink
    motion:
      - tests/test_r1034_video_cpu_pipeline.py::test_timeline_overlap_not_hold
      - tests/test_r1034_video_cpu_pipeline.py::test_motion_continuity
    local:
      - tests/test_r1034_video_cpu_pipeline.py::test_partial_model_is_rejected_before_import
---

# SPEC-935-R1034

## Autorização e escopo

Usuário autorizou implementar melhorias e escolheu explicitamente
“Playlist com consentimentos” e “Sim, instalação isolada”. Registrar direitos
e consentimentos como declarados, não documentalmente verificados. Sem upload
de voz/mídia a serviços externos, sem pagamento ou publicação. Usar apenas
um trecho de até 90 s do primeiro episódio inicialmente, preservando o original
e os masters Qiskit. Propósito piloto de avaliação, sem presumir uso comercial
permitido por pesos restritos. Sem GPU ou consulta nvidia-smi.

## Implementação nesta etapa

1. Ambiente Python isolado para ASR CPU/int8 e aquisição de trecho; pacotes
   oficiais com versões registradas, sem alterar ambientes anteriores.
2. Núcleo reutilizável e CLI: validação de locutores/consentimento, turnos com
   sobreposição legítima, cache invalidado por hash de entradas/parâmetros/
   versão de ferramenta, artefatos produzidos e seus hashes.
3. Legendas SRT/VTT/ASS a partir de palavras alinhadas ao áudio PT-BR final;
   rejeitar áudio diferente, tempos inválidos e palavras fora da duração;
   separar locutores sem apagar sobreposições. Escape correto para formatos.
4. Timeline de cenas com transições sobrepostas e duração correta, incluindo
   teste de continuidade e limites; base para motion 2D sem relógio CSS.
5. Adaptador ASR CPU que consome modelo local explícito e grava palavras reais.
   Não inferir nomes/identidades dos personagens a partir do ASR.
6. Tentativa limitada de obter o trecho público autorizado. Se acesso exigir
   autenticação, parar e pedir arquivo local, sem cookies, contorno ou retries
   ilimitados. Não declarar piloto dublado antes de síntese/mixagem reais.

## Aceites

Testes antes do núcleo: entrada inválida, falta de consentimento, troca de
áudio final, sobreposição multivoz, saída de legenda, cache adulterado e
transições. Validar instalação por import/versão e executar smoke em arquivos
temporários separados. Evidências em `pilots/r1034-multivoice/`.
R1033 continua pesquisa; não atualizar retroativamente suas ações.

## Limites de entrega

Core não identifica automaticamente atores com garantia. Diarização,
referências de cada voz, fidelidade vocal e interpretação continuam exigindo
amostra e revisão humana. Clonagem/lip sync não se tornam concluídos por este
núcleo de controle. Render Remotion precisa de aprovação específica ao plano;
esta etapa não contorna seu guard. Novo modelo Chatterbox V3 requer loader
compatível e smoke próprio; não misturar pesos por renomeação.

## Critérios de aceitação executáveis

- `consentimento`: locutor conhecido e declaração exigidos, sem inferir documentos.
- `tempo`: sobreposição entre pessoas preservada; conflito intrapessoal rejeitado.
- `audio`: hash e duração reais vinculam legenda à mixagem correta.
- `legendas`: formatos exportados sem injeção, colapso temporal ou sobrescrita.
- `cache`: mudanças em entradas/saídas/parâmetros invalidam retomada.
- `motion`: timeline e easing coerentes, sem alegar renderização.
- `local`: modelo incompleto rejeitado antes de carregar o backend.

## Estado do gate

RED de núcleo ausente e RED de oito regressões após revisão foram observados
no pytest e preservados em logs. A selagem histórica estrita do Core permanece
indisponível após timeout R1033; não foi contornada nem repetida. Entrega
incremental experimental, com inspeção criteria-only, não release de produção.
