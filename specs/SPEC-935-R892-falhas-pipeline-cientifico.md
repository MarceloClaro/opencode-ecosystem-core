---
spec_id: SPEC-935-R892
title: Propagar falhas científicas e impedir conclusão fictícia de delegações
component: marceloclaro.orchestrator
status: implemented
test_file: tests/test_r892_scientific_fail_closed.py
---

# R892 — Estados científicos vinculados à execução observada

## Contraprovas lidas

`scientific_discovery_pipeline` calcula falhas em revisão R104d e composição
R105, mas o retorno final usa `status=completed` incondicionalmente.
`_maswos_delegate` posta tarefa, fabrica a frase “estágio executado” e chama
`report_completion(success=True)` sem executar um especialista.

## Correção exigida

1. Reproduzir ambos com testes negativos antes de alterar produção.
2. Falha, bloqueio ou ausência de saída do estágio obrigatório impede conclusão
   científica. Propagar estágio/motivo; não compor sobre revisão que falhou nem
   atribuir execução à ausência de resultados. `strict_gates=False` não transforma
   falha de execução em sucesso nem revisão consultiva em aprovação científica.
3. Delegação somente é concluída quando existe resultado real e estado elegível
   no caminho canônico do Blackboard. Agente sugerido, string de status, tarefa
   postada ou disponibilidade não comprovam execução. Sem executor/resultado,
   devolver bloqueio explícito, sem chamar conclusão bem-sucedida ou premiar trust.
4. Escores e avaliações internas permanecem heurísticos. Fluxos de manuscrito
   não elevam confiança de agentes por conteúdo que eles próprios fabricaram.
5. Preservar contratos estruturados, testar as regressões dos consumidores e
   registrar observações no MetaBus com a natureza real da evidência.
6. `scientific_lab.native.evidence.annotate` não pode aceitar `human="false"`
   como confirmação humana. Exigir `human is True` para verificação afirmada;
   rejeitar valores truthy de outro tipo e preservar decisões pendentes.
7. O consumidor MASWOS não aprova execuções com estágios falhos, vazios,
   ignorados em dry-run ou seleção vazia, mesmo com nota heurística máxima.
   O contrato vale também para os estágios cloud e a banca interna não pode
   elevar essa execução incompleta a aprovação.
8. `academic_pipeline`, sua banca e o loop científico registram observações
   sem EMA ou prêmio de trust. Aprovação estrutural local não significa aceite
   científico; os retornos declaram revisão humana pendente.
9. R102 exige estado `completed`, flags booleanas verdadeiras e relatórios
   tipados com resumo útil; blacklist de poucos erros não basta para aceitar
   estados desconhecidos. Resultados MASWOS com `success` textual ou conteúdo
   que seja somente um rótulo de erro não contam como execução concluída.
10. Falha da banca obrigatória bloqueia aprovação e deve aparecer no resumo.
    Ajustes heurísticos de confiança não representam calibração empírica.

## Verificação local

`outputs/core-r892/red-valid.xml` conserva a execução anterior à correção:
37 falhas de comportamento e um controle positivo. `red.xml` conserva a
tentativa inicial, que também contém oito falhas causadas por construção inválida da fixture
Blackboard (registradas como falhas de chamada no JUnit), corrigidas antes da alteração de produção. Esse histórico local
não é uma atestação externa da cronologia de desenvolvimento.

## Limites

Não instalar modelos ou ativar contas para esconder um caminho ausente.
Resultados locais não constituem avaliação editorial ou revisão por pares.
O aceite corresponde aos caminhos corrigidos, não à ausência universal de bugs.
