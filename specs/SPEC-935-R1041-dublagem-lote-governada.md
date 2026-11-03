---
spec_id: SPEC-935-R1041
title: Dublagem local retomável, agentes, hooks e MCP compacto
component: integrations.dubbing_batch
status: specified
test_file: tests/test_r1041_dubbing_batch.py
depends_on:
  - SPEC-935-R1040
  - SPEC-935-R1035
---

# SPEC-935-R1041

## Demanda e escopo

O usuário solicita especializar agentes/hooks/MCP a partir do piloto e depois
dublar as outras 106 partes. Processamento exclusivamente local em CPU; mídia,
vozes e referências não são enviadas a serviços de IA. Consentimento já
declarado não será novamente solicitado. Preservar fonte, masters Qiskit,
partes válidas e todas as versões anteriores. Nunca editar pacote instalado.

## Problemas a impedir

O gate anterior de similaridade >=0,45 aceitou palavras extras (inclusive
"ponto"), palavras ausentes, mudança verbal e nomes errados. Tolerância de
0,35 s permitiu extrapolar o fim de P0006; o render truncava amostras. ASR,
espectrograma e fades não provam inteligibilidade nem ausência de ruído.
Prosódia por multiplicadores não prova emoção; gênero/idade não determinam
pitch. Os resultados anteriores continuam rascunhos, não baseline aprovado.

## Contratos

1. Perfis especializados criados/registrados pelo primário com spec/teste,
   origem e permissões explícitos; reutilizar perfis que já cubram o escopo.
   Cadastro/ativação não equivale a execução nem aprovação humana.
2. Um serviço Python/CLI e um MCP local reutilizam as mesmas funções; MCP
   só aceita IDs e operações delimitadas, sem shell arbitrário nem upload.
   Hooks executáveis do runner (não simples prompts) verificam pré-condições
   antes de efeitos. Falha/ausência de revisão bloqueia TTS e montagem.
3. Cache endereçado por conteúdo: hash dos insumos, parâmetros e versão;
   saídas conferidas ao retomar; cache adulterado falha, não é reutilizado.
   Um lock impede duas escritas simultâneas; não sobrescrever evidências.
4. Preparar o plano inteiro em uma chamada, reutilizando ASR integral, sem
   carregar modelo por fala. Cada unidade tem proprietário único por tempo
   médio e contexto separado; fronteira cruzada é marcada, nunca duplicada.
   Toda unidade é rascunho: locutor desconhecido, fonte/tradução não revisadas.
   Ausência de ASR não demonstra ausência de fala. Não fabricar nomes/vozes.
5. Ganhos de tokens são potenciais: registrar hits, chamadas e tamanho do
   resumo; não inventar economia medida. Status traz contagens, bloqueios e
   referências a recibos em vez de todas as transcrições.
6. Gate textual conservador: igualdade lexical normalizada é apenas triagem;
   inserção/omissão/substituição, inclusive flexão verbal e nomes, bloqueiam
   aceitação automática. Exceção exige revisão explícita, nunca afrouxar
   limiar para aprovar o lote. ASR vazio não autoriza dizer "ruído puro".
7. Duração vem de amostras reais, não números copiados; fim <= limite da parte
   e próxima fala, sem tolerância editorial de 0,35 s. Não cortar fonemas.
   Vincular texto, arquivo, hash da referência e processamento ao recibo.
8. Antes de TTS: fonte e sentido revisados, texto PT-BR revisado, personagem
   mapeado e referência íntegra, intenção/pragmática com evidência e incerteza.
   Para publicação/montagem: QA técnico e revisão audiovisual por parte.
   Não substituir vozes de criança/idoso/adulto nem criar identidade por pitch.
9. Os 107 intervalos devem cobrir [0,198016) sem lacunas/duplicações. P0006
   preservado e reauditado; as outras 106 só podem ser chamadas dubladas
   quando existirem áudio, vídeo e recibos conferidos. Planejado != executado.

## Aceites testáveis (antes do código)

- Particionamento sem perda/duplicação, cruzamentos e ASR vazio sinalizados.
- Rejeitar intervalos inválidos, caminhos externos/symlinks, IDs duplicados.
- Cache por conteúdo, retomada idempotente e rejeição de adulteração.
- Bloquear palavras extras, omissões, flexão errada, referência trocada,
  duração excedente, locutor desconhecido e fallback neutro não validado.
- Hooks ligados ao caminho real da ação; exceção nega.
- MCP retorna status pequeno e não aceita comandos arbitrários.
- Perfis gerenciados válidos e compilação da configuração preservadora.
- Regressões R1033–R1040 verdes; testes não certificam qualidade da mídia.

## Execução e limites

Evidência para as 106 partes: amostrar o meio de cada intervalo ASR e uma
grade esparsa nas partes sem ASR; extrair em um processo FFmpeg por parte,
OCR Tesseract local, parâmetros/versões/hash da imagem e do MP4. Texto inglês
queimado é evidência secundária, não transcrição turca certificada. Um frame
por unidade não cobre necessariamente todas as legendas; registrar esse limite.
O lote de evidências não realiza tradução, identificação de locutor ou TTS.
Retomada por parte verifica insumo, pedido e outputs; adulteração bloqueia.

Pré-processamento pode executar para todas as partes, preservando pendências.
Não gerar centenas de falas com personagens inventados para declarar tarefa
concluída. Se faltarem mapas/revisões, registrar contagem e impeditivos exatos.
Revisão humana de naturalidade/emoção continua distinta da triagem técnica.
