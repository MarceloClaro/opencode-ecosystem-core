# Consolidação DOAJ — 17/09/2026 (real)

Fonte: API aberta do DOAJ (https://doaj.org/api/search/articles/...)
Strings executadas: D1..D11 (ver LOG_EXECUCAO_REAL_R522.md)
Arquivos: execucao_real/doaj_*.json (exportações brutas preservadas)

Método: consolidação programática por título único; sobreposição entre strings mantida
como duplicada no fluxo (a deduplicação oficial ocorre na triagem, como previsto no protocolo).

## Saída do consolidado
- Total de registros recuperados (soma bruta por string): 33
- Itens únicos por título: 35 (alguns recuperados em mais de uma string)
- Itens na janela 2020-2025 listados no LOG (Seção 2)
- Fora da janela 2020-2025: registros de 2018/2026 arrolados mas não elegíveis sem emenda
  formal e prospectiva do protocolo (2026 apenas como atualização contextual fora do corpus)

## Limitação declarada
Esta consolidação NÃO constitui o conjunto incluído da revisão. É apenas a camada de
recuperação na base DOAJ. Scopus, WoS, SciELO, Educ@, CAPES e Google Acadêmico seguem
pendentes; a triagem texto completo não foi realizada.
