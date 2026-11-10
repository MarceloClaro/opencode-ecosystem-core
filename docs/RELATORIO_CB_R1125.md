# R1125 — progresso local, sem liberação formal

## Resultado principal

O protótipo foi corrigido para medir **paridade Pauli**, não P(00), e para
distinguir decaimentos efetivos de taxas de gerador. O desenho de CZ par tem
**posto 9 para 15 taxas**. Dois geradores válidos, um com erro XI e outro com
erro XZ de mesma intensidade, são indistinguíveis nesse desenho.

Não foram submetidos novos jobs GJQ. Nenhuma credencial foi necessária.
Não foram executados CB, GST ou PEC em hardware nesta rodada. Não houve
commit/push desta etapa: o gate formal continua bloqueado.

## Implementação local

- Gerador para os 15 Paulis em profundidades 0,2,4,8,16, com seeds e barreiras.
- Paridade com validação de counts, largura dos bits e suporte identidade.
- Ajuste direto E=A f_eff^m e IC95% bootstrap **condicional** de shots.
- Matriz anticomutação, teste de posto e inversão somente de espectro completo.
- Rejeição de gerador incompatível; probabilidades do canal separadas de taxas.
- Harness offline de manifesto/simulação/análise, hashes QASM, JSON estrito,
  vínculo entre dados e protocolo e proteção contra sobrescrita.
- Correções na skill, nos dois agentes e no harness, sem ampliar permissões.
- Análise de leitura agora informa **subespaço 00/11**, não matriz 4×4, e
  trata dados ausentes sem divisão por zero.

## Evidência numérica — exclusivamente sintética

Diretório: `harnesses/quantum-error-mitigation/resultados/r1125_simulation/`.

| Artefato | Papel |
|---|---|
| `manifest.json` | protocolo/ordem/seeds/QASM e hashes, sem autorização hardware |
| `synthetic_counts.json` | 150 circuitos simulados, 4.096 shots cada, taxas injetadas explícitas |
| `analysis.json` | primeira análise local, preservada |
| `analysis_v2.json` | análise atual com limites inferenciais explícitos |
| `audit/` | logs RED/GREEN, regressões, gates, reflexão e hashes |

Os 15 ajustes condicionais passaram no diagnóstico local. Erro absoluto
máximo dos decaimentos efetivos frente ao modelo injetado: **0,00119916**.
Nesta única realização, 13 dos 15 intervalos pontuais contiveram o valor
injetado; **isso não é validação de cobertura**. As 15 curvas não equivalem a
15 parâmetros independentes. A saída mantém `rates=null` e PEC bloqueado.

O simulador por matriz densidade injeta exp(L) após cada CZ. Há um teste
independente por exponencial de superoperador, além de testes algébricos.
Portas locais ideais, estacionariedade e SPAM multiplicativo continuam sendo
hipóteses. Não houve teste da compilação física GJQ.

## Testes e falhas registradas

- Primeiro RED: **44 falharam, 2 passaram**; primeiro GREEN: **46 passaram**.
- Após revisão adversarial: RED **9 falharam, 52 passaram**; GREEN focal com
  leitura: **67 passaram** (61 R1125 + 6 R1124).
- Regressão quântica R1109–R1125: **218 passaram**, 28 avisos de depreciação.
- Lifecycle R894 no Python do Core: **30 passaram**.
- Uma tentativa anterior incluiu lifecycle no venv quântico: 3 falhas por
  ausência de `whoosh`. A correção foi usar o ambiente adequado, sem instalar
  pacotes ou alterar testes. O log da falha foi preservado.
- Configuração OpenCode: `--check` passou; `git diff --check` passou.

### Gate formal

O coletor `TDDHistory` recusou a tentativa antes de executar pytest por
`source_manifest_limit` (mais de 20.000 arquivos-fonte no escopo).
Recibo rejeitado: `tdd-bb73b7243ff34e178ac117ab7027545b`.
`SpecVerifier` permaneceu negativo, sem histórico selado válido. Não houve
alteração do limite, falsa importação de logs como recibos ou promoção da spec.
Os testes brutos demonstram execução local, mas **não substituem esse gate**.

## Revisão e reflexão

- `task-b91ba825`: revisão matemática textual via executor Codex, após falha
  de limite de conta no executor inicial; confirmou órbitas/posto e contraprova.
- `task-609659fc`: revisão adversarial do contrato fornecido, não do código.
  Motivou parser JSON estrito, campos de tolerância/limites e contraprovas.
- O agente especializado não executou por exigência de assinatura OpenCode Go;
  não foi contabilizado como revisão concluída.
- O parecer sobre ocultar heterogeneidade por agregação foi confrontado:
  a implementação mantém os 10 pontos, não os reduz a 5 médias. O teste de
  dois conjuntos com desvios opostos bloqueia o ajuste compartilhado.
- Calibração do diagnóstico χ², cobertura em fronteiras, autenticação de
  resultados e independência temporal continuam pendentes.
- Reflexão e ciclo R1125 registrados no MetaBus/Evolution como bloqueados para
  promoção, sem elevar confiança. Sem posição acessível de stake, não se
  declarou débito/slashing fictício.

## Próximo passo

Projetar aquisição adicional/GST do par que resolva as combinações ausentes,
com gauge, ruído de referência, SPAM e compilação explícitos. Reavaliar posto
do modelo completo e o orçamento antes de hardware. GST apenas de q1 não
substitui caracterização do CZ. Ver `docs/HANDOFF_CB_GST.md` para a fonte
consultada, as retificações históricas e os bloqueios remanescentes.
