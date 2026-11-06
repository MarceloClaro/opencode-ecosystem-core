# SPEC-935-R1081 — Direção de arte Piranesi/Pencz

**Status:** implementado como contrato visual e provas determinísticas; arte
final não produzida.
**Data:** 2026-11-05
**Teste:** `tests/test_r1081_illustration_style.py`

## 1. Objetivo

Fixar a direção de arte das ilustrações do Molambudos e do assistente literário
na síntese **Giovanni Battista Piranesi (Carceri, 1750-3)** + **Georg Pencz
(1500-1550)**, com gramática visual, prompts, especificações de impressão e
provas de referência.

## 2. Não objetivos

- Não produzir arte final sem desenhista ou modelo de imagem.
- Não copiar uma prancha específica de Piranesi ou Pencz.
- Não simular prova histórica.
- Não retratar vítimas reais identificáveis.
- Não publicar, enviar à KDP ou declarar 10/10.
- Não usar upscale artificial para alegar 300 DPI.

## 3. Requisitos

| ID | Requisito | Critério |
|---|---|---|
| R1 | Linhagem | Piranesi para arquitetura/escala; Pencz para figura/emblema |
| R2 | Tipos de prancha | 6 tipos com uso, composição, prompt, negativo e legenda |
| R3 | Gramática | perspectiva, escala, luz, linha, cor, papel e motivos |
| R4 | Prompts | base EN, base PT, negativo EN/PT e ZH |
| R5 | Técnica | 300 DPI, duotone, TAC ≤210%, formatos e proveniência |
| R6 | Ética | domínio público, ficção, sem alvo real, aviso, revisão humana, IA declarada |
| R7 | Provas | 3 tratamentos determinísticos, sem IA e sem upscale |
| R8 | Manifesto | hashes, dimensões e limites das provas |
| R9 | Prova textual | descrição de prancha na voz do perfil, com status/findings/evidence/limitations |
| R10 | Teste | `tests/test_r1081_illustration_style.py` passa |

## 4. Tipos de prancha

1. `carceri-colonia` — hospital-colônia, currais, corredores.
2. `retrato-emblematico` — paciente, médico, Lúcia, mãe.
3. `tabela-alegorica` — ciclo, contaminação, culpa.
4. `paisagem-erodida` — seca, êxodo, estrada.
5. `anatomia-contaminacao` — corpo, doença, metamorfose.
6. `arquivo-doente` — laudo, carta, prova.

## 5. Técnica

- 300 DPI; duotone sépia ou 1-bit; um acento carmim.
- Papel `#F2E8CF`; tinta `#2B2117`; acento `#9B1B1B`.
- TAC ≤210%.
- 2× o tamanho final; TIFF 16-bit, PNG sem perdas ou SVG/PDF.
- Hash e manifesto; declarar homagem e IA.

## 6. Ética

Piranesi e Pencz são domínio público; a obra não copia uma prancha específica.
Toda imagem é reconstituição ficcional. Corpo, doença, violência e morte exigem
aviso. A arte final exige desenhista, revisão de sensibilidade e prova.

## 7. Aceitação

1. `python3 -m pytest tests/test_r1081_illustration_style.py -q` passa.
2. `style_pack.json` tem 6 tipos e prompts.
3. `samples_manifest.json` tem 3 provas com hashes.
4. `demo_plate.md` tem status, findings, evidence e limitations.
5. Nenhum upscale; nenhuma alegação de arte final.

## 8. Arquivos

| Caminho | Conteúdo |
|---|---|
| `reports/r1081/illustration_style/style_pack.json` | contrato visual |
| `reports/r1081/illustration_style/README.md` | guia de arte |
| `reports/r1081/illustration_style/make_samples.py` | provas determinísticas |
| `reports/r1081/illustration_style/samples/` | 3 provas + folha de contato |
| `reports/r1081/illustration_style/samples_manifest.json` | hashes e limites |
| `reports/r1081/illustration_style/demo_plate.md` | prova textual |
| `tests/test_r1081_illustration_style.py` | gate |
