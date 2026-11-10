# Notas de adaptação — submissão à *Minds and Machines*

**Data:** 10 de novembro de 2026.
**Status:** pacote editorial para revisão do autor. Não é submissão realizada.

## 1. Veículo escolhido

**Minds and Machines** (Springer) — *Journal for Artificial Intelligence, Philosophy and Cognitive Science*.

- **Tipo de artigo:** Original Research.
- **Extensão:** não há limite explícito nas diretrizes; o texto principal tem cerca de 8.000 palavras.
- **Avaliação:** duplo-cego.
- **Modelo:** híbrido — assinatura sem APC ou acesso aberto com APC.
- **Por que este veículo:** o escopo da revista é explicitamente filosófico e interdisciplinar: relação entre seres humanos e tecnologias; filosofia cognitiva; epistemologia; ética e governança da IA; status moral de agentes artificiais; implicações éticas e sociais do design, desenvolvimento e uso de tecnologias digitais. O artigo foi reestruturado para colocar o argumento conceitual em primeiro plano.
- **Vantagem sobre a *AI & Society*:** a política de IA da *Minds and Machines* exige documentação do uso de LLM, mas não contém a frase "strongly discouraged" que a *AI & Society* usa. Ainda assim, o uso deve ser declarado no método e nas declarações.

## 2. O que foi adaptado

### 2.1 Nova moldura filosófica

- **Título:** "The house that helps to think: authored cognitive prostheses, agentic AI, and the limits of epistemic sovereignty".
- **Subtítulo:** "A philosophical case study of a self-built agentic system".
- **Problema central:** quando uma pessoa projeta um sistema agêntico para compensar vulnerabilidades cognitivas, quem é o autor da cognição resultante e que tipo de artefato é esse?
- **Tese:** o Core é uma prótese cognitiva autoral; a assinatura cognitiva é uma configuração situada de escolhas documentáveis; o ideal de soberania epistêmica é necessariamente limitado pela dependência de agentes, modelos e registros.

### 2.2 Novas seções e argumentos

- **Seção 3 — O que é uma prótese cognitiva?**
  - Debate da mente estendida (Clark & Chalmers), críticas (Rupert, Sterelny, Adams & Aizawa).
  - Artefatos cognitivos (Norman), cognição distribuída (Hutchins, Hollan et al.).
  - Conta moderada da prótese: carga, transformação da tarefa e integração normativa.
  - **Taxonomia original:** próteses de armazenamento, procedurais, epistêmicas e agênticas; o Core como prótese epistêmica agêntica.
  - Por que "prótese" não é metáfora: analogia funcional, dependência, ajuste e cuidado.

- **Seção 4 — Autoria e assinatura cognitiva**
  - Distinção entre **autoria**, **agência** e **responsabilidade**.
  - Crítica da autoria composicional; Floridi & Sanders, Floridi.
  - Assinatura cognitiva com quatro critérios: documentabilidade, recorrência, contraevidência e poder explicativo.
  - Cinco marcas: memória frágil, contrato antes do impulso, verificação contra a convicção, arquitetura da interrupção e vocação didática.
  - Assinatura como **estilo de responsabilidade**, não impressão digital.
  - Risco de mito: celebração, justificação e prisão.

- **Seção 5 — Epistemologia da prótese**
  - Memória externalizada: traços vs. experiência; risco de falsa completude.
  - Verificação: TDD, SpecVerifier, gate anti-overclaim, `CORRIGENDUM`; coerência interna vs. verdade.
  - Confiança e falsa objetividade: trust scores e token economy como dispositivos de coordenação, não warrants epistêmicos.
  - Dependência epistêmica (Hardwig); distinção entre **trust** e **reliance**.
  - Humildade epistêmica como virtude institucionalizada.

- **Seção 6 — Ética do autodesign**
  - Cuidado e dependência; a prótese como "segunda doença".
  - As quatro fases do cuidado em Tronto: atenção, responsabilidade, competência e responsividade.
  - Desigualdade epistêmica (Fricker); acesso, manutenção e contestabilidade.
  - Ética da autoexperimentação: N-of-1, pré-registro, supervisão clínica.
  - Contestabilidade: a casa precisa ter portas.

- **Seção 7 — Objeções e respostas**
  1. "É apenas um sistema de gestão do conhecimento pessoal."
  2. "A tese da mente estendida é falsa; é apenas uma ferramenta."
  3. "A assinatura cognitiva não é empiricamente testável."
  4. "O autoestudo é enviesado e não sustenta teses filosóficas."
  5. "Usar IA para escrever sobre cognição co-produzida por IA é circular."

- **Seção 8 — Epistemologia N-of-1**
  - O protocolo foi encurtado e reenquadrado como resposta epistêmica: tratar a prótese como hipótese, não como crença.

### 2.3 Redução do detalhe técnico

- A arquitetura detalhada (MetaBus, Blackboard, TaskRuntime, etc.) foi movida para o material suplementar (Tabela S2).
- A tabela de contagens (S1), a tabela de vulnerabilidades (S3) e a matriz de desfechos (S4) também estão no suplemento.
- O texto principal mantém apenas uma tabela: as cinco marcas da assinatura cognitiva.

### 2.4 Referências novas

Foram acrescentadas:

- Adams & Aizawa (2001), sobre os limites da cognição.
- Hardwig (1985), sobre dependência epistêmica.
- Fricker (2007), sobre injustiça epistêmica.
- Tronto (1993), sobre ética do cuidado.
- Floridi & Sanders (2004), sobre a moralidade de agentes artificiais.
- Floridi (2013), sobre moralidade distribuída.

As referências já verificadas no artigo em português foram mantidas. As novas referências com DOI foram conferidas no Crossref.

### 2.5 Anonimização

- Nome do autor, ORCID, afiliação, e-mail e URL apenas na title page.
- Nome do sistema removido do título, abstract e corpo; o texto usa "the Core".
- Autocitações substituídas por "Core Project (2026a–f)".
- Referência ao TCC removida da versão anonimizada.
- Metadados do `.docx` do manuscrito sem autor.

## 3. O que o autor precisa fazer antes de submeter

1. **Ler e reescrever o texto em sua própria voz.** A versão em inglês é uma adaptação editorial; o autor deve revisar cada seção e assumir a autoria intelectual.
2. **Reduzir as palavras-chave de oito para seis.** A revista pede 4–6.
3. **Confirmar a declaração de uso de IA.** A *Minds and Machines* exige documentação do uso de LLM; a declaração está no método e nas declarações.
4. **Confirmar a divulgação de saúde.** O artigo trata o relato de AH/SD e risco de Alzheimer como autodeclaração, não diagnóstico.
5. **Reconciliar as contagens.** 374 entradas no `opencode.json` vs. 366 no bloco do `README.md`.
6. **Verificar o URL e a licença.** O repositório é público e o código é MIT; o texto do artigo não herda automaticamente essa licença.
7. **Decidir sobre acesso aberto.** A revista é híbrida: assinatura sem APC ou acesso aberto com APC.
8. **Preencher os campos do sistema de submissão:** dados do autor, declarações, revisores sugeridos, cover letter.
9. **Confirmar a política de preprint.** A versão em português está em repositório público; a title page e as declarações já a mencionam.
10. **Não submeter em duplicidade.** O manuscrito não pode estar em avaliação em outro veículo.

## 4. Riscos e limites

- **Não há garantia de aceite.** A revista é filosófica e seletiva; o artigo é um estudo de caso autoetnográfico, não um artigo empírico.
- **A revisão duplo-cega pode ser difícil** porque o sistema é público e o autor é o criador. A anonimização foi feita, mas o nome do sistema e o repositório podem ser reconhecíveis.
- **O autoestudo pode ser questionado.** A Seção 7 responde às objeções, mas a revisão por pares pode pedir mais distanciamento ou uma comparação com outros casos.
- **A extensão está confortável.** Cerca de 8.000 palavras no texto principal; não há limite explícito.
- **A divulgação de saúde pode suscitar questões de ética e privacidade.** O texto distingue relato, risco e diagnóstico, e não usa dados clínicos.
- **O uso de IA é declarado.** A política da *Minds and Machines* é menos restritiva que a da *AI & Society*, mas o autor deve estar preparado para explicar o processo.

## 5. Arquivos do pacote

| Arquivo | Conteúdo |
|---|---|
| `MANUSCRIPT_MINDS_MACHINES.md` | Manuscrito anonimizado em inglês |
| `TITLE_PAGE.md` | Título, autor, afiliação, declarações, preprint, uso de IA |
| `COVER_LETTER.md` | Carta ao editor |
| `SUPPLEMENTARY_MATERIAL.md` | Tabelas S1–S4, glossário e inventário do corpus |
| `SUBMISSION_CHECKLIST.md` | Checklist de submissão |
| `ADAPTATION_NOTES.md` | Este documento |

## 6. Alternativas

- **Philosophy & Technology** (Springer): filosofia da tecnologia; exigiria ênfase maior na mediação tecnológica e na ética, com menos estudo de caso.
- **AI & Society** (Springer): excelente encaixe societal, mas com política de IA mais restritiva; o pacote anterior está em `../submissao-ai-society/`.
- **Humanities and Social Sciences Communications** (Nature Portfolio): acesso aberto, com APC; exigiria moldura mais das humanidades/ciências sociais.
- **Revista brasileira Qualis A1/A2** em Filosofia, Educação ou Saúde Coletiva: exigiria tradução para o português e uma moldura disciplinar mais definida.

## 7. Observação final

O pacote está pronto para revisão do autor, não para submissão automática. A recomendação é que o autor leia o manuscrito em inglês, reescreva as passagens que não soem como sua voz, confirme as declarações, reduza as palavras-chave para seis e só então submeta. A decisão sobre o veículo e sobre o nível de divulgação de saúde é do autor.
