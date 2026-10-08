---
spec_id: SPEC-935-R664
title: Potenciais rastreaveis e composicao construivel por capacidades
status: green
validation_scope: local_runtime
release_gate: docs/evidence/R663_R666_RELEASE_GATE.json
component: scanners/potentiality_scanner.py + scanners/knowledge_composition.py
test_file: tests/test_r664_potentiality_composition.py
---

# SPEC-935-R664 — Potenciais e composição unitária

## Problema

R491 mede cobertura de declarações, sem separar disponibilidade e execução,
e sua chamada sem argumentos falha no pipeline legado. R490 oferece seis
classes de insumo, mas não explicita recursos, dependências internas, faltas
ou critérios rastreáveis para capacidades descritas por metadados.

## Contratos

1. DNA nasce somente de IDs de capacidades declaradas e seus metadados;
   nenhuma tokenização de código, importação, modelo ou inspeção de arquivo.
2. Listas legadas de strings continuam aceitas. Descritores distinguem
   declared, available, executed e externally_validated. Evidências precisam
   ter kind/ref/success e, para validação externa, validator explícito.
   Estado solicitado sem referência adequada é rebaixado; referências são
   registros informados, não autenticação externa efetuada pelo scanner.
3. Redundância conta módulos distintos, não ocorrências repetidas. DNA
   informa provedores, estados, evidências, dependências e capacidades ausentes.
   Centralidade inclui capacidades requeridas por pelo menos duas outras,
   mesmo quando possuem um único provedor.
4. Hipóteses incluem componentes presentes/ausentes, explicação, proveniência,
   cobertura declarativa e operacional, score/resistência heurísticos. Não
   são execução nem probabilidade calibrada. Requisitos repetidos não alteram
   cobertura. IDs legados repetidos são desambiguados por hash com aviso;
   strict_ids=True recusa a colisão. Nenhuma hipótese sobrescreve outra.
5. Além de receitas curadas, gerar combinações por dependências, interfaces
   de entrada/saída e metadados compartilhados. Ordenação determinística,
   no máximo 128 hipóteses, 256 capacidades e 8192 pares examinados; limites
   solicitados menores são respeitados e truncamento é comunicado.
6. Composição mantém R490 e acrescenta recursos, insumos tipados, faltas,
   dependências internas, critérios e mapa de construção. Metadados específicos
   precedem o fallback lexical. Falta de receita não fabrica métodos ou bases.
   requires usa source depende de target, como R483. Instalar uma ferramenta
   de validação não conclui a validação: critérios sem execução ficam pendentes.
7. scan() sem argumentos e PotentialityReport.items/get/to_dict atendem o
   pipeline legado; scan([]) permanece vazio. compose_many retorna report
   serializável para integração potencial→composição→sequenciamento→roadmap.
8. Sem mutar entradas, executar modelos, instalar pacotes ou registrar ciclo
   global nesta subtarefa. Testes R664 precedem implementação e regressões
   R490/R491/R492/R493 preservam contratos.

## Aceitação

- Contraprovas cobrem promoção sem evidência, pseudorredundância, ausência,
  combinações novas, bounds, insumos/dependências e informação incompleta.
- APIs antigas continuam funcionando; relatórios distinguem hipótese de execução.
- RED e GREEN registrados com evidência de testes herméticos.

## Evidência local

- RED inicial: 20 testes R664 falharam antes da implementação.
- GREEN: R490/R491/R492/R493/R496/R664, 89 testes aprovados.
- Fixtures são sintéticas; nenhum scanner executou modelos ou referências.
- Após revisão independente, R664 cobre 31 casos, incluindo preservação limitada
  de hashes, escopo, runtime e artefatos sem executar ou autenticar referências.
- Regressões finais R663–R666: 723 aprovados e um caso de PDF ignorado por
  dependência opcional ausente; ver relatórios XML no gate local.
