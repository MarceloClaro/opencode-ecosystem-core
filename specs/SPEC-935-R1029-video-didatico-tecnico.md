---
spec_id: SPEC-935-R1029
title: Skill de vídeo didático técnico e registro metacognitivo
component: .opencode/skills/video-didatico-tecnico
status: implemented
test_file: tests/test_r1029_video_didatico_skill.py
---

# SPEC-935-R1029 — Vídeo didático técnico

## Objetivo

Especializar o Core para produzir e revisar vídeos técnicos didáticos com
slides animados, narração, legendas e lip sync, preservando timing,
acessibilidade, proveniência e limites. Registrar as descobertas do piloto
Qiskit de forma metacognitiva.

## Entregáveis

- `.opencode/skills/video-didatico-tecnico/SKILL.md`.
- `references/principios-didaticos.md`, `efeitos-e-motion.md`,
  `pipeline-e-erros.md`, `registro-de-descobertas.md`.
- `pilots/r1026-quantum/DISCOVERIES.md` com 14 descobertas.
- `tests/test_r1029_video_didatico_skill.py`.

## Critérios

1. Skill com frontmatter, descrição e seções de princípios, efeitos, pipeline,
   metacognição e limites.
2. Referências locais existentes e links resolvidos.
3. Pelo menos 10 descobertas com evidência e impacto; marcadores de Wav2Lip,
   XTTS, Remotion, SAR, concat e watchdog.
4. Contrato de segurança: consentimento, revisão humana, licença, uso não
   comercial; ausência de promessas de qualidade garantida ou sincronia perfeita.
5. Scripts do pipeline existentes e executáveis; skill textual e sem ID
   duplicado; descoberta pelo dispatcher.

## Evidência

- RED inicial: 7 falhas por ausência da skill e do registro.
- GREEN local: **8 passed** em `tests/test_r1029_video_didatico_skill.py`.
- Não houve execução de LLM, voz ou vídeo induzida por esta suíte; os testes são
  estruturais e de contrato textual.
- Não foi executado `SpecVerifier` para esta skill de documentação; a evidência é
  o teste local acima.

## Limites

Os testes não provam obediência futura de um LLM, qualidade didática, sincronia
labial, inteligibilidade da voz ou adequação editorial. Esses pontos exigem
reprodução com áudio e revisão humana. O consentimento de voz é declarado, não
verificado; XTTS/CPML e Wav2Lip são não comerciais.
