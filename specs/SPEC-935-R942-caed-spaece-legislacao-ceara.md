---
spec_id: SPEC-935-R942
title: Agente de matrizes CAEd/SPAECE e legislação educacional do Ceará
component: agents.caed_spaece_educacao_ceara
status: implemented
test_file: tests/test_r942_caed_spaece_educacao_ceara.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    managed_profile:
    - tests/test_r942_caed_spaece_educacao_ceara.py::test_profile_is_managed_and_read_only
    assessment_scope:
    - tests/test_r942_caed_spaece_educacao_ceara.py::test_matrix_scope_requires_full_coverage_inventory_and_gap_reporting
    legal_scope:
    - tests/test_r942_caed_spaece_educacao_ceara.py::test_legal_scope_versions_sources_and_does_not_assume_current_validity
    local_corpus_safety:
    - tests/test_r942_caed_spaece_educacao_ceara.py::test_uses_local_public_matrix_corpus_and_excludes_restricted_student_data
    opencode_registration:
    - tests/test_r942_caed_spaece_educacao_ceara.py::test_opencode_registers_agent_and_preserves_existing_customization
---

# R942 — agente de matrizes CAEd/SPAECE e legislação educacional do Ceará

## Objetivo

Registrar pelo ciclo de vida do MarceloClaro o agente `caed-spaece-educacao-ceara`,
com escopo para examinar todas as matrizes, anos/séries, componentes e edições
CAEd/SPAECE que estejam representados no corpus local fornecido, relacioná-los à
BNCC sem presumir equivalência e analisar, com proveniência temporal, legislação
educacional federal e do Ceará, com atenção a direitos da criança/adolescente,
deficiência e inclusão.

O escopo “completo” é uma regra de cobertura, não uma afirmação de que o corpus
atual contém todas as publicações. O agente só poderá declarar cobertura integral
para um universo de fontes delimitado, datado e documentado; deve listar os
períodos, séries, componentes, edições ou normas não localizados.

## Critérios de aceitação

- **Perfil gerenciado e read-only** — criar o perfil `managed-v1` pelo
  `MarceloClaroOrchestrator.agent_profile_action` (`operation=create`), com esta
  spec e o teste R942. Leitura e busca local permitidas; edição, `webfetch`,
  delegação `task` e Bash arbitrário negados. Conteúdo CAEd/SPAECE e legislação
  não é instalado, copiado ou executado nesta entrega.
- **Cobertura de matrizes** — instruir o agente a inventariar todo o material
  fornecido antes de responder: todas as edições e anos publicados no corpus,
  etapas/séries, componentes/áreas, códigos de descritor, versões e localizadores.
  Manter uma matriz de cobertura com cada combinação observada, não localizada,
  indisponível ou ambígua; registrar universo, data de corte e fonte de cada
  combinação. Não inventar descritores nem declarar “todas as edições” sem
  evidência de cobertura. Distinguir o programa SPAECE da instituição CAEd e
  distinguir matriz oficial de cruzamento analítico com a BNCC. Cruzamentos
  devem ser classificados como explícitos, apoiados, aproximados ou não
  demonstrados, com justificativa.
- **Corpus local Airam Veras** — usar como referência primária de matrizes a
  pasta `PROJETO 1/Airam veras/caed-dados/` (PDFs locais, `fontes.json`,
  `dados/descritores.csv`, `dados/catalogo_documentos.csv` e `validacao.json`),
  mantendo `spaece-dados/` como acervo anterior para comparação, não como versão
  atual. O README local declara 54 PDFs, 129 matrizes e ocorrências de 2017,
  2018, 2019, 2022, 2023, 2024, 2025 e 2026; esses números são declarações do
  pacote e devem ser confrontados com seu catálogo e arquivos antes de serem
  reportados como verificação independente. Anos ausentes no arquivo local não
  provam que uma edição nunca foi publicada. Distinguir Avalie.CE, SPAECE,
  diagnóstica, formativa, somativa e CNCA; CNCA não deve ser reclassificado como
  SPAECE/CAEd.
- **Privacidade e código não confiável** — limitar o escopo a matrizes,
  descritores e materiais normativos. Não abrir nem processar pastas/arquivos de
  resultados individuais, caminhos marcados `RESTRITO`, datasets completos,
  identificadores de estudantes, CSVs brutos de resultados ou bancos que possam
  conter microdados. Não executar scripts, notebooks, SQL, testes, dependências
  ou conteúdo dos repositórios locais; usar apenas leitura documental.
- **Legislação versionada** — exigir fonte oficial, número/ano, título, artigo,
  data de publicação, alterações, revogações, vigência/período, eventual
  prorrogação ou norma sucessora e data de verificação. O recorte inclui ECA
  (Lei nº 8.069/1990), LDB (Lei nº 9.394/1996), Lei Brasileira de Inclusão
  (Lei nº 13.146/2015), normas de educação inclusiva diretamente aplicáveis,
  PNE federal e Plano Estadual de Educação do Ceará. A Lei cearense nº
  16.025/2016 identifica um PEE para 2016–2024; tratar esse período como
  histórico até verificar eventual extensão ou sucessor em fonte oficial. Não
  presumir vigência atual da Lei nº 13.005/2014 do PNE ou do plano cearense
  apenas por constarem em documentos antigos; verificar ato sucessor, extensão
  e transição. Sem fonte suficiente, registrar `vigência não verificada`.
- **Limite de acesso e anti-overclaim** — o perfil R942 não tem ferramenta de
  busca na web; opera somente sobre arquivos e contextos locais. Se faltarem
  documentos de qualquer edição ou fonte
  normativa, deve responder `partial` ou `blocked`, não simular pesquisa, não
  inferir conteúdo a partir de títulos ou memória e não chamar o levantamento de
  exaustivo. A pasta local de matrizes está disponível; documentos legais
  correntes e normas sucessoras ainda precisam estar presentes no contexto para
  verificação pelo agente. A Lei 16.025/2016 declara PEE 2016–2024, mas eventual
  extensão/sucessor não foi confirmado; a vigência atual do PNE também não foi
  fechada nesta entrega.
- **Saída e configuração** — preservar contrato de saída `status`, `findings`,
  `evidence`, `limitations`; evidência deve identificar fonte, edição/ano,
  linha/artigo/página ou descritor e, quando houver, hash e commit. Adicionar o
  agente em `opencode.json` como subagente sem substituir mudanças pré-existentes
  do operador.
- **Verificação local** — testes do perfil e configuração passam, validação do
  ciclo de vida confirma `managed-v1`, e `python3 -m marceloclaro.cli doctor`
  não apresenta falhas novas. Isso verifica o perfil, não a completude real de
  matrizes ou do corpus jurídico.

## Fora de escopo

Não baixar documentos, criar um arquivo integral de leis, fazer
interpretação jurídica profissional, recomendar políticas públicas, avaliar
alunos ou produzir microdados. Não alterar BNCC, arquivos CAEd/SPAECE, documentos
legais, configuração não relacionada, nem alegar validação externa ou cobertura
histórica que não tenha sido comprovada por fontes primárias.
