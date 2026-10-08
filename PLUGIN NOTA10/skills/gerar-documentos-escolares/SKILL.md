---
name: gerar-documentos-escolares
description: Preencher e gerar documentos do Prêmio Escola Nota Dez a partir de modelos Word, manuais, notas, planos e extratos. Usar para ofícios, checklist, pesquisa e mapa de preços, execução de receita e despesa, pagamentos, bens, doação, readequação, utilização de saldos e minuta de cooperação técnico-pedagógica. Entregar DOCX editável e PDF conferido, individualmente ou em lote, com dados rastreáveis e pendências explícitas.
---

# Gerar documentos escolares preenchidos

Executar o preenchimento solicitado, não se limitar a explicar como preencher. Usar pt-BR e valores em reais. Ler `../auditar-prestacao-escolar/references/regras-comuns.md`, [catálogo dos modelos](references/catalogo-modelos.md) e [contrato de preenchimento](references/preenchimento.md).

## Escolher os documentos e a edição

1. Identificar os documentos pelo propósito, não apenas pelo número do anexo. O acervo inclui 14 originais recebidos em 25/09/2026 e 11 modelos de trabalho: checklist, mapa de preços e anexos 2 a 10. Os anexos 1 são legislação, não formulário a preencher. Consultar `references/inventario-fontes.json` para caminhos, nomes originais e hashes.
2. Dar precedência ao modelo especificamente indicado pelo usuário/órgão. Os modelos de trabalho preservam a estrutura dos enviados, com ajustes documentados. Para exigência de reprodução exata, partir do original catalogado, usando a habilidade de documentos, e aplicar os mesmos controles. Não apresentar modelo adaptado como novo formulário oficial da SEDUC.
3. Consultar [edições e divergências](references/edicoes-e-divergencias.md) antes de usar normas, prazos, percentuais, limites ou rótulos legais. O nome “NOVO” não demonstra prevalência. Os dois POP de 2025 não são idênticos. Confirmar enquadramento e vigência para a data do ato; preservar a referência histórica de 2019 do plugin.

## Montar uma base única de preenchimento

4. Ler os documentos atuais e extrair escola, UEx, CNPJ, município, endereço, programa, edição SPAECE, ano do plano, ano do recebimento, parcela, premiada/apoiada, etapa, processo, empenho, conta e responsáveis por função/mandato. Não transformar o diretor em presidente da UEx ou autoridade da CREDE. O contexto Airam Veras não confirma CNPJ, INEP, mandato ou dados de processos anteriores.
5. Reutilizar os dados confirmados entre documentos do mesmo processo. Registrar a fonte de cada campo e de cada linha, com arquivo e página, ou mensagem explícita do usuário. Manter conflitos em pendência; não escolher silenciosamente. Diferenciar data da emissão, data do fato e data da verificação. Nunca preencher datas antigas com a data de hoje.
6. Criar a entrada conforme `assets/entrada-vazia.json` e o contrato. Aproveitar arquivos disponíveis antes de perguntar. Pedir num único bloco apenas os dados faltantes que mudem o documento. Se houver informação suficiente para uma minuta útil, gerar a parte possível e listar o restante; não anunciar documento integralmente preenchido se houver pendências.
7. Remover nomes, datas, valores e tombamento de exemplo das cópias de trabalho. Os exemplos “João”, “Joana”, “Joaquim”, “FULANO DE TAL”, “Mesa para computador”, 20/11/2023 e 123456789 não são dados da escola. Manter preços de fornecedor em branco/pendentes quando se tratar de solicitação de cotação; não criar proposta recebida.

## Calcular e produzir

8. Conferir documentos financeiros usando `../conciliar-recursos-escolares/SKILL.md`. Derivar valores com centavos exatos e registrar memória de cálculo. O gerador calcula apenas produtos e totais de linhas completas com fontes; ele não verifica o banco, validade de tributos ou aprovação do plano. Não converter valor desconhecido em zero. Separar saldo bancário, saldo das ações, rendimentos disponíveis e obrigações pendentes.
9. Executar o gerador com caminho absoluto, usando o Python disponível com `python-docx`:

   `python3 scripts/gerar_documentos.py entrada.json --saida pasta --modelos anexo-02,anexo-04`

   Para todos os documentos aplicáveis, usar `--modelos todos`; não gerar documentos inaplicáveis apenas para completar um pacote. Ler `preenchimento.json`, `pendencias.csv` e `alertas.csv` produzidos na pasta. Células `[PENDENTE]` têm seus campos identificados nesses controles. Resolver ou justificar os alertas antes de declarar os valores conferidos. As listas expandem linhas, sem limite artificial de três itens.
10. Usar as habilidades de documentos/PDF para renderizar os DOCX, inspecionar **todas** as páginas e corrigir cortes, textos sobrepostos, linhas ou assinaturas isoladas. Revalidar após qualquer ajuste. Exportar PDF somente depois da revisão. Para controles extensos ou cálculos editáveis, usar a habilidade de planilhas para XLSX e conferir fórmulas. Não afirmar que PDF/XLSX foi criado se a ferramenta/arquivo não existir.

## Autoridade, revisão e entrega

- Manter as linhas de assinatura vazias. Ofícios são solicitações, não autorizações. O anexo 10 é minuta para análise/emissão pela CREDE; a conclusão e o atesto exigem manifestação documentada da autoridade competente. Não declarar que a escola está habilitada à segunda parcela por inferência.
- No mapa, informar escolha e justificativa apenas quando documentadas. Menor número não prova que proposta é válida; não adjudicar nem homologar automaticamente. No checklist, indicar estado documental e página real da evidência; nunca marcar “conferido” porque um modelo foi produzido.
- Separar conferência de campos, revisão do conteúdo e aprovação oficial. O gerador sempre produz minutas, inclusive quando todos os campos possuem fontes. Retirar a indicação de minuta somente em versão solicitada para assinatura e após revisão dos dados, preservando a versão de trabalho.
- Entregar os arquivos efetivamente gerados e persistidos, com resumo objetivo do preenchimento e das pendências. A documentação de apoio não integra automaticamente o ofício; só afirmar “em anexo” para arquivos identificados e presentes. Não enviar, protocolar, assinar ou compartilhar sem autorização aplicável à ação.
- Ao retornar a um processo, ler a versão atual dos arquivos. Atualizar mantendo identidade e histórico; não reutilizar cadastro de outro processo ou escola.
