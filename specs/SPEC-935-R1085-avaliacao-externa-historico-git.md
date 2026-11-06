# SPEC-935-R1085 — Parecer externo e saneamento do histórico local

**Pedido autorizado (2026-11-06):** avaliar três repositórios para o Core/áudio;
depois reescrever commits e atualizar o repositório remoto. Esta autorização
não inclui instalar terceiros, executar síntese, publicar o livro ou substituir
histórico já compartilhado.

## Aceitação

1. `reports/r1085/parecer-repositorios.md` contém fonte e revisão de cada um
   dos três projetos, licença do código separada da licença do modelo/serviço,
   ganhos, sobreposição com o Core, riscos e decisão de piloto. Sem declarar
   melhora de áudio sem comparação humana executada. A edição canônica e as
   variantes de Molambudos permanecem inalteradas.
2. A reescrita se limita ao trecho **local** após o commit de `origin/codex/core-prontidao-rea`
   observado como `0e501aedf56e9b085f7bf650002983ca7d522a0b`. Confirmação
   ao vivo via `git ls-remote` antes do push; se houver divergência, abortar.
   O commit remoto, `origin/main` e a tag `v1.1.0` não são reescritos.
3. Os dois resíduos de build adicionados por `aba3fae1` e removidos depois por
   `4c96ac4a` nunca aparecem no histórico **novo** da branch publicado após o
   ancestral remoto: `literatura/livros/ia-odontologia/template/main.xdv` e
   `literatura/molambudos/Molambudos_VictoriaRegia/tri/main_kdp_print_160x230mm.synctex(busy)`.
   Fazer backup local apontando para o HEAD antigo ANTES da reescrita. O backup
   não é remoto nem indicação de publicação.
4. Preservar bytes de `literatura/` no HEAD final; não remover espaços com
   significado de quebra em Markdown nem alterar LaTeX, narrativa, imagens ou
   capas. Registrar avisos de whitespace remanescentes, sem dizer que foram
   saneados. Não usar `--force`/`--force-with-lease`.
5. RED: testes para fonte/limites do parecer e para ausência dos dois resíduos
   no histórico local falham previamente. GREEN: testes focados e regressões
   R1084 passam, `doctor` e `git diff --check` dos novos commits passam; hash
   de árvore literária antigo e novo coincide. Conferir remoto por SHA após
   `git push origin HEAD:refs/heads/codex/core-prontidao-rea` (fast-forward).

## Paradas e limites

- Se algum ref remoto passou a conter o trecho reescrito, se a branch mudou
  inesperadamente, se o backup faltar, se a árvore literária divergir ou se
  aparecer conflito não resolvido com segurança, não fazer push.
- Escopo público: somente branch `codex/core-prontidao-rea`; `main` permanece
  como está, salvo autorização específica. Não criar tag para o novo HEAD.
- Testes e `doctor` aferem contratos locais; não comprovam qualidade de voz,
  segurança integral de todos os arquivos nem aceitação editorial/KDP.

## Evidência local antes da atualização remota

- RED: `tests/test_r1085_avaliacao_historico.py` falhou 2/2 antes do parecer;
  depois do parecer falhou apenas a busca dos dois resíduos no intervalo.
- GREEN após rebase local: 79 testes focados incluindo R1084/R864/R822/R1085,
  `doctor` 22/22 e reconciliador `--check` sem drift.
- `literatura/` no HEAD anterior `595ecb1a` e no novo HEAD `c3c9c15c`:
  mesma árvore Git `f88b81418b8f750e5dec89ad8babe3d8d0799f95`. Os dois
  resíduos não aparecem em `git log 0e501aed..HEAD -- <path>`.
- **Não resolvidos:** o commit literário reescrito `0a0694fd` ainda tem 919
  avisos de whitespace de origens diversas, inclusive espaços de Markdown.
  Não atribuir limpeza desses avisos à reescrita; não modificar texto literário
  automaticamente. Esta evidência não prova ausência de segredos em todo o Git.
