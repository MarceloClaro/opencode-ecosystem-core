# Revisão e correções locais do Core — R929

Data: 19 de outubro de 2026. Contrato: [SPEC-935-R929](../specs/SPEC-935-R929-correcoes-core-regressoes.md).

Foram corrigidas falhas reproduzidas de persistência, concorrência, CLI,
grafo de código e diagnóstico. A seleção final concluiu **643 testes, todos
aprovados**, em 160,63 segundos. Os hashes das fontes monitoradas permaneceram
iguais entre o início e o término dessa seleção. Isso é evidência local do
escopo ensaiado; **não aprova o ecossistema inteiro para produção científica**.

## Problemas e comportamento corrigido

| Componente | Problema reproduzido | Comportamento após a correção |
|---|---|---|
| `evolution/cycles.py` | Gravar um ciclo eliminava extensões da raiz, campos desconhecidos e entradas históricas não modeláveis | O conteúdo JSON anterior e a ordem das entradas são preservados; linhas não modeladas continuam distinguíveis de modelos válidos |
| Registro de evolução | Arquivo inválido, gravação interrompida ou instância obsoleta podia apagar/substituir histórico | JSON inválido bloqueia gravação; serialização antecede publicação atômica; trava e comparação dos bytes recusam escritor obsoleto; falha de publicação reverte o append em memória |
| Alocação de ciclos | Duas threads da mesma instância podiam receber o mesmo ID; entradas brutas e sufixos históricos deixavam de reservar numerais | As três APIs protegem alocação e append pela mesma trava; IDs históricos participam da reserva sem serem promovidos a registros válidos |
| Validação do histórico | Scores inválidos ou inteiros JSON muito grandes derrubavam carregamento/estatísticas | Entradas incompatíveis são preservadas fora do modelo; overflow e números não finitos são recusados sem sobrescrita |
| `marceloclaro/cli.py` | Flags eram ignoradas e entradas inválidas podiam alcançar o primário | Comandos e opções cobertos pelo contrato são validados antes de inicializar o primário; argumentos legítimos e compatibilidade da ajuda são mantidos |
| CLI Lean, podcast e perfis | Recusa de operação podia resultar em código de saída zero | Lean exige `machine_checked` e `is_valid is True`; erro explícito do podcast e recusa de registro/ativação legado retornam código não zero |
| `integrations/python_code_graph.py` | O limitador podia não progredir quando metadados ou um símbolo isolado excediam o orçamento | Todos os caminhos relevantes passam pelo limite; redução progride ou devolve `response_too_large`, conservando o contrato do consumidor |
| Grafo AST | Anotações variádicas eram omitidas; mais de 20 homônimos eram cortados sem indicação | Usos de `*args`/`**kwargs` são atribuídos ao escopo da declaração; ambiguidades informam total, amostra e truncamento |
| Primário/contexto de código | Configuração inválida virava `AttributeError` ou observação metacognitiva indevida | A recusa `invalid_request` é devolvida antes de acessar a configuração ou persistir observação |
| `banca_rate` | Ausência de handler produzia `AttributeError` | Recusa explícita de operação indisponível; nenhuma nota é fabricada; handler concreto futuro continua possível |
| Doctor | Contagem física e modelos podiam vir de arquivos diferentes; linhas retidas eram descritas como perdidas | Usa a mesma origem configurada e distingue advertência por linhas não modeladas de perda efetiva de histórico |
| `core-check` | Ocultava advertências do doctor e reduzia o denominador; ignorava o histórico configurado | Propaga `warn`/`degraded`, conserva o denominador e recusa raiz/lista inválida ou histórico vazio |
| Descoberta de CLIs | Inventário construía executor sem necessidade | Resolver compartilhado sem executor, sem execução e sem cache de caminhos; instalação, remoção e overrides são observados novamente |
| Gate do catálogo | O mesmo JSON do baseline era reinterpretado para cada cartão | Cache limitado somente do parse de conteúdo relido; cada chamada relê o arquivo e confere o hash atual do cartão; alteração do baseline invalida imediatamente a chave |

Dois contratos de testes também foram reconciliados: comandos governados por
MCP são conferidos contra o primário e ferramentas realmente registradas; a
proibição de checksum inventado permanece na seção de instalação, sem proibir
hashes reais de evidências em outras seções do README. Contraprovas preservam
essas proteções.

## Evidência e alcance dos testes

O [recibo](evidence/r929/receipt.json) contém hashes de fontes e evidências,
versão do Python, base Git, preservação do histórico e limites. O
[JUnit final](evidence/r929/verified.xml) e a
[invocação registrada](evidence/r929/verified.json) descrevem a seleção de
643 casos, incluindo 62 casos R929 e regressões de persistência, orquestração,
MCP, raciocínio, governança, metacognição, contexto de código e rigor acadêmico.

Os casos negativos foram executados antes das respectivas correções. Há
artefatos RED para erros de publicação, concorrência, configuração, contratos
de retorno e diagnóstico. A primeira execução `red.xml` contém três erros de
fixture: eles **não contam como contraprovas válidas**. A fixture foi corrigida,
e `red-context.xml` registra os três `AttributeError` efetivamente reproduzidos.

Três revisores, previamente validados e ativados pelo primário, fizeram leitura
independente. Seus achados adicionais também receberam contraprovas e correção.
O aceite é limitado aos arquivos/contratos lidos, sem revisão científica externa
e sem presumir que as tarefas A2A foram concluídas por um executor do Core.
As correlações dos perfis e tarefas constam do recibo.

As fontes alteradas também passaram por compilação sintática e `git diff --check`.
Não foi executada uma campanha completa de mutação nesta rodada. As chamadas
com primário falso nos testes são fixtures; elas não demonstram autenticação,
saldo ou inferência de um provedor real.

## Tentativas globais e limites observados

O comando global pytest foi tentado duas vezes com prazo de 900 segundos.
Ambas as tentativas excederam o prazo e **não produziram aprovação global**.
A segunda registrou nove falhas antes dos últimos ajustes, em R110, R125,
R394, R443, R444, R445, R449 e R481. Esses contratos, ou os seus substitutos
MCP explicitamente conferidos, estão cobertos pela seleção final aprovada.
Os processos globais já haviam importado fontes anteriores; seus resultados
não representam uma execução integral do candidato final.

O limite de cinco segundos do teste R110 foi mantido. Ele falhou sob carga em
execuções intermediárias, passou na reexecução isolada e passou na seleção
final. Isso não garante a mesma latência sob toda carga ou em outra máquina.

O diagnóstico final é estrutural (`verification: installation_only`), com
**21 verificações aprovadas, uma advertência e nenhuma falha**. A advertência
identifica **78 entradas históricas preservadas, mas não modeladas** pelos
tipos atuais. Sua revisão/migração continua pendente: não foram convertidas
datas, listas, notas ou outros conteúdos por inferência. O ciclo R929 foi
acrescentado sem score e sem alegação de auditoria externa.

Continuam fora deste aceite:

- aprovação da suíte integral e ensaio de escala em produção;
- validação científica externa de artigos e experimentos;
- ramo nativo Windows da trava de gravação, não exercitado no WSL/Linux;
- três operações de grafo upstream que continuam bloqueadas por falhas
  conhecidas; o AST próprio não as libera;
- recarga de processos Python/MCP já abertos, que podem manter módulos antigos.

## Preservação do trabalho existente

O checkout continha alterações anteriores e recebeu alterações concomitantes.
Elas foram mantidas. Não houve instalação, treinamento, modificação da política
ITS-FINE ou acesso ao conteúdo de credenciais. Não foi criado commit que
misturasse essas alterações com as correções desta revisão. Os hashes do recibo
identificam o estado local examinado, sem atribuir todas as mudanças do checkout
a esta rodada.

Para reproduzir a seleção com estado temporário, consulte as
[instruções das evidências](evidence/r929/README.md).
