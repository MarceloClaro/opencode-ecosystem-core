# SPEC-929: Sincronização Documental e de Mapas da Expansão Jurídica

```yaml
spec_id: SPEC-929
title: Atualização coordenada de README, arquitetura, changelog, release notes e mapas após a expansão jurídica
version: 1.0.0
status: active
owner: marceloclaro
depends_on: [SPEC-921, SPEC-922, SPEC-923, SPEC-924, SPEC-925, SPEC-926, SPEC-927, SPEC-928, SPEC-029]
origin: pedido do usuário para atualizar mapas, documentações, README e artefatos correlatos
```

**STATUS**: IMPLEMENTADO  
**DATA**: 2026-07-08  
**AUTOR**: marceloclaro  
**VERSÃO**: 1.0

## 1. Objetivo

Sincronizar toda a documentação principal e os mapas do ecossistema com a nova camada jurídica integrada ao MCI, incluindo Datajud, AuxJuris, scanner jurídico de impacto, aba jurídica na webapp, especialização por domínio e benchmarks jurídicos por ramo.

## 2. Escopo

Arquivos a atualizar:

- `README.md`
- `ARCHITECTURE.md`
- `CHANGELOG.md`
- `RELEASE_NOTES.md`
- `diagram.mmd`
- `MAPA_ECOSSISTEMA_COMPLETO_2026-07-06.md`
- `maps/ecosystem_map_2026-07-06.json`

## 3. Critérios de Aceitação (TDD documental)

1. `README.md` reflete a expansão jurídica e o novo total de testes
2. `ARCHITECTURE.md` inclui a camada jurídica/AuxJuris/Legal Impact/Webapp
3. `CHANGELOG.md` contém uma nova versão para a expansão jurídica
4. `RELEASE_NOTES.md` contém uma nova release da expansão jurídica
5. `diagram.mmd` está alinhado com a arquitetura documentada
6. artefatos do mapa refletem os totais atuais de nós e vetores

## 4. Resultado Esperado

A documentação deixa de retratar o ecossistema como apenas científico/metacognitivo e passa a descrever corretamente sua nova capacidade de **inteligência jurídica integrada e especializada por ramo**.
