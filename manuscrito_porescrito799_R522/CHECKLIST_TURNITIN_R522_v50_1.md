# CHECKLIST TURNITIN — R522 v50.1 (23/09/2026)

**Escopo honesto:** o Turnitin é serviço **institucional** (acesso do autor via
rede municipal de Crateús-CE ou PUCRS). Este checklist prepara o material;
a execução na plataforma é feita pelo usuário na instituição.

## 1. Arquivo a enviar

- `PACOTE_DOCUMENTOS_PESQUISA_R522_2026-09-20/manuscrito_porescrito799_brasil_comparado_R522_v50_OFICIAL_M8_CONFERIDO.pdf`
  - 25 páginas, texto extraível, sem metadados de autor (LibreOffice), não criptografado
  - SHA-256: `f4f247daf05621b0ca461751…` (manifesto JSON no pacote)
  - Anonimato verificado: MARCELO/LARANJEIRA/JOÃO VICTOR/BEZERRA DE ARAÚJO **ausentes**
  - RH1/RH2 preservados como revisores humanos (identificadores anônimos, exigidos pelo periódico)
- Alternativa: subir o DOCX equivalente (mesmo conteúdo; PDF recomendado pelo Turnitin)

## 2. Pré-checagens automáticas feitas

- [x] PDF sem criptografia (extraível)
- [x] Nomes de autores ausentes do texto (v50.1 corrigiu v50)
- [x] Nenhum e-mail/ORCID/URL pessoal no corpo do manuscrito
- [x] Tabelas e Apêndice A com texto extraível
- [x] 25 páginas / ~61.8 mil chars — dentro de 1 upload Turnitin

## 3. Passos manuais na plataforma (responsabilidade do autor)

1. Acessar o Turnitin da instituição (classe/atribuição criada pelo professor/coordenação).
2. Criar **assignment** com "Allow submissions" habilitado para envio de rascunho.
3. Enviar `manuscrito_..._v50_OFICIAL_M8_CONFERIDO.pdf` como rascunho (draft mode).
4. Aguardar relatório de similaridade (pode levar minutos a horas).
5. Interpretar:
   - **< 10%**: zona confortável para manuscrito com citações diretas de corpus.
   - **10–20%**: revisar trechos sinalizados; tipicamente citações longas / referências.
   - **> 20%**: revisar blocos sinalizados (especialmente §discussão comparada, onde o corpus é citado em bloco).
6. Se houver self-match com o **preprint v49.2 depositado no Zenodo/OSF** (21/09/2026), é esperado e normalmente **excluível** no relatório (configuração "Exclude all quotations" + "Exclude sources" por decisão editorial).
7. Registrar nº do relatório + % final em `execucao_real/LOG_EXECUCAO_REAL_R522.md` (coluna pendência 3).

## 4. Decisão sobre citações longas

O corpus de 21 estudos exige citações diretas (ex.: decisões judiciais, obras
jurídicas). Se o relatório sinalizar essas passagens, decidir com o editor:
- manter citação direta curta com paráfrase;
- reduzir bloco citado (citar apenas trechos essenciais);
- registrar exclusão de citações no relatório (prática comum em revistas).

## 5. Depois do Turnitin

1. Assinar a declaração de IA preenchida (pendência 2 — ato manual).
2. Atualizar depósito OSF/Zenodo da v49.2 → v50.1 (opcional, sugerido após relatório).
3. Conferir instruções da Educação Por Escrito no sistema editorial.
4. Submeter (manuscrito cego + folha de rosto + declaração).

---
*Gerado por marceloclaro em 23/09/2026 — não substitui a execução institucional do Turnitin.*