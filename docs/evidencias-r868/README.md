# Resumos públicos da verificação local R868

Estes arquivos contêm somente campos selecionados e sanitizados de verificações
locais. Não incluem logs brutos, prompts, caminhos privados, conteúdo de alvos
privados ou credenciais. Os achados HTML publicados são de um fixture controlado
do operador, com 115 bytes.

| Arquivo | Alcance |
| --- | --- |
| [diagnostico-e-catalogo.json](diagnostico-e-catalogo.json) | Diagnóstico estrutural e snapshot separado do catálogo HTTP; nenhum comprova inferência |
| [analise-direta-controlada.json](analise-direta-controlada.json) | Inspeção estática e explicação diretas, alvo controlado intocado, worker com rede privada |
| [mcp-e-tentativas.json](mcp-e-tentativas.json) | Status MCP concluído, tentativas analíticas falhas, saída sem recibo bloqueada e timeout |
| [sonda-inferencia-local.json](sonda-inferencia-local.json) | Resposta de modelo em endpoint loopback, sem isolamento ou observação de saída externa do processo de inferência |
| [testes-e-ci.json](testes-e-ci.json) | Regressões específicas e leitura do JUnit anterior; CI remota e suíte consolidada atual não são afirmadas |

`source_sha256` identifica os bytes dos artefatos originais utilizados para
preparar cada resumo. Esses hashes possibilitam comparação quando o original
estiver acessível; não assinam o relato, não permitem reconstruir o original e
não constituem validação externa. Campos históricos conservam seu próprio
escopo. Ausência de relato de tráfego externo não equivale a ausência de tráfego.

O assistente não tem comprovação de operação autônoma universal por LLM.
Instalação, status, análise direta e entrega conduzida por modelo permanecem
resultados distintos.

O [fechamento R869](verificacao-final.json) registra a suíte integral concluída,
a execução de coordenação e o vínculo do candidato preparado. Os cinco
snapshots anteriores permanecem históricos e não recebem números posteriores.
