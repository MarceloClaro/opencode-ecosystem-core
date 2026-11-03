---
spec_id: SPEC-935-R929
title: Correções reproduzidas de histórico, CLI e grafo de código
component: evolution.cycles, agents.lifecycle, marceloclaro.cli, marceloclaro.doctor, marceloclaro.core_check, marceloclaro.governed_cli, integrations.harness_runtime, integrations.python_code_graph, academic.adversarial_research.service
status: implemented
test_file: tests/test_r929_core_regressions.py
---

# R929 — avaliação e correções do Core

## Escopo

Preservar mudanças existentes, dados de domínio, políticas ITS-FINE, credenciais,
modelos e serviços em execução. Não treinar, instalar dependências ou liberar
operações upstream bloqueadas. O diagnóstico estrutural inicial passou 22/22;
isso não certifica execução ou prontidão científica.

Reproduzir e corrigir: perda de campos/entradas do histórico, gravação truncante
ou obsoleta, códigos de saída incoerentes e argumentos de pesquisa ignorados,
laço sem progresso no limite de resposta do grafo e perda de validação do
consumidor primário. Anotações variádicas devem constar como usos de declaração.

## Contratos de aceitação

1. Registros antigos, extensões desconhecidas e metadados da raiz permanecem
   após record/save. JSON corrompido ou estrutura inválida bloqueia gravação.
   Uma instância obsoleta não sobrescreve outra; publicação é atômica. Falha
   de persistência não adiciona ciclo ou altera estatísticas em memória.
   As três APIs de registro serializam alocação e publicação na mesma
   instância. IDs brutos/históricos, inclusive com sufixo, reservam numerais.
   Números fora da faixa finita não derrubam a leitura ou apagam entradas.
2. Comando inválido e flags malformadas retornam erro antes de instanciar ou
   acionar o primário. Rejeição Lean e ativação não realizada não retornam
   sucesso. Casos positivos mantêm argumentos e JSON integral.
   Lean exige `machine_checked` e `is_valid is True`; podcast com erro
   explícito retorna código não zero, preservando a saída JSON.
3. Todo retorno do grafo respeita o orçamento de bytes e termina, inclusive
   erros de parsing e seleção ambígua. Truncamento é explícito; não se promete
   completude ou precisão semântica por reduzir a resposta.
   Amostras de candidatos informam total, quantidade devolvida e truncamento.
   A recusa mínima conserva o schema utilizado pelo provedor consumidor.
4. Configuração inválida do contexto devolve invalid_request; não causa
   AttributeError nem transforma a recusa em observação de sucesso.
5. RED antes de alterar cada comportamento, GREEN com casos negativos e
   positivos. Executar a seleção relevante e tentar o comando global pytest,
   registrando limites, skips, falhas preexistentes e escopo observado.
6. `banca_rate` sem implementação concreta recusa explicitamente a operação;
   não lança AttributeError nem inventa nota. Um handler futuro permanece
   subordinado ao contrato e à revisão humana.
7. Doctor e core-check comparam a mesma origem configurada. Linhas brutas
   integralmente retidas, mas não modeladas, geram advertência explícita;
   uma perda real continua sendo falha. Core-check propaga advertências e
   não reduz o denominador do diagnóstico para apresentar sucesso integral.
8. Descoberta estrutural não instancia executores nem armazena resultados
   de caminhos. O parse do baseline pode ser reutilizado apenas após nova
   leitura dos mesmos bytes, em cache limitado; alteração invalida a chave
   imediatamente e cada cartão continua sendo conferido pelo hash atual.
9. Contratos de testes distinguem comandos MCP de wrappers Python e
   checksums de instaladores de hashes reais de evidência documental.
   Não remover verificações de primário, ferramenta registrada ou integridade.

## Coordenação

Perfis existentes validados/ativados pelo MarceloClaro: command-regression
(task-bd8d4bd5), blind-review-ledger (task-ac674c98) e code-context-backend
(task-ad1ca2fb). Auditorias externas nesta conversa são somente leitura; a
execução e as correções ficam com o primário. Atribuição não prova execução.

## Evidência

Resultados, RED/GREEN, hashes, revisão por leitura e limites da tentativa
global estão em `docs/REVISAO_CORE_R929.md` e `docs/evidence/r929`.
`implemented` indica implementação do escopo; não indica liberação global.
Nenhuma revisão local é validação científica externa ou garantia de ausência
de bugs em todo o ecossistema. As entradas históricas não modeladas continuam
pendentes de revisão/migração, sem fabricação ou normalização de conteúdo.
