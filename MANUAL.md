# Manual do OpenCode Ecosystem Core

Este é o manual em linguagem simples. Para arquitetura técnica detalhada, veja [`ARCHITECTURE.md`](ARCHITECTURE.md). Para instalar, veja [`installer/README.md`](installer/README.md). Para ver como tudo se encaixa visualmente, abra o **[mapa interativo 3D da arquitetura](docs/architecture_map.html)** — tem um alternador Leigo/PhD no topo.

## O que é isso, em uma frase

Um sistema de agentes de software especializados (pesquisa, revisão, escrita acadêmica, raciocínio, etc.) coordenados por um orquestrador central chamado **marceloclaro**, que decide qual agente faz cada tarefa e aprende com os resultados ao longo do tempo.

## Como começar

Depois de instalado (veja [`installer/README.md`](installer/README.md)):

```bash
python3 -m marceloclaro.cli
```

Isso abre um menu interativo. Se preferir comandos diretos, sem menu:

```bash
python3 -m marceloclaro.cli status      # foto geral do sistema
python3 -m marceloclaro.cli doctor      # está tudo saudável?
python3 -m marceloclaro.cli helpdesk    # o que está errado E como corrigir
python3 -m marceloclaro.cli ajuda       # este resumo, no terminal
```

## O menu, explicado sem jargão

| Opção | O que faz | Em outras palavras |
|---|---|---|
| `[1]` Listar agentes | Mostra quem está disponível | Cada "agente" é uma especialidade (pesquisador, revisor, escritor acadêmico, auditor...) |
| `[2]` Postar tarefa | Descreve um trabalho e o sistema escolhe quem faz | O "Blackboard" é um quadro de avisos onde os agentes se candidatam à tarefa que combina com suas habilidades |
| `[3]` Reportar conclusão | Diz se um agente terminou com sucesso ou falhou | O sistema aprende: agentes que dão certo ganham mais confiança para tarefas futuras |
| `[4]` Consultar memória | Mostra o que o sistema já aprendeu | A "memória metacognitiva" é compartilhada por todo o ecossistema, não presa a um agente só |
| `[5]` Status geral | Uma foto completa: agentes, confiança, economia | Útil para ver "o que está acontecendo agora" |
| `[6]` Doctor | Checagem rápida (segundos) de saúde | Specs carregando, histórico intacto, CLIs externas instaladas |
| `[7]` Ajuda | Este resumo | — |
| `[8]` Helpdesk | Doctor + sugestão do que fazer para cada problema | Ex.: "CLI X ausente → rode este comando para instalar" |

## Perguntas frequentes

**"Blackboard", "MetaBus", "Reflexion" — o que são?**
São nomes técnicos internos. Na prática: o Blackboard é onde tarefas esperam um agente disponível; o MetaBus é a "memória compartilhada" de tudo que já aconteceu; Reflexion é o mecanismo que registra lições aprendidas depois de cada tarefa. Você não precisa entender os nomes para usar o menu — as opções acima já traduzem o que cada coisa faz.

**O `doctor` disse "degraded". É grave?**
Não necessariamente. "Degraded" significa que há avisos (`warn`), não falhas críticas (`fail`). Rode `[8] Helpdesk` para ver exatamente o que fazer em cada caso.

**Preciso instalar OpenCode, Antigravity, Claude Code E Ollama?**
Não — todos são opcionais para o ecossistema em Python puro funcionar. Cada um serve a um uso diferente: OpenCode CLI expõe o catálogo de agentes como comandos de terminal; Antigravity permite delegar tarefas a um agente externo do Google; Claude Code é o assistente de desenvolvimento que já lê `CLAUDE.md`/`AGENTS.md` automaticamente neste projeto; Ollama roda modelos de linguagem localmente e de graça. O `doctor`/`helpdesk` avisa quando algum está faltando, mas nunca bloqueia o uso por causa disso.

**Onde ficam os atalhos depois de instalar no Windows?**
Na Área de Trabalho, com o ícone próprio do projeto: "OpenCode Ecosystem", "Antigravity CLI", "Claude Code (Ecosystem)" e "Ecosystem (marceloclaro)".

**Quero desinstalar tudo.**
Veja o instalador da sua plataforma em [`installer/README.md`](installer/README.md) — cada um tem um script de desinstalação correspondente (`Uninstall-OpenCodeEcosystem.ps1` no Windows, `uninstall.sh` no Linux/macOS). Ações destrutivas (como remover o WSL inteiro) sempre pedem confirmação explícita antes de executar.

**As alegações do README/ARCHITECTURE são todas garantidas?**
Não cegamente — veja [`CORRIGENDUM.md`](CORRIGENDUM.md), um documento público que lista alegações que precisavam de ressalva (ex.: "Score médio" é autoavaliação interna, não benchmark externo).

## Troubleshooting rápido

| Sintoma | O que fazer |
|---|---|
| `doctor` mostra `opencode_config: fail` | Rode `python3 -m integrations.opencode_cli` para regenerar `opencode.json` |
| `doctor` mostra `external_clis: warn` | Rode `python3 -m marceloclaro.cli helpdesk` — ele mostra o comando exato de instalação de cada CLI ausente |
| `doctor` mostra `evolution_registry: fail` | Pare antes de gravar novos ciclos; o histórico pode estar incompleto — veja `evolution/cycles.json` manualmente |
| Atalho de desktop não abre nada no Windows | Confirme que o WSL/Ubuntu está instalado (`wsl --status` no PowerShell) e rode o instalador novamente |
| Import `MarceloClaroOrchestrator` falha | Rode `pip3 install -r requirements.txt` dentro da pasta do projeto |

Se nada disso resolver, `python3 -m marceloclaro.cli helpdesk` é sempre o primeiro passo — ele já roda todos os checks acima automaticamente.
