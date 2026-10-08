---
name: conciliar-recursos-escolares
description: Conferir e conciliar recursos escolares a partir de extratos e controles, incluindo repasses, rendimentos, despesas, tarifas, tributos, estornos, devoluções e transferências internas. Usar quando o pedido envolver contas, saldo, pagamentos, orçamento executado, conciliação bancária ou valores divergentes na prestação de contas.
---

# Conciliar recursos escolares

Ler `../auditar-prestacao-escolar/references/regras-comuns.md`. Fazer conferência financeira em pt-BR com centavos exatos; não converter igualdade de valores em aprovação documental, fiscal ou legal.

## Delimitar a base

1. Fixar programa, processo, exercício, parcela, contas incluídas, início e fim. Não somar empenhos repetidos em cabeçalhos nem somar parcelas/processos distintos sem identificação.
2. Obter extratos de corrente e aplicação completos, saldos iniciais/finais e controles de pagamentos. Distinguir movimentação bancária de lista administrativa. Se houver lacuna, entregar resultado parcial e lista do que falta.
3. Extrair cada movimento com data, tipo, valor, favorecido/documento, conta, origem e página. Conferir visualmente números obtidos de OCR. Manter categorias desconhecidas como pendentes de classificação, sem lançá-las arbitrariamente.
4. Consolidar corrente e aplicação somente no mesmo escopo. Identificar pares de aplicações/resgates como transferências internas, nunca como nova receita/despesa. Se os dois lados não estiverem disponíveis, não declarar fechamento consolidado.

## Calcular e cruzar

Normalizar os dados conforme [contrato-calculo.md](references/contrato-calculo.md) e executar `python3 scripts/conciliar.py entrada.json --output resultado.json`, usando o caminho absoluto do script deste skill. O script usa apenas a biblioteca padrão Python e não acessa contas nem a internet.

Usar entradas monetárias textuais, saldos desconhecidos como `null` e referências reais. Não preencher saldo ausente com zero. O cálculo é um auxiliar: conferir escopo, extração e classificação antes de interpretar.

- Saldo do controle = saldo inicial + entradas externas − saídas externas.
- Saldo bancário ajustado = saldo final agregado dos extratos + créditos já registrados no controle ainda não creditados no banco − débitos já registrados no controle ainda não debitados no banco.
- Diferença = saldo do controle − saldo bancário ajustado.

Vincular toda pendência conciliatória a documento e data; não criar ajustes para forçar saldo zero. Tarifas debitadas no banco e ausentes no controle são diferenças a investigar e registrar corretamente. Não ignorar tarifas por não constarem do plano; separar ocorrência financeira de elegibilidade da despesa. Não presumir que uma transferência interna com valores iguais seja o mesmo fato sem identificadores e contexto.

Para pagamentos com retenções, manter bruto, líquido, retido, recolhido e encargo patronal em campos separados na planilha de apoio. No fluxo de caixa, registrar líquido efetivamente pago e guias efetivamente debitadas, sem somar novamente o bruto que já inclui retenções. Retenção ainda não recolhida permanece obrigação a conferir. Não calcular alíquotas com a tabela histórica do manual.

Conferir duplicações por ID e possíveis repetições por data/valor/documento, mas nunca excluir automaticamente uma transação legítima por semelhança. Revisar saldo negativo, lançamentos fora do período, favorecidos divergentes, documento sem pagamento, pagamento sem documento, valores fracionados e ordens cronológicas inconsistentes sem presumir fraude.

## Entregar

Apresentar quadro de saldo inicial, entradas por tipo, saídas por tipo, tarifas, rendimentos, saldo calculado, saldo bancário, ajustes comprovados e diferença. Separar transações conciliadas, não localizadas, fontes ausentes e possíveis duplicações. Mostrar memória de cálculo reproduzível e premissas. Se o cálculo fechar, escrever **valores conciliados no escopo informado**, condicionado à verificação dos documentos; nunca **prestação de contas aprovada**.

Quando solicitado arquivo, usar XLSX com abas de identificação, extratos, pagamentos, conciliação e pendências, fórmulas verificáveis e ausência marcada como desconhecida. Produzir PDF explicativo quando útil/solicitado e persistir os arquivos. Antes de sugerir devolução, verificar a obrigação e as instruções oficiais do órgão; não usar conta histórica do manual nem realizar pagamento.

Para gerar os anexos e ofícios nos modelos do Escola Nota Dez, seguir `../gerar-documentos-escolares/SKILL.md`, usando apenas os dados e cálculos conferidos do mesmo processo.
