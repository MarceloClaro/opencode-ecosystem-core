---
spec_id: SPEC-935-R989
title: Conselho de treze cientistas com autonomia delimitada
component: scientific_lab.council
status: draft
test_file: tests/test_r989_scientific_council.py
---

# R989 — Conselho científico Feynman, método científico e decisão sob incerteza

## Objetivo

Atender ao pedido explícito de treze cientistas de busca, revisão, análise,
validação e auditoria. São agentes computacionais, não pessoas nem revisão por
pares independente. MarceloClaro permanece o único primário. Os especialistas
existentes continuam disponíveis; os novos perfis acrescentam um contrato comum
de conselho, não novos conectores, estatística ou memória paralela.

## Critérios de aceitação

1. Exatamente 13 perfis distintos: problema, busca, curadoria, referências,
   metodologia, estatística, análise qualitativa, reprodução, explicação Feynman,
   refutação adversarial, teoria dos jogos, ética/proveniência e auditoria final.
   Criação/registro somente por `agent_profile_action`; todos managed-v1,
   subordinados ao primário, com edição/rede/delegação direta negadas.
2. O plano declara fases, orçamento, quatro campos obrigatórios da saída e
   mecanismo, observações, inferências, refutador e menor experimento. Planejar
   não executa modelos; ausência de fontes não é inventada como busca concluída.
3. O ciclo de execução usa AutonomousCoordinator sob MarceloClaro, com contrato
   textual por etapa, uma tentativa por papel, no máximo 13 papéis e prazo
   global de até 600s. Exige confirmação explícita. Falha, timeout, limite ou
   cancelamento interrompem o ciclo; não há repetição automática de execução
   incerta. Contexto das etapas é delimitado, identificado como dado não confiável.
   Conferir o prazo novamente depois de validar o parecer; processamento tardio
   não pode produzir uma etapa aceita. Parecer `partial` é entrega válida
   (evidência insuficiente) e não interrompe; `blocked` (sem entrega) interrompe.
4. Resultado somente conta como entrega quando o executor reporta tentativa real
   concluída, agente correto e JSON conforme contrato. Toda referência deve apontar
   para ID e recorte literal do corpus fornecido. Hash/recorte conferido significa
   correspondência ao corpus, não autenticidade da fonte. Quebra de contrato
   interrompe; 13 votos não produzem verdade nem validação externa.
5. FeynmanGates FEG-01..06 orientam completude declarativa, nunca prova de
   compreensão. Não invocar teachback nem gerar selo de validação humana.
6. Minimax regret usa matriz explícita, finita, retangular e limitada; retorna
   todos os empates e arrependimentos por ação. Utilidades são declaradas pelo
   operador, sem priors/pesos ocultos. Nenhuma regra clínica ou probabilidade do
   ClinicalGameTheoryEngine é transplantada. A ação prioriza investigação, não
   a verdade de hipótese nem tratamento.
7. CLI `council list|plan|run` pela fachada científica; `run` exige fontes e
   `--confirm`. Configuração OpenCode preserva os demais agentes/comandos.
   Registro/ativação, execução e validação científica são estados distintos.

## Limites

Sem autoedição, instalação, publicação, coleta de participantes ou uso de
credenciais. Busca autônoma nesta versão formula/verifica estratégia sobre o
corpus; acesso externo continua pelos conectores autorizados do primário, não
pelos cientistas. Os 13 papéis podem compartilhar provedor: não são 13 fontes
independentes. Relatórios do executor não têm autenticação externa independente.
Revisão humana permanece necessária. OpenShell é etapa separada, não instalado.

## Verificação

Testes com executor falso claramente identificado testam coordenação e falhas,
não inferência. Perfil real validado separadamente. RED antes da implementação;
GREEN e gates locais registrados em recibos separados, sem alterar este contrato.
