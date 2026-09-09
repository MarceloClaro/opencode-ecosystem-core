# SPEC-935-R470 — Resolvedor de acesso restrito opcional e auditável (padrão open_science_only preservado)

## Objetivo
Especificar uma capacidade opcional, desabilitada por omissão e auditável, para resolução de acesso restrito mediante autorização humana explícita e declaração de base legal com evidência. Preservar integralmente o padrão `open_science_only` de `article_retrieval.py`, sem alterar `DEFAULT_SOURCES=[openalex,crossref,europepmc,arxiv]` e sem introduzir fallback automático para fontes restritas.

## Não-objetivos
- Não tornar sci-hub, scihub-cli ou qualquer resolvedor restrito padrão, dependência padrão ou fallback automático.
- Não automatizar, facilitar ou orientar violação de controles de acesso, paywalls, termos contratuais ou medidas tecnológicas de proteção.
- Não prestar aconselhamento jurídico, parecer sobre titularidade ou validação de direito de acesso.
- Não redistribuir, republicar ou compartilhar cópias obtidas via acesso restrito; PDFs conservam os direitos originais nos termos de `THIRD_PARTY_NOTICES`.

## Invariantes
1. O padrão do sistema permanece `open_science_only`; `choose_pdf` somente retorna cópia aberta com `rights_basis` em `open_access/preprint` ou `not_verified_open`.
2. Todo resolvedor de acesso restrito nasce desabilitado por omissão (`fail-closed`); ausência de configuração equivale a negação.
3. É vedado qualquer fallback automático do fluxo aberto para fluxo restrito; a transição exige invocação explícita e autorizada.
4. Nenhuma execução restrita ocorre sem autorização humana explícita acumulada à declaração de base legal com referência de evidência, ambas registradas em recibo.
5. Nenhum despacho de resolvedor externo utiliza `shell=True`; argumentos são passados como lista, sem interpolação de shell.
6. Somente resolvedores constantes de allowlist explícita, versionada e auditável podem ser despachados; descoberta local não autoriza uso.
7. Toda tentativa autorizada ou negada gera recibos auditáveis (`CLIExecutionReceipt` e recibo de download estendido) com identificador de autorização, resolvedor e limitações.
8. O orquestrador `marceloclaro` permanece o único coordenador autorizado a avaliar gates e ordenar o despacho; é vedada delegação direta que contorne o orquestrador.
9. Nenhum gate é contornável por variável de ambiente ambígua, valor padrão, ordem de fontes, cache ou descoberta automática; qualquer ambiguidade resulta em negação auditável.
10. Esta especificação não altera R468 (invariante 8: `scihub-cli` ausente do padrão), R469 (rejeição de default sci-hub com `fail-closed`), `SECURITY.md` (vedação de contorno sem autorização explícita) nem `THIRD_PARTY_NOTICES`.

## Modelo de autorização
O modelo é opt-in, explícito e negador por omissão, composto por três camadas cumulativas: variáveis de ambiente, flags de invocação e política `allow/ask/deny`.

Variáveis de ambiente (todas ausentes ou vazias equivalem a negado): `RESTRICTED_RESOLVER_ENABLED` (`0/1`, omissão `0`); `RESTRICTED_RESOLVER_POLICY` (`deny/ask/allow`, omissão `deny`); `RESTRICTED_RESOLVER_ALLOWLIST` (lista delimitada, omissão vazia); `RESTRICTED_RESOLVER_AUTHORIZATION_ID` (identificador da autorização humana); `RESTRICTED_RESOLVER_RIGHTS_BASIS` (declaração textual da base legal alegada); `RESTRICTED_RESOLVER_EVIDENCE_REF` (referência verificável à evidência, ex.: identificador de chamado, registro institucional ou referência catalográfica, sem conteúdo protegido).

Flags de invocação (exigem confirmação interativa salvo prova de operador humano registrado): `--enable-restricted-resolver`, `--resolver <nome-na-allowlist>`, `--authorize <authorization_id>`, `--rights-basis "<declaração>"`, `--evidence-ref "<referência>"`. A ausência de qualquer flag obrigatória implica negação com código de saída específico e recibo de negação.

Política `allow/ask/deny`: `deny` bloqueia toda tentativa; `ask` exige confirmação humana interativa adicional mesmo com flags presentes; `allow` permite apenas se habilitação, allowlist, autorização, base legal e evidência forem simultaneamente válidas. Nenhuma política promove o resolvedor a padrão ou altera a ordem de `DEFAULT_SOURCES`.

Exemplos de base legal aceitável para declaração (não validada pelo sistema, apenas registrada): assinatura institucional mediante proxy ou VPN institucional com evidência de vínculo vigente; cópia fornecida diretamente pelo autor com evidência da comunicação ou repositório do autor; obra em domínio público com evidência da fundamentação (data, norma aplicável, fonte catalográfica). A evidência é obrigatória, deve ser referenciável sem anexar conteúdo protegido e é registrada verbatim no recibo.

É vedado qualquer uso sem base legal declarada e sem evidência referenciada; declaração genérica, ausente ou não referenciada implica bloqueio. O sistema não verifica a veracidade ou suficiência jurídica da declaração; limita-se a exigir, registrar e auditar.

## Contratos e recibos
Toda operação restrita, deferida ou negada, emite `CLIExecutionReceipt` com: `command`, `resolver` (nome pleiteado ou `none`), `policy_effective` (`deny/ask/allow`), `enabled_effective` (booleano), `authorization_id` (ou `null`), `decision` (`allowed/denied`), `deny_code` (quando negado), `timestamp_utc`, `orchestrator` (`marceloclaro`) e `hash_sha256` do recibo.

O recibo de download, quando a execução for autorizada, estende o recibo aberto vigente com os campos obrigatórios: `resolver` (valor da allowlist); `rights_basis_human_declared` (texto declarado pelo humano, marcado como não verificado pelo sistema); `authorization_id` (identificador correlacionável ao `CLIExecutionReceipt`); `evidence_ref` (referência fornecida, sem conteúdo protegido); `limitations` (lista fixa incluindo `no-redistribution`, `original-rights-retained`, `jurisdiction-dependent`, `not-legal-advice`). Recibos de negação preservam os mesmos campos com valor `null` onde inaplicável e motivo de negação explícito. Nenhum arquivo é persistido sem recibo correspondente íntegro.

## Critérios de aceitação
- CA1: O padrão permanece inalterado; sem configuração restrita, `policy=open_science_only` e `DEFAULT_SOURCES=[openalex,crossref,europepmc,arxiv]` são observáveis em teste.
- CA2: Sem `--enable-restricted-resolver` e sem `RESTRICTED_RESOLVER_ENABLED=1`, qualquer pleito restrito permanece bloqueado e gera recibo de negação.
- CA3: Sem `--authorize` e sem `RESTRICTED_RESOLVER_AUTHORIZATION_ID` válido, o despacho é bloqueado com código de saída específico de ausência de autorização, verificável por teste.
- CA4: Sem `--rights-basis` e sem `--evidence-ref` (ou equivalentes de ambiente) válidos e não vazios, o despacho é bloqueado com código de saída específico de ausência de base legal/evidência.
- CA5: Com habilitação, política permissiva, allowlist contendo o resolvedor, autorização, base legal e evidência válidos, o despacho autorizado gera `CLIExecutionReceipt` e recibo de download estendido com todos os campos obrigatórios preenchidos.
- CA6: O despacho de resolvedor externo ocorre sem `shell=True`, com argumentos em forma de lista; teste estático ou por mock asserta a ausência de invocação via shell.
- CA7: `RESTRICTED_RESOLVER_POLICY=deny` bloqueia mesmo com todas as flags presentes; `ask` exige confirmação adicional registrada; teste cobre as três políticas.
- CA8: Mecanismos de descoberta local não promovem resolvedor restrito a padrão nem alteram a ordem de fontes; teste asserta que `DEFAULT_SOURCES` e `choose_pdf` conservam comportamento aberto.
- CA9: Resolvedor fora de `RESTRICTED_RESOLVER_ALLOWLIST` é negado mesmo quando habilitado e autorizado; teste cobre nome desconhecido e allowlist vazia.
- CA10: A suíte de testes não realiza download real de conteúdo sob paywall, não contém credenciais e utiliza mocks/fachadas; teste de rede restrita é proibido e verificado por inspeção.

## Riscos e limites honestos
Esta especificação não constitui parecer jurídico e não atesta a licitude de qualquer acesso; a juridicidade varia por jurisdição, contrato institucional, licença editorial e situação concreta do solicitante. Hash de recibo, identificador de autorização e referência de evidência proveem auditabilidade, não direito; `hash não é direito`. Não há certificação externa, validação editorial ou garantia de disponibilidade, integridade ou autenticidade de cópias restritas. O uso indevido permanece vedado por `SECURITY.md` e sujeito às responsabilidades do operador humano declarante.

## Plano TDD
RED: redigir testes de bloqueio verificando CA1–CA4 e CA7–CA10 antes de qualquer implementação: padrão inalterado, bloqueio sem flag, bloqueio sem autorização, bloqueio sem base legal/evidência, negação por política, negação fora da allowlist, ausência de `shell=True` e ausência de rede real. GREEN: implementar fachada mínima do resolvedor restrito permanentemente desabilitada por omissão, com avaliação de gates na ordem habilitação, política, allowlist, autorização, base legal e evidência, emissão de recibos de negação e despacho contido somente no caminho totalmente autorizado. VERIFY: executar `pytest` da suíte dedicada e `core-check` (incluindo diagnóstico de saúde do ambiente); considerar concluído somente com todos os CA verificados por teste e sem regressão do fluxo `open_science_only`.
