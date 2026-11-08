# Relatório de repetições {#repeticoes}

> Auditoria automática das 3000 laudas. Mede repetição textual, não
> qualidade pedagógica. Repetição intencional de template não é erro;
> repetição editorial sem função é candidata a corte na edição enxuta.

- Laudas analisadas: **3000**
- Palavras (texto limpo): **375.141**
- Parágrafos repetidos (≥ 2 ocorrências): **15.178**
- Baseline R1099: **21.031** parágrafos repetidos; após a poda R1102: **15.178**.
- N-gramas distintos: **43.819**

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
| 169 | RIGOR CIENTÍFICO A matemática é representação; não é o fenômeno. |
| 146 | Registre a diferença e uma possível explicação. |
| 146 | O que observar: não basta acertar; é preciso explicar por que acertou. |
| 100 | Desenhe a imagem e marque com um X o ponto em que ela falha. |
| 100 | Fidelidade proxy não é prova de emaranhamento. |
| 100 | Não há método com efeito garantido para toda turma. |
| 100 | Não há resposta automática; há deliberação e consequências. |
| 100 | Declare limite, evidência e o que ficou fora. |
| 100 | Governança: quem audita, quem responde e como reparar? |
| 90 | RIGOR CIENTÍFICO Backends têm ruído, calibração e deriva. |
| 90 | RIGOR CIENTÍFICO Quatro pontos e 1024 tiros não generalizam. |
| 90 | RIGOR CIENTÍFICO Ética envolve valores e poder. |
| 90 | RIGOR CIENTÍFICO O resultado de hoje não garante o de amanhã; calibração muda. |
| 90 | RIGOR CIENTÍFICO O teste é pequeno; não generaliza para outros dados ou modelos. |
| 90 | RIGOR CIENTÍFICO A técnica não funciona igual para todos os estudantes. |
| 90 | RIGOR CIENTÍFICO Não há consenso moral automático; há trade-offs. |
| 90 | RIGOR CIENTÍFICO O projeto não esgota o problema; escolhe um recorte. |
| 89 | RIGOR CIENTÍFICO A equação não explica por que o mundo segue a equação. |
| 80 | RIGOR CIENTÍFICO Medir produz uma amostra; não é ler um valor escondido. |
| 80 | RIGOR CIENTÍFICO Bohm é uma interpretação entre várias; não é consenso. |
| 80 | RIGOR CIENTÍFICO Circuito é um modelo; a ordem dos qubits importa. |
| 80 | RIGOR CIENTÍFICO Bibliotecas simulam; convenções podem mudar o resultado. |
| 80 | RIGOR CIENTÍFICO Backend tem ruído; um número não prova o estado. |
| 80 | RIGOR CIENTÍFICO Amostra pequena não generaliza; 4 pontos não são um artigo. |
| 80 | RIGOR CIENTÍFICO Pedagogia é contextual; não há método garantido. |
| 80 | RIGOR CIENTÍFICO Ética envolve valores e poder; não há resposta automática. |
| 80 | RIGOR CIENTÍFICO Todo projeto é um recorte; declare o limite. |
| 64 | Simulado: P(0000)+P(1111) = 1,000 (ideal 1,000) Backend: P(0000)+P(1111) = 0,788 (ideal 1,000) Sobreposição: 78,8% · task: — Sobreposição ≠ fidelidade de estado. |
| 58 | Simulado: ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1) Backend: ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1) Sobreposição: 98,9% · task: 9da79d10 Sobreposição ≠ fidelidade de estado. |
| 56 | RESULTADO · SIMULADO × BACKEND Experimento: Esfera de Bloch — Mede Z e X do estado H&#124;0⟩. |

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
| 400 | oficina e código e rigor |
| 400 | e código e rigor científico |
| 360 | ponte sonora termo liàng z |
| 300 | lauda lente ideia nivel l |
| 300 | lente ideia nivel l ideia |
| 300 | ideia nivel l ideia em |
| 300 | nivel l ideia em s |
| 300 | l ideia em s n |
| 300 | ideia em s n c |
| 300 | sh hé x n gài |
| 300 | hé x n gài niàn |
| 300 | é o conceito central leia |
| 300 | o conceito central leia em |

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
