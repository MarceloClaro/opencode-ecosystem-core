# Relatório de repetições {#repeticoes}

> Auditoria automática das 3000 laudas. Mede repetição textual, não
> qualidade pedagógica. Repetição intencional de template não é erro;
> repetição editorial sem função é candidata a corte na edição enxuta.

- Laudas analisadas: **3000**
- Palavras (texto limpo): **451.411**
- Parágrafos repetidos (≥ 2 ocorrências): **21.031**
- N-gramas distintos: **48.154**

## 1. Laudas por lente

| Lente | Laudas |
|---|---:|
| alem | 300 |
| analogia | 300 |
| checkpoint | 300 |
| dialogo | 300 |
| erro | 300 |
| etica | 300 |
| ideia | 300 |
| laboratorio | 300 |
| pratica | 300 |
| vida | 300 |

## 2. Parágrafos mais repetidos

| Ocorrências | Parágrafo |
|---:|---|
| 1000 | Para pesquisa: repita com outra seed/backend. |
| 200 | Para o professor: Diga 'interpretação', não 'prova'. |
| 179 | RIGOR CIENTÍFICO A matemática é representação; não é o fenômeno. |
| 146 | Registre a diferença e uma possível explicação. |
| 146 | O que observar: não basta acertar; é preciso explicar por que acertou. |
| 100 | Para o professor: Comece pelo concreto; só depois use a notação. |
| 100 | Desenhe a imagem e marque com um X o ponto em que ela falha. |
| 100 | Faça em 5 minutos; anote o que esperava antes de começar. |
| 100 | Como não cair: escreva um contraexemplo e teste com um colega. |
| 100 | Guarde uma pergunta para a próxima aula; não precisa resolver tudo hoje. |
| 100 | Ouça sem interromper; anote uma ideia que mudou sua opinião. |
| 100 | Onde isso aparece: procure um exemplo na sua casa ou na escola. |
| 100 | Para o professor: Confira a ordem dos qubits antes de comparar. |
| 100 | Para o professor: Se as bibliotecas divergirem, verifique a convenção. |
| 100 | Para o professor: Ruído, leitura e calibração são coisas distintas. |
| 100 | Para o professor: Explique o teto e o tamanho da amostra. |
| 100 | Para o professor: Use exemplos pequenos antes da fórmula. |
| 100 | Para o professor: Nanoaula é tempo e evidência, não fragmento. |
| 100 | Para o professor: Peça evidência, afetados e alternativas. |
| 100 | Para o professor: Exija um limite específico. |
| 100 | Para o professor: Use a notação de ket apenas depois do concreto; verifique P(0)+P(1)=1. |
| 100 | Teste rápido: desenhe a analogia e marque com um X o ponto em que ela deixa de explicar o conceito. |
| 100 | Por que acontece: o cérebro procura uma imagem simples e apaga a parte matemática que não se encaixa. |
| 100 | Como testar: escreva um contraexemplo em uma frase e veja se ele derruba sua explicação. |
| 100 | Conexão científica: este é o ponto em que a intuição precisa dar lugar a uma definição precisa. |
| 100 | A caixa de rigor abaixo guarda essa definição. |
| 100 | Para ir além: procure um exemplo em que a ideia falha e explique por quê. |
| 100 | Roteiro de 9 minutos: 1 minuto de silêncio; 4 minutos de falas sem interrupção; 2 minutos de respostas ao que foi ouvido; 2 minutos de síntese. |
| 100 | Regra: não corrija a fala do outro; pergunte o que o levou a dizer aquilo. |
| 100 | Registre: uma suposição que apareceu e uma pergunta nova. |

## 3. N-gramas mais repetidos (5 palavras)

| Ocorrências | N-grama |
|---:|---|
| 3000 | p c l g f |
| 2400 | resultado visual simulado backend sim |
| 2400 | visual simulado backend sim backend |
| 2400 | simulado backend sim backend p |
| 2400 | backend sim backend p c |
| 2400 | sim backend p c l |
| 2400 | backend p c l g |
| 1000 | para pesquisa repita com outra |
| 1000 | pesquisa repita com outra seed |
| 1000 | repita com outra seed backend |
| 1000 | com outra seed backend checkpoint |
| 578 | sobreposição fidelidade de estado script |
| 578 | fidelidade de estado script scripts |
| 578 | de estado script scripts experimentos |
| 578 | estado script scripts experimentos py |
| 578 | script scripts experimentos py e |
| 578 | scripts experimentos py e guoji |
| 578 | experimentos py e guoji oficina |
| 578 | py e guoji oficina e |
| 578 | e guoji oficina e código |
| 578 | guoji oficina e código e |
| 400 | outra seed backend checkpoint você |
| 400 | seed backend checkpoint você consegue |
| 360 | ponte sonora termo liàng z |
| 340 | outra seed backend checkpoint quem |
| 300 | lauda lente ideia nivel l |
| 300 | lente ideia nivel l ideia |
| 300 | ideia nivel l ideia em |
| 300 | nivel l ideia em s |
| 300 | l ideia em s n |

## 4. Leitura

- A repetição de **template** (topo, ponte, resultado, rodapé) é
  estrutural: ela ajuda a navegar. Não deve ser cortada sem substituição.
- A repetição de **frases de transição** e **micropráticas** é a principal
  candidata a compressão na edição enxuta.
- A repetição de **nomes de experimentos** é necessária para rastrear
  E01–E18; não é redundância.
- A edição enxuta deve manter **uma** ocorrência de cada template por
  módulo e usar remissões para o restante.

## 5. Ações recomendadas

1. Substituir micropráticas repetidas por uma lista de 10 micropráticas
   por módulo.
2. Usar `ver seção X` em vez de repetir a explicação de uma lente.
3. Manter a Ponte Sonora apenas uma vez por módulo na edição enxuta.
4. Manter as notas de cálculo específicas; remover as genéricas.
5. Revisar os 30 parágrafos acima com um editor humano.

> **Limite:** esta auditoria é lexical. Ela não decide o que é pedagogicamente
> necessário. A decisão de corte é humana e deve preservar a sequência
> didática.
