# Resposta técnica à revisão cega R828 / R830 / R832

Escopo: leitura dirigida de fontes e execução local. Decisão final humana.
Não há certificação de ausência universal de falhas ou validação externa.

| Exigência | Alteração e evidência local |
|---|---|
| Asserções por substring | R832 separa inventário e contratos descritivos de operações; cobra booleanos estritos, negações, ordem exata e SAT/UNSAT conforme fórmula. R836: 39 casos, 6/6 mutações detectadas. |
| Execução dinâmica e resposta constante | R838 reutiliza as gramáticas restritas de R818/R821. Atribuições explícitas participam do SMT; soma/integral formal refletem a entrada; texto recusado retorna fallback. Trust não registrado. RED: 8 falhas; GREEN inicial: 29 casos; regressão dirigida: 322 casos. |
| Gate comportamental duplicado | `trust.behavioral_gate` é canônico; `protocolos.behavioral_gate` só traduz a chamada e preserva integralmente o retorno. Scanner usa uma categoria canônica. |
| Cobertura circular | R835 mantém autodescoberta identificada como lexical. Entrada retida exige ID e SHA, sem enriquecimento na etapa noológica; cache considera a entrada. 81 categorias canônicas, 83 projeções. Trecho humano retido: 4/81, 5%; vazio: 0/81. 85 casos relacionados e 3/3 mutações detectadas. |
| Numeral de ciclo arbitrário | R836 consulta o maior numeral do ledger, reconhece sufixos históricos e recusa ledger inválido. Não usa número de entradas mais offset. Não reserva specs e não reescreve histórico. |

R828 agora testa o DiagnosticPipeline real com entrada retida e verifica que
diagnose não promove confiança. Fixtures de formatação são identificadas como
artificiais. Entrega sem spec no modo estrito e spec inexistente no modo legado
falham; o runner confiável continua sendo a fonte de evidência de execução.

Os objetivos originais de R828 — aumento de cobertura, escore teleológico e
redução de licenças ausentes — permanecem propostas pendentes. Os números
históricos fornecidos no despacho não servem como medição atual nem se comparam
diretamente ao corpus retido. Licença ausente não pode ser inventada.

A exigência de histórico RED recebeu implementação R839: execução pytest real,
recibos autenticados, vínculo de spec/testes/fixtures e ordem RED→GREEN. O gate
de software fecha quando falta esse histórico; inspeção de critérios é distinta
de entrega. Ver `TDD_HISTORICO_RED.md`. Registros antigos incompletos não são
transformados em prova por backfill fictício.

A rede visual R829 observa registros reais no terminal e no painel. Busca
lexical local encontrou três registros na sondagem do navegador, sem alterar
o arquivo de memória; demonstração, pausa e retorno a dados locais foram
executados. Exportação do EvidenceGraph preserva IDs e referências, sem
fabricar associação em exportações antigas.

Recibos: `outputs/core-r828/`, `core-r829/`, `core-r835/`, `core-r836/`,
`core-r837/` e `core-r838/`. A suíte integral e o registro de evolução são
consolidados separadamente em `outputs/core-r820/`; este texto não os presume.
