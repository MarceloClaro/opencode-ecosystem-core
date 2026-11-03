# Contrato do pacote de extração

Leia ao produzir os quatro arquivos. Use a mesma pasta de saída, IDs compartilhados e UTF-8. Registre segundos decimais no CSV e no JSON; apresente também `mm:ss.mmm` no relatório quando isso facilitar a consulta. Não acrescente casas decimais que o método não sustenta.

## referencia-de-edicao.md

O relatório precisa conter:

1. **Fonte e escopo:** identidade, inventário técnico verificado, intervalo solicitado, origem dos tempos e versão da extração.
2. **Cobertura:** extensão visual observada, áudio analisado, transcrição disponível, métodos e lacunas. Explique se é vídeo inteiro, clipe ou imagens.
3. **Mapa interpretado:** sequência das unidades, foco e acontecimentos, com links para IDs do CSV e timestamps reais.
4. **Fala:** transcrição temporizada quando possível, separada do texto visto na tela; marque palavras incertas e partes que não foram conferidas. Quando houver limite de acesso ou de reprodução do material, registre-o e use apenas os excertos necessários para sustentar a análise.
5. **Achados por dimensão:** descrição do original, classificação, IDs de evidência e limites. Cubra as dimensões do protocolo, mesmo que o resultado de alguma seja “não verificável”.
6. **Regras adaptáveis:** gatilho, ação, permanência, saída, exceções, requisito de mídia e critério de teste. Não confunda uma regra proposta com um fato observado.
7. **Aplicação e limites:** o que pode ser transferido, o que precisa de material próprio, quais técnicas precisam de teste e quais skills podem ajudar depois.

Não replique slogans, roteiro, depoimentos ou identidade da referência no bloco de aplicação. Uma transcrição analítica não é roteiro autorizado para o vídeo destino.

## mapa-de-cenas.csv

Use uma linha por segmento temporal observado, lacuna ou imagem pontual, com este cabeçalho:

```csv
record_id,unit_id,record_type,start_s,end_s,time_precision,visual_focus,framing_crop_zoom,text_hierarchy,captions,elements_insertions,transition,layers_depth,color_light,audio_event,speech_cue,speech_motion_relation,pace_pause,evidence_ids,notes
```

- `record_type`: `segmento`, `lacuna` ou `frame_pontual`.
- `record_id`: único; `unit_id`: agrupa registros que pertencem à mesma ideia, vazio quando desconhecido.
- `start_s`/`end_s`: números medidos na origem declarada; `segmento` e `lacuna` exigem fim maior que início. Para `frame_pontual`, início e fim podem ser o mesmo timestamp conhecido; ambos ficam vazios se o tempo da imagem não foi fornecido.
- `time_precision`: `verificado`, `aproximado` ou `desconhecido`. Se aproximado, explique o método e a margem conhecida nas notas; não invente margem numérica.
- Campos descritivos: fatos vistos/ouvidos ou texto literal `nao_verificado`. Uma ausência confirmada deve ser escrita como `ausente_no_intervalo_observado`, não confundida com falta de acesso.
- `speech_cue`: trecho mínimo que localiza a relação com a fala; se não há áudio verificável, use `nao_verificado`.
- `evidence_ids`: IDs separados por `|`, todos existentes no JSON. Lacunas não recebem evidência de observação do conteúdo.

Escreva com um gerador de CSV para escapar vírgulas, aspas e quebras corretamente. Registros de segmentos e lacunas devem formar uma sequência sem sobreposição na região cujo mapeamento temporal foi possível. Imagens pontuais não preenchem lacunas e não criam uma duração. Não invente cortes dentro de uma região inacessível.

## receita-visual.json

Use um objeto JSON com `schema_version: "1.0"` e estas chaves. Campos técnicos desconhecidos recebem `null`; arrays podem ficar vazios quando a limitação estiver declarada.

### reference

`id`, `source_type` (`arquivo`, `link`, `clipe` ou `frames`), `media_path` (relativo real ou `null`), `source_url` (URL fornecida sem credenciais, ou `null`), `sha256` (calculado ou `null`), `duration_s`, `width_px`, `height_px`, `fps`, `variable_fps`, `audio_present`, `time_origin` e `source_offset_s`.

`time_origin` descreve se os tempos partem do início do arquivo disponível ou de outro marco confirmado. `source_offset_s` só contém deslocamento no vídeo maior quando conhecido. Não transfira esse deslocamento silenciosamente aos timestamps dos outros arquivos. Para frames sem tempo, declare que a ordem não determina duração. Campos adicionais de metadados são permitidos quando identificados e verificados.

### coverage

Inclua `visual`, `audio` e `transcription`, cada um com:

- `status`: `completa`, `parcial`, `indisponivel` ou `nao_aplicavel`.
- `intervals`: objetos com `start_s`, `end_s` e `method` para trechos efetivamente analisados.
- `point_record_ids`: IDs de imagens observadas que não constituem intervalo temporal.
- `gaps`: intervalos conhecidos não analisados, cada um com motivo.
- `limitations`: lista de limitações reais.

Use `nao_aplicavel` apenas quando a modalidade não existe ou não pertence ao escopo confirmado, como transcrição de mídia sem fala. Ferramenta ausente exige `indisponivel`, não `nao_aplicavel`. Cobertura visual `completa` exige sequência temporal inspecionada e cobertura sem lacunas de toda a duração declarada; imagens isoladas não a satisfazem. A cobertura do clipe não implica cobertura do vídeo maior.

Se o inventário confirmar que o arquivo não tem faixa de áudio, use `audio_present: false`, cobertura de áudio e transcrição `nao_aplicavel` e explique a evidência técnica. Nesse caso, descreva a análise como visual; texto na tela não permite reconstruir a fala, avaliar sincronismo labial ou afirmar que a referência original nunca teve trilha. Não confunda esse caso com um arquivo que tem áudio mas não pôde ser ouvido, nem com imagens isoladas sem informação da mídia original.

### evidence

Lista de objetos com `id`, `record_ids`, `start_s`, `end_s`, `time_precision`, `method`, `description` e `artifact_path`.

`method` informa o modo real de observação ou medição. `artifact_path` é um arquivo auxiliar existente, relativo ao pacote, ou `null`. Para evidência pontual sem tempo, ambos os tempos são `null`. `description` registra o que foi constatado, sem trocar inferência por observação. Cada evidência se vincula a pelo menos um registro observado, nunca a uma lacuna.

### findings

Lista de objetos com `id`, `category`, `status`, `statement`, `evidence_ids` e `limitations`.

Use as categorias `enquadramento`, `crop_zoom_tracking`, `tipografia_hierarquia`, `cor_luz`, `legendas`, `elementos_insercoes`, `transicoes`, `composicao_camadas`, `alfa_3d`, `ritmo_pausas`, `audio_musica_sfx` e `fala_movimento`. Outras categorias podem complementar a análise.

`status` usa `observado`, `inferido` ou `nao_verificavel`. Observações e inferências têm pelo menos uma evidência. A inferência explicita por que é plausível e o que não pode provar. Para um achado não verificável, `evidence_ids` pode estar vazio, mas `limitations` explica o impedimento. Pelo menos um achado por categoria documenta presença, ausência observada ou limitação; isso impede omissões silenciosas.

### reusable_rules

Lista de objetos com `id`, `finding_ids`, `scope` (`recorrente`, `pontual` ou `proposta_condicional`), `trigger`, `action`, `hold`, `exit`, `preserve`, `avoid`, `required_materials`, `validation` e `adaptation_notes`.

Os IDs apontam para achados reais. Use `proposta_condicional` quando depender de inferência ou de uma solução ainda não testada. O gatilho usa a fala e a função do conteúdo destino, não um timestamp a ser copiado. `hold` pode descrever um critério de leitura; duração numérica observada deve estar identificada como dado da referência, não regra universal. `required_materials` diferencia entradas do usuário de recursos que precisariam ser produzidos ou obtidos com autorização.

### routing, limitations e outputs

- `routing`: objetos com `skill_id`, `reason`, `finding_ids`, `rule_ids` e `when_to_load`. Inclua somente encaminhamentos justificados por achados ou pelo pedido; carregar é uma decisão posterior, não consequência automática da lista.
- `limitations`: limites do pacote que afetam a aplicação; preserve lacunas e técnicas não comprovadas.
- `outputs`: `report: "referencia-de-edicao.md"`, `timeline: "mapa-de-cenas.csv"`, `recipe: "receita-visual.json"`, `recreation_prompt: "prompt-de-recriacao.txt"`.

Os IDs precisam resolver no próprio pacote. Nenhum caminho pode apontar à instalação pessoal do autor. Se a mídia ficar fora da pasta da extração, use o caminho relativo real a partir dela e declare que é uma entrada externa, não um asset incluído.

## prompt-de-recriacao.txt

Gere um prompt específico com as regras selecionadas desta referência. Não entregue apenas uma frase genérica nem cole o relatório inteiro. Use esta estrutura como contrato, preenchendo a parte da receita com IDs e decisões extraídos:

```text
Use o pacote de extração que forneci com este pedido para adaptar a linguagem visual ao meu [VIDEO DESTINO], no [FORMATO], com a identidade [MARCA]. Leia referencia-de-edicao.md, receita-visual.json e mapa-de-cenas.csv na mesma pasta deste prompt. Resolva os caminhos a partir dessa pasta. Se apenas este texto estiver acessível, identifique a falta dos arquivos antes de afirmar que aplicou sua receita.

Preserve minhas restrições, voz, conteúdo, materiais autorizados e decisões já aprovadas. Minha instrução atual e as autorizações existentes prevalecem sobre as sugestões desta receita. Não copie falas, voz, marcas, oferta, provas ou assets de terceiros. Se eu preencher [MARCA] como “sem identidade definida”, proponha uma direção própria; não adote a identidade da referência por ausência de informação.

REGRAS A APLICAR
Insira aqui as regras efetivamente extraídas, com seus IDs, gatilhos, função visual, exceções e critério de verificação. Diferencie observações do original de adaptações sugeridas. Inclua os limites relevantes de acesso e de técnica. Não deixe esta instrução de preenchimento no arquivo entregue.

Analise o vídeo destino real e recalcule a sequência pela sua fala e duração; os timestamps da referência servem como evidência, não como timeline para copiar. Selecione apenas as regras compatíveis com meu formato e materiais. Abra somente as skills disponíveis e relevantes indicadas na receita; o trabalho não depende de instalar outro pacote.

Antes de repetir um padrão novo, valide uma amostra que demonstre sua transição e relação visual mais importantes. Se já autorizei concluir a edição ou o lote com critérios suficientes, use a amostra como teste interno e prossiga. Aguarde nova decisão apenas quando eu tiver pedido aprovação prévia ou surgir uma mudança material não autorizada. Não use serviços pagos nem envie materiais a serviços externos sem autorização que cubra essa ação.

Se usar Remotion, anime por frames, sem CSS animations, transitions ou timers como relógio. Confira as APIs e dependências realmente disponíveis. Uma aparência em perspectiva não comprova 3D genuíno; uma máscara aproximada não substitui alfa real. Identifique qualquer adaptação técnica e teste seu resultado antes de ampliar. Preserve os originais e entregue somente o que foi solicitado.
```

Oriente o usuário a substituir `[VIDEO DESTINO]` pelo caminho do arquivo próprio, `[FORMATO]` por proporção/dimensões/destino e `[MARCA]` por nome e identidade autorizada, ou “sem identidade definida”. Não transforme placeholders ausentes em licença para inventar essas informações. Se o destino não foi fornecido durante a extração, isso não impede entregar este prompt para uso futuro.

## Checagem final do pacote

- Os quatro arquivos existem; JSON e CSV são analisáveis por leitores reais.
- IDs são únicos e referências cruzadas resolvem. Evidências citam registros observados e tempos compatíveis.
- Início não ultrapassa fim; intervalos conhecidos não ultrapassam a duração acessível; lacunas não são contadas como observação.
- O status de cobertura corresponde aos métodos usados. Medir a duração ou transcrever áudio não comprova cobertura visual.
- Os limites nos achados reaparecem nas regras dependentes e no prompt de recriação.
- Não há nome exato de fonte, ferramenta, alfa, 3D ou métrica tratado como fato sem evidência correspondente.
- Os três placeholders destinados ao usuário permanecem; as instruções editoriais de preenchimento do modelo foram substituídas pelas regras reais.
- Nenhuma edição, publicação ou serviço foi executado só porque o prompt de recriação foi gerado.
