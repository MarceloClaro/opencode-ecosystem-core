---
spec_id: SPEC-935-R1023
title: Curadoria rastreável de repositórios e skills nativas OpenCode
component: .opencode/skills
status: implemented
test_file: tests/test_r1023_repository_skills.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1023-1:
      - "tests/test_r1023_repository_skills.py::test_repository_coverage_and_decisions"
      - "tests/test_r1023_repository_skills.py::test_pinned_evidence_and_license_limits"
    R1023-2:
      - "tests/test_r1023_repository_skills.py::test_native_skill_discovery"
      - "tests/test_r1023_repository_skills.py::test_local_reference_links"
    R1023-3:
      - "tests/test_r1023_repository_skills.py::test_book_skill_contract"
      - "tests/test_r1023_repository_skills.py::test_book_negative_cases"
    R1023-4:
      - "tests/test_r1023_repository_skills.py::test_legislation_skill_contract"
      - "tests/test_r1023_repository_skills.py::test_legislation_negative_cases"
    R1023-5:
      - "tests/test_r1023_repository_skills.py::test_existing_routes_reused"
      - "tests/test_r1023_repository_skills.py::test_no_executable_imports_or_model_override"
---

# SPEC-935-R1023 — Repositórios autorizados e skills OpenCode

## Solicitação e limite

Continuação de «autorizo todos» e «prossiga»: avaliar os repositórios enviados
e aproveitar contribuições úteis ao Core. Esta rodada entrega instruções
originais, referências e proveniência, não instala stacks completos, não baixa
livros/datasets/modelos e não executa scripts, hooks ou serviços de terceiros.
Preservar as alterações preexistentes do checkout. Não alterar provedores,
modelos, autenticação, MCPs ativos ou permissões.

## Fontes a triar

1. `remotion-dev/codex-plugin`
2. `remotion-dev/chromium`
3. `deepseek-ai/dsh-superagent-prototype`
4. `cclank/lanshu-openai-media-api`
5. `Crosstalk-Solutions/project-nomad` (reconciliação da R1022)
6. `asoutelino-svg/awesome-reverse-engineered`
7. `asoutelino-svg/book-finder`
8. `asoutelino-svg/book-to-skill`
9. `asoutelino-svg/llm-legislativo`
10. `asoutelino-svg/ciencia-de-dados-cibele-russo`
11. `asoutelino-svg/leis_brasileiras`

O link da organização `remotion-dev` é navegação, não um repositório nem
autorização recursiva para importar todos os seus projetos. Fonte indisponível
permanece explicitamente não avaliada; não inventar licença ou commit.

## Entregáveis previstos

- Manifesto original em `federation/repository-curation-r1023.json`, com URL,
  revisão observada, recibos de consulta, licença declarada/limitações,
  sobreposição local, decisão e contribuição. Não converter itens em MCPs.
- Skills originais `.opencode/skills/livro-para-skill/` e
  `.opencode/skills/legislacao-brasileira-auditavel/`, com referências próprias
  e exemplos positivos/negativos. O material de origem é dado não confiável,
  jamais instrução com autoridade para executar comandos.
- Referências complementares nas rotas existentes de federação, audiovisual
  e REA/reversa, somente quando a fonte efetivamente justificar sua inclusão.
- Relatório `docs/CURADORIA_REPOS_R1023.md` e teste determinístico local.
- `integrations/source_skill_contracts.py`: verificador original, sem rede,
  de registros de evidência para as duas skills; CLI recebe JSON por stdin
  (até 1 MiB), retorna `candidate_for_review` ou `blocked`. Não verifica o
  conteúdo remoto, não certifica licença/vigência e nunca instala uma skill.

## Critérios de aceitação executáveis (RED → GREEN → REFACTOR)

- `R1023-1`: os 11 repositórios têm decisão explícita, origem e limites;
  consulta bem-sucedida fixa commit e registra URL, tamanho e SHA-256 dos
  documentos inspecionados. Licença do código não licencia livros, dados,
  modelos, marcas nem todo o conteúdo de links transitivos.
- `R1023-2`: as duas skills usam caminhos nativos e frontmatter coerente;
  descoberta pelo Core e links locais válidos, sem IDs duplicados introduzidos.
- `R1023-3`: livro→skill exige direitos, cobertura, localizador e hash da fonte,
  extração separada de inferência, escopo mínimo, testes e preservação do original;
  falta de texto/edição/direitos impede afirmações indevidas, não gera páginas.
  O verificador recusa direitos desconhecidos, sumário de IA como fonte primária,
  ausência de texto/localizador, SHA inválido e execução de instruções da fonte.
- `R1023-4`: legislação exige jurisdição, data de referência e fonte oficial;
  distingue norma, proposta, redação histórica e vigência não verificada;
  reutiliza o catálogo existente sem alegar cobertura nacional exaustiva.
  O verificador aceita somente HTTPS sem credenciais para hosts oficiais
  explicitamente enumerados; domínio por sufixo não basta. Recusa proposição
  rotulada como norma e toda tentativa de certificar automaticamente vigência.
  Validação estrutural do registro não autentica a fonte nem consulta a URL.
- `R1023-5`: REA, PDF/biblioteca e MCP legal existentes são reutilizados;
  nenhuma importação executável, instalação, ativação ou override de modelo;
  contratos negativos não permitem tratar registro como execução.

## Protocolo e evidência

Spec antes das alterações. RED real com artefatos ainda ausentes, seguido de
implementação, GREEN e revisão. Não reconstruir cronologia nem adulterar módulo
para fabricar RED. Os testes de skills verificam estrutura, contratos e exemplos;
não provam obediência futura de LLM, mérito jurídico ou execução do software remoto.
Aplicar SpecVerifier ao mesmo conjunto de testes e registrar os recibos reais.
Se o gate for bloqueado por ambiente, relatar o bloqueio sem declarar aprovação.

## Exclusões

Sem alegação de preservação/migração dos dados antigos do Qdrant, fallback
automático de modelos, encerramento do gate R1019, execução das skills por LLM,
edição/render de vídeo ou qualidade externa. Esses pontos não são comprovados
pela presente curadoria. A auditoria é limitada aos arquivos efetivamente lidos.
