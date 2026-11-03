# Piloto CPU multivoz — R1034

## Autorização

O usuário confirmou “Playlist com consentimentos” e instalação isolada.
`authorization.json` registra a declaração; documentos não foram verificados.
Nada publicado e nenhuma mídia/voz enviada a API de IA. Apenas aquisição
pública de um trecho e processamento local. Os masters R1032 são preservados.

## Implementado

`integrations/video_cpu_pipeline.py` fornece:

- validação de locutores e consentimento declarado, preservando turnos
  sobrepostos de pessoas diferentes;
- recibos de etapas vinculados a entrada, saída, parâmetros e versão;
  retomada rejeita cache adulterado ou configuração diferente;
- geração de SRT/VTT/ASS a partir de palavras alinhadas ao **áudio PT-BR final**,
  com hash e conferência da duração no CLI;
- quebra de linhas e sinalização de leitura acima de 17 caracteres/s;
  tempos não são esticados automaticamente para esconder excesso de texto;
- posições ASS distintas para sobreposições (precisam de revisão visual);
- timeline com transições sobrepostas, duração total correta e easing;
- ASR real `faster-whisper` CPU/int8 com modelo local explícito, duas threads
  e sem download implícito de pesos.

`motion/ContinuousProcess.tsx` é uma composição SVG/2D controlada por frames:
um objeto percorre as fases da dublagem. É um recurso didático separado, não
um efeito colocado nos episódios. Não usa CSS animation ou relógios.
Não foi renderizado: prévia/aprovação do plano Remotion precede exportação.

## Ambiente isolado

`/home/marceloclaro/.cache/opencode-pilot/venvs/r1034-cpu`

Versões pedidas em `requirements-requested.txt`; resolução completa em
`requirements-lock.txt`, hashes de downloads em `install-report.json`, imports
em `environment.json`. Instalação por wheels oficiais PyPI, sem builds de
fonte ou alteração dos ambientes Wav2Lip/XTTS anteriores.

## Comandos

```bash
# Planejar três cenas e sobreposição de 12 frames (não renderiza)
python3 -m integrations.video_cpu_pipeline timeline --durations 90 120 90 --transition 12

# ASR: informar arquivo existente e diretório explícito do modelo em cache.
# Não baixar um modelo apenas porque seu nome foi passado.
/home/marceloclaro/.cache/opencode-pilot/venvs/r1034-cpu/bin/python \
  -m integrations.video_cpu_pipeline transcribe --audio ARQUIVO_LOCAL \
  --model-dir DIRETORIO_LOCAL_CTRANSLATE2 --language tr --out NOVO_ARQUIVO_JSON

# Exportação somente depois de alinhar as palavras ao áudio PT-BR final
python3 -m integrations.video_cpu_pipeline captions \
  --alignment ALINHAMENTO_FINAL_JSON --audio MIXAGEM_FINAL_WAV \
  --speakers CADASTRO_JSON --out NOVA_PASTA
```

Formato de cadastro: mapa de IDs persistentes, cada qual com
`consent_declared: true` e metadados de referência/autorizações controlados
pelo operador. O programa **não** cria consentimento nem reconhece atores.
Alinhamento: `language: pt-BR`, `audio_sha256`, `duration` e lista `words`
com `speaker`, `start`, `end`, `text`.

## O que não está concluído

ASR não é tradução, diarização, clonagem ou lip sync. O cadastro ainda precisa
de locutores observados/revisados; não gerar “s1/s2” arbitrariamente para
alegar dublagem multivoz. Vozes dramáticas, música/efeitos, alinhamento real e
escuta humana dependem do piloto. Não há autorização técnica para processar
automaticamente os 153 vídeos só porque um trecho foi selecionado.

O núcleo é uma implementação incremental, não uma suíte completa de edição
com qualidade profissional certificada. Testes locais são diferentes de
aprovação de sincronia, fidelidade vocal e autorização jurídica.

## Resultado observado desta rodada

- 25 testes R1034 passaram; com R1033 são 31 regressões passando.
- Instalação isolada e imports de faster-whisper/CTranslate2/ONNX Runtime
  confirmados. Modelo `small` local carregou em CPU/int8.
- Smoke negativo: dois segundos de silêncio sintético, zero segmentos;
  execução de aproximadamente 6,28 s incluindo carga. Isso **não mede**
  reconhecimento de fala ou velocidade em episódios.
- Metadados do primeiro episódio: 2.690 s, idioma declarado `tr`, 25 fps.
- Duas tentativas limitadas de baixar apenas 180–240 s falharam em TLS/EOF
  no servidor de mídia. Não há trecho válido nem episódio dublado entregue.
  Não foram usados cookies, proxy ou desativação de validação TLS.
- Auditoria somente de código por Antigravity, tarefa `task-e7f3ffc5`:
  corrigidos tipos, conflitos intrapessoais, blocos de legenda, precisão ASS,
  duração real e arquivos mínimos do modelo. O alerta de symlink foi testado:
  a abertura exclusiva `x` já recusava o link, sem criar o destino.
- Composição TSX: conferir `motion-syntax-check.json`; análise sintática não
  é typecheck completo, preview ou render. TypeScript não estava instalado;
  foi usado o parser Babel já presente, sem instalar/renderizar Remotion.
- Gate formal limitado a criteria-only. Histórico estrito do Core ainda não
  selado; esta versão é experimental, não promovida a produção.

**Próxima entrada necessária:** arquivo local MP4/WAV do trecho autorizado
de 60–90 segundos. Com o arquivo, executar ASR, revisar turnos/locutores e só
então preparar tradução e referências para clonagem. Consentimentos já
declarados não precisam ser repetidos; guardar a documentação permanece com
o operador.
