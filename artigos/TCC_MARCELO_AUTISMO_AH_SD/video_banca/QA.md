# QA técnico — vídeo de banca

Verificação executada em 5 de novembro de 2026 sobre
`Dupla_Excepcionalidade_Banca.mp4`.

## 1. Metadados medidos

| Item | Medido | Critério | Situação |
|---|---|---|---|
| Contêiner | MP4 (`+faststart`) | reprodução em navegador | OK |
| Vídeo | H.264, 1920×1080, 30/1 fps, yuv420p | 16:9 Full HD | OK |
| Áudio | AAC, 48 kHz, 2 canais, 192 kbps | estéreo padrão | OK |
| Duração | 432,024 s (7 min 12 s) | ≈ 7 min | OK |
| Quadros | 12.958 | 30 fps efetivos (29,997) | OK |
| Tamanho | 16.300.674 bytes (16,3 MB) | entrega leve | OK |
| Vídeo bitrate | 119 kbps | slides estáticos | OK |
| Áudio bitrate | 174 kbps | voz limpa | OK |

## 2. Loudness (EBU R128)

| Métrica | Valor |
|---|---|
| Loudness integrada | **−16,04 LUFS** |
| True peak | **−1,44 dBTP** |
| Faixa de loudness (LRA) | 2,90 LU |

Adequado para publicação em web e reprodução em projetor. Sem clipping
(pico abaixo de 0 dBTP).

## 3. Imagem

- `blackdetect` (d=0,5 s; pix_th=0,10): **nenhum trecho preto**.
- Amostragem de quadros em 8, 25,4, 30, 45, 47,2, 60, 95, 100, 190, 300,
  305, 370, 425, 428 e 437 s: slides corretos, sem corte de texto, sem
  sobreposição entre conteúdo e legendas.
- Faixa de legendas reservada abaixo de y≈920; conteúdo dos slides termina
  em y≈860.
- Barra de progresso no topo (4 px) e contador “n / 14” no canto superior
  direito, sem colisão com as legendas.

## 4. Áudio e sincronia

- `silencedetect` (n=−45 dB, d=0,9 s): pausas de **≈1,5 s** entre cenas
  (0,20 s de entrada + ≈0,9 s de cauda do TTS + 0,20 s de respiro) e pausas
  naturais de ≈0,95 s entre frases.
- Cada cena inicia a fala 0,20 s após o corte visual; o slide entra antes da
  voz, como planejado.
- Nenhuma cena ficou sem áudio; a última fala (“Muito obrigado.”) termina
  antes do fim do segmento final.

## 5. Legendas

- **71 blocos** queimados via libass (ASS com `PlayResX/Y = 1920×1080`,
  Liberation Sans Bold 35 px, contorno 2,2 px, `MarginV = 48`).
- `legendas.srt` exportado do mesmo ASS: mesmos tempos e textos.
- Frases longas podem ocupar até 3 linhas; nenhuma frase foi cortada no meio.
- Tempos derivados dos `WordBoundary` do `edge-tts` por cena, deslocados pelo
  offset acumulado dos segmentos.

## 6. Conteúdo e conformidade

- Autor e instituição na abertura e no encerramento:
  **Marcelo Claro Laranjeira** — FACUMINAS, Pós-graduação Lato Sensu em
  Educação Especial e Inclusiva, Neuropsicopedagogia Institucional e Clínica,
  Brasília, 2026.
- **Sem linha de orientador(a)**, conforme decisão do autor.
- Encerramento com agradecimento e declaração explícita de **voz sintética**.
- Dados conferidos contra o TCC e as Sinopses do INEP: 294.394 → 918.877
  (TEA, +212%); 23.758 → 44.171 (AH/SD, +86%); razão 12,4 → 20,8;
  Nordeste 45,2; Sul 8,0; Ceará 121,8; Paraná 3,9; cenários 22,9 e 14,2.
- Cenários apresentados como exploratórios, não como previsões.

## 7. Integridade

```
133ae98dde5b1bf9d03e16320b2bd6356c333bd520e1c4b107b341f75eef2ba3  Dupla_Excepcionalidade_Banca.mp4
543f2c0f91d38a351728b9ecbd7e1a9bfef53333c64fc12b6b45d75f352129a7  legendas.srt
```

## 8. Limitações e revisão humana pendente

1. A voz é sintética; prosódia, ênfases e pausas não passaram por revisão
   humana de locução.
2. As legendas são geradas a partir dos tempos do TTS; podem divergir em
   até algumas décimas de segundo em relação à fala percebida.
3. O conteúdo repete os limites do TCC: série de quatro anos, dados
   agregados, ausência de cruzamento TEA × AH/SD.
4. Recomenda-se assistir integralmente ao vídeo antes da banca para conferir
   pronúncia de siglas e nomes próprios.

## 9. Checklist de entrega

- [x] MP4 1920×1080, 30 fps, 7 min 12 s
- [x] Áudio normalizado a −16 LUFS
- [x] Legendas queimadas e `legendas.srt`
- [x] Slides e gráficos editáveis (PNG)
- [x] Scripts reprodutíveis (`gerar_audio`, `gerar_graficos`, `gerar_slides`, `montar_video`)
- [x] Autor e agradecimento no encerramento
- [x] Declaração de voz sintética
- [x] Sem linha de orientador(a)
