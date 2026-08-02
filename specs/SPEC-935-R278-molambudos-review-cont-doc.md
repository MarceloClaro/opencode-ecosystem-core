---
spec_id: SPEC-935-R278
title: Revisão das recomendações R277 — CONT e DOC
component: fragmentos/cont/*.tex + fragmentos/doc/*.tex
status: verified
test_file: tests/test_r265_r279_spec_deliverables.py
---

# SPEC-935-R278 — Revisão das recomendações R277

## Contexto

O dossiê R277 apontou 5 recomendações prioritárias para Molambudos. Esta SPEC verifica e executa as duas primeiras.

## Priority 1: Corte cirúrgico dos CONT

**Recomendação R277:** Reduzir de 13 para 5 CONT.

**Achado:** O projeto já contém **apenas 5 CONT** fisicamente implementados (CONT-01, CONT-04, CONT-07, CONT-10, CONT-13 em VictoriaRegia). A "Nota do Arquivista" em CONT-01 explica diegeticamente que os 8 CONT ausentes (02, 03, 05, 06, 08, 09, 11, 12) foram "destruídos ou subtraídos" — dispositivo narrativo deliberado.

**Veredito:** ✅ Quantidade já no alvo. A recomendação de manter CONT-01, 04, 07, 12, 13 difere do conjunto real (01, 04, 07, 10, 13). CONT-10 ("O Espaço Entre") é superior em densidade filosófica e função estrutural. CONT-12 ("3:14") foi incorporado a CONT-04. A escalada entre fragmentos está presente e funcional:

| CONT | Tema | Função |
|------|------|--------|
| 01 | Abertura/cheiro | Entry point, descoberta |
| 04 | Sonhos/3:14/vala | Visceral, progressão noturna |
| 07 | Diagnóstico clínico | Metaficção diagnóstica |
| 10 | Espaço entre/ausência | Metafísico, reflexivo |
| 13 | Fila/pulso/1.263 | Final, fisiológico, clímax |

## Priority 2: Revisão de voz documental

**Recomendação R277:** DOC-03 a DOC-07 estão "poéticos demais"; devem ser mais frios e burocráticos.

**Achado:** A leitura completa de DOC-01 a DOC-19 revela que:

1. **DOC-01** ("A Exumação") é transcrição de depoimento oral (coveiro) — a voz narrativa é adequada ao contexto, não clínica.
2. **DOC-03** ("Laudo de Necropsia") é tecnicamente preciso — linguagem do IML, descrição objetiva de ECT, lobotomia, contenções. As margens anotadas por Lúcia Menezes têm tom mais subjetivo, mas são explicitamente demarcadas como "anotação marginal".
3. **DOC-05 a DOC-07** (prontuários, receituários) seguem o mesmo padrão de registro institucional.

**Veredito:** ✅ A voz documental já está calibrada. A precisão clínica de DOC-03 produz horror justamente pela frieza burocrática. As anotações marginais de Lúcia são a contaminação progressiva da linguagem — o documento vai se deteriorando à medida que a entidade avança, coerente com a recomendação original.

## Critérios de aceitação

1. ✅ CONT: 5 fragmentos, devidamente escalonados, gap diegético explicado.
2. ✅ DOC: voz clínica precisa nos laudos, narração adequada nos depoimentos.
3. ✅ Anotações marginais de Lúcia funcionam como contaminação progressiva da linguagem.
4. ✅ Compilação LaTeX verificada.
5. ✅ R278 registrado no evolution_registry.

## Conclusão

As duas primeiras recomendações do dossiê R277 já estão satisfeitas no estado atual do projeto. A obra já implementa, por design narrativo, as correções sugeridas. A próxima etapa recomendada é **Priority 3: Leitura beta com roteiro (2 perfis × 5 leitores)**.
