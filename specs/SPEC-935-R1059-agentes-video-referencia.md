# SPEC-935-R1059 — Agentes e receitas de vídeo por referência

**Status:** proposta de arquitetura; implementação e piloto pendentes.
**Solicitação:** estudar estilos e efeitos de outros vídeos e reutilizá-los na
produção com Remotion e outro framework, por agentes catalogados.
**Contrato textual:** TSPEC-2852ce55; tarefa A2A `task-04cc5cc9`.

## 1. Escopo desta consulta

Documentar viabilidade, arquitetura, responsabilidades e critérios de aceite.
Não instalar pacotes, criar/ativar perfis, analisar uma referência inexistente,
renderizar mídia ou modificar o vídeo R1058 nesta consulta. O usuário ainda
precisa fornecer as referências desejadas para a primeira aplicação real.

## 2. Evidência e estado observado

- `editor-workspace/remotion-smoke/package.json` declara Remotion e CLI
  `4.0.540`, React/React DOM `19.2.0`.
- Skill existente: `.claude/skills/cp-extratora-de-referencia/SKILL.md`;
  prevê observação temporal e quatro arquivos rastreáveis, não extração
  automática já comprovada.
- Skill existente: `.opencode/skills/remotion-auditavel/SKILL.md`;
  distingue licença, prévia, aprovação de render e QC.
- `agents/catalog/plugin-design.md` e `plugin-visualize.md` são perfis
  de coordenação com restrições; não equivalem a renderizadores de vídeo.
- Não foi encontrado `@motion-canvas/core/package.json` em `editor-workspace`.
  Isso não comprova ausência em toda a máquina. A integração proposta não foi
  executada nesta consulta.
- Consulta externa de arquitetura via `ecosystem_run`: resposta textual
  concluída; o executor informou bloqueio na leitura local. A conferência dos
  arquivos acima foi feita pelo primário, não por esse executor.
- Doctor: 22/22 verificações estruturais; não é teste do pipeline de mídia.

## 3. Arquitetura proposta

Referência acessível → observação com timecodes → receita visual → adaptação
ao roteiro/identidade → animações → composição → prévia → revisão → master/QC.

| Componente | Responsabilidade |
| --- | --- |
| Remotion | Composição, montagem, câmera, áudio, legendas e saída final |
| Motion Canvas | Animações vetoriais procedurais, diagramas e explicações |
| Adaptador a implementar | Intercâmbio por sequência PNG ou clipe; FPS, dimensões, duração, cores e transparência conferidos |
| Ferramentas de mídia disponíveis | Sondagem, extração de frames, montagem e QC; execução somente no escopo autorizado |

Não há pressuposto de runtime compartilhado ou integração nativa pronta.
Render Remotion deve ser derivado do frame, não de relógio ou animação CSS.
No intercâmbio, validar alinhamento temporal e alpha quando exigido; MP4
comum não deve ser presumido como portador de transparência.

## 4. Papéis propostos para o catálogo

Identificadores abaixo são candidatos, não agentes criados ou ativados.
Reutilizar perfis existentes quando cobrirem o contrato.

| Candidato | Entrada → saída |
| --- | --- |
| video-reference-analyst | Vídeo/trecho e direitos → cobertura, evidências, mapa de cenas |
| video-style-architect | Evidências e identidade própria → receita visual parametrizada |
| video-remotion-compositor | Roteiro, receita e assets → composição determinística |
| video-motion-canvas-animator | Cenas explicativas → animações e manifestos de exportação |
| video-quality-reviewer | Prévia, roteiro e critérios → achados técnicos, visuais e factuais |

MarceloClaro coordena os papéis. Antes de qualquer perfil permanente:
`agent_profile_action`/`ecosystem_agent_profile` para validação, criação e
registro; spec, testes, proveniência, capacidades, permissões e contrato de
saída explícitos. Registro não comprova execução. Sem promoção de confiança
por aprovação própria ou mera existência do cartão.

Um agente é uma responsabilidade; uma skill é um procedimento; um template
é código parametrizado; uma receita é um estilo documentado. Não criar um
agente por vídeo nem afirmar treinamento de modelo a partir dessa catalogação.

## 5. Contrato da receita e das referências

Reutilizar o contrato da skill: `referencia-de-edicao.md`,
`mapa-de-cenas.csv`, `receita-visual.json`, `prompt-de-recriacao.txt`.

Cada receita deve registrar versão, origem, intervalo observado, hashes quando
há arquivo local, direitos/limites, evidências, achados observados/inferidos/
não verificáveis, regras de composição, movimento, tipografia e ritmo,
parâmetros adaptáveis, compatibilidade e encaminhamentos. Fonte ou plugin
exato não podem ser deduzidos apenas pela aparência. Incluir revisão de áudio
ou declarar que ela não foi realizada.

Recriar a linguagem visual com conteúdo próprio; não transportar automaticamente
gravações, marcas, vozes, fontes, músicas ou assets de terceiros. Referência
não concede licença de reutilização. Não enviar mídia a serviços externos
sem autorização específica. Conferir elegibilidade da licença Remotion e
licenças das dependências antes de instalar/distribuir.

## 6. Aceitação da futura implementação (ainda pendente)

1. Testes primeiro: schema aceita receita válida e rejeita tempos inválidos,
   evidência ausente, direitos necessários ausentes e parâmetros incompatíveis.
2. Perfis validados pelo primário e roteados ao papel correto; sem duplicar
   capacidade existente, ampliar permissões silenciosamente ou executar mídia
   em uma tarefa limitada à análise.
3. Piloto curto baseado em referência real, com observação temporal declarada;
   verificar determinismo, FPS, resolução, alpha e alinhamento de áudio.
4. Prévia antes do master, com aprovação no escopo correspondente. Não prometer
   reprodução exata nem qualidade profissional apenas por metadados corretos.
5. Conferir legibilidade, sincronismo, transições, voz, cortes, conteúdo factual
   e geometria/cartografia quando presentes; revisão humana registrada.
6. Uma execução por destino, cache vinculado ao conteúdo e orçamento explícito;
   não repetir renders concorrentes, não reduzir resolução/voz silenciosamente,
   preservar originais e versões aprovadas.
7. QC medido no arquivo efetivamente entregue, com hash e recibo da cadeia real;
   testes técnicos não substituem revisão estética ou factual.

## 7. Documentação consultada

- Remotion: https://www.remotion.dev/docs/assets
- Remotion: https://www.remotion.dev/docs/use-current-frame
- Motion Canvas: https://motioncanvas.io/docs/rendering/image-sequence
- Motion Canvas: https://motioncanvas.io/docs/rendering/video
- Agentes OpenCode: https://opencode.ai/v2/docs/agents

Consulta aos frameworks por Context7, e documentação oficial de agentes.
APIs atuais não devem ser presumidas compatíveis com a versão local fixada.
Não houve instalação, novo render, criação de agentes ou publicação.

## 8. Continuação — referência Instagram fornecida

O usuário forneceu um link MP4 direto do domínio
`instagram.fjdo10-1.fna.fbcdn.net` e pediu recriação do vídeo. O escopo da
seção 1 registra a consulta anterior; esta continuação autoriza tentar obter
a referência e analisar sua linguagem visual para preparar a recriação.

- A URL assinada será usada apenas para acesso local; não versionar seus
  parâmetros. Preservar identidade por hash da URL e, se obtido, do arquivo.
- Sondagem/download limitado a 200 MiB e 120 segundos, sem autenticação,
  cookies importados, instalação, serviço pago ou envio da mídia a terceiros.
- Se a origem negar acesso ou falhar, registrar a resposta observada e pedir
  o MP4 ou link público do Reel, sem alegar ter assistido e sem contornar
  controles de acesso. Não inferir duração, formato ou efeitos pela URL.
- Se acessível, sondar a mídia e registrar cobertura visual, sonora e textual
  separadamente. Análise de estilo não implica clonagem de voz ou identidade.
- Aproveitar as quatro saídas do contrato da skill somente com evidência real;
  pacote bloqueado deve manter campos desconhecidos nulos e regras vazias.
- A recriação dependerá do conteúdo observado, dos materiais próprios ou
  autorizados e da direção de destino. Render e instalação seguem os gates
  existentes; não apresentar download ou receita como vídeo recriado.

Aceite desta etapa: recibo de acesso sem credenciais, integridade conferida
se houver mídia, relato fiel de sucesso/bloqueio e próximo passo executável.
Não sobrescrever o master R1058 nem seus assets.

## 9. Piloto autorizado — Monte Roraima

O usuário selecionou **Monte Roraima**, autorizou **instalação isolada do
Motion Canvas e prévia de 8–12 segundos**, sem serviços pagos ou envio da mídia
a terceiros. Depois forneceu o roteiro e os créditos de referência.

### Entrega limitada

- Prévia de **10 segundos, 720×1280, 30 fps, 300 frames**, identificada como
  estudo/recriação, sem marca Terra Ledger, clone vocal ou publicação.
- Projeto Motion Canvas isolado em `editor-workspace/r1059-motion-canvas/`;
  não atualizar dependências do projeto Remotion existente.
- Movimento explicativo original executado no Motion Canvas, exportado como
  sequência PNG e efetivamente utilizado na composição Remotion. Não basta
  incluir o nome de um framework em um prompt ou arquivo não executado.
- Mapa: contornos e coordenadas geográficas rastreáveis; cor, composição,
  câmera, títulos e ilustrações inspirados na referência, sem copiar seus
  arquivos de projeto ou assumir acesso às camadas originais.
- A amostra visual pode ser entregue sem narração, com essa limitação clara;
  não reutilizar a voz da referência. O roteiro completo fica como entrada
  fornecida, com números e atribuições a conferir antes do master.
- Imagens com créditos fornecidos só serão reutilizadas após localizar a
  fonte e conferir a licença específica; não presumir CC BY quando for BY-SA.
- Prévia exige aprovação do usuário antes de ampliar ao master.

### SDD/TDD e gates

Antes do código, testes em `tests/test_r1059_video_reference.py`: receita sem
  referência observada não pode declarar cobertura completa; intervalo fora
  da duração e evidência inexistente são rejeitados; manifestos de frames
  devem ter 300 entradas contínuas, resolução e fps idênticos ao contrato;
  coordenadas/transformações são determinísticas e não podem sair do mapa.
Após GREEN, verificação dos dois motores, prévia e QC técnico; aprovação
  estética e factual permanece humana. Persistir fonte, versões, comandos,
  hashes, perdas deliberadas e limites. Não treinar modelo por catalogação.

## 10. Resultado do piloto (2026-11-05)

**Status:** prévia renderizada e aprovada no QC técnico; revisão humana e
publicação pendentes. Não é o vídeo completo de 82 s.

| Item | Resultado |
|---|---|
| Arquivo | `pilots/r1059-roraima/out/roraima-preview-final.mp4` |
| Formato | 720×1280, 30 fps, 300 frames, 10,000 s |
| SHA-256 | `dfe16e765371ae29f8aab77df361c8db35978dee9ba2c170cfd403f55d9fe7d4` |
| Tamanho | 1.486.095 bytes |
| Motores | Motion Canvas 3.17.2 + Remotion 4.0.540 |
| QC | 300/300 frames · −14,47 LUFS · true peak −4,51 dBTP · 0 s de preto |
| Testes | `27 passed` em `tests/test_r1059_video_reference.py` |

### Execução comprovada

- O Motion Canvas rodou em navegador local e exportou **300 PNG RGBA**
  720×1280 por `Renderer` + `ImageExporter`, com raiz de integridade
  `49191d427744011db6e85f9d0ce32e0ea7087ab4bb76197c6f9805ad4e8f6e2e`.
- O Remotion consumiu esses frames na composição `RoraimaStudy`: o movimento
  da mesa, nuvens, conectores e pulso vem do Motion Canvas; mapa, legendas,
  etiquetas e áudio são montados no Remotion por frame.
- O mapa usa WMS EPSG:4326 com bbox declarada e as coordenadas são convertidas
  pela mesma função validada nos testes.
- A narração foi sintetizada localmente e conferida por ASR; nenhuma voz da
  referência foi clonada.

### Decisões deliberadas

- Não reutilizar marca, logotipo, chamada de inscrição, voz, música, fotos,
  capa de livro ou texto da referência.
- Bandeiras representadas por faixas de cor, sem brasões oficiais.
- A referência foi observada por amostragem de 2 fps; a cobertura continua
  declarada como **parcial**, inclusive no pacote `reference/`.
- O piloto cobre 10 s, não os 82 s da referência.

### Limites e próximo passo

- Revisão estética e factual humana ainda não registrada.
- Mapa ilustrativo, relevo generalizado e ponto triplo aproximado.
- Altitude “cerca de 2.800 m” conforme o roteiro fornecido, não medição nova.
- Para o vídeo completo: ampliar o roteiro por capítulos, produzir inserções
  licenciadas, medir a narração e validar cada transição em prévia.
