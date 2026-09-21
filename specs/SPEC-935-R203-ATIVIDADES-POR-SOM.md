# SPEC-935-R203 — Atividades de Cada Som (parte7, Volume 1)

**Status:** CONCLUÍDO
**Data:** 2026-09-12
**Autor:** marceloclaro (orquestrador primário)
**Gatilho do usuário:** "faltou atividades de cada sons diferente das letras e silabas"

## Problema

O Volume 1 tem atividades por **letra** (lições 1–32, missões) e por **sílaba** (folhas
Kumon FA–FU etc.), e tabelas informativas "Sons da Letra (IPA)", mas **nenhuma atividade
de treino por SOM (fonema)**: discriminação auditiva, classificação de palavras que contêm
(ou não) o som e contraste entre sons próximos (pares mínimos).

## Escopo

Criar `parte7-sons-atividades.tex`, módulo didático distinto:

1. **Guia de uso** para professor/família (audição antes de escrita; repetir devagar;
   variantes regionais aceitas; não é avaliação clínica; apoio à mão na garganta/nariz
   como recurso opcional).
2. **Quadro-síntese** dos son consistentes com as tabelas IPA existentes (TIPA): vogais
   orais/nasais, semivogais, consoantes, africadas regionais, nasalização de M/N final, H mudo,
   com grafias que produzem cada som.
3. **38 planchetas reproduzíveis** — uma por som — com estrutura fixa:
   A) Caça ao som (marcar palavras que têm o som); B) Separe (colunas tem/não tem);
   C) Complete (lacuna da grafia, com palavra para conferência); D) Ouça e compare
   (contrastes/pares mínimos quando existentes); caixa de pausa e pista articulatória.
4. Cada som referencia as habilidades BNCC de consciência fonológica (EF01LP03, EF01LP05,
   EF01LP07, EF01LP08, EF01LP09).

## Critérios de aceitação

- CA-01: `parte7-sons-atividades.tex` gerado por script (reproduzível) e incluído no main.tex.
- CA-02: ≥35 planchetas "Atividade de Som" presentes; cada uma com A/B/C/D e caixas pausa+pista.
- CA-03: inventário de sons consistente com as 62 linhas `\somipa` existentes (mapeamento
  manual verificado contra as tabelas da parte2).
- CA-04: palavras usadas existentes e corriqueiras do 1º ano; variações regionais marcadas
  com nota (R/T antes de I; R forte; L final vocalizado); nenhuma promessa clínica.
- CA-05: `pdflatex -interaction=nonstopmode` 2× → exit 0, 0 "Missing character".
- CA-06: versão 4.6 (capa, créditos, main.tex); PDF entregue; ciclo R505 registrado.

## Não-objetivo

- Não substitui fonoaudiólogo; atividades são observacionais e lúdicas.
- Não adiciona testes psicométricos nem cutoffs (mesma regra da parte6).
- Não reproduz a marca Boquinha®.