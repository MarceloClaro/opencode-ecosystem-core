---
spec_id: SPEC-935-R921
title: Inventário e extração seletiva de instruções de plugins locais
component: integrations.local_plugin_extraction, integrations.scientific_plugins
status: proposed
test_file: tests/test_r921_local_plugin_extraction.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    api_minima:
    - tests/test_r921_local_plugin_extraction.py::test_public_api_is_callable
    inventario_evidencia:
    - tests/test_r921_local_plugin_extraction.py::test_inventory_is_deterministic_read_only_non_authoritative_evidence
    namespaces:
    - tests/test_r921_local_plugin_extraction.py::test_only_present_authorized_namespaces_are_inspected
    sem_autorregistro:
    - tests/test_r921_local_plugin_extraction.py::test_unknown_manifest_cannot_register_or_authorize_a_plugin
    manifestos_locais:
    - tests/test_r921_local_plugin_extraction.py::test_supported_local_manifest_locations_share_the_same_contract
    licencas_permissivas:
    - tests/test_r921_local_plugin_extraction.py::test_recognizable_concordant_permissive_license_text_is_required
    licencas_insuficientes:
    - tests/test_r921_local_plugin_extraction.py::test_missing_spdx_only_conflicting_and_proprietary_licenses_are_reference_only
    licencas_por_subpasta:
    - tests/test_r921_local_plugin_extraction.py::test_nested_restriction_is_not_read_or_copied
    - tests/test_r921_local_plugin_extraction.py::test_permissive_child_cannot_relicense_a_restricted_ancestor
    proprietarios_conhecidos:
    - tests/test_r921_local_plugin_extraction.py::test_anthropic_document_skill_bodies_are_never_loaded
    host_sem_skills:
    - tests/test_r921_local_plugin_extraction.py::test_host_only_manifest_is_reference_only_without_transport_read
    filtro_instrucional:
    - tests/test_r921_local_plugin_extraction.py::test_only_instructional_text_license_notice_and_policy_are_copied
    - tests/test_r921_local_plugin_extraction.py::test_executable_text_is_excluded_without_reading
    - tests/test_r921_local_plugin_extraction.py::test_binary_or_non_utf8_instruction_is_rejected_before_writing
    catalogo_canonico:
    - tests/test_r921_local_plugin_extraction.py::test_new_plugins_use_the_canonical_catalog_and_pinned_sources
    delegacao_canonica:
    - tests/test_r921_local_plugin_extraction.py::test_public_extraction_delegates_to_canonical_service_without_legacy_sync
    integracao_canonica:
    - tests/test_r921_local_plugin_extraction.py::test_extract_eligible_installs_in_the_existing_registry_with_hashes_and_policy
    preservacao_registro:
    - tests/test_r921_local_plugin_extraction.py::test_existing_canonical_entries_survive_selective_extraction_and_repeat
    integridade_destino:
    - tests/test_r921_local_plugin_extraction.py::test_tampered_destination_is_not_overwritten_or_advertised_ready
    selecao_explicita:
    - tests/test_r921_local_plugin_extraction.py::test_selection_is_explicit_nonempty_unique_and_known_before_writing
    caminhos_identidade:
    - tests/test_r921_local_plugin_extraction.py::test_request_ids_cannot_be_paths
    - tests/test_r921_local_plugin_extraction.py::test_manifest_identity_version_and_skill_paths_cannot_escape
    - tests/test_r921_local_plugin_extraction.py::test_single_registered_id_must_match_pinned_source_and_version
    manifestos_ambiguos:
    - tests/test_r921_local_plugin_extraction.py::test_duplicate_json_keys_and_conflicting_manifests_are_rejected
    - tests/test_r921_local_plugin_extraction.py::test_duplicate_plugin_identity_across_packages_or_versions_is_rejected
    credenciais_por_nome:
    - tests/test_r921_local_plugin_extraction.py::test_sensitive_files_are_rejected_without_reading_and_before_batch_write
    segredo_no_texto:
    - tests/test_r921_local_plugin_extraction.py::test_secret_material_in_an_instruction_is_rejected_without_payload_leak
    texto_nao_secreto:
    - tests/test_r921_local_plugin_extraction.py::test_public_authentication_guidance_is_not_a_credential
    links_origem:
    - tests/test_r921_local_plugin_extraction.py::test_source_symlinks_are_rejected_even_inside_the_cache
    - tests/test_r921_local_plugin_extraction.py::test_special_source_files_are_rejected_without_opening
    raizes:
    - tests/test_r921_local_plugin_extraction.py::test_missing_file_and_symlink_cache_roots_are_rejected
    - tests/test_r921_local_plugin_extraction.py::test_cache_destination_overlap_is_rejected_without_writing
    confinamento_destino:
    - tests/test_r921_local_plugin_extraction.py::test_destination_symlink_escape_is_rejected_without_touching_outside
    limites:
    - tests/test_r921_local_plugin_extraction.py::test_package_limit_is_enforced_before_writing
    - tests/test_r921_local_plugin_extraction.py::test_per_package_file_limit_counts_excluded_files_too
    - tests/test_r921_local_plugin_extraction.py::test_single_file_byte_limit_is_enforced_before_body_read
    - tests/test_r921_local_plugin_extraction.py::test_total_byte_limit_is_enforced_before_writing
    colisao_destino:
    - tests/test_r921_local_plugin_extraction.py::test_existing_divergent_package_is_preserved_without_registry_creation
    registro_invalido:
    - tests/test_r921_local_plugin_extraction.py::test_invalid_retained_registry_is_rejected_without_replacing_it
    transacao:
    - tests/test_r921_local_plugin_extraction.py::test_registry_commit_failure_rolls_back_new_packages_and_cleans_staging
    deriva_origem:
    - tests/test_r921_local_plugin_extraction.py::test_source_change_before_registry_commit_aborts_and_cleans_staging
    sem_efeitos_externos:
    - tests/test_r921_local_plugin_extraction.py::test_import_hooks_transport_and_host_calls_never_execute
    autorizacao_nao_inferida:
    - tests/test_r921_local_plugin_extraction.py::test_result_does_not_claim_authentication_activation_or_external_validation
---

# R921 — extração local seletiva sob marceloclaro

## Autorização, fase e não objetivos

CFP `core-academic-mirofish-local-plugins`, fase 1: **somente esta spec e os
testes correspondentes**. Não implementar, copiar plugins reais, fazer bulk
sync, ativar skills, instalar, autenticar, executar hooks, consultar rede,
registrar agentes, alterar fachadas, publicar ou comitar nesta fase. Não rodar
`TDDHistory`: outro agente escreve testes em paralelo. Um pytest focal pode
demonstrar RED, sem representar aprovação SDD/BehavioralGate.

A pesquisa comunicada pelo primário encontrou o cache autorizado em
`/mnt/c/Users/marce/.codex/plugins/cache`, 25 IDs já presentes no catálogo
canônico e dois candidatos adicionais: `openai-curated-remote/zotero/0.1.2`
e `openai-curated-remote/sequence-viewer/0.1.52`, com indicação MIT a confirmar
no momento da operação. Estes dados **não** autorizam leitura do cache nesta
fase nem comprovam licença, prontidão ou autenticação de qualquer instalação.
Os testes usam exclusivamente caches sintéticos em `tmp_path`.

É proibido carregar/copiar corpos proprietários, inclusive
`anthropic-skills/skills/{docx,pdf,pptx,xlsx}`. Não ler `auth.json`, cookies,
`.env`, histórico ou credenciais. Os nomes acima são critérios de recusa,
não fontes para investigação. Licença permissiva na raiz não revoga restrições
em subpastas. Disponibilidade no host não transfere OAuth ou transporte ao Core.

## API final proposta

Novo módulo `integrations/local_plugin_extraction.py`, sem efeitos no import:

```python
def inventory_local_plugins(cache_root: str | Path) -> dict: ...
def extract_local_plugins(
    cache_root: str | Path, destination_root: str | Path, plugin_ids: list[str]
) -> dict: ...
```

`destination_root` significa **raiz de repositório do Core**, não raiz de cache,
pacote ou diretório livre de saída. A função de extração usa
`ScientificPluginService(destination_root).extract_eligible(...)`. Método
aditivo proposto, utilizável pelo primário sem nova fachada nesta etapa:

```python
ScientificPluginService(repo_root).extract_eligible(
    *, cache_root: str | Path, plugin_ids: list[str]
) -> dict
```

Foi inspecionada a classe real `ScientificPluginService`, em
`integrations.scientific_plugins`: construtor `repo_root`, métodos `status()`,
`skill(plugin_id, skill_name)`, `sync(...)`, `_registry()`. O armazenamento
canônico é `.opencode/scientific-plugins/registry.json` e os pacotes ficam em
`.opencode/scientific-plugins/packages/<id>/<version>`. A extração seletiva
**não chama `sync()`** nem usa cópia integral de árvore. Implementação futura
pode ter helpers privados; não expor segundo serviço/registro autoritativo.

Acrescentar ao `PLUGINS` canônico, preservando os IDs anteriores:

| ID | Nome | Origem relativa | Versão fixada |
| --- | --- | --- | --- |
| `zotero` | Zotero | `openai-curated-remote/zotero` | `0.1.2` |
| `sequence-viewer` | Sequence Viewer | `openai-curated-remote/sequence-viewer` | `0.1.52` |

Pacotes desconhecidos podem constar como evidência `reference_only`, mas não
se autorregistram. Manifestos locais não alteram `PLUGINS`, `HOST_OPERATIONS`
ou permissões. IDs registrados devem coincidir com origem/versão fixadas;
ID duplicado em outro caminho/versão é ambiguidade, não escolha de “latest”.

## Formatos de entrada e evidência

Descobrir apenas `<namespace>/<diretorio>/<versao>`, sem recursão ilimitada.
Namespaces autorizados: `openai-curated-remote`, `openai-bundled`,
`claude-cowork`, `created-by-me-remote`. Namespace ausente não é erro; namespace
desconhecido não é percorrido/lido. O acesso é somente leitura, sem default
para diretórios pessoais e sem sondar ancestrais/siblings do cache informado.

Manifestos reconhecidos: `.codex-plugin/plugin.json`,
`.claude-plugin/plugin.json`, `plugin.json`. Projetar apenas identidade
(`name` como ID slug, `version`), licença declarada e caminhos instrucionais
locais seguros; não copiar o manifesto nem seguir URLs/transporte MCP.
JSON com chaves duplicadas, identidade ambígua entre manifestos ou valores
de identidade/caminho inválidos é recusado. `skills: "./skills"` é permitido;
traversal, caminhos absolutos, separadores Windows e componentes `..` não são.

`inventory_local_plugins` retorna JSON serializável e determinístico, sem
timestamps mutáveis, corpos de skills, descrições privadas, transporte ou
credenciais. Campos obrigatórios:

* `schema_version: 1`, `kind: "local_plugin_evidence"`, `authoritative: false`;
* `cache_root` resolvido; `plugins` ordenados por ID/origem/versão;
* `limits` com os quatro limites abaixo;
* `executed: false`, `credentials_copied: false`, `hooks_executed: false`,
  `transport_imported: false`, `host_authentication: "not_verified"`,
  `external_validation: false`;
* cada plugin: `id`, `namespace`, `version`, `source_root`, `manifest_path`
  relativo, `manifest_sha256`, `disposition` (`eligible` ou `reference_only`),
  `reason_codes`, `files` (caminho relativo → SHA-256 dos arquivos elegíveis),
  `license_evidence` (lista de `{path, spdx, sha256}` de textos de licença).

O relatório é evidência local, **não registry** nem autorização para carregar
instruções. Host-only sem `SKILL.md`, proprietários, licença ausente,
SPDX isolado/sem texto reconhecível ou declaração discordante ficam
`reference_only`; extração solicitada deles não copia nada e os relaciona em
`reference_only`. Reason codes estáveis usados nos testes: `no_local_skills`,
`license_missing`, `license_text_unverified`, `license_conflict`,
`license_restricted`, `not_catalogued`. Podem ser aditivos; não conter conteúdo sensível.

## Política instrucional e licenças

Elegíveis somente MIT, Apache-2.0, BSD-2-Clause ou BSD-3-Clause com texto
reconhecível concordante em `LICENSE`, `LICENSE.txt`, `LICENSE.md` ou
equivalente `LICENCE` local. SPDX em manifesto/skill/README, por si só, não é
evidência. Fazer preflight de nomes/tipos/tamanhos e ler licenças antes dos
corpos instrucionais. Uma restrição/contradição em qualquer ancestral da
instrução bloqueia aquele ramo; filhos não podem “relicenciar” um ancestral
restritivo. Não ler corpo de ramo bloqueado, nem mesmo para calcular hash.
Os quatro ramos proprietários conhecidos permanecem bloqueados mesmo se
uma raiz ou manifesto falsamente anunciar MIT. Testes usam textos artificiais
reconhecíveis; a triagem automatizada não é parecer jurídico.

Allowlist de materiais: `skills/<skill>/SKILL.md`, referências textuais
`.md/.txt/.rst` dentro de `skills/<skill>/references/`, documentos textuais
nessas extensões sob `docs/`, `README.md` na raiz, `agents/openai.yaml` de cada
skill **somente como política de invocação**, e `LICENSE*`/`LICENCE*`/`NOTICE*`
dos ramos elegíveis. Preservar bytes UTF-8, nomes relativos, hashes, textos
de licença/NOTICE e política explícita (incluindo
`disable-model-invocation: true`/`allow_implicit_invocation: false`).

Não ler/copiar scripts, binários, executáveis, imagens, arquivos arbitrários,
hooks, agentes executáveis, `.git`, transporte (`mcp.json`/`.mcp.json`),
configuração de host ou payloads de manifestos. A recusa estrutural de links,
arquivos especiais/credenciais vale também dentro de caminhos excluídos.
Arquivos comuns excluídos não invalidam um pacote: apenas não são importados.
Extensão textual não autoriza bytes binários: leitura limitada de candidato
deve recusar NUL/UTF-8 inválido antes da cópia. Bit executável exclui arquivo
regular antes de abrir seu corpo, mesmo com extensão `.md`.
Proprietários nunca chegam a `service.skill(...)` pelo novo caminho.

Segredos em texto elegível causam recusa do lote com diagnóstico sanitizado,
incluindo atribuição concreta de chave/token, `Authorization: Bearer <valor>`
e chave privada PEM. Palavras isoladas como “authorization” em orientação
pública não são credenciais. Isto é defesa delimitada, não garantia universal
de detecção de segredos. Por nome, `.env` e variantes (inclusive exemplos),
`auth.json`, `credentials.json`, `tokens.json`, `cookies.sqlite`,
`history.jsonl`, `id_rsa` e equivalentes sensíveis são recusados **sem leitura**.

## Limites e validação antes da escrita

Constantes de política no novo módulo, reduzíveis nos testes (não novos
parâmetros públicos): `MAX_PACKAGES = 64`, `MAX_FILES_PER_PACKAGE = 256`,
`MAX_FILE_BYTES = 1_048_576`, `MAX_TOTAL_BYTES = 16_777_216`. `limits` usa as
chaves `max_packages`, `max_files_per_package`, `max_file_bytes`,
`max_total_bytes`. Contar todos os arquivos regulares descobertos, inclusive
excluídos; usar stat/lstat limitado para não carregar corpos excedentes ou
proibidos. Total agregado no cache autorizado/lote, não teto renovado por
pacote. Valores de teste menores não dependem de alocações volumosas.

Erros de entrada/segurança levantam `ValueError` antes de publicar ou criar
destinos/staging. Códigos sanitizados: `invalid_selection`, `unknown_plugin`,
`unsafe_path`, `duplicate_manifest`, `duplicate_plugin_id`, `sensitive_file`,
`secret_material`, `limit_exceeded`, `invalid_cache`, `source_destination_overlap`,
`destination_conflict`, `invalid_registry`, `source_changed`. I/O genuíno pode
propagar `OSError`; nunca escrever payload de arquivo/segredo no diagnóstico.
`source_mismatch` recusa identidade/origem/versão divergente do catálogo;
`unsafe_instruction` recusa candidato textual com bytes binários/UTF-8 inválido.

Seleção obrigatória é lista não vazia de IDs únicos, registrados e presentes;
`None` não significa bulk. Validar lote inteiro antes de escrever qualquer
plugin. Recusar symlinks (inclusive internos e componentes de raiz), traversal,
arquivos especiais, ID duplicado entre fontes/versões e identidade/versão
contrária ao catálogo. Não seguir caminhos fornecidos em manifestos para ler
credenciais ou arquivos externos. Recusar cache ausente/arquivo/symlink.

Recusar sobreposição em qualquer direção entre cache e `destination_root`,
symlinks na raiz ou árvore canônica de destino (incluindo registry e pacotes)
e colisão de saída com fontes. Apenas descendentes físicos do storage
canônico podem ser publicados. Não sobrescrever pacote divergente; repetição
idêntica é idempotente. Validar também entradas preexistentes do registry,
preservando-as; registry inválido não é substituído por um “limpo”.

## Transação, integração e ausência de ativação

Pré-validar tudo, preparar apenas arquivos elegíveis em staging local, conferir
hashes e estabilidade de origem. Publicar diretórios de pacote por
`os.rename`/`os.replace`, mantendo registry como ponto de commit, publicado
atomicamente por `os.replace`. Revalidar origem imediatamente antes desse
commit, inclusive após promover diretórios. Mudança de corpo, licença ou
manifesto durante a operação aborta. Falha de commit remove somente pacotes
novos desta transação e staging/ancestrais vazios criados; não deixar pacote
parcial ou registro de sucesso. Não reverter modificações externas na origem.
Não prometer recuperação contra queda de energia ou escritores concorrentes
não cooperativos; lock/journal durável são evolução futura.

`plugins` do retorno de extração contém as entradas efetivamente instaladas,
no mesmo formato canônico existente (`id`, `name`, `version`, `source_root`,
`package_root`, `files`, `skills`, `origin: "third_party_or_user"`). Não há
segundo registry; evidência adicional (licença, manifesto, limites) vai no
relatório retornado, campo `evidence`, com `limits` no topo. Retorno:
`status: "completed"`, `plugins`, `reference_only`, `evidence`, `limits` e os
seis indicadores negativos de execução/autenticação do inventário. Sem
elegíveis: nenhuma escrita, `plugins: []`. Status/skill canônicos conferem
hashes da cópia filtrada e política preservada. Apenas integridade local é
avaliada; não há “ativação”, conector, OAuth, validação externa ou confiança
instrucional automática. A fachada/alias científico é responsabilidade
posterior do primário e não é requisito de R921.

## Critérios de Aceitação Executáveis

- `api_minima` — duas funções públicas importáveis; ausência falha em assert no corpo, não na coleta/setup.
- `inventario_evidencia` — relatório determinístico, rastreável, não autoritativo e somente leitura.
- `namespaces` — visitar só namespaces autorizados presentes, sem ler os demais.
- `sem_autorregistro` — manifesto desconhecido permanece evidência e não altera o catálogo canônico.
- `manifestos_locais` — as três localizações declaradas de manifesto têm a mesma semântica segura.
- `licencas_permissivas` — MIT/Apache/BSD com evidência textual concordante habilitam somente instruções.
- `licencas_insuficientes` — ausência, SPDX isolado, contradição e proprietário são reference_only, sem cópia.
- `licencas_por_subpasta` — restrição local bloqueia seu ramo antes de carregar o corpo.
- `proprietarios_conhecidos` — docx/pdf/pptx/xlsx de anthropic-skills nunca são carregados.
- `host_sem_skills` — manifestos host-only não carregam transporte nem entram no registry de instruções.
- `filtro_instrucional` — cópia positiva de textos/licenças/políticas e negativa de código/hooks/binários/transporte.
- `catalogo_canonico` — novos IDs/versões/origens usam PLUGINS existente, sem autoridade do cache.
- `delegacao_canonica` — a API pública usa extract_eligible, nunca sync legado.
- `integracao_canonica` — uma extração serve status/skill no storage canônico com hashes/política.
- `preservacao_registro` — preservar entradas anteriores, seleção restrita e idempotência.
- `integridade_destino` — adulteração bloqueia leitura e reextração sem sobrescrita.
- `selecao_explicita` — não aceitar bulk implícito, vazios, duplicados, tipos errados ou IDs ausentes.
- `caminhos_identidade` — IDs/versões/caminhos não escapam das raízes físicas.
- `manifestos_ambiguos` — chaves duplicadas, manifestos discordantes e identidade repetida são recusados.
- `credenciais_por_nome` — não ler arquivos sensíveis e recusar lote antes da primeira cópia.
- `segredo_no_texto` — rejeitar valores secretos sintéticos sem vazá-los em erro/saída.
- `texto_nao_secreto` — orientação pública sobre autenticação não é segredo por mero vocabulário.
- `links_origem` — links internos/externos em qualquer parte do pacote são recusados.
- `raizes` — raízes inválidas e sobreposição cache/destino não produzem escrita.
- `confinamento_destino` — links de destino não alteram raízes externas.
- `limites` — limites de pacotes/arquivos/arquivo/total incluem materiais excluídos e precedem leitura/escrita.
- `colisao_destino` — pacote preexistente divergente é preservado sem registry novo.
- `registro_invalido` — registro retido inválido não é saneado silenciosamente.
- `transacao` — falha de commit mantém estado anterior e limpa staging/pacotes novos.
- `deriva_origem` — mudança antes do commit aborta sem desfazer a mudança externa.
- `sem_efeitos_externos` — import/extração não executam hooks, shell, rede ou chamadas de host.
- `autorizacao_nao_inferida` — resultados não promovem importação a auth, ativação ou validação externa.

## Plano de evidência desta fase

Coletar e executar apenas `tests/test_r921_local_plugin_extraction.py`, com
rede/subprocess/host bloqueados e leitura de corpos proibidos vigiada.
Todos os testes chamam um helper que executa `assert find_spec(...)` **no
corpo do teste**, antes de importar o módulo novo. Nenhuma fixture depende
dele; não usar `pytest.fail`, skip/xfail ou erro de import como RED.
Nodeids sem parametrização são exatos no frontmatter. Antes de futura entrega
de implementação, o primário deverá obter GREEN, revisão SpecVerifier e gate
comportamental; esta fase não os substitui nem altera histórico TDD/ciclos.
