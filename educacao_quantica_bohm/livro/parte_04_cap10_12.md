# 10. Prática 4 — Onda piloto e interferência {#cap10}

::: {.epigrafe}
“Ver a trajetória é fácil; ver o que a trajetória significa é o trabalho.”
:::

Esta prática usa NumPy e Matplotlib para construir um **modelo didático** de
trajetórias guiadas por um campo de fase. O objetivo não é resolver a equação de
Bohm, mas tornar visível a ideia: **a partícula segue uma trajetória; a onda
guia essa trajetória**.

## 10.1 O campo de velocidade

No modelo, a velocidade vertical é

\[
v_y(y,x) = -A\sin\!\left(\frac{2\pi y}{\lambda}\right)
\exp\!\left[-\left(\frac{x-x_0}{L}\right)^2\right].
\]

Isso cria “poços” de velocidade em \(y=0,\pm\lambda,\pm2\lambda\). As trajetórias
são integradas passo a passo:

```python
for x in np.linspace(0.20, 0.98, 650)[1:]:
    y = y + dx * vy(y, x)
```

O resultado são trajetórias que se agrupam nas franjas claras. A figura 1 do
capítulo 2 mostra o resultado.

## 10.2 A intensidade

A intensidade no anteparo é calculada pela fórmula de duas fendas:

\[
I(\theta) \propto \cos^2\!\left(\frac{\pi d\,\operatorname{sen}\theta}{\lambda}\right)
\operatorname{sinc}^2\!\left(\frac{\pi a\,\operatorname{sen}\theta}{\lambda}\right).
\]

A figura 2 mostra a curva. Repare: a **curva** é uma previsão quantitativa; as
**trajetórias** são uma imagem qualitativa.

## 10.3 Prática guiada

1. Rode a célula da prática 4 no notebook.
2. Mude a distância entre as fendas \(d\). O espaçamento das franjas aumenta ou
   diminui?
3. Mude o número de trajetórias. O padrão muda?
4. Mude a fase relativa entre as duas fendas. As trajetórias se deslocam?
5. Escreva uma frase: “o que este modelo mostra e o que ele não mostra?”.

::: {.box-limite}
**⚠️ Limite.** O modelo não inclui a equação de Schrödinger, potenciais, spin ou
interação com o aparelho. Ele mostra **uma ideia** (guia + trajetória), não uma
solução. Se você apresentar a figura como “prova” da teoria de Bohm, estará
confundindo pedagogia com evidência.
:::

::: {.box-pratica}
**🧪 Checkpoint da prática 4.**

- [ ] Você rodou o modelo.
- [ ] Você variou \(d\) e observou o espaçamento.
- [ ] Você distinguiu a curva de intensidade das trajetórias.
- [ ] Você escreveu uma frase sobre o limite.
:::

# 11. Prática 5 — Holograma e ordem implicada {#cap11}

::: {.epigrafe}
“Cada parte do holograma conta uma versão borrada do todo.”
:::

Esta prática usa a transformada de Fourier para construir uma **analogia
computacional** da ordem implicada. Não é holografia física; é uma forma de ver
como a informação pode estar distribuída.

## 11.1 O código

```python
letra = _letra_b(256)                     # imagem 256x256
F = np.fft.fftshift(np.fft.fft2(letra))   # espectro
yy, xx = np.mgrid[0:256, 0:256]
mask = ((xx-128)**2 + (yy-128)**2) < (0.06*256)**2
rec = np.abs(np.fft.ifft2(np.fft.ifftshift(F * mask)))
```

A máscara mantém apenas **1,1%** dos coeficientes. Mesmo assim, a reconstrução
mostra a letra “B” borrada.

## 11.2 Prática guiada

1. Rode a célula e compare original, espectro e reconstrução.
2. Diminua a máscara para 0,5%. O que acontece?
3. Aumente para 5%. O que melhora?
4. Retire o centro do espectro (frequências baixas). O que desaparece?
5. Escreva uma frase sobre a diferença entre “informação distribuída” e
   “holografia”.

::: {.box-limite}
**⚠️ Limite.** A analogia da ordem implicada é filosófica. Ela não explica o
emaranhamento, não prevê resultados e não substitui a teoria quântica. Use-a para
**pensar**, não para **provar**.
:::

::: {.box-pratica}
**🧪 Checkpoint da prática 5.**

- [ ] Você viu a reconstrução com 1,1%.
- [ ] Você comparou 0,5% e 5%.
- [ ] Você entendeu que a informação está distribuída.
- [ ] Você escreveu o limite da analogia.
:::

# 12. Prática 6 — Diálogo como experimento {#cap12}

::: {.epigrafe}
“O diálogo é um experimento com o próprio pensamento.”
:::

As práticas anteriores usaram código. Esta usa **presença**. O “dado” é qualitativo:
o que muda na pergunta, nas suposições e na escuta.

## 12.1 Desenho do experimento

| Elemento | Descrição |
|---|---|
| Pergunta | “O que acontece entre duas medições?” |
| Participantes | 6 a 10 estudantes |
| Facilitador | lê a pergunta, guarda o tempo, não opina |
| Observador | não fala; registra gestos, silêncios e suposições |
| Duração | 15 min |
| Registro | diário de suposições + notas do observador |

## 12.2 Roteiro

1. **Roda inicial (2 min).** Uma palavra por pessoa.
2. **Pergunta (1 min).** O facilitador lê e não explica.
3. **Rodada 1 (4 min).** Uma fala por pessoa, sem interrupção.
4. **Silêncio (1 min).** Todos escrevem uma suposição.
5. **Rodada 2 (5 min).** Respostas ao que foi ouvido, não à pessoa.
6. **Fechamento (2 min).** “O que eu levo?”.

## 12.3 O que observar

O observador registra:

- quantas vezes alguém defendeu uma posição;
- quantas vezes alguém reformulou a própria fala;
- quantos silêncios de mais de 3 segundos;
- que pergunta nova apareceu;
- se a pergunta inicial mudou.

Não há “certo” ou “errado”. Há evidência de qualidade do diálogo.

::: {.box-dialogo}
**🗣️ Regra de ouro.** Não corrija a fala do outro. Pergunte: “o que te levou a
dizer isso?”. A correção vem depois, se vier. O objetivo é ver o pensamento
funcionando, não vencer a conversa.
:::

::: {.box-pratica}
**🧪 Checkpoint da prática 6.**

- [ ] A roda aconteceu com tempo protegido.
- [ ] O observador registrou sem julgar.
- [ ] Cada participante escreveu uma suposição.
- [ ] A turma identificou uma pergunta nova.
- [ ] O diário foi preenchido.

Se algum item faltou, a prática não foi concluída — e tudo bem: dialogue é
prática, não performance.
:::