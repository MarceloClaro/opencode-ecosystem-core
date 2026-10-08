# Contrato de entrada do cálculo

O motor processa um escopo consolidado explicitamente descrito. Não extrai PDF, não verifica autenticidade, não calcula impostos, não decide legalidade e não escolhe ajustes conciliatórios. O agente deve classificar e referenciar as informações antes de executá-lo.

## Campos

- `escopo`: texto que identifique UEx/programa/processo/exercício/parcela.
- `moeda`: BRL.
- `periodo`: datas ISO `inicio` e `fim`, inclusivas.
- `contas_incluidas`: rótulos únicos das contas corrente/aplicação incluídas; usar rótulos internos quando não precisar exibir números.
- `saldo_inicial_controle`: saldo agregado imediatamente anterior ao primeiro movimento do período, texto monetário ou `null` se desconhecido.
- `saldo_final_banco`: saldo agregado de corrente e aplicação na data final, texto monetário ou `null`. Não usar só corrente quando o escopo inclui aplicação.
- `fontes_saldos`: objeto com as chaves dos saldos acima, cada qual apontando arquivo/página ou planilha/célula.
- `extratos_completos`: `true` apenas depois de conferir todos os extratos do período; `false` ou `null` caso contrário. É informação declarada, não checada pelo script.
- `movimentos`: lista obrigatória; pode estar vazia em período sem movimentação comprovado. Cada linha tem `id`, `data`, `tipo`, `valor`, `conta`, `fonte` e, quando houver, `documento`. Valor sempre não negativo; tipo define sentido. Ausência de fonte gera alerta, não fonte fictícia.
- `pendencias_bancarias`: lista opcional de fatos já contabilizados no controle e ainda não efetivados no banco. Cada item tem `id`, `natureza`, `valor`, `movimento_id`, `fonte`, `justificativa`. O valor deve coincidir com o movimento vinculado. Dividir pagamentos parciais em movimentos comprovados antes de ajustar, sem duplicar o lançamento original.
- `movimentos_anteriores_pendentes`: lista opcional para cheques ou créditos de período anterior ainda pendentes no banco. Usar os mesmos campos de movimento, data anterior ao início, valor positivo, fonte obrigatória e `incluido_no_saldo_inicial: true` somente após comprovar sua inclusão no controle inicial. Não entram novamente nas receitas/despesas do período; podem ser referenciados por `movimento_id` nas pendências bancárias. Não duplicar esses fatos nos movimentos correntes.

Entradas externas: `repasse`, `rendimento`, `contrapartida`, `ressarcimento`, `estorno_despesa`.
Saídas externas: `despesa`, `tarifa`, `tributo`, `devolucao`, `estorno_receita`.
Transferências internas: `transferencia_entrada` e `transferencia_saida`, com o mesmo `id_transferencia`, em duas contas distintas incluídas, valores iguais e fontes. Os pares são excluídos das receitas/despesas consolidadas. Par ausente ou divergente bloqueia o cálculo: completar a prova, ou recalcular escopo corretamente, sem inventar o outro lado.

As naturezas de pendência são `credito_ja_no_controle` (somar ao banco) e `debito_ja_no_controle` (subtrair do banco). Referir-se a fato pendente na data do saldo final. Um documento de despesa sem pagamento efetuado ou emitido não é automaticamente débito em trânsito. Não usar ajuste para ocultar erro, tarifa omitida ou documento faltante.

Valores aceitos: `"24500.00"`, `"24.500,00"`, `"R$ 24.500,00"` ou inteiro em texto. Rejeitar floats, `NaN`, múltiplos separadores inconsistentes, `"1.234"` ambíguo ou mais de duas casas. Saldos podem ser negativos, mas movimentos usam tipo e valor não negativo. Não tratar desconhecido como zero nem arredondar um erro de origem para fazê-lo caber.

## Exemplo sintético

Todos os identificadores e fontes abaixo são fictícios, apenas para explicar o formato. Não usar essas fontes no processo real.

```json
{
  "escopo": "EXEMPLO FICTÍCIO | programa X | processo E1 | parcela 1",
  "moeda": "BRL",
  "periodo": {"inicio": "2026-01-01", "fim": "2026-01-31"},
  "contas_incluidas": ["corrente"],
  "saldo_inicial_controle": "0.00",
  "saldo_final_banco": "815.00",
  "fontes_saldos": {
    "saldo_inicial_controle": "exemplo-sintetico, abertura",
    "saldo_final_banco": "exemplo-sintetico, fechamento"
  },
  "extratos_completos": true,
  "movimentos": [
    {"id":"E1","data":"2026-01-02","tipo":"repasse","valor":"1000.00","conta":"corrente","fonte":"exemplo-sintetico linha1"},
    {"id":"E2","data":"2026-01-05","tipo":"rendimento","valor":"20.00","conta":"corrente","fonte":"exemplo-sintetico linha2"},
    {"id":"E3","data":"2026-01-10","tipo":"despesa","valor":"200.00","conta":"corrente","fonte":"exemplo-sintetico linha3"},
    {"id":"E4","data":"2026-01-31","tipo":"tarifa","valor":"5.00","conta":"corrente","fonte":"exemplo-sintetico linha4"}
  ],
  "pendencias_bancarias": []
}
```

A saída contém totais por tipo, entradas, saídas, saldos, ajustes, diferença e alertas. `status_aritmetico` pode ser `nao_calculavel`, `divergencia` ou `valores_conciliados`. Mesmo o último estado não significa que documentos foram conferidos: a comprovação documental é explicitamente `nao_avaliada_pelo_script`. Relatar alertas e cobertura junto ao status, e conservar entrada/resultado para reprodução.
