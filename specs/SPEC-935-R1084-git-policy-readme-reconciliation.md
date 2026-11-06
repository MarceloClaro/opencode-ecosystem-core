# SPEC-935-R1084 — Política Git segura e README reconciliado

**Escopo (2026-11-06):** corrigir a exposição criada pela regra ampla `!literatura/**`,
remover dois resíduos de build rastreados, eliminar contagens contraditórias do README
e registrar com precisão o que um clone contém. A edição canônica do romance, as
fontes artísticas e os binários locais não serão modificados.

## Contrato e aceitação

1. A política de `literatura/` é **deny-by-default**: só fontes/documentos de
   extensões escolhidas e duas capas PDF explícitas, além dos PNGs da capa
   selecionada, ficam candidatos ao Git. `.env`, `.key`, `.pem`, `Zone.Identifier`,
   backups e artefatos de compilação permanecem ignorados, inclusive em pastas
   profundas. O repositório Git embutido e symlinks para `projetos/` continuam
   fora; `README.md`, fontes LaTeX e capas escolhidas continuam rastreáveis.
2. `main.xdv` e `main_kdp_print_160x230mm.synctex(busy)` saem **apenas do índice**,
   sem apagar os arquivos locais. Não versionar outros binários não inventariados.
3. O reconciliador cobre os badges de agentes, MCPs e checks do README, além
   dos blocos já existentes; sincronizar duas vezes não muda bytes e `--check`
   detecta drift sem escrever. Não atualizar números históricos como se fossem
   resultados presentes.
4. README principal e README do Molambudos revisados quanto a abertura, Book
   Studio, limites de arte, versão Git e links de entrada; o guia de reprodução
   vinculado deve refletir a allowlist: distinguir edição canônica de 435 pp, prova
   print-safe de 422 pp e capa provisória denominada 436 pp. Declarar ausência
   dos PDFs de miolo/EPUB/áudio de um clone, e não prometer publicação, nota,
   impressão certificada ou equivalência de 9.552 testes coletados com passados.
5. Retirar as isenções genéricas de whitespace de `.gitattributes`; preservar
   `*.sh text eol=lf`. Verificar `git diff --cached --check` no commit novo.
   Os avisos de commits **históricos** não podem ser apagados por commit aditivo:
   reescrever histórico/force-push fica fora do escopo.
6. RED: testes da política, de badges dinâmicos e da documentação falham no
   checkout anterior; GREEN: testes focais, regressão R822, reconciliador
   `--check` e `doctor` passam; diffs e commit final são conferidos.

## Limites

- Sem push, upload KDP, Git LFS ou inclusão automática de dados confidenciais.
- Não corrigir texto, ilustrações, capas ou paginação editorial nesta rodada.
- A checagem de padrões de segredo é heurística e não equivale a auditoria
  jurídica/de segurança de todos os arquivos já publicados no histórico.

## Evidências locais (alcance restrito)

- RED: `tests/test_r1084_git_policy_readme.py` falhou com 12 casos no baseline:
  segredos e builds reautorizados, arquivo de build rastreado, badges divergentes,
  variantes ausentes no README e gate de whitespace suprimido. Teste do guia
  vinculado também falhou antes da sua atualização.
- GREEN: 165 testes focados nas specs R822/R864/R886/R894/R1050/R1078/R1080–R1084
  passaram; `reconcile_operational_docs.py --check` sem drift e `doctor` 22/22.
- Revisão independente delegada não obteve diff por bloqueio do executor; o
  retorno heurístico de sucesso do orquestrador externo não prova auditoria.
  Verificação do índice/diff, links e padrões é feita localmente antes do commit.
