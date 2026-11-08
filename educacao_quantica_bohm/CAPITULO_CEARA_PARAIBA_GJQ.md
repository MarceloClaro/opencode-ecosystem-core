# Computação quântica no Ceará e na Paraíba: parceria de estudo e por que GJQ {#ceara-pb-gjq}


Este capítulo explica, sem inventar convênios, **onde a computação quântica
acontece no Ceará e na Paraíba**, como este livro se conecta a essa rede e por
que a plataforma **GJQ/Tiangong** foi escolhida para os testes de hardware.

![**Figura R5.** Rede de estudo: o Ceará forma e media; a Paraíba oferece
infraestrutura pública (CIQuanta); o GJQ/Tiangong oferece hardware e API; o livro
registra o caminho.](../livro/figuras_geradas/fig26_ceara_pb_gjq.png){#fig-r5}

## 1. Um mapa honesto

| Território | O que existe | O que este livro usa |
|---|---|---|
| **Ceará** | UFC, UECE, IFCE, rede estadual; grupos de física, computação e educação | mediação pedagógica, formação de professores e experimentos didáticos |
| **Paraíba** | CIQuanta, centro público de computação quântica; UFPB e UFCG | referência de infraestrutura pública e acesso por política |
| **Internacional** | GJQ/Tiangong, com hardware supercondutor e simuladores | execução real, API, QASM e task IDs |

> **Cuidado:** não afirmamos que exista um centro de hardware quântico no Ceará.
> O Ceará entra pela **formação e pela mediação**; a Paraíba entra pela
> **infraestrutura pública**; o GJQ entra pelo **acesso internacional**.

## 2. O que existe no Ceará

O Ceará tem universidades e institutos com grupos de física, computação,
engenharia e educação. O livro se apoia nessa rede para:

- traduzir conceitos para a escola básica;
- formar professores que não são físicos;
- testar sequências didáticas de 7, 21 e 70 minutos;
- produzir material em português, com ponte sonora de chinês.

O livro **não** afirma que UFC, UECE ou IFCE tenham um laboratório de hardware
quântico aberto; afirma que há **capital humano** para ensinar e pesquisar. A
diferença entre “ter grupo” e “ter hardware” é parte da honestidade científica.

## 3. O que existe na Paraíba: CIQuanta

O **CIQuanta** é o Centro Internacional de Computação e Tecnologias Quânticas do
Estado da Paraíba, em João Pessoa. Segundo o portal do centro, a estrutura
reúne laboratórios, auditórios e dois computadores (20 + 100 qubits), com uma
réplica aberta a visitas. A plataforma em nuvem é
`cloudciquanta.secties.pb.gov.br`.

O que isso significa para o livro:

- a Paraíba tem uma **política pública** de computação quântica, não apenas um
  laboratório isolado;
- o acesso depende de cadastro, fila e política de uso;
- o CIQuanta é a referência brasileira mais próxima para o leitor do Nordeste.

> **Limite:** disponibilidade, cadastro e preço podem mudar. Confirme no portal
> antes de planejar uma aula que dependa do CIQuanta.

## 4. Por que GJQ/Tiangong

O **GJQ/Tiangong** é uma plataforma internacional com:

- **Guoji No. 8** (20 qubits) e **Baihua** (156 qubits), ambos listados como
  hardware supercondutor;
- simuladores de amplitude, ruído e tensor network (MPS);
- editor QASM 2.0 e API Python (`gjq-client`);
- Sessions, Estimator, Sampler e task IDs auditáveis;
- documentação pública e exemplos de Bell, GHZ, CHSH, Hadamard test e SWAP test.

A escolha não foi “porque é mais bonito”. Foi porque o livro precisava de:

| Critério | Simulador local | CIQuanta | GJQ/Tiangong |
|---|---|---|---|
| Hardware real | não | sim | sim |
| API Python | não | portal | sim |
| QASM 2.0 | local | portal | editor + API |
| Task ID | não | depende | sim |
| Reprodução por JSON | sim | parcial | sim |
| Uso didático | alto | alto | alto |

O GJQ permite que o aluno veja **o mesmo circuito** no simulador e no hardware,
com um identificador de tarefa. É essa ponte que o livro registra.

## 5. O que é “parceria” nesta obra

A parceria é de **estudo e acesso**, não um convênio institucional formal:

- **Ceará:** formação, mediação e escrita;
- **Paraíba:** referência pública e infraestrutura;
- **GJQ:** acesso a hardware e API;
- **Livro:** código aberto, resultados, task IDs e limitações.

Não há, nesta edição, MOU, contrato de exclusividade ou endosso oficial das
instituições citadas. Se uma instituição quiser formalizar, o caminho é:
carta de intenção, plano de aulas, política de dados e revisão ética.

## 6. O que o aluno pode fazer

1. **Comece no simulador:** rode o Bell, o GHZ e o SWAP test localmente.
2. **Compare com o hardware:** envie o mesmo circuito ao Guoji08 ou ao Baihua.
3. **Calcule a diferença:** fidelidade proxy, sobreposição e comprimento de Bloch.
4. **Documente:** guarde task ID, counts, data e backend.
5. **Não generalize:** uma execução não é um ranking permanente.

## 7. O que falta

- acordo formal com CIQuanta e GJQ para uso em larga escala;
- tempo de hardware para turmas;
- formação de professores em QASM e Python;
- mais datasets e replicações;
- validação em hardware do VQC de 4 qubits (o piloto atual é simulado).

> **Mensagem final:** o Ceará ensina, a Paraíba oferece infraestrutura, o GJQ executa e o
> livro documenta. Essa é a parceria possível hoje — e ela já produz resultados
> reais, com limites declarados.

## Referências deste capítulo

CIQUANTA. *Centro Internacional de Computação e Tecnologias Quânticas do Estado
da Paraíba*. Disponível em: <https://cloudciquanta.secties.pb.gov.br>. Acesso
em: 7 nov. 2026.

TIANGONG / CETC-ICQ. *Quantum Programming Framework User Guide*. Disponível em:
<https://tiangongqs.com/docs/quantum/QuantumProgrammingFramework.html>. Acesso
em: 7 nov. 2026.

TIANGONG / CETC-ICQ. *Programming Quantum Circuits*. Disponível em:
<https://tiangongqs.com/docs/quantum/ProgrammingQuantumCircuits.html>. Acesso
em: 7 nov. 2026.

UNIVERSIDADE FEDERAL DO CEARÁ. Portal institucional:
<https://www.ufc.br>. Acesso em: 7 nov. 2026.

UNIVERSIDADE ESTADUAL DO CEARÁ. Portal institucional:
<https://www.uece.br>. Acesso em: 7 nov. 2026.

INSTITUTO FEDERAL DO CEARÁ. Portal institucional:
<https://www.ifce.edu.br>. Acesso em: 7 nov. 2026.