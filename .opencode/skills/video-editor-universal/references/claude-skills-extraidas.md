# Skills de edição extraídas do Claude

Fonte: `.claude/skills/` do projeto, pacote local do livro **Caixa Preta IA**
(Tiago Lemos, 2026). O livro autoriza copiar/adaptar comandos, modelos e
skills para os próprios projetos; não redistribua o conteúdo integral
publicamente sem autorização. As skills permanecem em `.claude/skills` como
fonte única e são descobertas pelo OpenCode; esta skill as orquestra.

| Skill | Função | Arquivos | SHA-256 da árvore |
|---|---|---:|---|
| `cp-apresentador-em-cena` | apresentador real, recorte, moldura, tracking | 4 | `a05f33f561a4…` |
| `cp-direcao-de-edicao` | decisão de foco, composição, continuidade, plano auditável | 7 | `789f2f0ba175…` |
| `cp-estilo-por-referencia` | traduzir referência em gramática visual própria | 3 | `36f28598ffc6…` |
| `cp-extratora-de-referencia` | extrair pacote verificável de uma referência | 4 | `f180cb24bb97…` |
| `cp-lettering-com-hierarquia` | tipografia animada, hierarquia e leitura | 3 | `1260777d2dcb…` |
| `cp-motion-explicativo` | motion que explica relação/processo | 3 | `aa710bbfd510…` |
| `cp-variacoes-controladas` | variações com uma variável por hipótese | 3 | `29f6cefbd7cf…` |
| `meia-briefing-de-edicao` | briefing executável sem repetir perguntas | 1 | `a9230165f1e0…` |
| `meia-legendas-e-enquadramento` | legendas sincronizadas e enquadramento | 2 | `08e8e1b845ee…` |
| `meia-revisao-economia` | revisão por intervalo e controle de retrabalho | 2 | `fcd7bd8b9052…` |

Manifesto completo, com bytes e caminhos: `claude-skills-manifest.json`.

## Como usar

- **Direção**: `cp-direcao-de-edicao` + `meia-briefing-de-edicao`.
- **Referência**: `cp-extratora-de-referencia` → `cp-estilo-por-referencia`
  (não copiar logo, texto, oferta ou asset de terceiros).
- **Apresentador**: `cp-apresentador-em-cena`; recorte é aproximação, revise
  borda/cabelo.
- **Texto**: `cp-lettering-com-hierarquia` + `meia-legendas-e-enquadramento`.
- **Animação**: `cp-motion-explicativo`; em Remotion, movimento vem dos frames,
  não de CSS/timers.
- **Variações**: `cp-variacoes-controladas`; uma mudança por versão.
- **Revisão**: `meia-revisao-economia`; intervalo + problema + mudança +
  preservar.

## Limites

As skills não instalam Remotion, não renderizam, não aprovam qualidade e não
substituem revisão humana. Uma skill descreve método; a execução real precisa
de projeto, assets, licença e ferramentas disponíveis.
