# Pesquisa — vídeo fluido em CPU e dublagem multivoz PT-BR

Data da consulta: 02/11/2026. SPEC-935-R1033.

**Estado: pesquisa documental; piloto audiovisual não executado.** Não foram
instalados pacotes, baixados episódios, renderizados novos vídeos, clonadas
novas vozes ou publicados arquivos. Nenhum master R1032 foi alterado.
Fontes completas e hashes: `evidence.json` e `sources/`. Os testes deste
dossiê verificam integridade documental, não qualidade de voz/imagem.

## 1. Recomendação direta

Há duas necessidades diferentes:

- **Aula/animação didática:** reaproveitar Remotion, acrescentar Manim Community
  com Cairo para transformações explicativas e finalizar em FFmpeg. Animação
  vetorial 2D pode ter reprodução fluida mesmo se a renderização demorar.
- **Série com personagens:** conservar a montagem original; começar pelo áudio
  multivoz e pelas legendas. Não inserir animações didáticas em episódios de
  drama nem aplicar lip sync em toda a playlist automaticamente.

Para vozes clonadas, **comparar Chatterbox com o modelo específico PT-BR e
XTTS v2**, sem declarar vencedor antes de ouvir e medir um piloto autorizado.
Chatterbox tem licença MIT declarada no código e no model card PT-BR; XTTS
tem código MPL-2.0, mas pesos sob CPML com restrições não comerciais. Licença
do software não concede direitos sobre personagens, atuações ou episódios.

**Bloqueio técnico específico:** o model card PT-BR lista
`t3_pt_br.safetensors` e `s3gen_v3.pt`, enquanto o loader genérico consultado
espera `s3gen.pt`, `ve.pt` e assets do repositório base. A revisão confirmou
**compatibilidade ainda não demonstrada** desse pacote regional com esse
loader. Não basta renomear arquivos ou misturar pesos: fixar a versão/loader
V3 correto e executar um smoke test autorizado antes de escolher o modelo.

## 2. Máquina e dimensão da playlist

Observação local: Intel i5-1035G1, quatro núcleos/oito threads; WSL expõe cerca
de 11 GiB de RAM. Manim e yt-dlp não foram encontrados no PATH nesta consulta
(isso não prova ausência em todos os ambientes). FFmpeg está no PATH; Remotion
já aparece no projeto anterior. Não foi consultada nem usada GPU.

A página pública da [playlist](https://www.youtube.com/playlist?list=PL2dcm-6042EC788TGxgH3qWF7MjpoJIv9)
informa **Wild Heart / Yabani, 1080p, English subtitles** e **153 vídeos**.
Foram enumeradas as primeiras **100 entradas**, com continuação pendente;
o primeiro item é *Wild Heart Episode 1*, 44:51. Não conhecemos a duração
total, todas as vozes, a disponibilidade de legendas separadas ou os direitos
de cada item. Metadados não confirmam idioma do áudio, conteúdo ou qualidade.
O inventário parcial está em `playlist-metadata.json`.

**Advertência de custo:** o log anterior do piloto Qiskit registra 1.413 s
para a inferência Wav2Lip de um trecho de 20 s (70,65 vezes a duração).
Uma extrapolação puramente linear para 45 minutos seria aproximadamente
53 horas **só de inferência**, antes de composição e revisão. Não é benchmark
da série, nem previsão garantida; cenas com vários rostos podem mudar o custo.
O registro histórico não mede Chatterbox, diarização ou separação musical.

## 3. Ferramentas e decisões

As licenças de código abaixo foram consultadas em fontes oficiais. Cada
checkpoint, pacote de voz e dependência requer confirmação própria antes do
uso. `evidence.json` registra explicitamente o que continua pendente.

| Ferramenta | Uso recomendado | CPU e restrições |
|---|---|---|
| [Manim Community](https://github.com/ManimCommunity/manim) | Circuitos, diagramas, processos, gráficos e objetos que se transformam | Cairo evita depender de OpenGL; MIT. Sem modelo generativo. Não instalado/testado nesta rodada. |
| [Remotion](https://github.com/remotion-dev/remotion) | Composição, tipografia, apresentador, cenas e versões 16:9/9:16 | Priorizar SVG/2D e render em software; licença própria, não MIT. Não supor que todo projeto 3D/WebGL seja adequado à CPU. |
| [FFmpeg](https://ffmpeg.org/ffmpeg-filters.html) | Montagem, áudio, fades, transições e legendas | Filtros de software; LGPL/GPL conforme compilação. Normalizar resolução, timebase e fps nas transições. |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Transcrição com tempos por palavra | CPU/int8 documentado; começar medindo `small` multilíngue. Código MIT; pesos Whisper oficiais MIT, conversões de terceiros a conferir. |
| [whisper.cpp](https://github.com/ggml-org/whisper.cpp) | Alternativa enxuta para ASR local | CPU e quantização documentados; MIT. Comparar com faster-whisper, não manter ambos rodando simultaneamente. |
| [pyannote.audio](https://github.com/pyannote/pyannote-audio) | Diarização: quem fala quando | Inferência local; custo de CPU a medir. Código MIT. Community-1 exige aceite/token; model card direto retornou 401. Termos dos pesos permanecem pendentes de acesso autorizado. |
| [WhisperX](https://github.com/m-bain/whisperX) | Alinhamento e associação dos segmentos com locutores | CPU/int8 documentado; código BSD-2-Clause na revisão consultada. Pesos de alinhamento/diarização separados, e falas sobrepostas continuam difíceis. |
| [Chatterbox](https://github.com/resemble-ai/chatterbox) + [PT-BR](https://huggingface.co/ResembleAI/Chatterbox-Multilingual-pt-br) | Candidato para clonagem autorizada em português brasileiro | Caminho CPU existe no código multilíngue; model card PT-BR declara MIT. É candidato, não solução comprovadamente rápida. Modelo específico depende de assets compartilhados e compatibilidade do loader. |
| [XTTS v2](https://huggingface.co/coqui/XTTS-v2) | Baseline conhecido do piloto anterior | Português suportado; código Coqui MPL-2.0, **pesos CPML**, não tratar como licença comercial irrestrita. Qualidade dramática e custo multivoz não medidos. |
| [Piper](https://github.com/OHF-Voice/piper1-gpl) | Vozes sintéticas alternativas para rascunho/uso licenciado | Otimizado para síntese local, tem vozes pt_BR; GPL-3.0, licença de cada voz separada. **Não equivale a clonar cada personagem.** |
| [audio-separator](https://github.com/nomadkaraoke/python-audio-separator) | Separar diálogo de acompanhamento quando não houver trilha M&E | CPU documentada; código MIT e modelos separados. Pode remover efeitos e deixar diálogo residual. Não separa automaticamente cada personagem. |
| [SoniTranslate](https://github.com/R3gm/SoniTranslate) | Referência de aplicação integrada multivoz | Documenta `--cpu_mode`; Apache-2.0 no código. Modelos/vozes podem ter outros termos; não promete integração rápida ou fala perfeita. |
| [pyVideoTrans](https://github.com/jianchang512/pyvideotrans) | Interface para tradução, legendas e dublagem | GPL-3.0; disponibilidade CPU depende do backend. Alguns serviços são remotos/pagos. Não ativar APIs nem transmitir mídia sem autorização. |
| [VideoLingo](https://github.com/Huanshere/VideoLingo) | Comparar fluxo de tradução e legendagem | Apache-2.0; documentação Linux favorece NVIDIA. Não é a primeira escolha para este WSL CPU sem ensaio dos backends. |

### Não escolher apenas por demonstrações bonitas

- **OpenVoice V2:** MIT, porém os seis idiomas nativos listados não incluem
  português. Pode participar de conversão de timbre com outra voz-base, mas
  não é uma solução PT-BR completa pronta por si só.
- **MuseTalk / LatentSync:** a documentação usa GPU; velocidade anunciada em
  GPU não vale para o i5. Não recomendados como primeira rota CPU.
- **stable-ts:** recursos úteis para timestamps, mas o repositório estava
  marcado como arquivado na API consultada; não adotá-lo como dependência
  nova principal sem assumir manutenção.
- **Argos Translate:** candidato de tradução local, não recomendado ainda
  para diálogo dramático desta série. É preciso conferir pacote de idiomas,
  licença e qualidade; o README por API falhou nesta consulta. Tradução literal
  ou pivô pelo inglês pode perder registro, intenção e relações entre personagens.

## 4. O que aproveitar de `biblioteca ai`

Os ZIPs `skills (1).zip` e `skills (2).zip` contêm sete skills de direção:
motion explicativo, direção de edição, lettering, apresentador em cena,
estilo por referência, extração de referência e variações controladas.
As sete já têm correspondentes em `.claude/skills/`. Seus bytes **não são
idênticos** aos do ZIP; não reinstalar por cima nem tratar como cópia exata.
ZIPs foram inspecionados sem extrair ou executar instaladores.

Aplicação mais útil:

- `cp-motion-explicativo`: cada ideia vira estado inicial → ação → resultado,
  em vez de cartões parados com zoom.
- `cp-direcao-de-edicao`: selecionar o que deve aparecer em cada fala.
- `cp-apresentador-em-cena`: manter rosto, gestos e conteúdo legíveis.
- `ficha-de-direcao.md`: fixar intenção, materiais, direitos e estilo do piloto.
- `mapa-de-cenas.csv`: ligar fala real, foco visual, ação, áudio e revisão.
- `checklist-da-amostra (1).md`: avaliar a amostra **em movimento**, com som;
  imagem estática não autoriza marcar sincronização/fluidez como verificadas.

Foram consultadas apenas as oito primeiras páginas dos dois livros de edição
pertinentes, além desses templates. São materiais licenciados, não uma licença
aberta para redistribuição integral. Outros PDFs pessoais não foram examinados.
As skills são instruções de direção; não incluem motores de voz ou acesso pago.

## 5. Como obter animações contínuas em CPU

1. Fechar narração/texto revisados e um mapa de eventos antes de animar.
2. Usar uma timeline única, controlada por frames. Para aula nova, 30 fps fixos
   são um ponto inicial; para episódios, preservar o fps original salvo motivo
   medido. Renderizar a velocidade baixa não implica playback travado.
3. Transformar os mesmos objetos entre estados: fio vira conexão ativa,
   componente muda de estado, gráfico destaca uma região. Evitar recomeçar
   uma lista de slides em cada frase.
4. Limitar a um movimento principal por vez, com easing e intervalos estáveis
   para leitura. Reaproveitar paleta, tipografia, margens e identidade visual.
5. Usar match cut ou transição curta, por exemplo 8–12 frames a 30 fps quando
   fizer sentido. A sobreposição reduz a duração total; recalcular a timeline.
   Não aplicar dissolve/zoom em todos os cortes por automatismo.
6. CPU: SVG/formas 2D, cache de cenas, prévia 720p, um job pesado por vez,
   concorrência inicial 1–2, depois medir RAM e tempo. Evitar sombras/blur
   excessivos, difusão text-to-video e 3D pesado para este caso.
7. A mancha anterior pede rever o recorte: preferir enquadramento limpo com
   fundo original ou cartão retangular se não houver segmentação temporal
   aprovada. Zoom/drift e interpolação não corrigem uma boca congelada.
8. Render em destino novo, com licença e aprovação explícitas. **Nunca burlar
   guard por `npm run`, concatenação de strings ou outro invólucro.**

## 6. Estratégia de dublagem de todas as falas

### A. Direitos, fontes e idioma

Obter arquivo autorizado, finalidade (pessoal/comercial/publicação), direitos
da adaptação e **consentimento específico de cada pessoa cuja voz será clonada**.
O consentimento da apresentadora Qiskit não cobre o elenco de Yabani. Sem
isso, oferecer vozes sintéticas licenciadas ou locutores autorizados, não
prometer reprodução das identidades originais.

Preservar original e extrair áudio em pistas separadas. Manter cópia 48 kHz
para mixagem e derivada adequada ao ASR. Se o áudio for turco, transcrever
turco e traduzir para PT-BR; legenda inglesa é uma fonte secundária, não o
original. Conferir se as legendas inglesas são embutidas na imagem: adicionar
SRT português não as remove. Preferir uma cópia limpa autorizada.

### B. Transcrição, locutores e continuidade

- ASR no idioma real, com timestamps por palavra, VAD e revisão de nomes.
- Diarização com marcas de confiança e **falas sobrepostas** preservadas.
  O resultado é `speaker_01`, não o nome de um ator/personagem.
- Cadastro persistente entre cenas e episódios: ID global, nome confirmado
  pelo operador, idioma, referências limpas, consentimento, versão do modelo
  e ajustes de pronúncia. Clusters locais não podem trocar vozes entre episódios.
- Separar referência por pessoa, sem música ou outros falantes; avaliar várias
  falas limpas em vez de confiar em um único fragmento mínimo. Riso, grito,
  choro e sussurro precisam de revisão; a identidade não garante interpretação.

### C. Tradução e geração das falas

Traduzir com contexto de cena, glossário e histórico de relações. Preservar
intenção, negação, humor, tratamento e informação; adaptar o comprimento para
o turno original sem resumir silenciosamente. LLM local ou serviço externo é
uma escolha posterior: nenhum texto de episódio foi enviado nesta pesquisa.

Gerar áudio por **turno/unidade de sentido**, com a mesma referência e perfil
de voz; não em blocos cegos de cinco segundos. Manter contexto prosódico,
pausas e emoção. Separar duração do texto, fala efetiva e silêncio disponível.
Se a fala não couber, rever a tradução ou regenerar; time-stretch leve é último
ajuste e deve ser ouvido. Não cortar a palavra final nem esticar agressivamente.

Processar em lotes retomáveis por cena/episódio, com hashes e cache, mantendo
continuidade semântica. Diferenciar lote de computação de corte editorial.
Para lip sync, usar plano contínuo ou contexto nas bordas, depois aparar pelos
timestamps; não repetir a solução que congelava as emendas de cinco segundos.

### D. Música, efeitos e mixagem

Preferir a trilha **M&E** (música e efeitos sem diálogo) do detentor dos direitos.
Se só houver mixagem estéreo, experimentar separação de fontes em CPU, ouvindo
vazamentos e perdas; não garantir reconstrução perfeita. Todos os personagens
podem cair na mesma pista vocal: diarização não resolve separação simultânea.

Montar falas em pistas próprias e conservar sobreposições legítimas. Microfades
servem para evitar cliques nas bordas, não para misturar indiscriminadamente
duas réplicas. Preservar ambiência; revisar loudness, pico verdadeiro e equilíbrio
com música sem cobrir consonantes. Não deixar diálogo original audível junto
da dublagem, salvo escolha editorial explícita.

### E. Legendas PT-BR realmente sincronizadas

**Alinhar o texto aprovado ao áudio PT-BR final**, após regenerações, ajustes
de duração e posicionamento. Não reutilizar cegamente os tempos das legendas
inglesas/originais. WhisperX tem caminho CPU; modelo de alinhamento português
e licença devem ser fixados antes do ensaio. Alinhamento automático também erra.
O código consultado aponta o default português
`jonatasgrosman/wav2vec2-large-xlsr-53-portuguese`; o model card desse checkpoint
não foi coletado, portanto sua licença específica continua pendente.

Exportar SRT e VTT; ASS quando forem necessárias posições/estilos ou duas vozes
simultâneas. Propor até duas linhas, cerca de 38–42 caracteres por linha e
meta inicial de até 17 caracteres/s, com quebras por sentido — metas editoriais,
não resultados medidos. Ajustar nomes, números, termos e acessibilidade.
Conferir fala, legenda e imagem em reprodução normal. Sincronia de legenda
com áudio não equivale a sincronia labial.

## 7. Piloto antes da playlist

Escolher **60–90 segundos autorizados**, com duas ou três vozes, troca de
locutor, música e pelo menos uma sobreposição. Medir separadamente:

- ASR/diarização: palavras perdidas, trocas de locutor e tempo de execução.
- TTS: segundos de processamento por segundo de fala, pico de RAM, fidelidade
  percebida, sotaque brasileiro, pronúncia e interpretação.
- Mixagem: vazamento do original, perdas de efeitos, clipes e transições.
- Legendas: timings, leitura e cobertura das falas.
- Vídeo: fluidez em playback com áudio, sem usar drift como proxy.

Comparar candidato e baseline em avaliação humana, documentar recusas e erros.
Só então extrapolar custo e decidir episódio completo. Sem receita de aceleração
que prometa tempo real. CPU permite tentar; não garante clonagem convincente
de todo o elenco nem acabamento profissional automático.

## 8. Verificação e limites da pesquisa

O doctor inicial passou 22/22 verificações **estruturais**. A busca web integrada
retornou HTTP 402, portanto foram usadas URLs oficiais diretas. O coletor teve
uma desconexão: bytes já salvos foram preservados, e os recibos recuperados
declaram timestamp de arquivo, sem inventar uma nova requisição bem-sucedida.
Houve ainda timeout/404 e acesso 401 ao modelo pyannote, registrados no índice.

O workflow externo `r1033-video-cpu-research` bloqueou antes da inferência por
ausência de `spec_id` no payload, apesar da spec em disco. Duas tentativas de
revisão nativa falharam por assinatura OpenCode Go indisponível. Posteriormente,
um contrato textual explícito `TSPEC-094f2d73` permitiu uma **nova revisão
textual independente** via Antigravity, tarefa `task-1ed85850`. O workflow
bloqueado não foi retomado. Os achados e a reconciliação estão em
`review-summary.md`; isto não é aprovação humana, audiovisual ou jurídica.
As recomendações são uma síntese do primário, sujeita a revisão humana.

Os seis testes R1033 são aceites documentais: fontes/hashes, licenças
separadas, escopo, plano, inventário e reconciliação da revisão. Não provam que os motores rodaram ou
que o pipeline audiovisual foi validado. Ausência de benchmark é explícita.
Nenhuma aprovação de voz, sincronização, qualidade ou autorização é inferida
de metadados, hashes ou testes de texto.

O RED das correções da revisão foi observado em `red-review-tests.txt`
(uma asserção falhou, cinco testes passaram). A tentativa de selar esse RED
pelo TDDHistory atingiu 180 s durante o snapshot de fontes, antes do log de
pytest; não produziu recibo aceito e não foi repetida. Não se declara gate
de entrega de software estrito. A validação final é documental/criteria-only.
