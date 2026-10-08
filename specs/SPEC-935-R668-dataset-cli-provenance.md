---
spec_id: SPEC-935-R668
title: Download real por Kaggle e Hugging Face CLI e dataset personalizado
status: green
validation_scope: local_runtime
component: integrations/dataset_cli.py
test_file: tests/test_r668_dataset_cli.py
---

# R668 — CLI de datasets com proveniência e composição delimitada

## Contratos

1. `DatasetCliIntegration.download` usa somente argv de CLIs conhecidos, sem shell,
   com timeout, metadados/licença, arquivos explícitos, limite de tamanho,
   diretório novo contido no workspace e hashes de conteúdo.
2. Hugging Face usa `hf datasets info`, listagem e `hf download --repo-type dataset`;
   resolve uma revisão imutável antes do download. Kaggle usa sua CLI oficial;
   ausência de autenticação ou erro remoto bloqueia, sem fabricar sucesso.
3. A saída separa instalação, configuração de autenticação e download concluído.
   Credenciais e saídas brutas de autenticação não entram nos relatórios.
4. Arquivos de fontes baixadas só compõem um dataset quando o manifesto, os
   hashes, o domínio, as unidades e a licença forem compatíveis. O adaptador
   delimitado desta rodada normaliza Iris em centímetros, preserva observações
   e origens, une espelhos pelo identificador e bloqueia valores divergentes.
5. Splits reprodutíveis train/validation/test mantêm grupos de observações
   numericamente idênticas no mesmo split para evitar vazamento entre conjuntos.
   Não mistura automaticamente semânticas de datasets de áreas diferentes.
6. Manifesto de composição registra schema, domínio, licença, fontes/revisões,
   transformações, semente, contagens, CSVs e proveniência por observação.
7. Kaggle versionado baixa o ZIP oficial com versão explícita, após verificar
   o tamanho de todo o pacote e até dez arquivos. A extração escreve somente
   os arquivos solicitados. Pacote excedente bloqueia antes do download.

## Critérios executáveis

- `R668-CLI` — argv fixos, limites e ausência de shell.
- `R668-DOWNLOAD` — sem arquivo ou retorno CLI inválido não há sucesso.
- `R668-PROVENANCE` — licença/revisão/hash permanecem na composição.
- `R668-SPLITS` — splits determinísticos e sem vazamento de grupos/observações.
- `R668-ABSTENTION` — credenciais, fonte adulterada ou semântica incompatível bloqueiam.

## Prova

Testes herméticos simulam apenas o transporte CLI para verificar contratos.
O probe separado executa os binários reais e produz evidência local de download
e composição. Não há upload, publicação, treino de modelo ou certificação externa.

Contraprova RED do endpoint/limite: `docs/evidence/R668_KAGGLE_ARCHIVE_RED.xml`;
GREEN: `docs/evidence/R668_KAGGLE_ARCHIVE_GREEN.xml` e `R667_R671_GREEN.xml`.
Prova real: `docs/evidence/R671_REAL_20261004_195302/probe.json`.
Consolidação: `docs/evidence/R667_R671_RELEASE_GATE.json`.
