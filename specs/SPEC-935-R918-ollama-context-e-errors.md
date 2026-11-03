---
spec_id: SPEC-935-R918
title: Confiabilidade de contexto e erros para Ollama local
component: integrations.opencode_agent_sdk
status: proposed
test_file: tests/test_r918_ollama_context_reliability.py
---

# R918 — Confiabilidade de contexto e erros para Ollama local

## Objetivo
Melhorar a previsibilidade das chamadas locais OpenAI-compatíveis, priorizando Ollama, para que limites de contexto, falhas HTTP, quota, uso de tokens e indisponibilidade apareçam como recibos acionáveis. Não alterar o modelo padrão, não substituir provedor automaticamente e não truncar conteúdo sem autorização explícita.

## Requisitos
- **RF-01:** Preservar identidade e configuração do modelo escolhido; endpoint ou modelo não disponível resulta em erro explícito, sem fallback em nuvem.
- **RF-02:** Distinguir contexto excedido, quota/rate limit, autenticação, servidor indisponível, timeout e resposta malformada.
- **RF-03:** Quando existir janela de contexto declarada, fazer pré-checagem conservadora de entrada + reserva de saída + margem; identificar estimativa como heurística, não tokenizer exato.
- **RF-04:** Não truncar, resumir nem descartar mensagens/ferramentas silenciosamente. Pré-checagem excedida retorna erro com remediação e nenhum POST.
- **RF-05:** Preservar tokens de uso informados pelo provedor; quando ausentes, emitir estimativa marcada como estimada e não faturável.
- **RF-06:** `429`/quota preserva `Retry-After` e não faz retry nem troca de modelo/provedor automaticamente.
- **RF-07:** Diagnóstico `/models` continua sendo sinal de conectividade; não será rotulado como inferência ou qualidade.
- **RF-08:** Para Ollama loopback, consultar `/api/show` antes da pré-checagem, distinguir `PARAMETER num_ctx` do default documentado e limitar o orçamento ao menor entre a janela observada e um teto explícito do operador.

## Critérios de aceitação
- `R918-AC1`: Uma entrada acima do orçamento conhecido é bloqueada antes da requisição, sem perda silenciosa de contexto.
- `R918-AC2`: Erros de contexto e quota têm códigos estáveis, mensagem limitada e nenhuma repetição/fallback implícito.
- `R918-AC3`: Uso exato do provider e estimativa local são distinguíveis no evento `usage`.
- `R918-AC4`: As opções aceitam janela, reserva de saída e margem apenas dentro de limites validados; padrão do modelo permanece inalterado.
- `R918-AC5`: Testes HTTP mockados cobrem sucesso, contexto, quota, indisponibilidade, timeout e nenhuma chamada quando preflight bloqueia.
- `R918-AC6`: As respostas incluem diagnóstico/remediação, mas não afirmam que a correção melhorou qualidade sem benchmark comparável.
- `R918-AC7`: Contexto do Modelfile observado pelo `/api/show` prevalece sobre janela maior declarada no catálogo OpenCode; se o probe não responder, a limitação fica explícita e não vira inferência de contexto disponível.

## Não objetivos
Não executar um benchmark científico de qualidade, medir custo do plano de assinatura, instalar/baixar modelos, alterar Modelfiles, editar `opencode.json` para trocar o padrão, fazer retries automáticos nem inferir contagem exata de tokens a partir de caracteres.
