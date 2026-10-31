---
spec_id: SPEC-935-R986
title: Separação entre identidade do release e validação da supercamada científica
version: 1.0.0
status: green
test_file: tests/test_r986_scientific_layer_doctor_evidence.py
---

# SPEC-935-R986 — doctor da supercamada científica com evidência explícita

## Problema

`scientific_lab.runtime.installed_status()` marca v4.1.1 como
`installed_verified` quando versão e hash do arquivo `PACKAGE_MANIFEST.sha256`
coincidem com o registro. Isso confirma somente a identidade declarada do
manifesto. O comando `doctor` executa depois dois validadores da supercamada,
mas a saída estruturada já foi impressa e não contém os resultados por
validador. No estado atual, o identificador/hash do release confere, enquanto
`validate_ecosystem.py` falha pela referência interna ausente
`references/production-hardening-reproducible-distribution.md`.

O usuário precisa distinguir instalação/identidade do pacote de prontidão
operacional e da validação executada, sem esconder a falha nem chamar integridade
de manifesto de validação externa, científica ou de segurança.

## Escopo

- Manter `status` como sondagem somente leitura sem executar validadores.
- No `doctor`, emitir um resultado estruturado por validador executado,
  incluindo nome, código de saída, estado e classe de erro segura quando houver,
  mais status agregado.
- Preservar campos existentes de compatibilidade; documentar que
  `installed_verified`/`verified_release` qualificam versão e hash esperado do
  manifesto, não a integridade arquivo a arquivo nem a saúde do pacote.
- Fazer o processo terminar com código diferente de zero quando qualquer
  validador falhar, ainda que a identidade do release seja reconhecida.
- Limitar o tempo de cada validador e tratar timeout/erro de execução como
  falha estruturada, sem vazar stdout/stderr arbitrário.
- Cobrir, em testes herméticos, cenário de identidade correta e validador
  falhando, cenário de sucesso, erro/timeout, e garantir que `status` não execute
  validadores.

## Invariantes e fora de escopo

1. Não editar nem reparar a instalação fora do workspace em
   `~/.local/share/pesquisador-universal/skill` nesta alteração.
2. Não chamar conectores científicos, rede, downloaders, ferramentas hospedadas
   ou credenciais durante os testes.
3. Não incluir stdout/stderr arbitrário dos scripts externos no relatório
   estruturado; registrar somente nomes e códigos de saída.
4. Não reclassificar a capacidade científica nativa do Core se o fallback
   externo falhar.
5. Este doctor é diagnóstico computacional. Não constitui revisão humana,
   verificação externa, validação científica, certificação de release ou
   autorização editorial.

## Critérios de aceitação

1. `installed_status` expõe claramente o escopo limitado da checagem de versão
   e hash do manifesto, preservando compatibilidade com consumidores existentes.
2. O comando `status` não inicia scripts de validação.
3. A resposta de `doctor` inclui `package_validation.status` e uma entrada para
   cada validador (`validate_contracts.py`, `validate_ecosystem.py`) com
   `exit_code` e estado; saída malsucedida não pode coexistir com um resumo
   agregado de sucesso.
4. `doctor` retorna zero somente quando o Core é compatível, a identidade
   declarada do release confere e todos os validadores terminam com código zero.
5. Cada validador possui timeout finito; timeout e erro de execução são
   relatados como falha, sem inserir texto livre stdout/stderr no JSON.
6. Testes herméticos demonstram falha, sucesso, timeout e erro sem executar a
   instalação real nem usar rede.
7. Testes existentes de despacho nativo e fallbacks permanecem verdes.

## RED/GREEN

RED: testar que a estrutura atual não expõe escopo limitado nem códigos por
validador e que a falha do validator não se reflete em resultado estruturado.
GREEN: implementar o relatório, manter a fronteira entre identidade e
validação e passar os testes deste arquivo e das regressões da bridge.

## Evidência de execução

RED: os seis casos de contrato adicionados inicialmente falharam na estrutura
antiga (escopo do manifesto ausente, retorno inteiro do validador, ausência de
timeout e doctor sem resultado estruturado). Um teste que `status` não executa
validadores já passou. GREEN: a nova suíte R986: **7 passed**; regressões R984,
camada nativa, bridge v4.1, governança, SDD/TDD e BNCC R940/R942: **58 passed**
no conjunto direcionado. `tests/test_sdd_tdd.py` está incluído.

Sondagem real, sem alterar a instalação em `~/.local/share`: `status` reconhece
a identidade v4.1.1 e hash esperado do manifesto, explicitamente sem validar os
arquivos individuais. `doctor` reportou `doctor_status=degraded` e
`package_validation.status=failed`: `validate_contracts.py` exit 0 e
`validate_ecosystem.py` exit 1, devido à referência interna ausente
`references/production-hardening-reproducible-distribution.md`. O resultado
negativo foi preservado no exit code do `doctor`; a camada nativa v4.2 continua
separada. O verificador genérico de pacotes científicos também bloqueou o
pacote OdontoCA por incompatibilidade de formato, conforme SPEC-985.

Apenas validações locais, herméticas e diagnósticos estruturais foram executados;
nenhuma busca científica, fonte externa, credencial ou validação independente
foi acionada pelo doctor. A API pública do GitHub não encontrou repositório para
consultas direcionadas ao identificador do release e à conta MarceloClaro; a
consulta PyPI exata por `pesquisador-universal` também não encontrou pacote.
`scientific_lab/UPSTREAM_RELEASE.json` declara
`externally_certified=false`, `reproducible_build_verified=false` e
`signed_release_verified=false`. Como não foi identificada uma origem autoritativa
para reconstruir/recuperar o artefato, a instalação externa foi mantida intacta;
a referência ausente não foi fabricada.

O catálogo de plugins científicos continua sem execução ou validação externa:
`ngs-analysis-workbench` espera 0.2.18, mas o pacote local é 0.2.16 e o status
falha fechado (`version_mismatch`, hash_integrity=false); Zotero 0.1.2 não está
instalado. Conectores hospedados continuam com autenticação não verificada. Não
houve atualização/downgrade do pacote NGS nem importação de Zotero, pois faltam
artefatos upstream autorizados e hashes correspondentes.
