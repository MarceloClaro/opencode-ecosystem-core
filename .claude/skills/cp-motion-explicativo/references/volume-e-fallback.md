# Volume e fallback

Leia quando a cena precisar de profundidade real, câmera ou objetos que se abrem em camadas.

## O volume resolve uma pergunta?

Descreva qual relação se perderia em uma vista plana. Exemplos úteis: revelar o interior de um objeto, mostrar um caminho contornando obstáculos, separar peças e reconstruir o conjunto. Se a justificativa for apenas “parecer premium”, uma composição 2D pode servir melhor.

Um vídeo ou uma imagem aplicados a um plano podem integrar uma cena 3D, mas girar esse plano não cria a geometria do objeto representado. Objetos que precisam revelar lateral, espessura ou interior exigem volumes correspondentes.

## Teste antes de ampliar

Em Remotion, a integração documentada usa Three.js e React Three Fiber por `ThreeCanvas` de `@remotion/three`. Confira versões e orientações atuais no [guia oficial da integração](https://www.remotion.dev/docs/three), inclusive o ambiente de renderização. Calcule posições, câmera e materiais a partir do frame; não mantenha uma simulação que dependa dos frames anteriores terem sido reproduzidos.

Construa aproximadamente cinco segundos que incluam o ângulo crítico, a oclusão e a transformação principal. Renderize como vídeo no ambiente que produzirá o final. Verifique:

- Laterais ou espessuras aparecem quando a câmera muda; a luz responde à geometria.
- A sombra de contato e a oclusão ajudam a distinguir os planos.
- A câmera não atravessa objetos e os rótulos continuam ligados ao que descrevem.
- As partes se separam e retornam à mesma montagem, sem trocar de identidade.
- O arquivo reproduz o movimento; uma captura estática não substitui esse teste.

## Reduza complexidade com intenção

Se o teste falhar, primeiro identifique se o problema é geometria, dependência, contexto gráfico, carregamento ou desempenho. Simplifique materiais, segmentos e quantidade de objetos preservando a relação espacial.

Se o ambiente não executar a técnica, informe o limite observado. Uma vista explodida 2D, um corte esquemático ou planos em perspectiva podem preservar parte da explicação. Identifique a alternativa como tal. Use-a quando a representação for uma escolha aberta no escopo; se 3D genuíno for requisito explícito, essa mudança depende de decisão do usuário. Não troque a técnica silenciosamente nem contrate render pago para contornar o limite sem autorização.
