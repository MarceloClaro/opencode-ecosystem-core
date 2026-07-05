# Spec: REST Client (core/rest_client.py)

**Versao:** 1.0.0 | **Status:** active | **SWEBOK:** adaptativa | **Revisao:** 2026-05-27

## 1. Comportamento
Cliente HTTP com retry, timeout, logging estruturado e DI. Wrapper sobre httpx com exponential backoff, log automatico de requests/responses e tratamento uniforme de erros HTTP.

## 2. Usuarios
- Usuarios: MCPs que fazem chamadas HTTP externas (websearch, fetch, context7)
- Volume: variavel (depende do uso de MCPs externos)
- Ambiente: Python 3.11+, httpx

## 3. Restricoes
- Retry com exponential backoff (max 3 tentativas)
- Timeout padrao: 30s
- Logging automatico (metodo, URL, status, latencia)
- Suporte a DI (Container)

## 4. Bordas
- Timeout: levanta excecao apos retries esgotados
- 429 (Rate Limit): espera pelo Retry-After header
- 5xx: retry com backoff
- 4xx: nao retry (erro do cliente)

## 5. Criterios
- [ ] GET request com sucesso retorna resposta
- [ ] Timeout apos 30s levanta excecao
- [ ] Retry em 503 com backoff exponencial
- [ ] 404 nao dispara retry
- [ ] Logging registra todas as chamadas
