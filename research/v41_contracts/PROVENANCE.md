# Proveniência dos contratos v4.1

Os 6 arquivos `.schema.json` deste diretório são **cópias byte-idênticas** dos
contratos da skill Pesquisador Universal v4.1 (JSON Schema Draft 2020-12),
extraídas do bundle congelado:

- Origem: `opencode-ecosystem-core-pesquisador-universal-v4.1-com-trilogia-full-bundle/opencode-ecosystem-core-pesquisador-universal-v4.1-com-trilogia/SCIENTIFIC_LAYER/SOURCE/schemas/`
- Commit de referência da skill: integração ao Core `a5478054ceb8fc34eb0d254a30a3c451d6d864cd` (2026-09-07)
- Copiados em: 2026-10-06, ciclo R703 (Fase A da integração R702)
- Licença: Core MIT; o bundle declara-se "adaptação independente inspirada" no Core. Contratos JSON funcionais importados como padrões de validação, sem redistribuição de binários, modelos ou corpora.

## SHA-256 das cópias (verificar contra MANIFEST.sha256 do bundle)

```
ad997fda64205f9e3d56f057ce2897cf4edf6cc30845f00cf934a29ea5911fef  article-download-receipt.schema.json
dbf45211fc45cf44032329b507da9ca4644f2d2e2b03ae40db4c3b66a9cfc3e6  execution-receipt.schema.json
3c2b4dfee276ea39a3cc5c64f3362d18443fd1c22751b4e1e711fed9209ec772  release-manifest.schema.json
204aadd656066cce63efcd8443f06858cc0319efa129ac60606ba4de1fd19d48  screening-decision.schema.json
c741375f9710955b1bb24d4ced232d8ead3dce74e5470404819f88b575b39049  snowball-manifest.schema.json
e2baf62b50322a87e7b2ff0a2348a09c707b26fb66325de4b738909af9af4e7c  study-record.schema.json
```

## Uso no pipeline do artigo (R702 → R703)

| Contrato | Ferramenta consumidora |
|---|---|
| `screening-decision` + `study-record` + `snowball-manifest` | MCP `registrar_triagem` (triagem PRISMA auditável por estudo) |
| `article-download-receipt` | recibo de proveniência por fonte (futuro: `auditar_referencia` estendida) |
| `execution-receipt` + `release-manifest` | MCP `emitir_manifesto` (manifesto de release do artigo) |

Nota anti-overclaim: schemas são contratos de validação, não prova de
qualidade científica. A comparação 96,7 × 69,7 do bundle é autoavaliação
heurística dos autores, não benchmark externo.
