# SPEC-935-R901 — Atualização integral do livro Core

Status: entregue com verificação local; ver manifesto R907.

## Solicitação e escopo

Atualizar minuciosamente o livro técnico e científico `livro-core`, preservando
as fontes editáveis e produzindo um PDF compilado e conferido visualmente.
Reconciliar fundamentos, instalação, arquitetura, orquestração, memória,
SDD/TDD, raciocínio, pesquisa, integrações, agentes, infraestrutura, catálogo,
ativação e material de reprodução com o código e os recibos desta edição.

## Contrato editorial

1. Usar português brasileiro formal e explicações didáticas, com entrada,
   mecanismo, saída, exemplo verificável e limites nos novos percursos.
2. Identificar o snapshot de código; distinguir inventário estático, contrato,
   teste executado, autenticação, inferência, entrega aceita e validação externa.
3. Contagens correntes provêm da configuração e dos geradores; números históricos
   permanecem apenas quando explicitamente datados ou usados em exemplos hipotéticos.
4. Cobrir R886–R897: metacognição, memória persistente, contexto de código,
   proveniência científica, ciclo de vida de perfis, plugins, Wolfram, grafo Python
   e CI local independente. Explicar as operações nativas bloqueadas, o timeout
   observado no grafo atual e os limites do ZIP REA fornecido.
5. Manter o catálogo gerado a partir do conjunto de agentes configurados, sem
   copiar alegações promocionais das descrições como resultados comprovados.
6. Modificar os geradores como fontes autoritativas dos capítulos gerados.
7. Citações novas precisam de fonte primária pertinente; documentação local
   sustenta apenas fatos do Core. Não inventar DOI, execução ou mérito científico.
8. Equilibrar compreensão inicial, mecanismo técnico e práxis: usar os livros
   técnicos legíveis de `biblioteca ai/` como modelos editoriais de progressão,
   sem transpor seu conteúdo ou suas conclusões para o Core.
9. Conservar uma sequência lógica coesa e coerente. Um caso condutor liga
   problema, arquitetura, delegação, memória, aceite, raciocínio, pesquisa e
   reprodução; cada parte produz uma saída que prepara a seguinte.
10. Práticas guiadas incluem objetivo, entrada, ação, conferência observável,
    tratamento de falha e reflexão. A presença desses campos é estrutura
    editorial, sem alegação de eficácia pedagógica medida.

## Critérios de aceitação

- O catálogo e os macros reconciliam com os agentes/MCPs/comandos configurados.
- O livro contém explicações dos novos contratos, seus percursos e limites.
- O recibo dos 1.130 testes identifica a execução e o snapshot `f930e19`, sem
  transferir esse aceite ao mérito científico ou a uma revisão externa.
- `check.py` e os gates editoriais R617–R620 e R901 aplicáveis passam.
- `latexmk` gera o PDF sem erro fatal; referências não resolvidas e estouros
  materiais de página são corrigidos.
- Páginas representativas das partes alteradas são renderizadas e inspecionadas.
- Um manifesto conserva fontes, hashes, comandos, resultados e limitações;
  o ciclo de evolução registra a entrega sem alegação de auditoria externa.

## Verificação

`tests/test_r901_livro_atualizacao_integral.py`; gates editoriais existentes;
compilação LaTeX e análise de log; extração de texto; inspeção de imagens do PDF.

## Fora de escopo

Alterar o runtime do Core para fazê-lo coincidir com a narrativa; publicar
artigos ou resultados científicos; modificar documentos de outros trabalhos;
elevar confiança, classificação editorial ou disponibilidade dos provedores.
