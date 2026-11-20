---
spec_id: SPEC-935-R1251
title: Instalação isolada do SDK Tiangong no Linux
component: external_sdk.gjq_client
status: proposed
test_file: tests/test_r1251_gjq_client_isolated_install.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    AC1:
      - tests/test_r1251_gjq_client_isolated_install.py::test_official_release_is_importable_only_from_isolated_venv
    AC2:
      - tests/test_r1251_gjq_client_isolated_install.py::test_local_sdk_symbols_import_without_cloud_authentication
    AC3:
      - tests/test_r1251_gjq_client_isolated_install.py::test_isolated_python_environment_and_distribution_origin
    AC4:
      - tests/test_r1251_gjq_client_isolated_install.py::test_smoke_does_not_construct_cloud_client_or_submit_jobs
---

# SPEC-935-R1251 — Instalação isolada do SDK Tiangong no Linux

## Demanda e autoridade

Validar a alternativa compatível com Linux após o checkout editável
`guoji-quantum/gjq_client` declarar suporte exclusivo a Windows x64. O usuário
escolheu explicitamente instalar o pacote publicado no PyPI em um ambiente
virtual isolado. A versão alvo é `gjq-client==0.2.2`, coerente com o checkout
inspecionado; qualquer divergência de publicação bloqueia a instalação, não
autoriza selecionar versão silenciosamente.

## Escopo

1. Criar venv dedicado em `/tmp/opencode/gjq-client-venv` usando Python 3.12.
2. Instalar apenas o release PyPI pinado e suas dependências nesse venv.
3. Validar import do pacote e dos símbolos de simulação local por subprocesso
   que use o interpretador do venv, sem instanciar serviço cloud.
4. Preservar o checkout fonte `/tmp/opencode/gjq_client`; não tentar `pip install
   -e .` nele neste host Linux.

## Fora de escopo e segurança

- Não instalar no `.venv` do Core nem alterar `pyproject.toml`, lockfiles ou
  dependências do projeto.
- Não ler, criar, copiar ou exibir API key; não autenticar; não ler cache de
  conta. O smoke test usa HOME temporário vazio e remove `GJQ_API_KEY` do
  ambiente filho.
- Não construir `GJQRuntimeService`, selecionar backend, chamar API cloud,
  abrir sessão, criar/submeter/consultar job, reservar recurso ou acessar QPU.
- Não executar o pacote além de imports e inspeção de metadados; nenhum script
  de exemplo ou payload do repositório será executado.
- A instalação transfere dependências de terceiros ao venv isolado; não equivale
  a autenticação, acesso live ou validação de hardware.

## Critérios de aceitação executáveis

- `AC1` — `gjq-client==0.2.2` importa pelo interpretador dedicado e o caminho do
  módulo reside sob `/tmp/opencode/gjq-client-venv`, sem fallback para o Core.
- `AC2` — `LocalSimulator` e `Sampler` são importáveis sem API key, service ou
  conexão cloud; o teste usa ambiente filho sem `GJQ_API_KEY` e HOME temporário.
- `AC3` — distribuição identificada como `gjq-client` versão `0.2.2`, origem de
  instalação não editável e `sys.prefix` igual ao venv dedicado.
- `AC4` — smoke test é somente importação/metadados; não cria `GJQRuntimeService`,
  não chama `.run()` e não executa submissão de job.
- Todos os critérios têm teste vinculado; instalar é posterior a RED formal e
  GREEN/SpecVerifier ocorre depois da instalação, junto de regressão focal.

## Evidência e limitações

- Checkout upstream clonado em `/tmp/opencode/gjq_client`, commit
  `a37d9eacbbb783699c70f50eee48df332f57ab5e`.
- `setup.py` do checkout contém um bloqueio explícito para plataformas distintas
  de Windows x64; o ambiente de execução é Linux com Python 3.12.3.
- README upstream orienta usuários Linux/macOS a instalar o release PyPI, não a
  editar esse checkout binário. A documentação web é referência, não argumento
  de instalação do `pip`.
- Evidência de instalação/import local não comprova disponibilidade dos backends,
  conectividade, elegibilidade da conta, qualidade do simulador ou execução QPU.
