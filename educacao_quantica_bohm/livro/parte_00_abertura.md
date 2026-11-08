```{=html}
<div class="capa">
  <div class="capa-arte"></div>
  <div class="capa-conteudo">
    <p class="capa-eyebrow">OPENCODE ECOSYSTEM CORE · EDIÇÃO BLACK</p>
    <h1 class="capa-titulo">Bohm na Escola</h1>
    <p class="capa-subtitulo">Onda piloto, diálogo e totalidade no ensino de informação quântica</p>
    <p class="capa-livro">Livro didático e laboratório · PennyLane · Cirq · Qiskit</p>
    <p class="capa-publico">9º ano do Ensino Fundamental e Ensino Médio</p>
    <div class="capa-selo">BNCC Computação · Design black · Práticas de laboratório</div>
  </div>
</div>
```

```{=html}
<div class="rosto">
  <p class="rosto-colecao">Coleção Educação Básica · Edição Black</p>
  <h1 class="rosto-titulo">Bohm na Escola</h1>
  <p class="rosto-subtitulo">Onda piloto, diálogo e totalidade no ensino de informação quântica</p>
  <p class="rosto-linha"></p>
  <p class="rosto-descricao">Livro do estudante, laboratório de práticas e manual do professor.<br>
  Uma aula sobre o que pode estar acontecendo — e sobre como pensar juntos.</p>
  <p class="rosto-autoria">Orquestração editorial: <strong>marceloclaro</strong><br>
  OpenCode Ecosystem Core</p>
  <p class="rosto-edicao">1.ª edição · 2026</p>
  <p class="rosto-aviso">Material didático para uso em sala de aula.<br>
  Bohm é apresentado como uma lente entre várias — não como consenso científico.<br>
  </p>
</div>
```

# Como ler este livro {#como-ler}

Esta edição foi desenhada em **preto**, para tela, projetor e leitura noturna.
Ela não substitui a edição clara: para impressão em grande quantidade, o fundo
escuro consome tinta. Use esta versão quando a tela for o meio principal.

## Os sinais do caminho

::: {.box-bohm}
**🌊 Lente de Bohm.** Uma ideia de David Bohm — onda piloto, diálogo, ordem
implicada — apresentada com o cuidado de distinguir **interpretação**, **analogia**
e **fato experimental**.
:::

::: {.box-pratica}
**🧪 Prática de laboratório.** Código executável em PennyLane, Cirq ou Qiskit.
Toda prática tem objetivo, código, resultado esperado e um checkpoint.
:::

::: {.box-limite}
**⚠️ Limite.** O ponto em que a analogia, o modelo ou a interpretação deixa de
funcionar. Não é um detalhe: é parte do conceito.
:::

::: {.box-dialogo}
**🗣️ Roda de diálogo.** Um gesto bohminiano: suspender suposições, escutar,
desacelerar e investigar o pensamento em conjunto.
:::

::: {.box-diario}
**✍️ Diário de bordo.** Três perguntas: o que eu vi, o que eu suponho, o que eu
quero testar. O diário é o elo entre a prática e o pensamento.
:::

## A promessa e o limite desta edição

A promessa é simples: você vai **ver** a mecânica quântica funcionando em três
bibliotecas diferentes, vai **desenhar** o mesmo estado de Bell em PennyLane,
Cirq e Qiskit, e vai **discutir** o que essas representações não mostram.

O limite é igualmente simples: nenhuma dessas bibliotecas prova que a onda piloto
é a descrição correta do mundo. Elas calculam previsões. A interpretação de Bohm
é uma das leituras possíveis dessas previsões — não a única, nem a majoritária.

> **Regra de ouro desta edição:** sempre que alguém disser “a física quântica é
> assim”, pergunte: *isso é um resultado experimental, uma interpretação ou uma
> analogia?* As três coisas têm valor, mas não são a mesma coisa.

## O que você precisa ter em mãos

- Este livro (PDF ou HTML).
- O notebook `AULA_BOHM_LABORATORIO.ipynb` no Google Colab ou Jupyter.
- Acesso à internet para instalar as bibliotecas na primeira vez.
- Caderno, lápis e, se possível, um projetor para as rodas de diálogo.

## Instalação rápida (Colab)

No início do notebook, execute uma vez:

```bash
!pip install -q pennylane qiskit cirq pylatexenc
```

As três bibliotecas são gratuitas e de código aberto. O notebook foi testado com
PennyLane 0.45, Cirq 1.7 e Qiskit 2.6. Versões diferentes podem mudar pequenos
detalhes de desenho, mas os conceitos permanecem.

# Carta ao estudante {#carta-estudante}

Você já ouviu que a mecânica quântica é estranha. Provavelmente ouviu também que
ninguém entende. As duas frases são meio verdadeiras e meio preguiçosas.

David Bohm foi um físico que levou a estranheza a sério. Em vez de dizer “não
pergunte o que acontece antes da medição”, ele propôs uma imagem: **uma onda que
guia partículas que sempre têm uma posição**. Essa imagem não é a única, mas é
poderosa — e nos obriga a dizer, com clareza, o que estamos supondo.

Este livro usa Bohm de três modos:

1. **Como lente ontológica:** e se houver uma trajetória? O que ganhamos e o que
   perdemos ao imaginar isso?
2. **Como pedagogia do diálogo:** como pensar junto sem transformar a conversa
   em disputa?
3. **Como poética da totalidade:** a ideia de que o todo pode estar presente em
   cada parte — uma analogia para o emaranhamento, não uma prova.

Você não precisa concordar com Bohm. Precisa saber **o que ele propôs**, **por que
isso faz as mesmas previsões** e **qual é o preço** da proposta. Isso é educação
científica: não é colecionar nomes, é aprender a avaliar modelos.

::: {.box-diario}
**✍️ Antes de começar.** Escreva em uma frase: *o que eu acho que acontece entre
duas medições?* Guarde. No final, releia e veja se a pergunta mudou.
:::

# Carta ao professor {#carta-professor}

Esta edição nasceu de um pedido: ensinar Bohm na educação básica, com rigor e com
prática o tempo todo, usando ilustrações geradas por PennyLane, Cirq e Qiskit.

## O que esta edição é

- Uma **lente interpretativa** sobre a informação quântica, não um curso de
  mecânica quântica completa.
- Um **laboratório** com três bibliotecas reais e figuras geradas por código.
- Uma **pedagogia de diálogo** inspirada em Bohm, com protocolo de sala.
- Um material **visual black**, pensado para tela e projetor.
- Um convite a separar **fato**, **interpretação** e **analogia**.

## O que esta edição não é

- Não afirma que a onda piloto é a interpretação correta.
- Não afirma que a ordem implicada é uma teoria física comprovada.
- Não substitui a edição clara para impressão em massa.
- Não promete aprendizagem, nota ou aprovação.

## Como usar em 100 minutos

| Tempo | Bloco | O que fazer |
|---|---|---|
| 0–10 | Abertura | pergunta: “o que acontece entre duas medições?” |
| 10–25 | Lente de Bohm | cap. 1–2 + figura da onda piloto |
| 25–45 | Diálogo | cap. 3 + roda de 15 min |
| 45–70 | Laboratório | cap. 6–7 + PennyLane/Cirq/Qiskit |
| 70–85 | Totalidade | cap. 4–5 + holograma/emaranhamento |
| 85–100 | Síntese | projeto + diário + checkpoint |

## Como usar em duas aulas de 50 minutos

- **Aula A:** cap. 1–3 + roda de diálogo + prática PennyLane.
- **Aula B:** cap. 4–6 + práticas Cirq/Qiskit + projeto.

## Uma advertência sobre o design black

O fundo preto é ótimo para projetor e tela, mas **não é econômico para impressão**.
Se a escola for imprimir para 40 estudantes, use a edição clara ou imprima apenas
as páginas de prática. Esta edição foi feita para ser lida com luz baixa e para
destacar as figuras geradas por código.

## Uma advertência sobre Bohm

Bohm não é consenso. A interpretação de onda piloto faz as mesmas previsões da
mecânica quântica não relativística, mas paga um preço: **não localidade** e uma
descrição em espaço de configuração. Apresente-a como uma lente, não como a
verdade revelada. O valor pedagógico está em comparar modelos — não em recrutar
adeptos.