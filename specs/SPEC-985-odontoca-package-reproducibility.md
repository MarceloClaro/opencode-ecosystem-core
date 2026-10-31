---
spec_id: SPEC-985
title: Dependências explícitas e reprodução local do pacote OdontoCA
version: 1.0.0
status: green
test_file: odonto/local/tests/test_dependency_manifest.py
---

# SPEC-985 — reprodução do pacote OdontoCA sem dependências implícitas

## Problema

O pacote `odonto/local` lê a fonte primária `Table_S1.xlsx` com pandas, mas o
ambiente principal do Core não tem `openpyxl`. A suíte local passou sob o
Python de sistema e falhou em dois testes sob `.venv` com `ImportError`, embora
o README não declare o backend Excel. Isso torna a prova de reprodução
dependente do acaso do ambiente e impede validar a fonte clínica real de forma
repetível.

## Escopo

- Criar uma lista de dependências runtime exata, ancorada nas versões que
  acompanham os artefatos/model card atuais: NumPy, pandas, scikit-learn,
  openpyxl, OpenCV headless e joblib.
- Separar dependências de teste em `requirements-dev.txt`.
- Atualizar o README com criação/ativação de venv e instalação reproduzível.
- Teste hermético que verifica pins necessários e alinha versões centrais com
  o model card publicado.
- Reexecutar os testes do pacote no ambiente que contém as dependências.

## Regras invioláveis

1. Não baixar nem acessar dados Kaggle nesta alteração.
2. A fonte `Table_S1.xlsx` permanece fixa por SHA-256 fail-closed; nenhum dado
   é sobrescrito ou redistribuído.
3. Nenhum modelo é treinado como efeito colateral de instalar/testar o pacote;
   testes de treino existentes usam fixtures sintéticas ou a fonte verificada
   conforme suas próprias regras.
4. `requirements.txt` não inclui XGBoost, LightGBM, SHAP, PyTorch ou CNN; são
   opcionais/fora de escopo e não podem virar instalação implícita.
5. Dependências são fixadas, e instalação no venv do Core é verificação local,
   não mudança do lockfile global nem alegação de instalação portátil.

## Critérios de aceitação

1. `odonto/local/requirements.txt` declara pins exatos para as dependências
   runtime, inclusive `openpyxl` necessário a `pandas.read_excel`.
2. `requirements-dev.txt` referencia runtime e fixa pytest separado.
3. README explica setup local sem downloads de datasets e distingue execução
   de tests/treino empírico.
4. Teste hermético valida os pins e a sincronização de versões com o model card.
5. `odonto/local/tests/` passa no ambiente com os pins; prova real apenas lê
   `Table_S1.xlsx` local e revalida seu SHA-256. Não se afirma validação externa,
   utilidade clínica ou desempenho em outra coorte.

## Evidência inicial

- `.venv` do Core: 30/32 passaram; os dois testes que leem a planilha falharam
  com `ModuleNotFoundError: openpyxl`.
- Python de sistema: 32/32 passaram; `openpyxl 3.1.5`, pandas 3.0.3,
  scikit-learn 1.9.0, NumPy 2.5.1, OpenCV 5.0.0 e joblib 1.5.3 presentes.
- Model card: fonte `Table_S1.xlsx` hash correto; intended use research only;
  nenhum uso clínico; sem validação externa; 83 eventos/81 crianças.

## Evidência de execução

RED: três testes do manifesto falharam porque não havia `requirements.txt`,
`requirements-dev.txt` nem instrução de setup reproduzível.
GREEN: `odonto/local/tests/` — **35 passed** após instalar no venv o pin
`openpyxl==3.1.5` (mais `et-xmlfile==2.0.0`); a suíte lê a Table_S1 local e
verifica seu hash/coorte, sem download Kaggle. Regressão do manifest: 3 passed.
BNCC local R940/R942: 8 passed. O hash do `odontoca_clinical_model.joblib`
coincidiu com o model card (`ad32c8836f4d1394448d1d30fc9c0c5f0cc101659b5f7d27ca02a24415197772`).
O verificador genérico `ecosystem_scientific_verify` bloqueou este diretório por
`FileNotFoundError` de formato/manifest esperado; por isso não é contado como
aceite do pacote.

## Limites

Pins reproduzem o ambiente observado, não garantem instalação em todos os
sistemas operacionais. Não houve acesso a paciente, download Kaggle, validação
externa ou uso clínico. O pacote é estudo de desenvolvimento; a validação
prospectiva independente permanece pendente conforme
`external_validation_protocol.md` (83 eventos vs. 240 recomendados para o modelo
primário), e a determinação ética da análise secundária ainda requer confirmação
dos autores.
