# SPEC-935-R911 — Atlas mental, estrutural e operacional do livro

Status: execução; resultados físicos no manifesto final.

## Objetivo

Completar o livro com mapas mentais, diagramas e fluxogramas locais das arquiteturas,
mais o mapa global, legendas e navegação. Preservar prosa, deduções R910 e fontes.
O atlas existente é introdutório e não substitui esta decomposição por subsistema.

## Contrato visual e de fonte

- Dezoito temas de arquitetura, cada um com três vistas: mapa mental (conceitos),
  diagrama estrutural (responsabilidades e conexões) e fluxograma (operação delimitada).
- Figuras vetoriais legíveis em A4, texto de nós de pelo menos 9 pt no tamanho final,
  sem redução global que torne rótulos ilegíveis; mapas largos podem usar página paisagem.
- Toda arquitetura tem capítulo consumidor, objetivo, mecanismo, exemplo de leitura,
  legenda, fontes reais e limites. Setas diferenciam estrutura, import, evento,
  transferência de dado e sequência curada; sequência não é chamada automática.
- O mapa completo estático é extraído do snapshot Git 759d253, preservando cada módulo
  Python classificado e cada par de importação declarado, inclusive módulos isolados.
  SVG/DOT/Mermaid integrais acompanham a visão por camadas legível no livro. Nada
  desse inventário é apresentado como traço de execução ou prontidão operacional.
- Artefatos curados e gráficos estáticos ficam separados, com correspondência explícita.
  As oito camadas editoriais e as camadas de pastas são taxonomias distintas.
- Editar fontes e geradores autoritativos, regenerar saídas; preservar o editor aberto.
- Não retirar hipóteses, provas, citações e correções de R910; revalidar custódia Lean.

## Aceitação

SDD/TDD: teste RED do atlas ausente e mutações que removam vistas, referências e arestas.
Validação de inventário, símbolos e hashes; revisão independente assistida por IA.
As figuras novas devem estar efetivamente no PDF, não apenas em links/JSON externos.
Compilar main.tex existente, verificar coordenadas e limites de figuras em todas as
páginas e inspecionar visualmente todas as novas pranchas em amostras legíveis.
Rodar gates editoriais R617–R620/R814/R901/R907/R908/R910/R911 aplicáveis, reexecutar
Lean após congelar fontes e registrar R911 sem alegação de validação externa.
Publicar fontes e evidências na branch autorizada, preservando alterações alheias.
