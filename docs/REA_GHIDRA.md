# Análise estática nativa pelo MarceloClaro

O REA usa Ghidra 12.1.4 e JDK completo 21 isolados em
`~/.local/share/opencode-core/native-rea`. Não altera o Java padrão do sistema.
As distribuições oficiais, suas licenças e hashes estão no recibo
`install-receipt-r823.json` desse diretório; os artefatos grandes ficam fora do Git.

Para inspecionar uma função de um binário local:

```bash
python3 -m marceloclaro.cli rea analyze_binary /caminho/arquivo.elf --procedure main --timeout 180
```

No gateway MCP `ecosystem_rea`, envie:

```json
{"operation":"analyze_binary","path":"/caminho/arquivo.elf","procedure":"main","timeout_seconds":180}
```

MarceloClaro conserva a coordenação e registra a observação sem elevar confiança
por autoavaliação. A ponte admite arquivo até 128 MiB e procedimento textual até
256 caracteres. Somente chama `open_binary` com Ghidra, `analyze_function`,
`binary_session` e `close_binary`. O alvo não é executado. A função pode ser
identificada pelo símbolo ou por endereço informado pelo provider.

`analyze` permanece a análise JavaScript existente. `session` consulta identidade
e disponibilidade de providers; `status` só inspeciona arquivos/configuração e
declara `installation_only`. Descoberta não comprova análise concluída.

`GHIDRA_INSTALL_DIR` e `JAVA_HOME` explícitos têm precedência. Um override
inválido não usa instalação alternativa. Na ausência dessas variáveis, a ponte
transporta os caminhos isolados para o processo filho, inclusive no launcher
MCP. Não carrega `.env` implicitamente nem edita configurações globais de clientes.

A conclusão exige Evidence do provider e digest correspondente ao alvo.
O fechamento é comprovado por sessão posterior com `open=false`, porque o ACK
de `close_binary` é `result=null`. Timeout/cancelamento mantêm resultado de falha;
o fechamento cooperativo é blindado e limitado, seguido da limpeza do transporte.
`cleanup.closed=false` indica ausência de confirmação MCP, mesmo quando a prova
de processos mostra que a limpeza forçada terminou. Não substituir esse estado
por uma alegação de fechamento gracioso.

O gateway exporta a resposta completa em `.opencode/rea/evidence/<sha256>.json`
e entrega resumo finito com o arquivo e hash. Consulte pseudocódigo, assembly,
fluxo de valores, limitações e perfil no artefato integral. O pseudocódigo não é
código-fonte original nem valida comportamento dinâmico.

Em `outputs/core-r823`, a prova real do fixture ELF e as provas de cancelamento,
timeout e MCP estão separadas dos testes herméticos. O fixture não foi executado,
seu digest permaneceu igual e o marker de execução não foi criado. As provas são
internas; não constituem validação externa.

Fontes: [Ghidra 12.1.4 oficial](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build),
[Temurin JDK 21 oficial](https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21.0.12.1%2B1),
[REA solicitado](https://github.com/MarceloClaro/rea).
