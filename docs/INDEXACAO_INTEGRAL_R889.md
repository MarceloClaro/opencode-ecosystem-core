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
