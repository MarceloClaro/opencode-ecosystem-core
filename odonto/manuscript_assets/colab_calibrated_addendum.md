# 29. Recalibração aninhada por criança — análise corrigida

**Correção da validação:** o resultado anterior (AP 0,2318/0,2414) é reproduzível no scikit-learn 1.6.1, porém `StratifiedGroupKFold(shuffle=True)` dessa versão pode desalinhar as contagens de classe e os grupos. A célula abaixo reproduz a lógica corrigida da divisão em qualquer uma das versões testadas, por permutação explícita de rótulos de grupo seguida de `shuffle=False`. Com essa divisão corrigida, os resultados-base são AP 0,1665/0,1784 e ROC-AUC 0,6865/0,7372 para os modelos mínimo/espacial. A mudança nos números decorre da divisão das crianças, sem representar piora ou melhora biológica.

**Calibração sem vazamento:** em cada uma das cinco dobras externas, o C é escolhido nas três dobras internas. As previsões cruzadas internas treinam dois mapas de risco: intercepto apenas e intercepto mais inclinação. Eles são aplicados somente ao teste externo. O ajuste do mapa não usa os rótulos das crianças do teste externo. Os intervalos das diferenças vêm de bootstrap pareado por criança das previsões externas já ajustadas.

| Modelo | Probabilidade | AP | ROC-AUC | Brier | Log-loss |
|---|---|---:|---:|---:|---:|
| Clínico mínimo | Original corrigido | 0,1665 | 0,6865 | 0,08060 | 0,28836 |
| Clínico mínimo | Intercepto + inclinação | 0,1920 | 0,7153 | 0,07451 | 0,26802 |
| Clínico espacial | Original corrigido | 0,1784 | 0,7372 | 0,07536 | 0,26899 |
| Clínico espacial | Intercepto + inclinação | 0,1759 | 0,7387 | 0,07395 | 0,26381 |

No modelo mínimo, a diferença de Brier (recalibrado − original) foi −0,00610, IC95% bootstrap por criança [−0,01173; −0,000672]. A melhora dos demais desfechos e do modelo espacial requer cautela; não há validação externa nem evidência de utilidade clínica. Esta é uma análise exploratória posterior à avaliação original. A saída contém somente métricas agregadas e figuras, em `/content/OdontoCA_v1_3/10_calibracao`.
