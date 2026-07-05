# Regras invariantes do projeto

## Domínio acadêmico
R1. Toda afirmação factual deve citar fonte com DOI verificável.
R2. Referências seguem ABNT NBR 6023:2018.
R3. Anteprojeto ≤ 7 laudas, anônimo, margens ABNT (sup/inf 2,5cm; esq/dir 3,0cm).
R4. Times New Roman 12pt, espaçamento 1,5.
R5. Arquivo de inscrição: PDF único ≤ 15MB, ordem exata do edital.

## Ética e LGPD
E1. Nenhum dado pessoal de participantes trafega em servidores externos.
E2. Todo uso de IA deve ser declarado (Resolução PRPPG/UFC nº 39/2025).
E3. Participantes do grupo focal assinam TCLE antes de qualquer coleta.
E4. Projeto submetido ao CEP/UFC antes do início da Fase 3.

## Segurança
S1. Nunca expor tokens, chaves API ou senhas em logs ou commits.
S2. Arquivos de dados de participantes são criptografados em repouso.
S3. Logs de auditoria são imutáveis (hash SHA-256).

## Qualidade do texto
Q1. Zero travessões (—) substituídos por ponto e vírgula ou dois-pontos.
Q2. Zero palavras proibidas pelo TSAC (87 padrões anti-IA).
Q3. Correção ortográfica antes de cada entrega (ptbr_corrector.py).
Q4. Todas as siglas expandidas na primeira ocorrência.

## Versionamento
V1. Cada versão do anteprojeto é um commit separado com mensagem descritiva.
V2. Spec e código versionados juntos no mesmo commit.
V3. Branches: feat/ para novas seções, fix/ para correções, review/ para validação.
