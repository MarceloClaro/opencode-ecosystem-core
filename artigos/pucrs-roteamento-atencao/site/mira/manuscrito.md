# Roteamento inspirado em atenção

## Uma escolha explicável

Entre agentes diferentes, uma tarefa precisa encontrar candidatos capazes e disponíveis. O trabalho estuda uma heurística auditável, com critérios e pesos fixos. Não houve aprendizagem desses pesos.

## Filtrar antes de comparar

- A disponibilidade é obrigatória.
- Todas as capacidades requeridas devem estar presentes.
- Identificadores inválidos e duplicados ficam fora.
- Um candidato excluído não participa da normalização.

## Quatro critérios se combinam

O pipeline combina semântica, cobertura, confiança e carga livre. Os coeficientes são fixos: 0,30; 0,35; 0,25; 0,10. Entre os candidatos elegíveis, a cobertura é sempre completa.

## Pesos que somam um

O softmax transforma utilidades em pesos normalizados. A subtração do maior escore evita exponenciais positivas grandes. Normalização não é calibração probabilística.

## Ana e Cid

- Ana: semântica 0,8417; confiança 0,9; carga livre 0,9.
- Cid: semântica 0,7703; confiança 0,7; carga livre 0,6.
- Utilidades: aproximadamente 0,9175 e 0,8161.
- Pesos: aproximadamente 0,5253 e 0,4747.

## Evidência em dois planos

- Onze propriedades documentadas em Lean 4 sobre aritmética real exata.
- Bancada interna sintética: 200 decisões em cinco piscinas.
- Arrependimento médio do roteamento: 0,0421.
- Comparadores simples: aleatório 0,1882; menor carga 0,2167; maior cobertura 0,2118.

## O alcance dos resultados

As margens são exploratórias e ignoram o agrupamento por piscina. A confiança foi construída como proxy informativa da qualidade latente. Os lemas sobre reais não certificam integralmente Python nem IEEE-754. A revisão editorial não reexecutou a bateria científica.

## Continuidade da pesquisa

- Certificação do cálculo em ponto flutuante.
- Análise estatística com agrupamento.
- Comparação externa e reprodução independente.
- Conferência institucional da minuta antes da submissão.

## Fonte da apresentação

Conteúdo editorial derivado de dissertacao-abnt.tex, versão revista de 10 de outubro de 2026. Autor: Marcelo Claro Laranjeira. Esta apresentação não é uma nova execução experimental.
