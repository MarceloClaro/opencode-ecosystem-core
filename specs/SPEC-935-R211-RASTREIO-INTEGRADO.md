# SPEC-935-R211 — Caderno de Atividades + Rastreio Integrado Sequenciado

## Contexto

A coleção Alfabetizar Bem possui volumes didáticos (1–5), Caderno Motor e o
Volume Profissional de Sondagem e Rastreio (uso restrito). Até aqui, o rastreio
existia apenas como volume separado. Esta spec define a **integração sistêmica**:
pontos de **rastreio sequenciado (checkpoints)** intercalados **entre as unidades**
dos volumes, conectando cada unidade a um domínio da Sondagem (Parte A) e às
fichas de confirmação (Parte B) do Volume Profissional.

Objetivo: gerar **volumes completos de ações e desenvolvimento proposto** com
progressão lógica e coesa — o aluno faz a atividade, o professor observa e
registra, e, em caso de sinais, o profissional habilitado aplica a ficha VP.

## Princípios

1. **Nunca diagnostica**: o checkpoint é observação pedagógica sequenciada.
2. **Entre as atividades**: aplica-se ao fim de unidades estratégicas, antes de
   avançar, seguindo a Rota 1A–1D se houver sinais.
3. **Coeso**: cada checkpoint declara domínio da sondagem + ficha VP + encaminhamento.
4. **Sistêmico**: gerador programático (rastreio_integrado.py) capaz de inserir
   checkpoints em todos os volumes a partir de um mapeamento estruturado.
5. **Reproduzível**: geração idempotente (rodar 2x não duplica) e testável.

## Critérios de aceitação

- AC1: Classe `alfabetizar.cls` expõe o ambiente `rastreio` e o comando
      `\checkpoint{...}` com Passo 1 (autoavaliação SIM/NÃO), Passo 2 (observação
      S/F/R/N) e Passo 3 (regra de encaminhamento).
- AC2: `rastreio_integrado.py` gera `VolumeN/checkpoints/rastreio-u*.tex` com
      LaTeX válido para cada entrada do mapeamento (Volume 1: 6 checkpoints).
- AC3: Injeção idempotente dos `\input{checkpoints/...}` nas âncoras entre
      unidades do Volume 1 (após U1, U2, U3, U5, U7, U10).
- AC4: Testes (pytest) verificam geração, contagem de itens, idempotência e
      presença de aviso "não diagnostica".
- AC5: Volume 1 recompila (XeLaTeX 2×) com 0 erros e entrega
      `Volume_1_1ano_v5.2.pdf`.
- AC6: EvolutionRegistry registra R518 (correção Unidade 10) e R519 (rastreio
      integrado).

## Mapeamento inicial (Volume 1)

| CP | Após unidade | Domínio (Parte A) | Ficha VP |
|----|--------------|-------------------|----------|
| u1 | Unidade 1 (Vogais) | Consciência Fonológica; Linguagem Oral | Ficha 19 (Desvio Fonológico); 18 (TDL) |
| u2 | Unidade 2 (Consoantes Bloco 1) | Leitura; Escrita/Ortografia | Ficha 1 (Dislexia); 3 (Disgrafia) |
| u3 | Unidade 3 (Sílabas Diretas) | Leitura; Consciência Fonológica | Ficha 1 (Dislexia) |
| u4 | Unidade 5 (Consoantes Bloco 2) | Escrita/Ortografia | Ficha 2 (Disortografia); 1 (Dislexia) |
| u5 | Unidade 7 (Ditongos Nasais) | Processamento Auditivo; Consciência Fonológica | Ficha 17 (TPAC); 6 (TDAH H/I) |
| u6 | Unidade 10 (Ditongos ÃE/ÕE) | Leitura; Fluência | Ficha 1 (Dislexia); 25 (sinais DI leve) |

## Estrutura gerada

```
VolumeN/
  checkpoints/
    rastreio-u1.tex .. rastreio-uN.tex   (gerado)
  parte2-sequencia-didatica.tex          (injeção de \input entre unidades)
livro-alfabetizacao/rastreio_integrado.py (gerador)
livro-alfabetizacao/tests/test_rastreio_integrado.py
```