# SPEC-935-R1087 — Hero SVG do README na `main`

**Escopo:** revisar `docs/images/readme-hero.svg` exibido pelo README da branch
`main`, sem misturar commits de desenvolvimento de outras branches. Base remota
observada em 2026-11-06: `e51a4f668f2f1aa6f481307e2429117643af91cb`.

## Critérios de aceitação

1. Hero vetorial autocontido em português: mensagem fiel à evidência antes da
   narrativa, contrato/teste/revisão humana; sem prometer que ferramentas nunca
   inventam dados, aprovam artigos ou substituem decisão humana.
2. Sem números fixos de agentes, MCPs, testes ou `doctor`: as contagens do
   README são geradas fora do SVG e podem mudar independentemente dele.
3. SVG válido com `viewBox`, `<title>` e `<desc>` não vazios associados a
   `aria-labelledby`; nenhum script, `foreignObject`, fonte, imagem ou URL
   externos. Evitar animação para não prejudicar pessoas com sensibilidade a
   movimento e para compatibilidade com README/GitHub. O `alt` do `<img>` no
   README comunica a mesma mensagem ao leitor quando o SVG é incorporado.
4. Diagrama/escrita legíveis em renderizações de 1200 e 600 px; sem recorte ou
   sobreposição perceptível; contraste suficiente no fundo escuro. Salvar
   previews em `/tmp/opencode` (não versionar raster sem solicitação).
5. RED: testes novos falham no SVG atual por metadados, números estáticos e
   afirmações indevidas; GREEN: testes novos e testes de README relevantes,
   XML parse, renderização `rsvg-convert` e `git diff --check` passam.
6. Publicação só por push fast-forward de commit focado para `main`, após
   comparar o SHA remoto ao ancestral. Se a `main` avançar, parar e reavaliar.

## Limites

- Esta é revisão técnica/visual de um banner, não teste de resultado científico,
  experiência em todos os clientes, nem parecer artístico externo.
- O `doctor` do worktree em `/tmp/opencode` pode avisar sobre CLIs/Colibri
  ausentes porque binários locais não acompanham o checkout; essas dependências
  não são requisito para editar SVG. Não apresentar o diagnóstico como 22/22
  se houver avisos nesta localização.

## Evidência de execução local (antes do push)

- RED: 3 dos 4 testes novos falharam com SVG inicial (metadados de acesso,
  números fixos e tipografia de 12 px). Dois novos casos falharam em seguida
  para texto que saía do painel e `alt` desatualizado no README.
- GREEN: 91 testes focados passaram, incluindo documentação e política R1084;
  o teste legado R822 precisou do `.venv` local do operador, vinculado
  temporariamente ao worktree e não versionado. Reconciliador `--check` limpo.
- `rsvg-convert` gerou previews 1200×420 e 600×210; inspeção visual detectou
  e corrigiu o texto que atravessava a borda do painel. Prévia em
  `/tmp/opencode/readme-hero-r1087-{desktop,narrow}.png`, fora do índice.
- `doctor` no worktree: **21/22**, com aviso exclusivo de runtime Colibri
  não disponível nesta localização. Não equivale a validação artística.
