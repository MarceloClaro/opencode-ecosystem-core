# R1094 — Molambudos, Edição Grimório (RPG)

**Objeto:** `literatura/molambudos/Molambudos_Grimorio_R1094/`, derivado da
R1075. **Não substitui** a R1075, a R1077, a canônica ou o EPUB.

**Status:** variante visual de grimório/RPG, compilada e verificada localmente.
**Não é um jogo completo**, não é um sistema de regras, não é nova ISBN, não é
publicação e não é certificação KDP. O aparato de mesa é **opcional**. O aparato opcional não altera o texto, a ordem ou o desfecho.

## 1. Artefatos

| Artefato | Estado | SHA-256 |
|---|---|---|
| `main.pdf` | 391 pp; 160 × 230 mm; fontes embutidas | `047957ac4bd16c97b88ffd5c088896fb1b22ca2030d24fc26d510c5eb1c4a20d` |
| `capa/capa_grimorio.pdf` | 1 página; 160 × 230 mm; capa frontal | `82438c27e1cb0deca21b9e910c99f882c5ab857bedc70d62f9cd34142800f13f` |
| `capa/capa_grimorio.png` | prévia 300 DPI | regenerável a partir do PDF |
| `main.tex` | fonte LaTeX com a camada RPG | — |
| `book.json` | manifesto da edição | — |

## 2. Direção de arte

- **Paleta:** tinta `#1A120C`, papel `#EFE0BF`, ouro `#B08D57`, sangue
  `#7A1E1E`, teal `#1F5C57`, violeta `#4B2A5E`.
- **Tipografia:** EB Garamond no corpo; `yfonts` (`ygoth`) nas iniciais
  circulares, nos numerais romanos das partes e no título. Os títulos com
  acento ficam em versaletes de EB Garamond, para não perder glifos.
- **Abertura de fragmento:** selo circular com a inicial gótica, etiqueta da
  família, título em Garamond, filete dourado e código do fragmento.
- **Abertura de parte:** página preta, moldura dupla dourada, numeral romano
  gótico, título em versaletes, ícone e a linha “Arquivo 1.260 · Acesso
  restrito”.
- **Página:** papel pergaminho, cabeçalho em versaletes, folio entre losangos
  dourados e margem externa ampliada (30 mm) para respirar.
- **Caixas:** `tcolorbox` em duas famílias — pergaminho com moldura dourada
  (`rpgbox`) e preto com texto dourado (`rpgdark`).
- **Dados:** ícone `\faDiceD20` nas caixas e nas tabelas; nenhuma aleatoriedade
  altera o texto.

## 3. Aparato de mesa

| Página (PDF) | Peça | Função |
|---:|---|---|
| 1 | Folha de rosto Grimório | título gótico, selo d20, créditos |
| 17 | Protocolo de Mesa | quatro modos de leitura + rota d20 + códigos |
| 19 | Ficha do Paciente 1.263 | identificação, atributos, trilha 0–20, sintomas, registro |
| 20 | Verso da ficha | sintomas, registro e notas do jogador |
| 23 | Tabela de Rotas d20 | vinte entradas com fragmento, título e página |
| 39 | MEM-01 | abertura de fragmento com selo gótico |
| 372 | Handouts | seis provas iconográficas em cartões individuais |
| 388 | Verbete da Criatura | ficha incompleta, quote, reação d6 |

O aparato **não acrescenta fatos novos** ao romance. A tabela d20 escolhe por
onde entrar; a ficha organiza a leitura; o verbete da criatura é um artefato
ficcional declaradamente incompleto. A frase “não é um stat block jogável”
aparece no próprio verbete.

## 4. Ética preservada

- O **Aviso ao Leitor** e a página **Cuidado** continuam no volume, com CVV,
  CAPS e o direito de interromper.
- A **Nota Histórica** mantém a distinção entre a versão narrativa do Colônia e
  a instituição histórica; a **Nota do Arquivista** separa dor histórica de
  prontuário ficcional.
- A **Ficha do Paciente 1.263** diz “Formulário opcional, sem valor clínico.
  Uso ficcional. Não deve ser enviado a ninguém.”
- O **bestiário** não transforma vítimas reais em monstros: a criatura é
  “consequência”, e a ficha é declarada incompleta.
- As imagens dos handouts continuam marcadas como **reconstituições ficcionais**.

## 5. Compilação e verificação

```bash
cd literatura/molambudos/Molambudos_Grimorio_R1094
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex

cd capa
pdflatex -interaction=nonstopmode -halt-on-error capa_grimorio.tex
pdflatex -interaction=nonstopmode -halt-on-error capa_grimorio.tex
pdftoppm -png -r 300 -singlefile capa_grimorio.pdf capa_grimorio
```

- 391 páginas; 160 × 230 mm; fontes embutidas; texto extraível.
- Dois `Overfull \hbox` de 1,04 pt e 1,61 pt — abaixo do limite de 2 pt e
  invisíveis na impressão.
- Capa de 1 página, 160 × 230 mm, arte da capa escolhida, título gótico, sem
  ISBN falso e sem “62 anos” debaixo da terra.
- Testes: `python3 -m pytest -q tests/test_r1094_molambudos_grimorio.py`.
- R1075 intacta: PDF `bd78c8…`, 84 fragmentos, “223 rotas”.

## 6. Limites

- **Não é um jogo completo.** As fichas e tabelas são aparato de leitura, não
  um sistema testado em mesa; não há regras de combate, progressão ou mestre.
- **Não substitui a R1075.** A edição de leitura/canônica do ciclo continua
  sendo a R1075; esta é uma variante visual.
- **Não é KDP/preflight.** A capa é frontal, sem lombada, contracapa ou
  sangria de capa; não houve previewer oficial nem prova física.
- **Não é nova ISBN.** O ISBN do miolo continua o da edição, e a capa não
  imprime código de barras.
- **Não há validação humana externa.** A tipografia, a legibilidade e o
  equilíbrio visual pedem revisão humana; nenhuma nota 10/10 é certificada.
- **Dados e fichas não são canônicos.** São dispositivos de leitura; o texto
  literário não depende deles.

---

*Esta é uma edição visual de grimório/RPG. Não certifica 10/10, não é um jogo
completo e não substitui a edição de leitura R1075.*
