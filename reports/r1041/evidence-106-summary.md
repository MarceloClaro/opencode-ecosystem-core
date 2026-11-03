# Evidência OCR das 106 partes — R1041

- Comando: `python3 -m integrations.dubbing_evidence --root pilots/r1035-02XpQTA-_XE`
- Partes processadas: **106** (P0006 excluído; o piloto tem tratamento próprio).
- Frames extraídos: **1.997**.
- Erros: **0** em `reports/r1041/evidence-106-errors.log`.
- Novas dublagens: **0**; o pipeline é somente leitura de fonte + OCR.
- Recibo:
  `pilots/r1035-02XpQTA-_XE/.dubbing-evidence/receipt-f57a9200896e30e085b041d5e9bf36b0cdbf9e10669cd2076f54076fdd866599.json`

## Método

Para cada parte, o serviço lê a unidade ASR preparada e extrai **um frame no
meio** de cada unidade; partes sem ASR recebem amostragem esparsa a cada 10 s.
O frame é recortado da região de legenda, ampliado, binarizado e passado ao
Tesseract (`eng`, psm 6). Cada imagem e o manifesto têm SHA-256; a retomada
verifica insumo, chave e hashes.

## Limites

- Uma imagem por unidade não cobre legendas que mudam dentro do mesmo trecho.
- O inglês queimado é tradução secundária; não é o texto turco original.
- OCR pode omitir, misturar ou inventar caracteres.
- Amostragem esparsa em parte sem ASR **não** prova ausência de fala.
- Nenhum frame foi revisado por humano; `source_review` permanece `pending`.
- O lote não traduz, não identifica locutor e não dubla.

## Estado

As 106 partes têm evidência visual coletada e recibo; a dublagem continua
bloqueada até mapa de locutores, tradução/revisão e TTS aprovados.
