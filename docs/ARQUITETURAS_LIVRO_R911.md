# Atlas das arquiteturas do livro — R911

O atlas complementa a sequência didática do livro existente. Cada um dos 18 temas tem mapa mental, diagrama de responsabilidades e fluxo delimitado com decisão, recusa e recuperação. As figuras estão junto aos capítulos consumidores; o panorama e o índice navegável estão no capítulo de arquitetura.

## Escopos e legenda

- Mapa mental: agrupamento editorial; linhas associam conceitos.
- Diagrama: seis responsabilidades por tema, com relações tipadas e evidência por aresta.
- Fluxo: percurso delimitado da operação descrita; não significa pipeline universal.
- Azul cheio: chamada; roxo tracejado: evento; verde pontilhado: dado; cinza sem ponta: organização; âmbar traço-ponto: fronteira ou recusa.
- 18 temas editoriais, 18 camadas classificadas por pasta e oito andares do modelo anterior são taxonomias diferentes.

## Percurso dos 18 temas

| ID | Tema | Capítulo principal |
|---|---|---|
| AR01 | Interfaces, configuração e entrada no Core | `mod-01c-instalacao.tex` |
| AR02 | Primário, elegibilidade e seleção de agentes | `mod-02-orquestracao.tex` |
| AR03 | Blackboard A2A e circulação no MetaBus | `mod-03-memoria-mci.tex` |
| AR04 | Workflows, checkpoints e executores de leitura | `mod-02-orquestracao.tex` |
| AR05 | Ciclo de vida de agentes e perfis gerenciados | `mod-13-ativacao-agentes.tex` |
| AR06 | Memória metacognitiva, observação e leitura visual | `mod-03-memoria-mci.tex` |
| AR07 | RAG, conhecimento e evidências | `mod-03-memoria-mci.tex` |
| AR08 | Especificação, TDD e aceite | `mod-04-qualidade-sdd.tex` |
| AR09 | Confiança, economia e governança | `mod-02-orquestracao.tex` |
| AR10 | Raciocínio, matemática e otimização | `mod-05-raciocinio.tex` |
| AR11 | Ciência, artigos e experimentos | `mod-06-ciencia.tex` |
| AR12 | Fronteiras MCP e conectores do host | `mod-07-integracoes.tex` |
| AR13 | REA, camadas e inspeção local | `mod-07-integracoes.tex` |
| AR14 | Inteligência estrutural de código e grafo Python | `mod-07-integracoes.tex` |
| AR15 | Diagnóstico e evolução rastreável | `mod-08-ecossistema.tex` |
| AR16 | Infraestrutura, dados e segurança local | `mod-09-infra.tex` |
| AR17 | Plugins, skills e federação de artefatos | `mod-08-ecossistema.tex` |
| AR18 | Publicação, livro e provas Lean | `mod-15-epilogo-reproducao.tex` |

## Mapa integral e integridade

O snapshot Git `759d25325c0c4d1fbc84cadf8e0652627ed96253` foi extraído sem executar o código: 693 módulos Python classificados de produção, 965 pares internos únicos, 1.083 declarações AST e zero erros de parsing. O exportador registra separadamente seis imports dinâmicos, 4.045 imports externos/não encontrados e oito superfícies não Python. Esses números delimitam o extrator, não a completude funcional do ecossistema.

O livro inclui o mapa mental dos 18 temas, um diagrama das fronteiras dos processos e caminhos direto/delegado, um fluxo de uso e conferência e a matriz integral entre as 18 camadas estáticas. O grafo individual de 693 módulos, inclusive isolados, acompanha o livro em SVG ampliável, DOT e Mermaid em `docs/architecture-r911/`; não se reduz esse grafo a caracteres ilegíveis numa folha A4.

- [SVG completo](architecture-r911/dependencies.svg)
- [Mermaid completo](architecture-r911/dependencies.mmd)
- [Inventário do snapshot](architecture-r911/architecture-inventory.json)
- [Correspondência e contagens](architecture-r911/mermaid-correspondence.json)

As fontes autoritativas são `livro-core/atlas/data-orchestration.json`, `data-science.json` e `livro-core/gen_architecture_atlas.py`. O manifesto `architectures.json` contém fonte por componente, por aresta e por fluxo, além de hashes dos 57 arquivos Python referenciados. A presença AST verifica localização dos símbolos; a pertinência semântica depende da leitura das fontes, não é provada pelo parser.

## Fronteiras conservadas

- CLI, MCP e Streamlit podem criar instâncias próprias do primário; cache em um processo não é estado distribuído universal.
- REA direto chama o bridge; não exige necessariamente CFP e conclusão A2A.
- Atribuição, instalação, autenticação e inferência são estados diferentes.
- O workflow atual executa sequencialmente; o DAG descreve dependências.
- O gate SDD depende da operação e da especificação associada.
- RAG e EvidenceGraph são superfícies distintas; não se presume gravação automática de toda resposta.
- Importação estática não demonstra execução, validade científica ou qualidade editorial.

## Verificação e reprodução

Os testes R911 exercitam contratos inválidos, símbolos inexistentes, decisão anterior ao passo de execução, rejeição e recuperação, conservação de todos os nós e pares entre formatos e separação da legenda. Esses testes editoriais não são contabilizados como cobertura funcional do Core. A execução RED inicial e a mutação da ordem do gate são preservadas como evidência.

A reconstrução usa o gerador do atlas, o inventário de fontes e o documento principal existente. A compilação integrada do arquivo aberto isoladamente falha por ser um fragmento com `\chapter`; a compilação do livro completo em `livro-core/main.tex` é a verificação aplicável. O recibo Lean deve corresponder às fontes finais, sem transformar desenhos ou imports em teoremas.

O recibo final `verification-book-r911.json` registra compilação, testes, contagens, hashes e amostragem visual. A revisão de fontes e imagens é assistida por IA; a decisão editorial e científica final permanece humana.
