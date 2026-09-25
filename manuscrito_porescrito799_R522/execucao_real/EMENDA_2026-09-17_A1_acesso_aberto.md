# EMENDA AO PROTOCOLO — SPEC-935-R522
## EMENDA-2026-09-17-A1: Alteração formal e prospectiva das fontes de informação para modalidade de acesso aberto

**Protocolo alterado:** SPEC-935-R522 — manuscrito v2.0
(`manuscrito_porescrito799_brasil_comparado_R522_v20_protocolo_ABNT.docx`, seção 3.4)
**Data da emenda:** 17/09/2026 (prospectiva — anterior à conclusão das buscas; sem retroatividade de dados)
**Autoria da emenda:** orquestrador `marceloclaro` — [A CONFIRMAR PELOS AUTORES]
**Tipo:** alteração de escopo de fontes de informação (metodologia — não altera PICo, critérios de elegibilidade, janela temporal, desenho JBI/PRISMA-ScR nem a regra anti-overclaim)

---

## 1. Texto alterado

**De (protocolo v2.0, seção 3.4):**
> "Planejam-se buscas em Scopus, Web of Science Core Collection, SciELO, Educ@, Portal de Periódicos CAPES e DOAJ, com Google Acadêmico apenas como fonte complementar."

**Para:**
> "As buscas serão executadas em fontes de **acesso aberto e auditáveis sem credenciais institucionais**: **DOAJ, OpenAlex, SciELO, Educ@ e Google Acadêmico** (este último promovido a fonte primária de varredura, uma vez que a modalidade de acesso aberto o exige), mais **base de preprints** (SciELO Preprints / SSRN) para literatura em estágio de pré-publicação. Scopus, Web of Science Core Collection e Portal de Periódicos CAPES passam a ser **fontes opcionais de validação a posteriori**, executáveis caso credenciais institucionais sejam disponibilizadas pelos autores antes da conclusão da triagem — sem que sua ausência bloqueie a revisão. Cada busca registra data, string integral, filtros, quantidade recuperada e exportação arquivada."

## 2. Justificativa

1. **Auditabilidade:** todas as fontes mantidas são acessíveis por API pública ou interface aberta, permitindo exportações arquiváveis e reprodução integral — requisito da política anti-overclaim (R110) e do próprio protocolo (3.8).
2. **Cobertura adequada ao objeto:** a literatura brasileira de educação jurídica concentra-se em periódicos de acesso aberto (SciELO, Educ@, revistas jurídicas brasileiras indexadas no DOAJ/OpenAlex); a literatura internacional sobre *legal education + GenAI* está amplamente coberta no OpenAlex (metadados globais curados).
3. **Viabilidade sem credenciais:** remove o bloqueio institucional (Scopus/WoS exigiram credenciais que não estão disponíveis na data da emenda).
4. **Desenho de revisão de escopo:** por mapear campo heterogêneo, a cobertura aberta com duas bases internacionais (DOAJ + OpenAlex) e duas nacionais (SciELO + Educ@) + Google Acadêmico é metodologicamente defensável, desde que declarada a limitação (preenchimento da lista de verificação PRISMA-ScR item 6).

## 3. Impactos e salvaguardas

- O fluxograma PRISMA-ScR (futura Seção 4) reportará **somente as fontes efetivamente executadas**, com seus números; nenhuma fonte não executada gerará número (regra do `LOG_EXECUCAO_REAL_R522.md`).
- A diferença de cobertura vs. busca clássica Scopus/WoS será declarada como **limitação explícita** na seção de limitações do manuscrito (não como ausência, mas como recorte de acesso aberto).
- **Snowballing** (varredura de referências dos estudos incluídos), se utilizado, será registrado como etapa complementar.
- Alteração **não** retroage sobre dados já coletados; toda busca passa a seguir a modalidade emendada.
- 2026 permanece **fora do corpus** (apenas atualização contextual), salvo nova emenda.

## 4. Registro

- **LOG_EXECUCAO_REAL_R522.md** — atualizado para refletir a modalidade emendada.
- **protocolo_OSF_R522.md** — seção de emendas acrescentada (pré-registro deve versionar emendas — protocolo v2.0, seção 3.2).
- **cycles.json** — ciclo R524 registra a emenda.

**Assinatura eletrônica do orquestrador:** marceloclaro — 17/09/2026 20:25 UTC-3
**Validação necessária:** autores devem aprovar a emenda antes do registro definitivo no OSF (a confirmação fica anexada ao pré-registro).