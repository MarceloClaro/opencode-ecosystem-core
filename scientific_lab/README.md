# Scientific Lab — camada nativa v4.2 e fallback externo v4.1

O caminho essencial de pesquisa, revisão sistemática e Evidence Graph está
implementado no Core (`scientific_lab/native/`). A supercamada v4.1 instalada
continua opcional para módulos avançados ainda não migrados.

Os comandos nativos são encaminhados localmente, sem exigir a supercamada externa:

```bash
python -m marceloclaro.scientific_lab native-status
python -m marceloclaro.scientific_lab research search "tema" --workspace .
python -m marceloclaro.scientific_lab review --help
python -m marceloclaro.scientific_lab evidence --help
```

`mesh`, `mission`, `living`, `synthesis`, `grade`, `causal`, `federation` e
`production` continuam como fallback v4.1; sua prontidão é distinta da camada
nativa. A instalação completa v4.1 usa por padrão:

```bash
~/.local/share/pesquisador-universal/skill
```

Também é possível definir `PESQUISADOR_UNIVERSAL_HOME=/caminho/para/skill`.
Use `status` para consultar versão e identidade do manifesto. `installed_verified`
confirma somente a versão e o SHA-256 esperado do arquivo de manifesto; não
valida os arquivos individuais nem a prontidão operacional. O comando não executa
scripts externos.

Use `doctor` para ver compatibilidade do Core, prontidão nativa e resultado dos
validadores locais da supercamada separadamente. O campo `package_validation`
lista os scripts, códigos de saída e estado agregado; stdout/stderr dos scripts
não entra no JSON. `doctor_status=degraded` indica que a identidade declarada do
release foi reconhecida, mas ao menos uma validação falhou. A presença do pacote
externo não comprova execução de modelos, autenticação de conectores, validação
externa independente ou validade científica.

O resolvedor restrito permanece desabilitado por omissão; ver R470 e
`marceloclaro.scientific_lab restricted --help`.
