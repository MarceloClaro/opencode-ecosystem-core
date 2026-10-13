# Histórico RED executado e gate de entrega

Uma entrega de software não é aprovada apenas porque os testes atuais estão
verdes. O gate requer uma execução RED anterior, vinculada à mesma especificação,
aos mesmos alvos e bytes do oráculo: árvore de testes, fixtures, conftests e
configurações enumeradas. RED exige falha de asserção na fase
de execução: importação, coleta, timeout, skip e xfail não são RED válido.
O escopo suportado no Core é `tests` ou um alvo nessa árvore. Opções de seleção
do pytest em `addopts` são anuladas; os IDs executados devem pertencer aos alvos
registrados, com execução de pelo menos um caso por alvo.

Antes de editar a implementação:

```bash
python -m marceloclaro.cli tdd-history red SPEC-ID --timeout 1200
```

O comando passa pelo primário MarceloClaro e executa os testes declarados pela
spec. `accepted: true` significa que o RED foi executado e registrado, sem
aprovar a entrega. Depois da correção, pode-se verificar o par explicitamente:

```bash
python -m marceloclaro.cli tdd-history green SPEC-ID --timeout 1200
```

Na conclusão de software, o primário usa `TDDRunner.run_delivery_test`. Ele
confere o RED antes de iniciar testes, executa e registra GREEN, preserva a
verificação granular existente em uma segunda execução e emite evidência selada.
`SpecVerifier` valida novamente o par e os hashes atuais. Falta, adulteração,
alteração de testes/spec/fixtures, GREEN anterior ao RED ou mudança posterior do
código fecham a entrega, inclusive no modo legado. Confiança e stakes recebem
resultado de falha nessa situação.

A execução autônoma estrita exige `network run ... --spec SPEC-ID` e confere o
RED antes de chamar um executor. A autocorreção também faz essa conferência
antes de aplicar o patch. Refatoração reprovada bloqueia o ciclo; não se presume
restauração de arquivos que o runtime não realizou.

Recibos possuem assinatura local e cadeia de hashes. Saída, JUnit, registro de
coleta e de fases pytest, versões dos testes e manifesto de fontes são
conservados no diretório privado `MCI_STATE_DIR/tdd-history` ou
`.mci_state/tdd-history`. A chave não integra artefatos públicos. O manifesto
cobre os tipos de fonte e configurações enumerados em `sdd/tdd_history.py`;
dependências externas e dados fora desse escopo exigem verificação própria.

`require_red_history=False` permite **inspeção explícita de critérios** e produz
`verification_scope: criteria_only`. Não é o caminho de entrega do primário nem
uma autorização para dispensar o histórico em uma entrega de software. A
inspeção não promove confiança. Specs sem `test_file` usadas em tarefas não
relacionadas a software conservam sua verificação de critérios.

Quando a versão atual já está verde e não existe RED autenticável, o sistema
fecha o gate. Ele não transforma logs arbitrários, hashes digitados ou falhas
fabricadas em uma execução no passado. Reexecução de uma versão anterior deve
registrar essa versão e a data efetiva da reexecução; histórico antigo incompleto
não é preenchido por presunção.

Assinatura e selos detectam adulteração de artefatos e claims de entrada. Não
isolam o dono do host ou um processo com acesso à mesma chave/código, nem validam
a qualidade do oráculo. Evidência é local, sem certificação externa. A limpeza
POSIX cobre o grupo criado para a fase; Windows nativo e processos que escapem
desse grupo exigem prova própria.

Spec e testes: R839. Evidências: `outputs/core-r839/`.
