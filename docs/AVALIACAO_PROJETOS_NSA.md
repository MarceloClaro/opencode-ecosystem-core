# Ghidra, SkillTree e fractalrabbit no Core

Avaliação de 11/10/2026. Os três projetos foram consultados em suas fontes
oficiais; esta avaliação não instala nem habilita nenhum deles.

## Atualização executada em 12/10/2026

A proposta Ghidra foi implementada na R823: distribuição 12.1.4 conferida
por SHA-256, JDK 21 isolado e análise estática de um ELF conhecido pelo caminho
`ecosystem_rea` → `MarceloClaroOrchestrator` → REA → Ghidra. A função
`fixture_add` produziu o pseudocódigo esperado; o alvo não foi executado.
Cancelamento e timeout reais encerraram Node/Java e removeram o projeto
temporário. No timeout, o encerramento dos processos foi observado, mas o
provider não confirmou o fechamento gracioso da sessão MCP.

O [recibo R823](../outputs/core-r823/summary.json) e o
[manual de uso](REA_GHIDRA.md) são as referências atuais. A avaliação original
abaixo conserva o estado observado em 11/10. SkillTree e fractalrabbit
continuam propostas opcionais, sem instalação nesta revisão.

## Prioridades recomendadas

| Projeto | Prioridade para este Core | Aplicação proposta |
|---|---|---|
| Ghidra 12.1.4 | Alta para completar a integração REA com binários | Análise estática, descompilação e extração de evidências de executáveis pelo provider Ghidra já existente no REA |
| skills-service / SkillTree | Condicional, para capacitação de usuários | Trilhas do manual e do livro, exercícios, progresso e visualização de treinamentos |
| fractalrabbit | Experimental, para pesquisa com trajetórias | Dados sintéticos com hábitos e observação esporádica para comparar algoritmos de trajetória e detecção de anomalias |

Essas prioridades são inferências de adequação ao projeto. A origem dos
repositórios não certifica a correção, segurança ou eficácia deste Core.

## Ghidra: a dependência mais diretamente relacionada ao REA

A [release 12.1.4](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build)
publica a distribuição e seu SHA-256. O
[manual dessa versão](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.1.4_build/GhidraDocs/GettingStarted.md)
documenta execução headless, Java 21 de 64 bits com JDK, e mínimos de 4 GB de
RAM e 1 GB de armazenamento para os binários instalados.

O Core já coordena REA 6.4.0 por `MarceloClaroOrchestrator.rea_action`; a
[sessão real](../outputs/core-r820/gateway-session-summary.json) distingue o
catálogo anunciado do provider Ghidra, que retornou `not_configured` e solicitou
`GHIDRA_INSTALL_DIR`. Portanto, instalar e validar esse provider preencheria
uma lacuna operacional concreta. A análise JavaScript já executada continua
sendo uma prova distinta de análise nativa.

A implementação recomendada mantém Ghidra em um diretório de runtime externo
ao repositório, confere a distribuição por hash, configura o ambiente do
processo REA e usa o provider upstream. O aceite exige análise real de um
binário pequeno conhecido, identidade da ferramenta, hashes do alvo e da
evidência, cancelamento e encerramento do processo. Instalar o ZIP ou listar
ferramentas, isoladamente, não satisfaz esse aceite. O processo continua
coordenado pelo agente primário; não se duplicam as 170 ferramentas no contexto
de todos os agentes.

## SkillTree: treinamento de pessoas

O [skills-service](https://github.com/NationalSecurityAgency/skills-service)
é a implementação SkillTree: plataforma de microaprendizagem com gamificação,
visualizações, bibliotecas de integração e painel de administração de
treinamentos. Seu nome não descreve um runtime de `SKILL.md` para agentes.

O uso recomendado é uma integração opcional para trilhas de formação do Core,
se esse produto educacional for desejado. Eventos de exercícios precisam ter
critérios e recibos verificáveis; pontos e progresso não passam a ser confiança
científica do MetaBus nem confirmação da capacidade de um agente. Serviço,
autenticação, armazenamento e manutenção seriam requisitos próprios dessa
integração. O núcleo de orquestração não deve depender da disponibilidade de
uma plataforma de treinamento.

## fractalrabbit: experimentos com dados sintéticos

O [fractalrabbit](https://github.com/NationalSecurityAgency/fractalrabbit)
gera trajetórias sintéticas com preferência por locais visitados e relatos
esporádicos. O README descreve três processos estocásticos e aplicações em
trajetórias conjuntas, anomalias e subconjuntos consistentes de dados
corrompidos. A versão Java recebe parâmetros e escreve CSV.

Uma integração opcional de pesquisa poderia registrar parâmetros, origem,
seed quando suportada e hashes dos CSVs, com `synthetic=true` em toda evidência.
A relação com escolhas de agentes do Core é uma hipótese a testar: a saída
não demonstra melhor raciocínio, autonomia, roteamento ou desempenho real do
orquestrador. Só se justifica promovê-lo a dependência de um módulo após definir
o experimento e compará-lo a um baseline apropriado.

## Ordem proposta

1. Concluir os gates das correções atuais do Core.
2. Integrar e provar Ghidra pelo caminho central REA, se for solicitada sua implementação.
3. Desenvolver SkillTree conforme uma necessidade concreta de capacitação.
4. Incorporar fractalrabbit em um experimento de pesquisa com escopo e métricas definidos.
