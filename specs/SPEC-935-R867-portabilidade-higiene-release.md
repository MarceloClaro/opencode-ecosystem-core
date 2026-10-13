---
spec_id: SPEC-935-R867
title: Portabilidade dos testes e higiene de licença na entrega
component: tests
status: implemented
test_file: tests/test_r867_portable_release.py
---

# R867 — Portabilidade e higiene

Os testes de Lean R747/R755 utilizavam caminho absoluto de outra máquina.
R852 guardava uma licença de máquina real em literal para verificar que ela
não aparecia em recibos. A verificação deve conservar esse cuidado sem
versionar a própria licença. O lock npm deve permitir instalar os mesmos
pacotes usados pelos testes TypeScript.

## Critérios de Aceitação Executáveis

- `portabilidade` — importar os testes Lean em um checkout temporário deriva
  REPO daquele checkout. O projeto externo Mathlib continua opcional.
- `licenca` — o teste R852 não contém a chave observada; verifica ausência de
  campos de licença nos recibos, sem publicar um valor real para compará-lo.
- `lock` — package-lock do OpenCode é versionável; npm ci é reproduzível.

Nenhum arquivo de licença ou estado de execução é apagado da máquina. As
requisições privadas já rastreadas são removidas apenas do índice Git.
