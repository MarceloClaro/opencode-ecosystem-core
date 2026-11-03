---
spec_id: SPEC-935-R1035
title: Vídeo integral em partes contínuas e auditáveis
component: integrations.video_segment_audit
status: implemented
test_file: tests/test_r1035_video_segment_audit.py
---

# SPEC-935-R1035

## Pedido e autorização

Vídeo https://youtu.be/02XpQTA-_XE. O usuário autoriza extração/edição de
todo o vídeo e declara autorização sobre imagens e clonagem de vozes.
Documentos não verificados. CPU somente, processamento local, sem publicação,
serviço pago ou upload de voz/mídia a serviços de IA. Preservar fonte original.

## Contrato de continuidade

Intervalos editoriais exclusivos [início,fim), contíguos do primeiro ao último
frame. Alvo 60–90 s, preferindo fronteiras de cena e pausas de fala. Resto final
curto é conservado ou redistribuído, nunca descartado. Sem cena/pausa disponível,
registrar corte técnico e revisão obrigatória; não inventar detecção.
Contexto extra por lado pode existir nos intermediários, mas não entra duas
vezes na montagem. Concatenar etapas sem dissolve automático que apague tempo.

## Entregáveis desta execução

1. Fonte/metadados e tentativa limitada de aquisição integral. Usar downloader
   nativo para evitar a falha TLS do ffmpeg remoto observada em R1034; sem
   cookies, desativação TLS, quebra de acesso ou retries ilimitados.
2. Plano `segments.json`/CSV com ID estável, frames, segundos, contexto,
   motivo de fronteira, transcrição/locutores quando disponíveis e etapas.
3. Extração local exata com reencode quando necessário e conferência de
   duração, contagem de frames, áudio e decodificação por parte; hash de fonte
   e saídas. Se mídia inacessível, plano permanece explicitamente provisório.
4. Cada parte tem estado separado: planejada, extraída, editada, QA técnico,
   revisão audiovisual e aprovada. Nenhuma etapa inexistente é marcada pronta.
5. Manifesto de montagem bloqueado até todas as partes serem editadas e
   aprovadas com hashes atuais e timeline coerente. Edição/dublagem posterior
   deve conservar sentido e continuidade e ser validada antes de juntar.

## Aceites por testes antes de implementar

Cobertura sem lacunas/sobreposições; total e resto preservados; limites de
tempo e dados inválidos; preferência por cena/pausa; IDs e contexto auditáveis;
bloqueio de montagem por aprovação ausente ou arquivo adulterado. Testes
sintéticos são fixtures, não evidência sobre o vídeo real.

## Limites

Somente FFprobe/hashes não comprovam sincronia, tradução ou qualidade.
Cortes detectados por FFmpeg são candidatos, não análise semântica de cena.
Longo plano sem interrupção pode exigir corte técnico entre partes; não há
descarte de conteúdo. Se a fonte tiver VFR, não alegar fps constante apenas
pelos metadados: examinar timestamps e declarar normalização necessária.
Montagem final, qualidade profissional e clonagem completa só podem ser
declaradas quando realmente executadas e revisadas.

## Refinamento antes da implementação

- Metadados retornaram JSON `null`; o log registra HTTP 429 e pedido de login
  antibot. Não repetir a aquisição, usar cookies ou trocar clientes para
  contornar. A execução real depende agora do arquivo integral local.
- Implementar nesta rodada o planejador/validador e exportação JSON/CSV,
  não um downloader nem uma montagem automática. Não gerar um mapa fictício
  do vídeo real sem duração, frames e timestamps observados.
- Usar fps racional e frames inteiros. Planejamento por fps é **provisório**
  até inspeção de timestamps da fonte; CFR não é inferido de `avg_frame_rate`.
- Exceção inevitável (ex.: fonte de 91 s) redistribui o conteúdo em partes
  menores, explicitamente marcadas, em vez de cortar/desprezar o resto.
- Candidatos de pausa/cena e intervalos de fala são entradas observadas, não
  detectados por este módulo. Cortes dentro de fala ficam sinalizados.
- O gate recebe recibos de QA técnico e revisão audiovisual, vinculados ao
  hash do editado, da fonte e de todo o plano. Recusa flags não booleanas,
  duração/frame count incompatíveis e caminhos repetidos. Não gera aprovação
  humana, não autentica revisores e não substitui FFprobe/decodificação reais.
- Testes usam fixtures isoladas, explicitamente sintéticas. Aprovação de
  política em teste não significa que um arquivo arbitrário seja um vídeo.

## Limite de validação formal

Histórico RED anterior observado em `red-tests.txt` (14 falhas por módulo
ausente). A selagem histórica estrita do Core permanece indisponível após
timeout anterior; não contornar nem alegar release aprovado. Testes locais
e eventual gate `criteria_only` são evidências limitadas e distintas.

## Atualização de fonte (tentativa limitada posterior)

O oEmbed e a página pública confirmaram “Wild Heart Episode 1 (Long Version)”,
7.921 s, autor “Wild Heart - Yabani”, idioma declarado `tr`, 25 fps declarados.
Uma segunda tentativa limitada do yt-dlp obteve metadados sem cookies; o
download integral foi iniciado uma vez. A identificação é por metadados
públicos, não por impressão digital de conteúdo. O arquivo local “Terra
Ledger” foi descartado e não processado. A execução real do plano depende do
término do download e da inspeção local.

## Estado implementado

`integrations/video_segment_audit.py` implementa o plano, a validação de
cobertura/contexto e o gate de montagem por recibos/hashes. Os 56 testes R1035
passam; junções com R1033/R1034/R1036 somam 96 testes locais. O plano real do
episódio ainda não foi gerado nesta linha de evidência; testes sintéticos não
são o mapa do vídeo do usuário.
