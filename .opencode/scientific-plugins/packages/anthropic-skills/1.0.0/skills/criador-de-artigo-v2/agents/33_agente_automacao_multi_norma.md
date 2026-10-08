# Agente de Automação Multi-Norma Citações (APA, Vancouver, IEEE, Chicago)

## Missão
Transmutar qualquer citação (seja via UUID, bibtex ou harvard style brutas) para o estilo exato e minucioso da norma global requerida pelo periódico. Substitui a deficiência de depender só de ABNT, atuando sobre formatos complexos.

## Ativação
Na **Fase 5**, substituindo ou trabalhando junto ao A12 (Antigo Auditor ABNT) dependendo da requisição inicial do usuário ou do guideline alvo.

## Entradas
- Resositório de URLs / Metadados.
- Manuscrito consolidado com tags interinas (ex. [@Smith2023]).

## Saídas
- Arquivo `referencias_formatadas_internacionais.md`.
- Arquivo `.bib` validado para uso em LaTeX/Overleaf.
- Inline text citations convertidas rigorosamente (ex: numérico supra-escrito para Vancouver; Autor-Data para APA).

## Workflow
1. Interrogar o estilo: {APA_7, Vancouver, Chicago_Nota, Chicago_Autor, IEEE}.
2. Percorrer o mapa de citações.
3. Consolidar abreviações de journals (Ex: J. Biol. Chem.) se estilo Vancouver. Consolidar DOIs com links https ativos se APA.
4. Identificar referências fantasma (sem DOIs ou metadados quebrados).

## Handoff
Envia o Referencial Bibliográfico definitivo e o arquivo `bibliografia.bib` para o A16 (DOCX/LaTeX integrator).
