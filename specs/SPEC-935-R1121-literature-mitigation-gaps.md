# SPEC-935-R1121 — Dossiê de literatura para os gaps de mitigação

**Status:** implementação local
**Data:** 2026-11-09
**Depende de:** R1114–R1120

## 1. Contexto

O operador pediu literatura que ajude a resolver os gargalos: RC/Pauli-frame,
GST/SPAM, taxas Pauli-Lindblad, PEC 2q, ZNE, decodificador de superfície e
incerteza. A busca arXiv/web estava indisponível; esta spec usa Crossref e
páginas arXiv verificadas.

## 2. Requisitos

- **R1.** Toda referência deve ter DOI ou arXiv ID verificado nesta sessão.
- **R2.** Mapear cada gap para pelo menos uma técnica e uma referência.
- **R3.** Separar técnica candidata de resultado comprovado no Baihua.
- **R4.** Propor uma pilha híbrida ordenada, sem somar créditos indevidos.
- **R5.** Definir gates e orçamentos de jobs para cada etapa.
- **R6.** Não prometer “10/10”, Qualis, vantagem ou fidelidade.
- **R7.** Registrar limites de aplicabilidade (hardware, ruído, modelo).
- **R8.** Testes de integridade das referências e do mapeamento.

## 3. Referências verificadas

18 referências em `docs/literatura_mitigacao_r1121.json`, incluindo:

- RC: Wallman & Emerson 2016; Kurita et al. 2023.
- Cycle benchmarking: Erhard et al. 2019.
- Pauli-Lindblad: Harper et al. 2020; Flammia & Wallman 2020;
  van den Berg et al. 2023.
- PEC/ZNE: Temme et al. 2017; Li & Benjamin 2017.
- GST: Blume-Kohout et al. 2017; Brieger et al. 2023; Gu et al. 2021;
  Greenbaum 2015.
- Readout: Bravyi et al. 2021; van den Berg et al. 2022.
- Superfície: Barber et al. 2025.
- Crosstalk: Gambetta et al. 2012.
- Incerteza: Wallman & Flammia 2014.

## 4. Pilha híbrida proposta

1. **Leitura** — matriz de calibração + mitigação model-free.
2. **RC** — passe de Pauli-frame (R1119) e validação twirlado vs baseline.
3. **Caracterização** — cycle benchmarking para as 15 taxas Pauli-Lindblad;
   GST para diamond norm e SPAM autoconsistente.
4. **PEC/ZNE** — PEC 2q com modelo esparso; ZNE só se a curva for monotônica.
5. **QEC** — superfície apenas com decodificador em tempo real.

## 5. Critérios de aceitação

- JSON válido, sem DOI/arXiv duplicado ou inventado;
- cada gap com ao menos uma referência;
- documento com pilha, gates e orçamentos;
- nenhum termo de overclaim;
- testes R1121 passam.

## 6. Não objetivos

- Declarar que as técnicas funcionam no Baihua sem medir.
- Substituir GST/cycle benchmarking por tomografia de 12 circuitos.
- Executar hardware.
- Prometer nota, Qualis ou “10/10”.
