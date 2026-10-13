---
spec_id: SPEC-935-R815
title: Triagem lexical científica bilíngue com negação e limites explícitos
component: scanners/scientific_reasoning_scanner.py
status: implemented
round_id: R815
test_file: tests/test_r815_scientific_lexical_screening.py
---

# SPEC-935-R815 — Correção da triagem lexical científica

O scanner R223 conta substrings em português e divide o total por quatro.
Isso atribui pontos a `sem` por conter `se`, distingue traduções equivalentes,
conta uma limitação negada como método realizado e satura a nota antes de
cobrir o vocabulário. R645 congelou a reprodução histórica desses defeitos;
três de seus testes também pressupõem uma versão antiga do manuscrito OdontoCA.

## Contrato

1. Preservar `scan_text`, `evaluate_hypothesis`, os campos de score, as listas
   públicas de palavras e os rótulos legados de status. Qualificar esses
   rótulos explicitamente como faixas de uma heurística lexical, sem avaliação
   de qualidade científica, risco de viés, validade clínica ou PROBAST+AI.
2. Usar fronteiras de palavras Unicode e normalização de acentos e travessões.
   Reconhecer aliases PT/EN agrupados por conceito, contando cada conceito uma
   única vez. Textos controlados semanticamente equivalentes têm os mesmos
   indicadores; traduções integrais podem conter descrições distintas.
3. Normalizar cada dimensão pelo total de seis grupos conceituais. Não saturar
   com quatro grupos, nem aumentar scores repetindo aliases. Os grupos de
   falsificabilidade são hipótese, condição, previsão, refutação, teste empírico
   e mensuração. Os metodológicos são desenho/controle/mascaramento, amostragem,
   incerteza, variáveis, comparação de referência e reprodutibilidade.
4. Excluir afirmações com negação local reconhecida antes ou depois do termo,
   em PT/EN, e rótulos de seção Markdown. Registrar os conceitos afirmativos e
   negados para inspeção. Tratar `mas`/`but` e fronteiras de sentenças como
   limites de escopo. Essa regra local não é interpretação semântica geral.
5. Detectar os quatro gatilhos categóricos legados também em inglês, sem
   sinalizar sua negação explícita. Não inferir ausência de falácias pela
   ausência de gatilhos, nem recomendar controle em todo desenho de estudo.
6. O campo legado `is_testable` indica apenas condição e previsão textuais;
   exige ambos e não prova testabilidade. Uma premissa negativa mantém essa
   estrutura; negar um método próximo não nega o conector. Entradas vazias produzem zero;
   tipos diferentes de string são rejeitados com ValueError.
7. Reconciliar R645 para proteger o comportamento corrigido e os limites de
   interpretação. Não modificar manuscritos EN/PT, S4 ou suas conclusões; guardar
   hashes antes/depois. S4 permanece uma avaliação interna descrita no arquivo,
   sem promoção a validação externa.
8. As descrições MCP assíncronas e do wrapper síncrono apresentam triagem
   lexical e ausência de avaliação de qualidade científica. Preservar nomes,
   campos de entrada e rótulos agregados legados. Tanto scientific_reasoning_scan quanto
   o ramo scientific_rigor de super_rigor_audit devem transportar os metadados
   e limites íntegros, sem editar a implementação do pipeline.
9. Indexar uma vez palavras, limites de frases e linhas, mantendo as janelas
   de oito/sete palavras e a semântica usual sem varrer prefixo e sufixo
   completos a cada ocorrência. A entrada controlada de 28.800 caracteres
   repetidos deve concluir em menos de dois segundos no teste local.
10. Reconhecer negações coordenadas locais com `nem`, `neither` e `nor`.
11. Limitar as duas ferramentas MCP científicas a 1.000.000 de caracteres
    Unicode no schema. Rejeitar excesso explicitamente antes de iniciar
    scanners, inclusive no handler registrado pelo SDK, sem eco de valores.

## Verificação

RED de R645 preservado em `outputs/core-r815/r645-baseline-red.txt`.
Contraprovas RED/GREEN, regressões R223/R224 e contratos do pipeline são
registrados em `outputs/core-r815`. A suíte geral e o ciclo de evolução são
coordenados pelo agente primário MarceloClaro nesta revisão do Core.

Resultados locais: baseline R645 **3 failed, 6 passed**; contraprovas iniciais
**45 failed, 8 passed**; complemento de escopo da negação **3 failed**;
regressão R815/R645/R223/R224/R767/R809 **100 passed**. Quatro mutações sintéticas
confinadas a processos Python separados foram detectadas pelos testes: remoção
de fronteiras, de aliases ingleses, da negação e restauração do divisor quatro.
Hashes antes/depois de EN/PT/S4 coincidem. Esses resultados validam o contrato
operacional local, sem validar cientificamente a heurística ou os manuscritos.

Extensão da interface `scanners/scanners_mcp_server.py`: RED das descrições
**4 failed, 4 passed**; regressão ampliada com R229/R232/R660 **189 passed** em
65,35 s. Prova em processo MCP stdio real executou initialize, tools/list e
as duas ferramentas científicas, preservando metadados e negação. Evidence
íntegra: `outputs/core-r815/mcp-stdio-evidence.json`, SHA-256
`93d29e46cc9555dc0ef88b75e807953b05522dbe340fe1b969d3c35ef54c7653`.
As descrições dos scanners literários adjacentes também qualificam a triagem
como heurística; nomes e schemas permanecem compatíveis.

## Contraprovas da revisão independente

A revisão adicional reproduziu dez falhas: negação coordenada, tempo de
processamento e ausência de limite MCP. O contexto indexado preservou os
relatórios de 400 textos usuais controlados e de EN/PT/S4; seus hashes não
mudaram. A medição de 28.800 caracteres passou de mais de oito segundos
(processo interrompido pelo prazo) para 0,0678 s nesta rodada local.

A validação automática do SDK ecoava o texto excessivo no erro de schema;
duas novas contraprovas RED demonstraram o problema. O handler usa agora a
validação sanitizada já existente, com o mesmo schema, antes de qualquer
scanner. GREEN final R815: 67 testes em 5,18 s. A regressão ampla aprovou
199 testes; depois da alteração do decorator, os 81 contratos MCP passaram
em 52,26 s. A união dos relatórios cobre 201 casos distintos.
Um processo MCP stdio real inicializou, anunciou os limites e executou as
duas ferramentas: negação coordenada foi preservada e cada excesso retornou
erro com apenas 114 caracteres, sem eco do sentinela sintético. As evidências
adicionais são `outputs/core-r815/corrective-*`, preservando os logs históricos.

Mutação adicional: quatro de cinco variantes isoladas foram detectadas,
incluindo retorno à varredura de frase/prefixo completo, remoção das negações,
remoção do limite e restauração do eco do SDK. Uma variante mais fraca que
reintroduz apenas tokenização do prefixo permaneceu abaixo do limiar de dois
segundos; o teste de tempo não demonstra complexidade assintótica de toda
variante possível. O resultado sobrevivente permanece registrado no resumo.
