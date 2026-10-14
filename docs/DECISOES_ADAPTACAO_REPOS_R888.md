# Decisões de adaptação — nove repositórios (R888)

A revisão priorizou contribuições que se conectam ao primário e ao MetaBus.
Os levantamentos [A](AVALIACAO_REPOS_R888_A.md) e
[B](AVALIACAO_REPOS_R888_B.md) registram fontes fixadas, amostras, licenças,
rede e limitações; seus manifestos permitem localizar os arquivos lidos.

| Repositório | Utilidade para o Core | Decisão desta etapa |
|---|---|---|
| mira-animator | Apresentações e fontes vinculadas | Referência; licença não comercial e caminhos de rede exigem escopo próprio |
| RAGnaRock | Retorno compacto de recuperação, fonte e posição | Padrão reimplementado na projeção de contexto R887, sem outro daemon |
| superhuman | Datasets, prompts e método de avaliação | Corrigir harness IMO local; benchmark sem solver não é execução |
| opentwins | Composição e estado desejado/observado | Referência para domínio industrial; não instalar infraestrutura adicional |
| science-skills | Limites científicos, evidência e divulgação seletiva | Aplicar separação de resultado/medida/prova no harness e nas consultas |
| feynman-tutor | Perguntas de compreensão e memória pedagógica | Candidato de modalidade futura; MetaBus permanece canônico |
| MiroFish | Cenários e orçamento de simulações | Referência; cenário sintético não comprova previsão do mundo real |
| MiroFish-Offline | Interfaces de armazenamento e configuração local | Candidato externo; defaults locais não comprovam bloqueio de rede |
| transformers | Modelos locais opcionais e tokenização | Backend futuro isolado; não substituir o roteador ou baixar pesos neste ciclo |

## Mudanças adaptadas

`integrations/code_context_view.py` transporta somente snippets compactos com
caminho, hash da fonte, revisão e posição quando disponibilizada pelo provedor.
Remove memória e estimativas comerciais do provedor, deduplica trechos e recusa
conteúdo sem proveniência compatível. O primário o inclui no briefing existente:
MCP/CLI → primário → provedor isolado → contexto citado → Blackboard → executor.
Código recuperado continua sendo dado não confiável, sem autoridade instrucional.
Essa implementação é própria; não copia o daemon ou o algoritmo silábico RAGnaRock.

`integrations/deepmind/imobench_harness.py` separa a entrada pública do solver
do gabarito mantido pelo avaliador. A falta de solver produz `not_executed`;
igualdade completa substitui o falso acerto por substring. Nota textual ou
resposta curta correta não certifica prova formal. O adapter do solver local
retorna resposta calculada separada da justificativa. O corpus amostral
continua pequeno e conhecido, sem alegação de generalização ou desempenho humano.
O consumidor DeepThink também passa a distinguir a heurística textual do
resultado do verificador, removendo títulos e confiança fixa de prova concluída
quando a entrada não foi demonstrada. O escopo formal é o aceito pelo verificador,
não uma certificação geral da linguagem natural.

## Uso efetivo do REA

Foram concluídas cinco inspeções estáticas compatíveis: duas entradas JavaScript,
um HTML e dois subconjuntos de frontend JavaScript. O REA não executou os
aplicativos nem seus instaladores. Pedidos Python/Markdown não suportados e as
tentativas JavaScript inicialmente mal delimitadas foram mantidos como falhas
nos recibos. A leitura dessas linguagens foi uma atividade estática separada.

Os relatórios REA ajudaram a delimitar superfícies e a evitar a execução dos
runtimes originais. A descoberta do vazamento do benchmark veio da leitura e
reprodução do próprio harness do Core; não deve ser atribuída ao parser REA.

## Aceite e limites

`verification-local-r888.json` registra os testes dirigidos, os recibos e os
artefatos alterados. Nenhum dos nove runtimes foi instalado como consequência
desta curadoria. O único binário novo pertence ao piloto R887 previamente
especificado; três ferramentas de grafo desse piloto foram bloqueadas após
contraprova local. Economia de tokens não foi demonstrada na fixture usada.
Não há auditoria integral dos nove projetos ou validação externa de qualidade.
