# evo-55 — R424: Autoria com ORCID no manuscrito

## Objetivo

Adicionar a autoria do manuscrito — **Marcelo Claro Laranjeira**,
ORCID https://orcid.org/0000-0001-8996-2887 — no cabeçalho do artigo
(MD, TeX, PDF e DOCX) e na carta ao editor.

## Mudanças

1. **MD canônico**: linha "**Autor:** Marcelo Claro Laranjeira — ORCID:
   https://orcid.org/0000-0001-8996-2887" após o título trilíngue.
2. **TeX**: "\noindent\textbf{Autor:} Marcelo Claro Laranjeira --- ORCID:
   \href{...}{https://orcid.org/0000-0001-8996-2887}" com hyperlink.
3. **CARTA_AO_EDITOR.md**: autor + ORCID no cabeçalho e na assinatura;
   autoria no singular; correção do overclaim "validações ... e por tempo"
   → "e a análises de subperíodos" (paridade com R422/ID6 do manuscrito).
4. **Artefatos**: PDF recompilado (20 páginas, 0 Overfull/Underfull) e
   DOCX regenerado (16 tabelas).
5. **Testes**: 3 novos — R410 (autor/ORCID no MD e na carta) e R411
   (autor/ORCID no TeX).

## Verificação

- Suíte R408–R424: **369 testes passed**.
- LaTeX: 20 páginas, 0 Overfull, 0 Underfull; DOCX regenerado.
- Doctor: 10/12 pass, 0 failed (warns pré-existentes).

## Lições

- A autoria deve estar no cabeçalho trilíngue (padrão RBEP) e na carta ao
  editor, que é o documento de submissão — a assinatura institucional
  genérica foi substituída pelo autor nomeado com ORCID.
- A carta ao editor continha o mesmo overclaim "por tempo" corrigido no
  manuscrito em R422 — documentos de submissão compartilham as regras de
  anti-overclaim do manuscrito.
