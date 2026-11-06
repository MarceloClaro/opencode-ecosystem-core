# Checklist KDP — Pré-publicação (Molambudos: O Diário do Paciente 1.260)

Checklist operacional para submissão na Amazon KDP (impressão sob demanda + eBook). Marque cada item ao concluir. Este documento assume que o preflight técnico (fontes, margens, sangria) já foi aprovado.

---

## 1. Conta e dados da conta KDP (uma vez)

- [ ] Conta KDP criada/ativa (kdp.amazon.com)
- [ ] Dados fiscais preenchidos (CPF/CNPJ, formulário de imposto — W-8BEN para Brasil)
- [ ] Dados bancários para royalties (transferência internacional ou Payoneer)
- [ ] Conta de e-mail verificada e 2FA ativada

## 2. Metadata do livro

- [ ] **Título:** Molambudos — O Diário do Paciente 1.260
- [ ] **Subtítulo (opcional):** definido? (ex.: "um arquivo ficcional") — decidir antes do upload
- [ ] **Autor:** Marcelo Claro
- [ ] **Descrição (sinopse):** 300–400 caracteres; aprovada por leitor beta antes de publicar
- [ ] **Palavras-chave (7 campos):** ex.: "ficção literária brasileira", "horror literário", "romance psicológico", "diário ficcional", "literatura brasileira contemporânea", "suspense", "colônia psiquiátrica" — validar com a ferramenta de busca KDP
- [ ] **Categorias (2):** Ficção > Horror; Ficção > Psicológica (ou equivalentes BISAC)
- [ ] **Público adulto:** NÃO marcar "18+" (obra é adulta mas sem conteúdo sexual explícito) — confirmar com a política KDP
- [ ] **Idioma:** Português (Brasil)
- [ ] **Data de publicação:** agendar ou publicar imediatamente

## 3. Arquivos de impressão (capa + miolo)

- [ ] **Miolo:** `miolo_kdp_160x230mm.pdf` (419 páginas; 160×230mm; verificado: 0 overfulls, fontes incorporadas)
- [ ] **Capa completa (com lombada):** `capa_completa.pdf` — conferir no "Capa" do KDP:
  - [ ] Dimensões do PDF batem com a calculadora KDP (largura = 2×160mm + lombada + 2×sangria)
  - [ ] Lombada calculada com o número final de páginas (419) — **recalcular se páginas mudarem**
  - [ ] Sem texto importante nas margens de corte (3mm)
  - [ ] Código de barras/ISBN: o KDP adiciona automaticamente ao enviar a capa — não incluir manualmente
- [ ] **Upload e revisão visual:** usar o Visualizador KDP (Kindle Create Preview) para folhear página por página:
  - [ ] Página 1 (rosto) no lugar certo
  - [ ] Página 5 (AVISO AO LEITOR) visível
  - [ ] Margens internas/externas sem texto cortado
  - [ ] Nenhuma página em branco indesejada no final

## 4. ISBN e direitos

- [ ] **ISBN:** usar ISBN gratuito do KDP ou ISBN próprio (decidir; ISBN próprio permite distribuição ampliada)
- [ ] **Página de direitos autorais:** já incluída no miolo (ficha catalográfica) — conferir se contém:
  - [ ] © 2026 Marcelo Claro
  - [ ] Aviso de obra de ficção (personagens/locais fictícios)
  - [ ] Aviso de direitos reservados

## 5. Prova digital e física (OBRIGATÓRIO antes de publicar)

- [ ] Solicitar **prova digital** (grátis) e folhear integralmente o PDF de prova
- [ ] Solicitar **prova física** (cópia do autor, com desconto) e conferir:
  - [ ] Capa: cores, nitidez, alinhamento da lombada
  - [ ] Miolo: encadernação, margens, papel
  - [ ] Tipografia: densidade de tinta, legibilidade
  - [ ] Abertura: livro abre plano (não fecha sozinho)
- [ ] Conferir **contracapa** (`contracapa.pdf`) com texto/sinopse corretos e código de barras posicionado

## 6. Preço e distribuição

- [ ] **Preço de capa (BRL):** decidir (sugestão: faixa de mercado para 419 páginas em brochura)
- [ ] **Royalties:** conferir tabela KDP Brasil (impressão: 60% menos custo de impressão; varia por mercado)
- [ ] **Distribuição:** somente Amazon ou expandida (IngramSpark exige ISBN próprio — decidir)
- [ ] **Territórios:** Brasil + demais mercados de língua portuguesa (se aplicável)

## 7. eBook (opcional, segunda fase)

- [ ] Converter `main.tex` (versão digital) para ePub/KPF — usar agente `kdp-ebook-epub-phd` quando decidir
- [ ] Capa digital (1600×2560 px mínimo) — derivar de `capa_completa.pdf`
- [ ] Metadata digital + sumário navegável
- [ ] Upload separado na KDP (título pode ter versões impressa e digital)

## 8. Pós-publicação

- [ ] Receber e-mail de aprovação (até 72h)
- [ ] Revisar a página do produto (Amazon) publicamente
- [ ] Solicitar 1 exemplar do autor (impresso) para arquivo pessoal
- [ ] Registrar data de lançamento e iniciar divulgação (redes, mailing, resenhas)
- [ ] **Corrigir apenas erros críticos** após publicação (reupload de correções leva até 72h e pode resetar avaliações — usar com parcimônia)

---

## Lembretes finais

- A **prova física** é o gate final: nunca publicar sem ela.
- Se o número de páginas mudar **qualquer** página, recalcular lombada e re-gerar `capa_completa.pdf`.
- Manter backup dos PDFs aprovados em `_archive/` (versão publicada = fonte da verdade).
