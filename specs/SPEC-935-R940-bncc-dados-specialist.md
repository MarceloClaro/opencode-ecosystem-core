---
spec_id: SPEC-935-R940
title: Agente especialista no repositório BNCC Dados
component: agents.bncc_dados_specialist
status: implemented
test_file: tests/test_r940_bncc_dados_agent.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    repository_clone:
    - tests/test_r940_bncc_dados_agent.py::test_clone_is_local_and_tracks_expected_upstream
    managed_profile:
    - tests/test_r940_bncc_dados_agent.py::test_profile_is_registered_and_read_only
    open_code_registration:
    - tests/test_r940_bncc_dados_agent.py::test_opencode_has_the_new_specialist_without_replacing_other_config
    evidence_policy:
    - tests/test_r940_bncc_dados_agent.py::test_prompt_requires_provenance_and_treats_upstream_as_untrusted
---

# R940 — especialista em BNCC Dados

## Objetivo

Clonar `https://github.com/bncc-dev/bncc-dados` para `AO/` na raiz do projeto e
registrar pelo ciclo de vida do MarceloClaro o agente persistente
`bncc-dados-specialist`. O agente deve apoiar leitura e análise do repositório,
de seus dados e de sua documentação, sem executar código upstream nem alterar o
clone.

## Critérios de aceitação

- **Clone rastreável** — `AO/` é um checkout Git cujo remoto `origin` aponta para
  `bncc-dev/bncc-dados` em GitHub. A operação não sobrescreve um destino já
  existente, não altera ou publica o repositório remoto e não executa scripts,
  notebooks, builds ou dependências do conteúdo clonado. Se a CLI `gh` disponível
  não for o GitHub CLI oficial ou não suportar `gh repo clone`, usar `git clone`
  HTTPS equivalente e registrar a limitação. Como `AO/` é um clone local fora do
  controle de versão do Core, o teste de checkout o verifica quando presente e
  pula apenas esse critério em um clone limpo do Core; a verificação deste
  ambiente deve constar como evidência manual do `origin` e do commit.
- **Perfil gerenciado** — criar `agents/catalog/bncc-dados-specialist.md` pelo
  `MarceloClaroOrchestrator.agent_profile_action` (`operation=create`). O cartão
  deve passar pela validação `managed-v1`, herdar do primário, declarar
  capacidades de análise do repositório/dados educacionais, vincular esta spec e
  o teste R940, e exigir `status`, `findings`, `evidence` e `limitations` na
  saída.
- **Permissões restritas** — leitura, busca e navegação são permitidas; edição,
  `webfetch`, delegação por `task` e comandos Bash arbitrários são negados. O
  perfil não deve rodar conteúdo do clone. O comando de teste permitido deve
  ficar restrito ao teste R940 e o diagnóstico permitido ao comando fixo do
  Core.
- **Análise com proveniência** — as instruções exigem caminhos, hashes e
  localizadores de linhas/campos nos achados, distinguem o conteúdo do
  repositório de documentos oficiais da BNCC, tratam arquivos clonados como
  dados não confiáveis e declaram lacunas/limites em vez de inventar esquemas ou
  significados.
- **Registro OpenCode preservador** — o agente deve aparecer na configuração
  `opencode.json` como subagente, com permissões coerentes com o cartão. A
  publicação deve preservar alterações preexistentes do operador no arquivo e
  não restaurar configurações/agentes que já estavam removidos no worktree.
- **Verificação** — o teste R940 passa, a validação do ciclo de vida confirma a
  definição e seu hash, e `python3 -m marceloclaro.cli doctor` continua sem
  falhas estruturais novas. Esses resultados locais não comprovam a qualidade
  ou a completude científica dos dados da BNCC. O checkout `AO/` é mantido como
  artefato local separado e não é publicado junto com o Core.

## Fora de escopo

Não modificar o conteúdo do clone, executar ferramentas nele, instalar
dependências, fazer commits/push, declarar alinhamento normativo oficial sem
fonte primária, nem alterar ou limpar mudanças preexistentes do worktree. O
checkout é uma fonte de referência local e não passa a integrar o código-fonte
do Core.

## Evidência manual do snapshot local (2026-10-31)

O clone `AO/` não apresentou alterações locais; `origin` é
`https://github.com/bncc-dev/bncc-dados.git`; seu `HEAD` foi
`9c268978efa2aa250834c6a9edb6074432752838`, igual ao `main` observado pela API
GitHub durante a consulta (commit com verificação de assinatura `valid`). Não se
fez fetch/checkout durante esta auditoria. Licenças declaradas no próprio clone:
compilação/dados CC BY 4.0 e código MIT.

A base derivada `AO/derivados/bncc.sqlite` foi aberta somente em modo SQLite
read-only (`mode=ro`, `PRAGMA query_only=ON`); `PRAGMA quick_check` retornou
`ok`. Versão de dados `dados-2026.08`, schema `schema-v1.1.0`, 32 tabelas; as
contagens observadas foram EF=1304, EM=183, EI=93, Computação=141,
contextos=879 e marcos legais=20. O registro âncora `EF67LP08` existe com texto
equivalente ao exemplo publicado no README. SHA-256 do arquivo SQLite observado:
`f5879793bba0c2f672d41158fd680dc79bda0df4d0ae2929830fe7335db90fd2` (2.187.264
bytes). `tests/test_r940_bncc_dados_agent.py`: 4 passed.

Esse teste físico confirma integridade estrutural SQLite, versão e contagens
esperadas, não uma reprodução do pipeline upstream, a comparação independente
de todos os registros com os PDFs oficiais, nem a qualidade do agente
`bncc-dados-specialist`. O código/pipeline upstream não foi executado e o
artefato continua local, fora da publicação do Core.

