# SPEC-935-R210 — Volume Profissional: Sondagem e Rastreio (integrado ao livro)

**Status:** EM EXECUÇÃO
**Ciclo de evolução:** R210 → registro R512 (evolution registry)
**Escopo:** `livro-alfabetizacao/VolumeProfissional/` — componente integrante da
coleção Alfabetizar Bem, para uso de **psicólogo, psicopedagogo e
neuropsicopedagogo** (avaliação do aluno e orientação de professores).

## Contexto (decisões do autor)

- O material de rastreio **pertence à versão profissional** e deve estar
  **integrado ao livro** (não é arquivo solto).
- Desenho definido pelo autor: **uma Sondagem Inicial minuciosa e completa,
  aplicada antes da primeira atividade**; as demais fichas seguem como
  **confirmações**, de forma **investigativa e com rastreio sistemático**.
- Uso profissional restrito: psicólogo, psicopedagogo, neuropsicopedagogo.
  O profissional avalia o aluno e orienta os professores.

## Fundamentos éticos e legais (invioláveis)

- Nenhuma ficha gera diagnóstico. Diagnóstico é ato privativo de psicólogo
  (Lei 4.119/1962; Resolução CFP 009/2018), psiquiatra, neurologista pediatrico
  e fonoaudiólogo, conforme o caso.
- Testes psicológicos validados são referidos **por nome** (SATEPSI/CFP) e
  **não reproduzidos**; aplicação somente por psicólogo.
- Nenhum instrumento protegido por direitos autorais é copiado; as fichas são
  **autorais**, baseadas em sinais de alerta da literatura, com limites de
  validade explícitos (rastreio ≠ teste normatizado).
- A criança nunca vê os instrumentos; resultados são sigilosos e servem ao
  planejamento pedagógico e encaminhamento.
- Público-alvo: 6–10 anos (ajustável), conforme decisão do autor.

## Entregáveis

1. `VolumeProfissional/main.tex` gerado por script reproduzível
   (`gerar_rastreio.py`);
2. **Parte A — Sondagem Inicial Minuciosa e Completa** (antes da 1ª atividade):
   11 domínios × 10 itens (escala 0-1-2; campo observação) + instruções de
   aplicação e leitura (prioridade de investigação, nunca diagnóstico);
3. **Parte B — 30 fichas de Rastreio Sistemático e Investigativo** (confirmação):
   para cada condição/desvio: sinais de alerta (itens sim/às vezes/não), como
   investigar (tarefas sistemáticas), exclusões/confundidores, instrumentos
   validados para confirmação (referência), encaminhamento, adaptações
   pedagógicas iniciais, bibliografia;
4. **Parte C — Folha de síntese** e fluxo de encaminhamento;
5. PDF `Volume_Profissional_Sondagem_Rastreio_v1.0.pdf` entregue em Downloads.

## Lista das 30 fichas (Parte B)

1 Dislexia | 2 Disortografia | 3 Disgrafia | 4 Discalculia | 5 TDAH-desatento
| 6 TDAH-hiperativo/impulsivo | 7 TEA nível 1 | 8 TEA nível 2/3 | 9 TOD
| 10 Transtorno de conduta | 11 Ansiedade de separação | 12 Ansiedade
generalizada | 13 Fobia/ansiedade escolar e social | 14 Depressão infantil
| 15 TOC | 16 Mutismo seletivo | 17 TPAC | 18 TDL | 19 Desvio fonológico
| 20 Gagueira | 21 Apraxia de fala infantil | 22 TDC/dispraxia | 23 Tiques e
Tourette | 24 Ausências (sinais — encaminhamento médico) | 25 DI leve
| 26 Altas habilidades/superdotação | 27 TANV | 28 Deficiência auditiva
(sinais) | 29 Baixa visão (sinais) | 30 TCS (comunicação social pragmática).

## Critérios de aceitação (gate SDD)

- [x] AC1: `gerar_rastreio.py` reproduzível gera `main.tex` com: sondagem
      inicial (11 domínios × 10 itens) + 30 fichas de rastreio + síntese
      (+ folha de perfil do aluno).
- [x] AC2: compilação `xelatex` 2× → exit 0; 0 "Missing character";
      0 erros; 23 overfull (21 de 5–15pt, 2 de 15–40pt — aceitos/documentados);
      74 páginas.
- [x] AC3: aviso de uso restrito + aviso legal presente na capa e nas fichas
      (macro `\avisolegal`; 33 ocorrências de "não diagnostica" no PDF).
- [x] AC4: instrumentos de terceiros citados apenas por referência
      (56 menções a SATEPSI/TDE-II/ADOS/WISC etc. — sem reprodução de itens).
- [x] AC5: PDF `Volume_Profissional_Sondagem_Rastreio_v1.0.pdf` entregue em
      Downloads/Alfabetizar_Bem (74 páginas).
- [x] AC6: ciclo R512 registrado no EvolutionRegistry (325 ciclos totais).

## Restrições

- Sem reprodução de testes/marcas (SATEPSI, WISC, TDE, ADOS etc. como
  referência apenas).
- Sem pontuação diagnóstica nas fichas do material do aluno (separação
  mantida: instrumentos ficam neste volume profissional).
- Uso exclusivo de fontes livres/irrestritas dos livros (sem SchoolScriptDashed).