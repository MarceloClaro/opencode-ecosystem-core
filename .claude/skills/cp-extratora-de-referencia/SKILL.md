---
name: cp-extratora-de-referencia
description: Analise temporalmente um vídeo de referência e extraia um pacote verificável de padrões de edição para reutilização em outro vídeo. Use para mapear cenas, fala, composição, tipografia, movimento e áudio e gerar relatório, CSV, receita JSON e prompt de recriação; extração não autoriza produzir a edição.
---

# Extratora de referência

Converta uma referência observada em um sistema reutilizável de decisões. Separe o que o vídeo mostra, a hipótese sobre sua construção e a regra que poderá orientar outro material. Preserve a evidência sem transportar conteúdo, voz, marca ou promessas de terceiros para a nova edição.

## Delimite a extração

Identifique o arquivo ou link fornecido, o intervalo solicitado e o que está realmente acessível. O padrão é analisar o vídeo completo quando disponível. Se o usuário forneceu somente trecho ou frames, analise esse material e declare o limite; não exija outro arquivo para começar o que já é possível.

Leia [Protocolo de observação](references/protocolo-de-observacao.md) antes da análise. Faça inventário técnico e registre separadamente cobertura visual, escuta do áudio e transcrição. Uma duração obtida por metadados não prova que o conteúdo inteiro foi observado. Frames espaçados não comprovam cortes, movimentos ou áudio nos intervalos.

Use ferramentas já disponíveis e adequadas ao material. Não instale pacotes, baixe modelos grandes, envie mídia a serviços externos ou use processamento pago por presunção. Reaproveite autorização existente que cubra essas ações; sem ela, use o caminho disponível e informe a limitação que afeta o resultado. Esta skill não exige outro pacote de skills para funcionar.

Se o pedido for apenas extrair, entregue o pacote de análise. O prompt de recriação é um arquivo para uso posterior, não uma instrução para executar uma edição agora. Se o usuário também pediu editar, conclua a extração útil e prossiga somente dentro desse escopo já autorizado.

## Observe a sequência real

Faça uma passagem temporal de toda a extensão acessível, depois aproxime cortes, transições e acontecimentos que definem o estilo. Divida a timeline por cortes e por mudanças relevantes dentro do mesmo plano. Agrupe esses registros em unidades de sentido, mantendo os tempos do material de origem.

Registre enquadramento, crop, zoom e acompanhamento do sujeito; tipografia e hierarquia; cor e luz; legendas; elementos e inserções; transições; composição, camadas, aparente oclusão e volume; ritmo e pausas; voz, música e SFX; relação entre fala e movimento. Cada dimensão deve ter achado ou limitação explícita, não um campo preenchido por suposição.

Quando houver áudio acessível, transcreva com intervalos verificáveis e marque palavras incertas. Se a ferramenta não permitir ouvir ou transcrever, registre isso. Não deduza a fala pelo texto na tela, nem conclua que não existe música porque não conseguiu escutar.

Classifique cada achado:

- `observado`: visto, ouvido ou medido por uma ferramenta identificada, com evidência localizável.
- `inferido`: interpretação sustentada por evidência, acompanhada do que permanece incerto.
- `nao_verificavel`: não foi possível confirmar com os materiais ou métodos disponíveis; explique o motivo.

Não invente timestamps, frames, nomes exatos de fontes, plugins, ferramentas, assets ocultos, canal alfa, geometria 3D ou métricas de retenção. Aparência não prova método de produção. “Texto desaparece atrás da pessoa” pode ser observado; “foi usado um modelo de segmentação específico” não decorre disso.

## Extraia regras, sem copiar a peça

Associe cada regra a achados e evidências. Registre gatilho, ação, permanência, saída, o que preservar e como verificar o resultado. Expresse a regra em relação à função da fala e ao espaço disponível, sem importar os tempos absolutos da referência para outro roteiro.

Separe a descrição do original da aplicação sugerida. Exemplo: observar uma demonstração em tela cheia durante determinada frase pode sustentar “dar área à prova quando ela precisa ser examinada”. Isso não autoriza copiar a demonstração, a frase ou a oferta.

Regras apoiadas apenas em inferência continuam condicionais e precisam de teste. Não transforme uma ocorrência isolada em padrão universal. Identifique exceções e alternativas quando formato, duração, recursos ou identidade do destino forem diferentes.

## Produza os quatro arquivos

Leia [Contrato do pacote](references/contrato-do-pacote.md) e gere, na mesma pasta de saída:

1. `referencia-de-edicao.md`: inventário, cobertura, timeline interpretada, transcrição quando possível, evidências, padrões e limites.
2. `mapa-de-cenas.csv`: registros temporais por corte ou unidade visual, inclusive lacunas de cobertura.
3. `receita-visual.json`: fonte, cobertura, evidências, achados, regras e encaminhamentos em estrutura reutilizável.
4. `prompt-de-recriacao.txt`: comando adaptável com `[VIDEO DESTINO]`, `[FORMATO]` e `[MARCA]`, sem conteúdo de terceiros embutido.

Use caminhos relativos ao projeto real e referências relativas entre os quatro arquivos. Não invente um arquivo de mídia local para representar um link ou um asset que não foi entregue. Preserve a origem; não sobrescreva um pacote existente de outra referência. Para a mesma referência, crie uma nova versão ou diretório de saída e peça autorização antes de substituir resultados anteriores. O contrato explica como registrar tempos desconhecidos e análise parcial sem fingir completude.

## Encaminhe somente o que for útil

Registre os encaminhamentos relevantes na receita. Carregue uma skill de apoio somente se a tarefa atual pedir a decisão ou execução que ela resolve; encontrar lettering não exige abrir todas as skills durante uma extração.

| Achado ou próximo trabalho | Skill do mesmo pacote |
| --- | --- |
| Adaptar a receita ao vídeo destino e à identidade própria | [Estilo por referência](../cp-estilo-por-referencia/SKILL.md) |
| Definir foco, encadeamento ou ocupação da tela | [Direção de edição](../cp-direcao-de-edicao/SKILL.md) |
| Converter uma relação em ação, processo ou volume | [Motion explicativo](../cp-motion-explicativo/SKILL.md) |
| Resolver crop, moldura, tracking ou viabilidade de alfa | [Apresentador em cena](../cp-apresentador-em-cena/SKILL.md) |
| Aplicar hierarquia e construção tipográfica | [Lettering com hierarquia](../cp-lettering-com-hierarquia/SKILL.md) |
| Criar variações e lotes de um padrão aprovado | [Variações controladas](../cp-variacoes-controladas/SKILL.md) |

Se a skill apontada não estiver disponível na instalação, mantenha o encaminhamento como opcional e siga com o pacote extraído. Não exija instalar o bônus nem carregue uma skill que só será usada em trabalho futuro.

## Verifique e entregue

Confira os quatro arquivos pelo contrato, incluindo IDs, intervalos, caminhos e distinção entre evidência e regra. Revise pontos críticos no vídeo: limites dos cortes, duração dos estados, sincronismo e lacunas declaradas. Validação de estrutura não substitui essa observação.

Entregue os links dos quatro arquivos, a cobertura alcançada e os limites que afetam a reutilização. Não diga “análise completa” se alguma modalidade necessária ficou parcial ou inacessível. A amostra de uma futura edição respeita as aprovações já dadas; não crie uma nova espera obrigatória quando a execução já foi autorizada com critérios suficientes.

Respeite direitos, licença, consentimento e privacidade da referência e das pessoas nela presentes. A análise não concede direito de reutilizar a gravação, a voz, a marca ou os assets observados.

## Salvaguardas adicionais

- Preserve os arquivos originais e não sobrescreva a versão aprovada; grave novas saídas em destino distinto.
- Não envie mídia, voz, rosto, transcrição ou material confidencial a serviços externos, gratuitos ou pagos, sem autorização específica que cubra a transferência.
- Respeite direitos, licença, consentimento e privacidade; uma referência não concede licença para copiar conteúdo de terceiros.
