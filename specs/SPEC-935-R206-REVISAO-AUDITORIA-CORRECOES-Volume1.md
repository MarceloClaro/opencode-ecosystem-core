# SPEC-935-R206 — Revisão Auditoria e Correções do Volume 1 (v4.8 → v4.9)

**Status:** CONCLUÍDO
**Rótulo:** R206
**Data:** 12 de setembro de 2026
**Origem:** Auditoria completa do Volume 1 (parecer entregue antes da execução) +
aprovação explícita do usuário (inclui item da cedilha Ç e incorporação pontual
do princípio freiriano da palavra geradora).

## Objetivo

Corrigir os achados críticos e menores da auditoria do Volume 1 do livro
"Alfabetizar Bem" (método híbrido Fônico-Kumon + Técnica da Boquinha), sem
alterar a arquitetura das 7 partes nem a sequência didática já validada pelos
ciclos R203-R205.

## Mudanças

### parte2-sequencia-didatica.tex
1. **C1 — Ditongos nasais (Lições 27-29):**
   - Títulos corrigidos: `AON` → `\~AO`, `AOE` → `\~AE`, `OIE` → `\~OE`.
   - Palavras sem til corrigidas para a grafia oficial: mão, não, pão, tão, são,
     coração, mamão / mãe, pães, cães, mães, mamãe / põe, limões, aviões, balões.
   - Palavras inventadas removidas (NAE, MOE, NOE) e falsos nasais corrigidos
     (POEIRA, COENTRO, PEDAL, McDonald removidos do contexto de ditongo nasal).
   - Regras reescritas com grafia correta: ÃO (escrito ÃO no fim de palavras e
     AM no fim de verbos); ÃE; ÕE.
   - Exercícios de lacuna ajustados para a forma canônica (n+ão, m+ãe, p+ões).
   - Dicas do professor reescritas com pares mínimos válidos (MÃO × MAU, MÃE × MAU,
     PÕE × POEIRA) e acentuação corrigida.
   - Itens de múltipla escolha: removida a opção "diphthong" (não pertinente).
2. **C2 — Regras dos ditongos** (coberto acima, com evidência fonográfica).
3. **C4 — Lição 24:** título renomeado para `Consonantes do Bloco 2 --- F, G, J, K,
   N, P, V, Z, W, Y` (antes omitia K, W, Y).
4. **M1 + item cedilha — Lição 22 (Letra C):**
   - Título: `A Letra C (Aberto: CA, CO, CU)` → `A Letra C (dois sons: K e S) e a
     Cedilha`.
   - Terceira entrada no quadro de sons da C: **Cedilha (Ç) = som de S antes de
     A, O, U**.
   - Nova plancheta `Cedilha --- o C com Rabinho` com: palavra geradora MAÇÃ,
     atividade de discriminação (tem/não tem Ç, som de S), recombinação
     silábica (CA+ÇA=CAÇA; MA+ÇÃ=MAÇÃ; A+ÇÚ+CAR=AÇÚCAR; PA+ÇO+CA=PAÇOCA) e
     regra explícita (Ç só antes de A, O, U; CE/CI usam o próprio C).
   - Caixa de pista da C corrigida (estava parcial: só caía no som K).
   - Família silábica da C: adicionadas palavras com Ç (caçada, caçador, maçã,
     açúcar, paçoca); typo `cac'a` (cacá) eliminado.
5. **M2 — Lição 30 (X):** pista articulatória inicial cita os quatro sons
   (ch, ks, s, z) em vez de apenas dois.
6. **M3 — Acentuação dos verbos:** `esta` → `est\'a` quando verbo (L20 frases e
   predicado; L6 e L12 dicas; L1 exercício) — pronomes demonstrativos mantidos.
7. **Palavra geradora (freiriana):** destaque `Palavra geradora do bloco` nas
   Lições 27 (MÃO), 28 (MÃE) e 29 (PÕE), e MAÇÃ na Lição 22/Cedilha.

### parte1-fundamentacao.tex
8. **C3 — Mapa de Micro-Passos reescrito** para refletir a execução real da
   parte2 (sílabas CV e frases curtas com M,S,T,R,L antes de B..Y; X, Q, H após
   os ditongos nasais; menção à cedilha no passo C).
9. **Nova subseção `Palavra Geradora (inspiração em Paulo Freire)`** na
   Fundamentação: reconhece a contribuição freiriana (palavra geradora, leitura
   de mundo, recombinação silábica) como camada de sentido sobre o método
   híbrido — sem reivindicar o método Freire integral (honestidade autoral).

### parte3-kumon.tex
10. **Nova subseção `Recombinação Silábica (Descoberta de Novas Palavras)`** no
    Guia de Progressão do Professor.
11. Comentário editorial nas folhas B-07/B-08: são revisão de letras com lição
    própria na parte2 (não ensino de letras novas).

### main.tex
12. Versão `4.8` → `4.9 --- Setembro de 2026` (2 ocorrências).

## Critérios de aceitação (gate SDD)

- [x] Nenhuma palavra inventada (NAE/MOE/NOE) permanece nas Lições 27-29.
- [x] Todas as palavras com ditongo nasal têm til na fonte LaTeX (`\~A`, `\~a`, `\~O`, `\~o`, `\~E`, `\~e`).
- [x] O título das 3 lições de ditongo mostra ÃO/ÃE/ÕE.
- [x] A cedilha tem ensino explícito na Lição 22: regra + som + recombinação + palavra geradora.
- [x] O título da Lição 24 lista as 10 letras do bloco 2.
- [x] Mapa de Micro-Passos descreve a sequência real (B..Y após sílabas/frases; X/Q/H após ditongos).
- [x] Seção freiriana presente na parte1 com linguagem honesta (não afirma ser "método Freire").
- [x] Compilação: 2× `pdflatex -interaction=nonstopmode`, exit 0, zero "Missing character".
- [x] Número de overfulls não aumenta além da linha de base (~43, estéticos).
- [x] `pdftotext` confirma a renderização correta (mão, mãe, põe, cedilha, título L24, v4.9).
- [x] Registro do ciclo no EvolutionRegistry (R508).

## Verificação (evidência)

- Logs de compilação sem erros; contagem de páginas do PDF final.
- Greps de verificação pós-patch (títulos, palavras, eliminação de NAE/MOE/NOE).
- `pdftotext` do PDF v4.9.

## Registro de evolução

- Ciclo R508, score a definir após verificação; lessons: (1) revisão exige ler o
  *arquivo de verdade* antes de apontar falhas (linhas mudam entre ciclos);
  (2) acentuação em maiúsculas e palavras inventadas são erros silenciosos na
  impressão — precisam de grep sistemático; (3) cedilha é lacuna clássica de
  método fônico e precisa de ensino explícito; (4) incorporação freiriana deve
  ser pontual e honesta (palavra geradora como sentido, não substituição do
  método).