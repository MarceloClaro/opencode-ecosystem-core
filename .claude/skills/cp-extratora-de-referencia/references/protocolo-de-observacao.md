# Protocolo de observação

Use antes de interpretar a referência. O método precisa permitir voltar ao mesmo ponto e diferenciar conteúdo observado de hipótese de construção.

## 1. Identidade e inventário

Identifique a fonte por um ID estável dentro do pacote. Registre nome ou localizador fornecido, caminho relativo real quando houver arquivo, tamanho e hash quando calculáveis. Um hash ajuda a evitar reutilizar a análise depois que alguém substituiu a mídia com o mesmo nome; não invente esse identificador se não foi calculado.

Inspecione com as ferramentas disponíveis, como um leitor de metadados ou `ffprobe` quando instalado. Registre duração, dimensões, proporção, orientação, FPS e taxa variável quando verificáveis; presença de faixas de áudio, canais, frequência de amostragem e codecs quando disponíveis. Para campos desconhecidos, use `null` e indique a limitação. Não trate codec ou extensão como prova de transparência visual.

Declare a origem dos tempos. Use segundos decimais a partir do início do arquivo acessível. Se ele for um recorte de outro vídeo e a posição original não for conhecida, não atribua tempos no vídeo maior. Guarde o deslocamento de origem somente se tiver sido confirmado. Em mídia com taxa variável, prefira timestamps de apresentação; não converta índice em segundos usando uma média de FPS como se fosse exata.

Para um link inacessível, ainda é possível criar um pacote que documente o impedimento, mas não uma análise temporal inventada. Para frames sem tempos, registre a ordem fornecida como ordem de imagens, não como prova de duração ou de corte. A ausência de áudio nos frames não prova que o vídeo de origem era silencioso: nesse caso, `audio_present` permanece `null` e a cobertura de áudio é `indisponivel`.

## 2. Cobertura de ponta a ponta

Faça uma passagem visual temporal por toda a duração acessível, com reprodução ou ferramenta que exponha a sequência em movimento. Conte apenas intervalos efetivamente inspecionados. Uma ferramenta de detecção de cortes ou folha de contato pode orientar a revisão; sozinha não comprova transições, ações entre frames ou cobertura temporal integral.

Escute o áudio disponível ou use uma ferramenta capaz de analisá-lo, distinguindo o que foi ouvido do que foi inferido por sinais. Se houver transcrição automática, confira as passagens usadas como evidência contra o áudio quando a escuta for possível. Identifique trechos incertos, nomes e números. Não afirme conferência auditiva que não aconteceu.

Mantenha três coberturas independentes: visual, áudio e transcrição. Cada uma lista intervalos inspecionados, método e lacunas. Um clipe de dez segundos pode ter análise completa do clipe e cobertura desconhecida do vídeo de origem. Escreva essas duas afirmações separadamente.

Se o vídeo for longo, trabalhe em blocos contíguos com uma pequena sobreposição para revisar suas junções. Observe o último trecho e o encerramento. Não apresente uma amostra dos primeiros minutos como padrão confirmado do restante.

## 3. Timeline por corte e por unidade

Marque cada corte confirmado. Dentro de um mesmo plano, crie outro registro quando mudar o foco principal, o estado de uma demonstração, a composição ou uma transformação relevante. Uma unidade de sentido pode conter vários cortes; preserve um `unit_id` comum sem apagar os cortes individuais.

Use intervalos de início inclusivo e fim exclusivo. Registros consecutivos podem compartilhar a fronteira. Uma transição que cruza dois planos aparece em um registro próprio ou em um dos registros com sua extensão anotada; não duplique a duração para inflar a cobertura. Se a fronteira não puder ser localizada com precisão, marque o tempo como aproximado e explique o método.

Cada registro precisa permitir reconstruir a sequência: estado inicial, ação percebida, estado final, foco, relação com a fala e evento de saída. Não basta listar “zoom”, “título” e “ícone” sem dizer quando e para que aparecem.

Nas lacunas, use registros de cobertura não observada. Para uma imagem isolada, use observação pontual; nunca estenda o estado de um frame até o próximo como se soubesse o que ocorreu no intervalo.

## 4. Dimensões a observar

| Dimensão | Evidência útil | Limite a preservar |
| --- | --- | --- |
| Enquadramento e crop | Região visível da pessoa, folga de cabeça, tamanho relativo, mudança de janela | Não atribuir rastreamento automático apenas porque o rosto ficou centralizado |
| Zoom e tracking | Trajetória aparente, início/fim, estabilidade, resposta a deslocamentos | Distinguir movimento de câmera, crop e escala como hipóteses quando não forem separáveis |
| Tipografia e hierarquia | Família visual, peso aparente, caixa, largura, posições, quebras, construção | Descrever características quando a fonte exata não for verificável |
| Cor e luz | Relações de contraste, dominante, acentos, sombras, separação de planos | Valores de cor são amostras dos pixels comprimidos, não a paleta de origem comprovada |
| Legendas | Posição, quantidade visível, quebras, destaques, sincronismo com áudio | Sem áudio, só a aparência do texto pode ser confirmada |
| Elementos e inserções | O que aparece, tamanho, função, entrada, permanência e saída | Um screenshot no vídeo não prova que o arquivo original está disponível |
| Transições | Mudança observada entre estados e elemento que mantém continuidade | Não nomear plugin ou preset pela semelhança |
| Composição e camadas | Sobreposição, paralaxe, oclusão, separação de planos | O vídeo achatado não revela diretamente a pilha do projeto |
| Alfa e 3D | Contorno aparente, oclusão, laterais, luz e mudança de ponto de vista | Classificar o método como inferido sem projeto ou dados que o comprovem |
| Ritmo e pausas | Duração medida das unidades, estados estáveis, cortes e respiros | Não inferir retenção, conversão ou velocidade de produção a partir do ritmo |
| Áudio, música e SFX | Voz, presença audível, função, entradas/saídas e relação de volume | Não nomear faixa, licença, fonte ou loudness exato sem identificação ou medição |
| Fala e movimento | Trecho falado, verbo/ideia que dispara ação e diferença temporal medida | Não substituir fala por texto de tela ou inventar precisão de sincronismo |

## 5. Evidências e limites de generalização

Associe um achado a um ou mais registros e aos intervalos efetivamente observados. Referências a capturas ou trechos de QA são opcionais; se citadas, os arquivos devem existir com caminhos relativos. Não incorpore cópias da referência ao pacote distribuível sem necessidade e autorização de uso.

Uma regra recorrente precisa de exemplos em mais de uma ocorrência quando disponíveis. Se só ocorreu uma vez, descreva como escolha pontual transferível, sem alegar frequência. Uma técnica invisível continua incerta mesmo que seja a explicação mais provável.

Conclua com limites concretos: trechos não acessados, transcrição não conferida, áudio indisponível, fonte não identificada, técnica 3D inferida, recursos não fornecidos. Esses limites seguem para a receita e para o prompt de recriação, sem bloquear as regras que já têm evidência suficiente.
