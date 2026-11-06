# R1080 — Assistente de Romance Psicológico (Linhagem Molambudos)

**Status:** catálogo, prompt, protocolo de tradução e perfil gerenciado
registrado (`romance-psicologico-molambudos`).
**Não é terapia, não é NLP clínico e não é validação literária.**
**Não há nota 10/10, publicação ou garantia de qualidade.**

## 1. Codex e edição de imagens

**Sim, para edição determinística; não, para edição generativa sem modelo.**

O executor `codex` está instalado e disponível, em modo
`cli-read-only-windows-interop`. Ele pode:

- analisar imagens e metadados;
- gerar scripts Python/ImageMagick/cairosvg/WeasyPrint;
- calcular hashes, dimensões, DPI e CMYK;
- montar contact sheets, previews e composições.

Ele **não** é um modelo de imagem. Para inpainting, outpainting, troca de estilo
ou “editar por prompt”, é preciso uma API de imagens ou um modelo local de
difusão. O modelo `gemini-nano-banana-2.1` estava indisponível nesta conexão.

Nesta ponte, Codex é read-only: ele devolve o script; o Core executa, verifica e
registra. **Não fazer upscale artificial para alegar 300 DPI**; preferir
re-render vetorial.

O Codex foi acionado em 2026-11-05 (`task-ce22a7df`, spec `TSPEC-43c399c2`) e
devolveu um script de capa. Ele **não foi executado**: depende de `svglib`
(ausente), usa PyMuPDF (AGPL) e rejeita os elementos `<text>` dos SVGs atuais.
A revisão está em `codex_cover_review.md`; a versão segura e reprodutível está
em `reports/r1078/cover/build_cover.py` (WeasyPrint + cairosvg + pypdf).

Detalhes e prompts: `codex_image_workflow.md`.

A direção de arte das ilustrações foi fixada em **Piranesi (Carceri, 1750-3) +
Pencz (1500-1550)**: arquitetura opressiva, figura pequena e legível, hachura,
chiaroscuro e um acento carmim. O pacote está em
`reports/r1081/illustration_style/`.

## 2. Identidade do assistente

**Nome de trabalho:** Assistente de Romance Psicológico — Linhagem Molambudos.

**DNA:**

- prosa sensorial e corporal;
- tensão psicológica por acumulação;
- horror sistêmico (instituição, família, pobreza, memória);
- arquivo doente (laudo, carta, foto, formulário);
- motivos recorrentes (dente, leite, poeira, zumbido, ciclo);
- indução narrativa (focalização, indireto livre, narrador não confiável);
- metaficção contida (livro dentro do livro, leitor como paciente);
- frase curta para impacto, longa para hipnose;
- traduzibilidade PT-BR/EN/ZH.

**O que “NLP” e “mentalismo” significam aqui:** metáforas de ofício para
**direção de atenção**, **repetição motívica**, **ancoragem sensorial**,
**ambiguidade controlada** e **misdirection ficcional**. Não são alegação de
eficácia clínica nem instrução para manipular pessoas reais.

## 3. Catálogo de estilos (16)

| ID | Estilo | Use quando | Tensão | Risco de tradução |
|---|---|---|---|---|
| `sepia-visceral` | Sépia Visceral | pobreza, seca, corpo, arquivo | acumulação lenta | oralidade rural |
| `laudo-clinico` | Laudo Clínico | diagnóstico, perícia, burocracia | frieza que racha | jargão médico |
| `fervor-apocaliptico` | Fervor Apocalíptico | multidão, praga, fanatismo | espiral coletiva | cadência bíblica |
| `gotico-rural` | Gótico Rural | casa, herança, segredo | revelação tardia | hierarquia familiar |
| `body-horror-feral` | Body Horror Feral | metamorfose, fome, parto | pico constante | precisão anatômica |
| `espiral-metaficcional` | Espiral Metaficcional | livro dentro do livro, leitor | vertigem | segunda pessoa |
| `minimalismo-cortante` | Minimalismo Cortante | trauma, violência off-page | understatement | subtexto |
| `barroco-febril` | Barroco Febril | delírio, culpa, febre | hipnose | frase longa |
| `elegia-documental` | Elegia Documental | arquivo, foto, luto | revelação lenta | marcas de arquivo |
| `terror-sistemico` | Terror Sistêmico | instituição, protocolo | opressão difusa | jargão institucional |
| `realismo-magico-sujo` | Realismo Mágico Sujo | família, milagre, humor | maravilhoso banal | oralidade/humor |
| `noir-tropical` | Noir Tropical | crime, desejo, cidade | perseguição | gíria |
| `horror-cosmico-rural` | Horror Cósmico Rural | culto, céu, geometria | awe/dread | escala e vazio |
| `pulp-frenetico` | Pulp Frenético | serial, cliffhanger | picos | ritmo/clareza |
| `confissao-intima` | Confissão Íntima | culpa, desejo, vergonha | intimidade | voz baixa |
| `epico-coral` | Épico Coral | gerações, migração | escala | parentesco/tempo |

Cada estilo no JSON traz: `use_when`, `syntax`, `lexicon`, `sensory_channels`,
`pov`, `tension_curve`, `motifs`, `reader_effect`, `translation` (PT-BR/EN/ZH),
`risks` e `prompt`.

### 3.1 Motor de tag lines

O catálogo inclui `tagline_engine` com seis padrões:

1. **Objeto-segredo:** “Toda casa guarda um crime. Esta também.”
2. **Leitor visto:** “Você não está lendo um livro. Está sendo lido.”
3. **Lugar cobra:** “O sertão não esquece. Ele cobra.”
4. **Depois do milagre:** “A chuva veio. Depois, veio o resto.”
5. **Arquivo aberto:** “O arquivo está aberto. Só falta o seu nome.”
6. **Ciclo:** “O ciclo não termina. Ele muda de corpo.”

**Limite:** a tag line promete a experiência, não engana sobre o conteúdo; o
aviso de conteúdo vem antes do gancho.

## 4. Protocolo de tradução PT-BR / EN / ZH

### PT-BR

- Preservar `tu`/`você`, `pra`, diminutivos e regionalismos como voz.
- Não corrigir dialeto para “português de manual”.
- Manter a violência de registro e a hierarquia social.
- Datas, siglas e documentos brasileiros precisam de contexto.

### EN

- Verbo curto e concreto; não explicar o exótico.
- Controlar o comprimento da frase; o inglês tende a encurtar.
- Não traduzir gíria por equivalente de outra região; adaptar a função.
- Horror com precisão, não “gross-out”.
- Diálogo com `said` neutro; não empilhar verbos de fala.

### ZH

- Decidir `你`/`您` por relação, não por literalidade.
- Usar `量词` e `四字格` com moderação.
- Atenção à segmentação e à pontuação (`。——……`).
- Adaptar comida, paisagem, parentesco e religião.
- Verificar sensibilidade histórica e política antes de publicar.
- Preservar ambiguidade; não explicar o horror.

### QA

1. Glossário de termos e nomes.
2. Back-translation de passagens-chave.
3. Leitura em voz alta.
4. Revisão de sensibilidade por falante nativo.
5. COMET/chrF/BLEU apenas como diagnóstico.
6. `translation_brief.md` por capítulo.

## 5. Os 23 repositórios que você listou

A análise completa está em `repos_analysis.md`. Resumo:

- **Maioria é LaTeX/tipografia**, não estilo literário: Tufte, tex-book-template,
  CTeX, texufpel, livro-aberto, contextgarden, nature-tex, DND-5e.
- **Hifenização:** `hyphenation/tex-hyphen` é crítico para PT/EN; chinês exige
  regra própria, não hifenização silábica.
- **Tradução:** `NiuTrans/MTBook` é livro-texto, não ferramenta; para QA, usar
  COMET/sacreBLEU (R1078).
- **Imagem:** `awesome-text-to-image-studies` é mapa de pesquisa, não modelo.
- **Licenças:** 13 sem licença declarada, 2 com `NOASSERTION`, 2 GPL-3.0,
  2 CC e 4 MIT. Nada foi clonado ou embutido; verificar antes de usar.
- **Lacuna:** os repositórios ensinam **formato**; o catálogo R1080 cobre **voz**.

## 6. Contrato ético

1. **Ficção.** Laudo, foto, carta e citação são ficcionais ou licenciados; não
   apresentar como prova histórica.
2. **Aviso de conteúdo.** Abuso, autoagressão, doença, morte, violência e trauma
   sinalizados no início e nos metadados.
3. **Sem alvo real.** Não mirar pessoas, famílias ou comunidades identificáveis.
4. **Sem coerção.** Não instruir chantagem, isolamento ou exploração de
   vulnerabilidades reais.
5. **Sem alegação clínica.** O texto não “cura”, não “reprograma”, não
   “diagnostica”.
6. **Sem plágio.** Pastiche e influência declarados; não copiar voz de autor vivo.
7. **Tradução com revisão humana.** Nenhuma tradução automática é publicada sem
   leitura crítica e sensibilidade cultural.

A liberdade artística é ampla. A responsabilidade sobre o leitor é parte do
ofício.

## 7. Como usar

1. Carregar `assistant_prompt.md` no orquestrador ou no agente
   `literary-style-voice-phd`.
2. Selecionar 1 estilo dominante e 1 estilo de contraste por capítulo.
3. Usar `style_catalog.json` para `prompt`, `motifs` e `translation`.
4. Usar `tagline_engine` para título, abertura e back cover.
5. Rodar `quality_gates` antes de entregar.
6. Escrever `translation_brief.md` antes de traduzir.
7. Nunca publicar tradução automática sem revisão humana.

## 8. Verificação

- 16 estilos; 16 IDs únicos.
- 3 línguas por estilo: `pt-BR`, `en`, `zh`.
- 2+ canais sensoriais e 2+ motivos por estilo.
- Blocos `ethics`, `translation_protocol`, `tagline_engine` e `quality_gates`.
- Teste: `tests/test_r1080_style_catalog.py`.
- Perfil gerenciado registrado: `romance-psicologico-molambudos`; nenhum modelo de imagem foi executado.
- O subagente registrado não executou nesta sessão: o modelo padrão exige
  assinatura OpenCode Go. A prancha-demonstração foi produzida pelo orquestrador
  na voz do perfil (`reports/r1081/illustration_style/demo_plate.md`).

## 9. Limites

- Não é NLP clínico, terapia ou diagnóstico.
- Não garante qualidade literária, prêmio ou aceite editorial.
- Não substitui leitor crítico, tradutor, revisor de sensibilidade ou designer.
- Não gera imagens sem modelo/API.
- Não faz upload KDP, nova ISBN ou publicação.
- Não declara 10/10.

## 10. Arquivos

| Caminho | Conteúdo |
|---|---|
| `style_catalog.json` | 16 estilos, ética, tradução, tag lines e gates |
| `assistant_prompt.md` | system prompt e contrato de voz |
| `codex_image_workflow.md` | o que o Codex faz e não faz com imagens |
| `repos_analysis.md` | análise dos 23 repositórios |
| `../r1081/illustration_style/` | direção de arte Piranesi/Pencz, prompts e provas |
