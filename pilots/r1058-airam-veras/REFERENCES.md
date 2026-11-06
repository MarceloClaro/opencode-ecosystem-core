# Referências, créditos e limites — R1058

## 1. Documentos da escola

| Documento | Uso | Cuidado |
|---|---|---|
| `Plano_Acao_SPAECE_Novembro_2026_5Ano_A_B_Airam_Veras.pdf` (34 p.) | diagnóstico agregado, metas, cronograma, planos de aula, exemplos de conteúdo, responsabilidades | documento pedagógico interno; não é o calendário oficial do SPAECE |
| `Dossie_Unico_5Ano_A_B_Airam_Veras_2026_Com_Matematica_CORRIGIDO.pdf` (3.226 p.) | consolidado CAEd/UFJF, data-base 11/08/2026; resultados agregados, fluência, escrita, marcadores H | contém dados nominais; **não** foram usados nomes, notas individuais ou rankings |
| Capa do dossiê institucional | logo “Escola de Cidadania Airam Veras” | uso institucional; marca da escola |

**Rotina semanal:** planejamento fornecido pela escola em 04/11/2026 (segunda e quarta: leitura/interpretação e produção textual; terça: Matemática, problemas e geometria; quinta: simulados, correção e revisão; sexta: vídeos, Torta na Cara, Tabuada Divertida e Bingo). A prova SPAECE de LP e Matemática foi corrigida para **01/12/2026, terça-feira**; a preparação termina em 30/11/2026.

**Data-base:** 11/08/2026. Os números são linha de base histórica, não
resultado de novembro de 2026. O plano declara 19 datas letivas potenciais
entre 03 e 30/11, condicionadas ao calendário escolar.

## 2. Dados agregados usados no vídeo

- 55 estudantes previstos: 5º A (27), 5º B (28).
- Língua Portuguesa: 70% adequado na escola; 78% no 5º A; 63% no 5º B;
  22% intermediário; 7% defasagem no consolidado.
- Matemática: 62% adequado; 59% no 5º A; 65% no 5º B; 30% intermediário;
  8% defasagem.
- Fluência: 43 fluentes, 5 iniciantes, 2 pré-leitores entre 50 avaliados;
  5 resultados do 5º B sem registro.
- Escrita: média 6,5; 66% entre satisfatório e avançado; 16% abaixo de
  intermediário no consolidado.
- Marcadores de menor acerto:
  - LP 5º A: H18/H19 26%, H12 41%, H05 52%, H11 56%.
  - LP 5º B: H05 22%, H18 26%, H19 30%, H12 37%, H20 44%.
  - MAT 5º A: H18 33%, H12 37%, H01/H14 41%, H08/H11 48%.
  - MAT 5º B: H12 23%, H14 33%, H11 42%, H01/H18 46%.

**Advertência:** H01–H20 são marcadores do arquivo CAEd analisado. Sem
dicionário de equivalência, não são descritores oficiais do SPAECE. O vídeo
mantém essa ressalva na tela.

## 3. Mapa e localização

- **Coordenadas do equipamento:** latitude `-5.1872778`, longitude
  `-40.6627838`, obtidas no OpenStreetMap/Nominatim para “E.C. Airam Veras”.
- **Endereço retornado pelo OSM:** Rua Capistrano de Abreu, Ipase, Crateús,
  Ceará, 63700-450.
- **Bairro no vídeo:** Maratoan, conforme indicação local do solicitante. A
  relação de bairro “Maratoan” do OSM tem limite norte em aproximadamente
  `-5.18757`; a coordenada do equipamento está a cerca de 30 m ao norte desse
  limite. O registro de endereço do OSM indica Ipase. A divergência é mantida
  como cautela, não escondida.
- **Limites estaduais/municipais:** API de malhas do IBGE,
  `https://servicodados.ibge.gov.br/api/v3/malhas/estados/23` e
  `.../municipios/2304103` (Ceará/Crateús), formato GeoJSON.
- **Mapa de ruas:** tiles © OpenStreetMap contributors, licença ODbL 1.0,
  `https://www.openstreetmap.org/copyright`. Atribuição visível no vídeo.
- **Uso:** poucas dezenas de tiles estáticos, sem scraping em massa; mapas
  gerados localmente para o vídeo.

## 4. Ferramentas

| Ferramenta | Uso | Licença/observação |
|---|---|---|
| Remotion | composição e render | licença própria da Remotion; conferir termos por uso |
| FFmpeg | mux, normalização, QC | build local LGPL/GPL |
| Edge TTS (`pt-BR-FranciscaNeural`) | narração institucional sintética | serviço Microsoft; sem clonagem; conferir termos de uso antes de publicar |
| XTTS v2 (Coqui) | clonagem do agradecimento final do autor | referência local de 25 s, autorizada pelo próprio autor; modelo executado em CPU; não publicar o modelo/voz sem nova autorização |
| Pillow / matplotlib | mapas, logo, imagens | licenças livres |
| DejaVu Sans | tipografia | licença Bitstream Vera |
| OpenStreetMap | mapa de ruas | ODbL 1.0 |
| IBGE | malhas | dados públicos |

## 5. Voz, pronúncia e clonagem

- A grafia institucional na tela é **Airam Veras**. A locução usa **“Véras”**
  para marcar a sílaba tônica indicada pelo autor.
- A narração institucional usa Edge TTS `pt-BR-FranciscaNeural`.
- O agradecimento final usa XTTS v2 com referência local de 25 s do próprio
  autor (trecho 11,5–36,5 s do vídeo `oNOsPBNYSwc`, canal “Prof. Marcelo
  Claro”), mediante autorização explícita registrada na conversa.
- Por custo de inferência em CPU, a clonagem foi aplicada apenas à frase curta
  do agradecimento; o restante permanece com a voz institucional. A referência
  e o modelo não foram publicados; o áudio é ignorado pelo Git.
- A clonagem não é usada para simular fala de terceiros, cobrança, autenticação
  ou qualquer finalidade fora deste vídeo.

## 6. O que não foi usado

- Nenhum nome, nota individual, código de estudante ou ranking do dossiê.
- Nenhuma voz humana clonada ou áudio do vídeo de referência.
- Nenhum resultado de novembro, previsão de prova ou promoção de escola.
- Nenhum dado sensível, credencial ou sessão pessoal.

## 7. Limites

- O vídeo é uma **síntese pedagógica** do plano e do consolidado; não substitui
  a leitura integral dos PDFs, o plano oficial, a matriz do SPAECE ou a decisão
  da equipe escolar.
- A linha de base é de agosto; não representa o desempenho atual.
- Metas são propostas, não garantias.
- H01–H20 não são descritores oficiais sem dicionário de equivalência.
- O mapa é ilustrativo e pedagógico; não é mapa de resultados nem limite
  oficial de bairro.
- Não há validação externa, aceite editorial ou publicação automática.
