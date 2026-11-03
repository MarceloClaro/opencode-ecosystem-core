# Piloto supervisionado de apoio à pesquisa — R931

**Status: protocolo com pendências. O piloto não foi executado.**

Esta entrega organiza a passagem de testes locais para um caso real de baixa
criticidade. Não implanta serviço, não inicia busca, inferência de pesquisa ou
treinamento, não lê corpus/dados pessoais nem altera permissões. Revisão do
protocolo por agente é revisão textual assistida, não execução da pesquisa ou
parecer científico humano independente.

- Contrato: [contrato.json](piloto-pesquisa-r931/contrato.json).
- Especificação: [SPEC-935-R931](../specs/SPEC-935-R931-piloto-pesquisa-supervisionado.md).
- Testes: [test_r931_research_pilot_contract.py](../tests/test_r931_research_pilot_contract.py).

## 1. Objetivo e escopo proposto

Avaliar a capacidade de apoiar uma pergunta bibliográfica aprovada, com origem
de cada referência, trilha de triagem e suporte localizado para cada alegação
central. O produto proposto é um **relatório interno revisado**, não uma revisão
sistemática concluída, recomendação clínica, manuscrito aprovado ou evidência de
eficácia do Core. O desenho acadêmico e a diretriz de relato dependem da pergunta.

Proposta conservadora: **1 operador, 1 tarefa por vez e até 20 referências
incluídas**. Esses números são limites propostos, não capacidade medida, SLA ou
configuração de enforcement já instalada. Limites de registros candidatos,
chamadas, tempo, memória e custo precisam ser congelados no G0. `null` significa
decisão pendente; não significa ilimitado, gratuito ou automaticamente permitido.

## 2. Evidência existente e o que não demonstra

| Fonte histórica | Observação | Limite |
|---|---|---|
| [R928](../outputs/core-r928/final-gates.json) | 469 testes selecionados; SDD 6/6; inferência/quantização do toy em CPU | Não demonstra qualidade bibliográfica, LLM real, SLA ou operação Android |
| [R929](evidence/r929/receipt.json) | 643 testes em seleção separada; persistência, CLI, grafo e diagnóstico | Não é aceite de suíte integral, produção ou validação científica |

Os testes **não foram somados**. Os recibos acima **não foram revalidados** para
a árvore atual nesta etapa; os testes documentais conferem o que os arquivos
arquivados dizem, não a autenticidade externa de sua emissão ou sua aplicação
a versões posteriores. Mudanças de fonte exigem verificação apropriada ao novo
candidato. Gates internos em shadow mode não substituem autorização humana.

O diagnóstico estrutural consultado nesta etapa tem 21 verificações aprovadas,
1 advertência e 0 falhas; não ensaia autenticação, inferência ou carga. A
advertência trata de **78 entradas históricas preservadas e não modeladas**:
não migrar/apagar por inferência nem tratar preservação como validação do conteúdo.

Outros limites preservados:

- A **suíte upstream** do ITS-FINE 0.0.15 não veio no TGZ (`not_shipped`). Obter
  origem oficial ou documentar risco residual e testes compensatórios antes de
  depender desse componente numa liberação; não inventar execução da suíte.
- O **treinamento em GPU** não está pronto neste WSL. Isso não impede pesquisa
  bibliográfica ou ensaios CPU, mas nem a GPU disponível autorizaria treino sem
  modelo, dados, receita e consentimento próprios.
- Gallery/OpenManus/LQC continuam inspeções estáticas, não dependências
  operacionais aprovadas para este piloto.

## 3. Gates de passagem — todos pendentes

| Gate | Evidência exigida | Responsabilidade |
|---|---|---|
| **G0 — escopo e autorização** | Pergunta, corpus, provedor/serviços, responsáveis, limites, baseline e métricas congelados; aceite vinculado ao SHA256 do contrato | Operador e responsável humano |
| **G1 — corpus admissível** | Corpus não vazio com identificadores, direitos de acesso e triagem; sem dados pessoais no piloto | Curadoria/dados |
| **G2 — qualidade de tarefa** | Comparação com baseline manual; matriz referência → alegação → recorte; revisão humana distinta do autor | Revisor humano |
| **G3 — segurança e recuperação** | Acesso real autorizado, cancelamento, queda de worker, retomada sem duplicação, logs sem segredos e restauração por hashes | Técnico/segurança |
| **G4 — operação restrita** | Medições brutas de tempo, memória, falhas e custo na carga congelada de uma tarefa por vez | Operação |
| **G5 — decisão de continuidade** | Revisão das evidências, desvios e riscos; aceite/recusa humano apenas para o escopo do piloto | Responsáveis humano/técnico/pesquisa |

Cada gate depende do anterior. Não substituir `pending` por `passed` sem anexar
evidência, identidade do responsável e aceite humano. Se houver mudança de
corpus, provedor, orçamento ou método depois do congelamento, registrar desvio
e novo contrato/aceite antes de executar. Aumento de escala, publicação externa
e produção exigem **contrato de release separado**, mesmo depois de G5.

O JSON não é um mecanismo de autorização ou controle de acesso: nenhuma rotina
de implantação foi adicionada para interpretar esses campos. Ainda será preciso
exercitar os controles reais. Aprovação documental **não concede autorização**
para executar o piloto e não certifica segurança ou qualidade científica.

## 4. Medidas propostas, sem resultados

| Medida | Numerador / denominador ou população | Alvo proposto |
|---|---|---|
| Cobertura de metadados | Incluídas conferidas em fonte primária / todas as incluídas | 100% |
| Rastreabilidade de alegações | Alegações centrais com suporte localizado e aceite humano / todas as centrais inventariadas | 100% |
| Alegações sem suporte | Contagem no relatório não vazio, incluindo pendências | 0 |
| Documentação da triagem | Candidatos com decisão, motivo, origem e responsável / todos os recuperados | 100% |
| Latência p95 | Workload, N e janela previamente definidos; falhas/timeouts separados | A definir |
| Memória máxima | Árvore de processos no host/runtime escolhido | A definir |
| Custo total | Todas as chamadas, tentativas e falhas, com tarifas/data | A definir |

Resultados, tamanho de amostra e medições permanecem nulos. População ou
denominador vazio **não passa**; `0/0` não é 100%. O revisor humano inventaria
as alegações para evitar selecionar apenas as fáceis. Os alvos de integridade
não medem originalidade, utilidade, causalidade ou validade científica externa.
Congelar baseline, workload e critérios antes da execução; calibração não deve
ser relatada como avaliação final. Se houver ajuste posterior, usar novo protocolo.

## 5. Auditoria bibliográfica mínima

Para cada registro/alegação: DOI ou identificador persistente quando disponível;
URL primária dos metadados; data; autoria/título/ano conferidos; licença ou base
legal de acesso; nível efetivamente lido (metadados, abstract ou texto integral);
alegação; localizador de suporte; limites; decisão/motivo de triagem; revisor e
status. Preservar contradições e casos negativos encontrados sem fabricar sua
existência, tamanho ou um consenso.

Referência não confirmada recebe `[NÃO VERIFICADA]` e não sustenta alegação
central no relatório aceito. Metadados corretos não provam que o conteúdo sustenta
a frase; abstract não é texto integral lido. Não usar Sci-Hub, contornar paywall
ou redistribuir texto sem direito. Se houver apenas metadados/abstract, limitar
a alegação ao conteúdo acessível ou registrar pendência.

Uma mesma revisão por IA ou banca simulada não constitui revisor humano,
avaliação por pares ou aprovação editorial. Dados humanos, clínicos ou pessoais
ficam fora deste piloto; eventual inclusão exige revisão específica de ética,
consentimento e proteção de dados, sem presumir aprovação institucional.

## 6. Parada, recuperação e riscos

Parar antes de efeitos adicionais se houver orçamento excedido, acesso sem
direito, segredo/dado pessoal, alegação central não verificada, hash divergente
ou cleanup incerto. Preservar logs permitidos e artefatos parciais claramente
rotulados; não publicar sucesso a partir de uma saída antiga.

Ensaios ainda necessários: cancelar e conferir encerramento de processos;
interromper worker sem falso sucesso; restaurar backup por hashes; retomar sem
duplicação; testar autenticação e trilha de acesso no caminho real. Para o piloto
local, acesso autorizado ao host não deve ser confundido com autenticação de
um serviço multiusuário. Nenhum desses ensaios end-to-end foi feito por R931.

| Risco | Tratamento antes da execução |
|---|---|
| Métricas favorecem corpus escolhido | Congelar critérios/baseline e declarar seleção/limites |
| Fonte maliciosa contém instruções | Tratar texto recuperado como dado; sem execução de comandos/hooks |
| Custo/tempo ou candidatos sem teto | Congelar orçamento de chamadas/candidatos/tempo/custo; testar parada |
| Logs expõem dados | Minimizar conteúdo e aprovar retenção; sem credenciais em recibos |
| Integridade documental vira overclaim | Separar testes do contrato, ensaios do piloto e liberação de produção |

## 7. Verificação documental e próximo marco

```bash
python3 -m pytest tests/test_r931_research_pilot_contract.py -q
```

Esses testes verificam consistência, fronteiras e correspondência com recibos
históricos. Não executam pesquisa nem demonstram que os controles planejados
estão implantados. O gate SDD desta entrega é somente do contrato R931; não
reutiliza o GREEN R928 como aceite da árvore atual ou da produção.

**Pergunta necessária para abrir o G0:** qual é a primeira pergunta de pesquisa
e qual corpus público/licenciado poderá ser usado? Depois disso, delimitar
provedor, responsáveis e orçamento e pedir aceite do contrato congelado. Não
exigir que o usuário decida todos os campos agora nem escolher um tema por ele.
