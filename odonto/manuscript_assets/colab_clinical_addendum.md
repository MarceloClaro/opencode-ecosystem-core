# 28. Adendo clínico v1.3.3 — validação interna exploratória

**Estado executado separadamente:** a análise abaixo foi executada sobre o suplemento clínico público Table S1, fixado no commit `e5868fe5` e verificado por SHA-256. Os resultados anteriores do perfil `CI_SMOKE` são sintéticos e não representam desempenho clínico.

**Coorte e alvo:** 997 transições H→H/H→C foram reconstruídas (84 eventos). Uma transição com intervalo de seguimento zero foi excluída: **996 transições, 83 eventos, 81 crianças**; seguimento de 2–5 meses. O alvo é incidência de cárie em um dente inicialmente hígido.

**Método:** dois modelos de regressão logística penalizada, mínimo clínico e clínico-espacial; cinco folds externos e três internos estratificados e agrupados por criança; seleção de regularização dentro do treino; 1.000 reamostragens bootstrap por criança das predições fora da amostra. A classe positiva é localizada explicitamente. Variáveis futuras, o desfecho e o intervalo de seguimento não entram como preditores.

| Modelo | AP | ROC-AUC | Brier | Inclinação de calibração |
|---|---:|---:|---:|---:|
| Clínico mínimo | 0,166 | 0,686 | 0,0806 | 0,516 |
| Clínico-espacial | 0,178 | 0,737 | 0,0754 | 0,605 |

A diferença de AP foi 0,012, com intervalo bootstrap de 95% de −0,046 a 0,058. Portanto, a vantagem do modelo espacial **não está estabelecida**. A calibração ainda precisa melhorar. Não houve validação externa, microbioma real pareado nem imagem clínica pareada. Nenhum resultado autoriza uso assistencial.

**Fluxo atualizado:** Table S1 pública → verificação de versão/hash → reconstrução dente-visita → exclusão de intervalo não positivo → atributos disponíveis em t → CV aninhada agrupada por criança → predições fora da amostra → discriminação, calibração e bootstrap → validação externa prospectiva antes de qualquer avaliação de uso clínico.

A célula seguinte reproduz a análise depois de executar as células anteriores de reconstrução longitudinal. Salva somente estatísticas agregadas e figuras em `/content/OdontoCA_v1_3/09_clinical_addendum`; não exporta registros individuais.
