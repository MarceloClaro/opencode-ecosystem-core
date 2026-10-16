# Atualização integral do livro Core — plano de execução R901

> Para agentes executores: aplicar o plano no contexto atual, sob o primário MarceloClaro, com os perfis registrados nos recibos R901.

**Goal:** entregar o livro atualizado do prefácio à consulta final, fluido, didático, tecnicamente delimitado e compilado.

**Architecture:** um caso condutor liga problema, arquitetura, coordenação, memória, gate, cálculo, pesquisa e reprodução. Catálogo e fichas passam para a consulta final. TeX e geradores permanecem as fontes autoritativas; a inspeção de PDF verifica a apresentação.

**Tech Stack:** LaTeX, TikZ, geradores Python, pytest, latexmk e Poppler.

**Spec:** `specs/SPEC-935-R901-livro-core-atualizacao-integral.md`.

## Restrições globais

- Português brasileiro formal, três níveis de leitura e práxis com conferência/reflexão.
- Usar a Biblioteca IA como modelo editorial; não copiar páginas nem transplantar resultados.
- Não converter inventário, nome de engine ou nota interna em execução ou validação externa.
- Preservar arquivos de outros trabalhos e manter aberto o documento do editor.
- Registrar novos perfis pelo primário antes da delegação.

## Foco da revisão

- Sequência incorreta entre publicação, CFP, seleção, atribuição e execução.
- Histórico antigo apresentado como estado corrente ou medida sem denominador.
- Citação literal sem suporte recuperado, ou literatura usada para certificar código.
- Exemplos e imagens que confundem analogia, chamada e evidência.
- Layout com figura ilegível, texto cortado, fonte pequena ou remissões abertas.

## Tarefas e critérios

- [x] Diagnosticar o ambiente e registrar os recortes de trabalho via primário.
- [x] Auditar as fontes e reproduzir o RED editorial antes das mudanças.
- [x] Examinar os livros legíveis da Biblioteca IA e registrar os limites.
- [x] Usar REA em inspeção estática confinada do shell derivado do mapa; preservar a recusa da página completa por tamanho.
- [x] Corrigir mecanismos, unidades e alegações nos capítulos e seus geradores.
- [x] Reordenar a leitura principal, acrescentar pontes específicas e práticas do caso condutor.
- [x] Reconciliar o catálogo com identidades canônicas e regenerar suas fichas.
- [x] Criar pranchas TikZ e ajustar tipografia, legendas e espaço de leitura.
- [x] Regenerar o inventário final e executar os gates editoriais integrados.
- [x] Compilar o projeto existente, corrigir erros e conferir figuras, tabelas, referências e transições renderizadas.
- [x] Registrar o ciclo, o manifesto, os hashes e os limites; publicar somente o escopo autorizado.
