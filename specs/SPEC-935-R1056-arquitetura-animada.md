# SPEC-935-R1056 — Documentação e arquitetura animada

## Estado e objetivo

Em execução. Atualizar README/documentação com o piloto R1055 já commitado
(`c800112d`) e oferecer GIFs das vistas Mermaid publicadas, sem converter
diagramas em alegações de execução real. Commit local autorizado; sem push.

## Escopo

- Documentos Markdown rastreados na raiz e em `docs/`, exceto artefatos gerados
  desta rodada. Inventário inicial: 45 blocos Mermaid em 14 documentos.
- Todos os 22 fluxos de `docs/architecture/flows.json`; deduplicação por SHA-256
  do Mermaid. Mesma fonte em vários documentos reutiliza a mesma animação.
- Visão geral de arquitetura e pipeline R1055; fontes Mermaid preservadas.
- Grafo integral permanece original; GIF complementar agregado por camadas,
  explicitamente rotulado como síntese, não substituto dos 707 módulos.
- Não regenerar o inventário histórico R916 como se fosse uma nova auditoria.
- Não alterar conteúdo dos vídeos nem instalar dependências de terceiros.

## Contrato visual

Fundo sóbrio, texto contrastante, câmera suave quando necessário, destaque
sequencial para leitura de arestas já existentes. Primeiro e último quadros
estáveis. Animação é guia de leitura, nunca telemetria ou ordem comprovada de
execução. GIF executa um ciclo, sem loop infinito. PNG/SVG estáticos e fonte
sempre acessíveis; galeria com GIFs sob demanda para evitar sobrecarga.

## Aceites verificáveis

1. Inventário identifica todos os blocos do escopo, seus títulos e fontes; a
   cobertura de todos os 22 fluxos é testada e nenhuma fonte é truncada.
2. GIFs multiframe decodificáveis, dimensões limitadas, duração documentada,
   tamanho <= 3 MB por GIF, orçamento agregado <= 60 MB. SHA-256 de fontes,
   renderizador e saídas em manifesto. Sem links externos de render.
3. Exportação usa Mermaid instalado, modo estrito, sem callbacks/cliques,
   fontes locais, e rejeita diretivas/URLs executáveis. Caminhos confinados;
   falhas não viram arquivos falsamente aprovados.
4. `--check` não escreve nem renderiza: detecta ausência, fonte alterada,
   mídia corrompida, hash divergente ou lacuna de cobertura.
5. README, índice, arquitetura, manual e PROGRESS ligam para galeria e R1055;
   relatos deixam claro que MP4 é local, QC não aprova estética/ciência.
6. Sincronizador R881 conserva Mermaid e âncoras originais e inclui GIF/PNG
   quando manifestados, de forma idempotente. Inventários históricos intactos.
7. RED observado antes da implementação, GREEN e regressões pertinentes;
   inspeção visual de amostra de GIFs; commit apenas do escopo desta rodada.

## Plano

1. Diagnóstico/memória/inventário e spec (esta etapa).
2. Testes RED de descoberta, confinamento, cobertura e verificação de mídia.
3. Exportador local e visualização reutilizável com manifesto e galeria.
4. Atualização documental R1055 e links dos fluxos.
5. GREEN, regressão, inspeção, revisão independente e reflexão registrada.
6. Commit local com evidências e limites; sem publicação externa.

## Limites

Histórico R1055 tem testes estáticos, não prova retrospectiva de TDD nem
aprovação perceptual. Consultas ao ecossistema nesta rodada retornaram
workflow `r1056-architecture-gif-review` bloqueado por `spec_id_required`;
nenhuma análise externa foi concluída por esse workflow. Não contornar gates
nem atribuir aprovação a agentes que não executaram.
