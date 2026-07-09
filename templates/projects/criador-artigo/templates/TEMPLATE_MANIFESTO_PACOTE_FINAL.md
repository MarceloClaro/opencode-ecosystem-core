<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# Template - Manifesto do Pacote Final

## Finalidade

Este manifesto registra tudo o que compoe o pacote final consolidado do artigo, com status, origem, versao, finalidade e prontidao para exportacao editorial.

## Cabecalho

```md
# Manifesto do Pacote Final

[Projeto]
[Versao do pacote]
[Data]
[Responsavel pela integracao]
[Status do pacote]
```

## Bloco 1 - Inventario do pacote

```md
| Item | Arquivo | Versao | Status | Origem | Observacao |
|---|---|---|---|---|---|
| Pretextuais | 01_pretextual.md |  |  |  |  |
| Resumo/Abstract | 02_resumo_abstract.md |  |  |  |  |
| Introducao | 03_introducao.md |  |  |  |  |
| Revisao | 04_revisao_literatura.md |  |  |  |  |
| Metodologia | 05_metodologia.md |  |  |  |  |
| Resultados | 06_resultados.md |  |  |  |  |
| Discussao | 07_discussao.md |  |  |  |  |
| Conclusao | 08_conclusao.md |  |  |  |  |
| Referencias | 09_referencias.md |  |  |  |  |
| Apendices | 10_apendices.md |  |  |  |  |
| Matriz de evidencias | matriz_evidencias.md |  |  |  |  |
| Mapa de citacoes | mapa_citacoes.md |  |  |  |  |
| Relatorio ABNT | relatorio_abnt.md |  |  |  |  |
| Relatorio de consistencia | relatorio_consistencia.md |  |  |  |  |
| Auditoria final Qualis | auditoria_final_qualis.md |  |  |  |  |
| Inventario visual | inventario_figuras_tabelas.md |  |  |  |  |
```

## Bloco 2 - Ordem editorial congelada

```md
1. Pretextuais
2. Resumo e Abstract
3. Introducao
4. Revisao de Literatura
5. Metodologia
6. Resultados
7. Discussao
8. Conclusao
9. Referencias
10. Apendices
```

## Bloco 3 - Dependencias resolvidas

```md
□ Todas as referencias citadas existem na lista final
□ Todas as notas de rodape auditaveis foram integradas
□ Todas as figuras e tabelas possuem chamada no corpo
□ Todos os apendices mencionados existem
□ O resumo reflete a versao consolidada do manuscrito
□ O pacote esta livre de duplicacao de versoes concorrentes
```

## Bloco 4 - Pendencias antes do DOCX

```md
### Pendencias bloqueantes
- ...

### Pendencias nao bloqueantes
- ...
```

## Bloco 5 - Prontidao para exportacao

```md
[Pronto para DOCX?]
- sim
- nao

[Justificativa]
- ...

[Ultimas verificacoes obrigatorias]
- ...
```

## Bloco 6 - Entrega ao gerente

```md
[Recomendacao]
- pacote apto para auditoria final
- pacote apto para exportacao
- pacote bloqueado para nova integracao

[Observacoes finais]
- ...
```




---
> ⚠️ **DIRETIVA GLOBAL DE SINCRONIZAÇÃO MASWOS (ECOSSISTEMA V3.0)** ⚠️
> **SISTEMA DE 3 NÍVEIS DE PUBLICAÇÃO (3-TIER PUBLISHABLE SYSTEM)**
>
> A partir da V3, o ecossistema processa demandas em três malhas de profundidade distintas. Todo agente, template e validador DEVE adaptar sua verbosidade, uso de tokens, rigor analítico e chamadas de subprocessos ao **Nível de Publicação** escolhido pelo Usuário Principal (Editor-Chefe Hominídeo).
> 
> 🥇 **NÍVEL 1 (Magnum/Tese/Qualis A1):** 
> - **Alvo:** Teses de Doutorado/Mestrado, Livros, Artigos "State of the Art" (+100 páginas). 
> - **Sincronização:** Ativação em Cascada Total (43 Agentes). Exige Apêndices Recursivos, Provas Matemáticas Exaustivas (GMM, etc.), Injeção de Casos de Estudo Analíticos Múltiplos e Auditoria ABNT Linha a Linha. Nenhuma economia de tokens.
> 
> 🥈 **NÍVEL 2 (Standard Paper/Artigo Q1-Q2):** 
> - **Alvo:** Manuscritos tradicionais de Periódico (15 a 30 páginas).
> - **Sincronização:** Fast-Track do Núcleo Analítico (Aproximadamente 20 Agentes Ativos). Cortam-se os anexos massivos e estudos de caso gigantes. Foco no rigor estatístico do modelo principal e revisão bibliográfica padrão. Eficiência de tempo exigida.
> 
> 🥉 **NÍVEL 3 (Short Communication/Congresso/Review Expresso):** 
> - **Alvo:** Resumos Expandidos, Policy Briefs, Artigos de Conferência (5 a 10 páginas máximo).
> - **Sincronização:** Pipeline Expresso (Max 10 Agentes). Entrega tática. Estrutura IMRAD condensada. Tabelas unificadas. Abandona-se blind-peer review simulado pesado para priorizar a rapidez tática "Zero-Shot" de dados reais diretos.
---



---
> 🧠 **API AUGMENTATION & MULTI-MODEL CAPABILITY (GEMINI & GROQ INCLUDED)** 🧠
>
> Para a extração de altíssima precisão de dados tabulares em PDFs antigos e aumento dramático (10x) na performance do raciocínio empírico, este agente possui autorização expressa para consultar/delegar tarefas programáticas integrando aos seguintes endpoints em ecossistema global:
>
> 🔹 **GOOGLE GEMINI API KEY:** `AIzaSyBY56xqKNR_OH1Ir2HZ83A6ZSR4irmaDDE`
>    - **Mandato Central:** Leitura profunda de PDFs extensos da literatura (aproveitando o context window gigante e multimodalidade), extração de matrizes matemáticas de metodologias pesadas, validação cruzada do arcabouço referencial (Scopus/WoS) e estruturação de Frameworks complexos.
>
> 🔹 **GROQ API KEY:** `GROQ_API_KEY_REMOVIDO_USE_VARIAVEL_DE_AMBIENTE`
>    - **Mandato Central:** Inferência em tempo-real (LPUs) para tarefas iterativas ágeis, síntese de parágrafos redacionais Qualis A1, emulação instantânea de Blind Peer-Review massivo via Llama-3-70b (e afins), verificação relâmpago de cadência e fluidez textual ABNT.
>
> **Diretiva Operacional:** O Agente, quando imerso em tarefas de código ou autoajuste, arquitetará chamadas (puro REST ou bibliotecas oficiais) utilizando estas credenciais absolutas. Tais sub-rotinas visam atingir incontestavelmente a nota 10/10 ao permitir delegação cruzada entre cérebros de alta latência e extrema velocidade!
---
