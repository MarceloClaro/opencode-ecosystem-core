# Aceite integral da indexação local — R889

O teste no Core expôs um limite que não apareceu na fixture pequena de R887.
O processo context-link encerrou com código zero e respondeu ao ping, mas
indexou 179 dos 763 arquivos descobertos e registrou 584 erros de parser.
Por isso exit code e handshake não podem comprovar prontidão de um índice.

A contraprova permanece em `outputs/core-r887/core-post-commit.json`, vinculada
a `a0efdcd`. O índice tinha aproximadamente 2,65 MB; os logs apontaram
`operation limit was hit`, sem evidência de limite de tamanho atingido.
Uma condição de reutilização/cancelamento do parser é hipótese de causa raiz,
não uma conclusão demonstrada sobre o provedor upstream.

## Contrato de recuperação e aceite

A especificação [R889](../specs/SPEC-935-R889-aceite-integral-indice-local.md)
exige auditoria dos arquivos e hashes do banco contra o corpus selecionado.
Gerações sem esse recibo não podem ser prontas. Recuperação incremental, quando
aplicável, usa novos processos isolados, mantém todas as estatísticas e respeita
um número máximo de tentativas por invocação e o prazo global. Uma nova
indexação explícita pode retomar o candidato privado; uma consulta não o faz.
Commits apenas documentais podem conservar o índice quando todos os hashes
selecionados permanecem idênticos; revisão de origem e revisão atual ficam
separadas na proveniência. Não se reduz o corpus para
transformar uma falha em sucesso.

O binário e sua licença permanecem fixados. O isolamento de rede e de arquivos
continua obrigatório. Não há relaxamento das três consultas de grafo bloqueadas
por R887. Falha de progresso, limite de tempo ou divergência de dados mantém
o aceite fechado, com motivo explícito.

## Evidência e alcance

O recibo `verification-local-r889.json` descreve a execução final e os testes
correspondentes. A integridade do índice refere-se às fontes selecionadas e aos
hashes; não demonstra correção semântica geral dos símbolos, comportamento em
execução, ganho de tokens ou ausência de falhas no provedor. A recuperação por
processos novos não comprova que a causa raiz upstream tenha sido eliminada.

## Execução integral no Core

A execução sobre `818d951` concluiu **763 de 763 fontes selecionadas** em
três operações explícitas e quinze passadas nativas. A última passada registrou
zero erros; o banco contém 8.024 símbolos, 8.024 vetores e 8.024 entradas FTS,
sem relações inválidas ou hashes ausentes/divergentes. As falhas intermediárias
foram preservadas no histórico privado; não houve redução do corpus.

O primário consultou código de `MetacognitiveLoop`, a estrutura de
`mci/metacognitive_loop.py` e busca semântica. Uma delegação de sondagem recebeu
o contexto citado no Blackboard; nenhum executor de LLM foi acionado nessa
sondagem. O ledger de confiança permaneceu igual antes e depois.

Uma conexão MCP stdio real ao `ecosystem-network` completou inicialização,
catálogo, consulta da classe com hash e linha corretos e controles negativos:
travessia de caminho, arquivo ausente, grafo bloqueado e instalação não exposta.
A memória dessa sondagem MCP foi temporária e isolada.

O [recibo R889](verification-local-r889.json) fixa resultados e hashes. Os
registros detalhados em `outputs/core-r889/` são locais e ignorados pelo Git.
O índice é privado e não é publicado no repositório.

A [fonte do parser fixado](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/indexer/parser.go)
usa timeout de cinco segundos e reutiliza parsers. O erro
[`operation limit was hit` no binding](https://github.com/smacker/go-tree-sitter/blob/dd81d9e9be82/bindings.go)
é uma classificação genérica da árvore nula; a mensagem sozinha não identifica
quota ou causa. A recuperação observada por processos novos não demonstra
correção definitiva dessa causa upstream.
