# Uso e limites do scanner científico

`ScientificReasoningScanner.scan_text(text)` realiza triagem lexical em
português e inglês. O resultado ajuda a localizar vocabulário e possíveis
afirmações categóricas para revisão humana. Não examina dados, não confirma que
um método foi executado e não avalia qualidade científica ou validade clínica.

Os campos históricos `sri_score`, `falsifiability_score`, `methodology_score`
e `status` continuam disponíveis. `high_rigor`, `moderate_rigor` e `low_rigor`
são nomes legados das faixas numéricas. Leia-os sempre com
`score_kind="lexical_heuristic"`, `scientific_quality_assessed=false`,
`risk_of_bias_assessed=false` e `limitations`. Mesmo uma nota 100 não constitui
aprovação editorial ou avaliação de risco de viés.

A versão R815 conta conceitos PT/EN com fronteiras de palavras, normalizando
acentos e variantes de travessão. Cada dimensão contém seis grupos; aliases
do mesmo grupo contam uma única vez. Quatro grupos representam 66,67% da
dimensão, não 100%. As dimensões são combinadas com pesos históricos 0,4 e 0,6,
com penalidade de 15 pontos por categoria de gatilho categórico detectado.

`matched_concepts` permite inspecionar os grupos reconhecidos em afirmações;
`negated_concepts` registra os reconhecidos em negações locais. Ambos podem
conter o mesmo grupo quando o texto apresenta afirmações distintas. Títulos
Markdown isolados ou rótulos iniciais em negrito não comprovam métodos.
`Não há grupo de controle` e `No control group was used` não concedem pontos
de desenho. Controle não é obrigatório para todos os desenhos científicos.
Coordenações explícitas com `nem`, `neither` e `nor` também são registradas
como negação, sem conceder pontos aos métodos negados.

A negação usa uma janela lexical local e limites de frases, contrastes como
`mas`/`but` e vírgulas posteriores ao termo. Não é análise sintática ou
semântica geral: citações, referências bibliográficas, ironia, coordenações
complexas, omissões e negadores distantes podem produzir falsos positivos ou
negativos. A ausência de gatilhos também não comprova ausência de falácias.
Traduções integrais podem mencionar conceitos em estruturas diferentes;
equivalência de scores só é garantida para os casos controlados testados.
O contexto de palavras, frases e linhas é indexado uma vez por entrada;
cada ocorrência consulta no máximo oito palavras anteriores e sete posteriores.
Não há nova varredura do texto inteiro para cada ocorrência de um alias.

`evaluate_hypothesis(text)` conserva o campo `is_testable` como indicador da
presença de condição e previsão textuais. Ele exige ambos, inclusive quando a
premissa é negativa, e não determina testabilidade real ou validade da
hipótese. Entradas vazias têm score zero; outros tipos são rejeitados.

A triagem não realiza PROBAST+AI e não substitui revisão estruturada. Para
OdontoCA, os manuscritos EN/PT e o S4 mantêm suas conclusões e limitações
próprias. O scanner não promove a avaliação interna de S4 a validação externa,
nem autoriza uso clínico. Resultados anteriores à R815 foram calculados por
uma regra diferente e não devem ser comparados numericamente sem reexecução
e identificação da versão.

As ferramentas MCP `scientific_reasoning_scan` e `super_rigor_audit` anunciam
esses limites em suas descrições. A primeira retorna os metadados diretamente
no relatório; a segunda os conserva em `scientific_rigor`. Os nomes e os
rótulos agregados legados do pipeline são preservados. Ambas aceitam no máximo
1.000.000 de caracteres Unicode por chamada, conforme `maxLength` nos schemas.
Excesso é recusado antes dos scanners, com erro MCP explícito que informa
a regra e o caminho, sem ecoar o texto. A API Python direta mantém seu contrato;
o limite pertence à fronteira MCP. Textos maiores exigem triagem por partes,
cujos scores não devem ser tratados como o score de uma análise integral.
Esses rótulos também não representam aprovação científica.

Contrato: `specs/SPEC-935-R815-scanner-lexical-bilingue.md`. Contraprovas e
regressões: R815, R645, R223 e R224. Logs de execução e hashes dos documentos
preservados: `outputs/core-r815`.
