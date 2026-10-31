# gemini-client — executor Gemini portátil

Cliente mínimo (Rust, `ureq` + `rustls`) que chama a API Gemini
(`generateContent`) com uma `GEMINI_API_KEY`. Alternativa ao `agy`, que exige
OAuth de conta e keyring do sistema — inviável em sandbox headless.

## Compilar

```bash
cd integrations/gemini_client
cargo build --release
# binário em target/release/gemini-client (~5 MB, ligado a libc)
```

## Usar

```bash
printf 'Responda somente: OK' | GEMINI_API_KEY=... ./target/release/gemini-client
```

- `GEMINI_API_KEY` (obrigatória) — chave de API do Gemini.
- `GEMINI_MODEL` (opcional) — modelo; padrão `gemini-3.5-flash`.
- Prompt é lido de `stdin`; a resposta (texto) é impressa em `stdout`.

## Notas de segurança/limites

- **TLS skip-verify**: o cliente aceita qualquer certificado. Isso é necessário
  DENTRO do sandbox OpenShell, onde o proxy de rede faz MITM TLS com certificado
  próprio. Fora do sandbox, não use este cliente como cliente TLS confiável.
- **Sem credencial embutida**: a chave vem do ambiente, nunca do código.
- **Quota**: a chave gratuita do Gemini tem cota (HTTP 429 ao esgotar). Rotacione
  a chave para reabastecer.
- A saída é o texto do modelo; cabe ao chamador validar (o conselho R989 valida
  JSON/evidência com `scientific_lab.council.validate_report`).

Ver `docs/PROCEDIMENTO_OPENSHELL_GEMINI_CONSELHO.md` para o fluxo completo de
reprodução (OpenShell → executor → conselho).
