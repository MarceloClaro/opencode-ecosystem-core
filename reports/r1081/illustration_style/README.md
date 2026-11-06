# R1081 — Direção de arte: Piranesi 1750-3 / Pencz 1500-1550

**Status:** contrato visual criado; provas determinísticas geradas; **arte final
não produzida** e **modelo de imagem indisponível**.
**Não é prova histórica, não é publicação e não é validação de impressão.**

## 1. Por que esses dois artistas

**Giovanni Battista Piranesi (1720–1778)** — as *Carceri d'invenzione* (primeira
série, c. 1745–1750; reimpressão de 1761) dão a arquitetura da opressão:
arcos sobrepostos, escadas impossíveis, vigas, correntes, escala gigantesca,
chiaroscuro e a sensação de que o espaço é maior que o corpo.

**Georg Pencz (c. 1500–1550)** — a gravura do Renascimento alemão dá a figura:
contorno límpido, hachura fina, gesto legível, draperia, composição equilibrada
e emblema moral. Pencz impede que a arquitetura engula o humano.

**Síntese:** Piranesi constrói a prisão; Pencz coloca o corpo dentro dela. A
arquitetura domina a escala; a figura carrega o sentido moral.

## 2. Gramática visual

| Elemento | Regra |
|---|---|
| Perspectiva | uma linha de fuga dominante; diagonal ou eixo central |
| Escala | figura humana pequena, exceto no retrato emblemático |
| Luz | fonte única lateral; sombras profundas; hachura nas áreas escuras |
| Linha | água-forte, hachura cruzada, contorno nítido; sem aerógrafo |
| Cor | duotone sépia; **um** acento carmim por prancha |
| Papel | cream `#F2E8CF`; marca de placa; textura discreta |
| Composição | arco, porta, corredor ou moldura de placa; margem generosa |
| Legenda | small caps fora da imagem; crédito de ficção |

### 2.1 Motivos

Arcos, escadas, corredores, celas, camas, correntes, polias, vigas, chaves,
livros-razão, carimbos, ossos, corvos, carrascos, cruz, espelho, poeira, seca,
carroça, dentes, leite, zumbido.

## 3. Seis tipos de prancha

| ID | Nome | Uso | Piranesi | Pencz |
|---|---|---|---|---|
| `carceri-colonia` | Carceri do Colônia | hospital-colônia, currais, corredores | arcos, escada impossível, escala | funcionário/paciente pequenos |
| `retrato-emblematico` | Retrato Emblemático | paciente, médico, Lúcia, mãe | fundo em ruína | rosto, mãos, emblema |
| `tabela-alegorica` | Tabela Alegórica | ciclo, contaminação, culpa | ruína como palco | figuras e atributos |
| `paisagem-erodida` | Paisagem Erodida | seca, êxodo, estrada | ruína geológica, sublime | figuras minúsculas |
| `anatomia-contaminacao` | Anatomia da Contaminação | corpo, doença, metamorfose | sombra profunda | linha anatômica |
| `arquivo-doente` | Arquivo Doente | laudo, carta, prova | labirinto de estantes | ornamento e selo |

Cada tipo tem `prompt`, `negative`, `composition` e `caption` no
`style_pack.json`.

## 4. Prompts

**Base (EN):**

> Old master etching, Piranesi carceri architecture and Georg Pencz figure,
> fine cross-hatching, dramatic chiaroscuro, sepia ink on cream paper, plate
> mark, high detail, print-ready line art, no text.

**Negativo (EN):**

> photorealistic, 3D render, glossy, neon, anime, cartoon, watermark, signature,
> modern objects, color photograph, soft digital gradients, fake historical
> document, real person, text, logo.

**PT-BR e ZH** estão no `style_pack.json`. Use o prompt do tipo de prancha, não
apenas o base.

## 5. Especificações de impressão

| Item | Valor |
|---|---|
| DPI | **300** |
| Cor | duotone sépia ou 1-bit; um acento carmim |
| Papel | `#F2E8CF` |
| Tinta | `#2B2117` |
| Acento | `#9B1B1B` |
| TAC | ≤210% nos elementos de texto/linha |
| Tamanho | 2× o tamanho final |
| Formatos | TIFF 16-bit, PNG sem perdas, SVG/PDF vetorial |
| Proveniência | hash + manifesto; declarar homagem e IA |

## 6. O que foi possível executar agora

O modelo de imagem `gemini-nano-banana-2.1` está indisponível nesta conexão.
Portanto:

- **não** foram geradas ilustrações novas;
- foram geradas **provas determinísticas** de tratamento sobre três pranchas
  existentes, para testar contraste, linha, duotone e composição;
- as provas são **referência de direção**, não arte final;
- qualquer imagem futura precisa de desenhista ou modelo de imagem com revisão
  humana.

As provas estão em `samples/` e o manifesto em `samples_manifest.json`.

### 6.1 Prova textual

A prancha-demonstração está em `demo_plate.md`: uma descrição de
`carceri-colonia` na voz do perfil, com status, findings, evidence e limitations.
O perfil foi ativado, mas o subagente não executou porque o modelo padrão exige
assinatura OpenCode Go; a demonstração foi produzida pelo orquestrador na mesma
voz e está marcada como prévia, não arte final.

## 7. Ética

1. Piranesi e Pencz são **domínio público**; a obra não copia uma prancha
   específica.
2. Toda imagem é **reconstituição ficcional**; não é prova histórica.
3. Não retratar vítimas reais identificáveis.
4. Corpo, doença, violência e morte exigem **aviso de conteúdo**.
5. A arte final exige desenhista, revisão de sensibilidade e prova de impressão.
6. Imagem gerada ou assistida por IA deve ser **declarada** no manifesto.

## 8. Como usar

1. Escolher o tipo de prancha.
2. Copiar `prompt` e `negative` do JSON.
3. Gerar em 300 DPI, 2× o tamanho final.
4. Aplicar duotone e um acento carmim.
5. Revisar rosto, mãos, arquitetura e anacronismos.
6. Marcar a imagem como ficcional e registrar o hash.
7. Aprovar com revisão humana antes de entrar no livro.

## 9. Arquivos

| Caminho | Conteúdo |
|---|---|
| `style_pack.json` | gramática, 6 tipos, prompts, técnica e ética |
| `samples/` | provas determinísticas de tratamento |
| `samples_manifest.json` | hashes e limites das provas |
| `README.md` | este documento |

## 10. Limites

- Não é arte final, não é prova física e não é upload KDP.
- Não há modelo de imagem disponível nesta conexão.
- As provas não substituem desenho original.
- Nenhuma nota 10/10, publicação ou validação externa é declarada.
