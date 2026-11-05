# Relatório de dados — Censo Escolar 2021–2024

**TCC:** Dupla excepcionalidade no Brasil: autismo, altas habilidades/superdotação e desafios de identificação
**Autor:** Marcelo Claro Laranjeira
**Data de extração:** 5 de novembro de 2026
**Fontes:** Sinopses Estatísticas da Educação Básica do INEP (2021, 2022, 2023 e 2024).

---

## 1. Fontes e tabelas

| Ano | Arquivo | Tabelas usadas |
|---|---|---|
| 2021 | `sinopses_estatisticas_censo_escolar_2021.zip` | 1.3; 1.43 (classes comuns); 1.49 (classes exclusivas) |
| 2022 | `sinopses_estatisticas_censo_escolar_2022.zip` | 1.3; 1.43; 1.49 |
| 2023 | `sinopse_estatistica_censo_escolar_2023.zip` | 1.3; 1.44; 1.50 |
| 2024 | `sinopse_estatistica_censo_escolar_2024.zip` | 1.3; 1.44; 1.50 |

As tabelas 1.43/1.49 (2021–2022) e 1.44/1.50 (2023–2024) trazem as matrículas da educação especial em classes comuns e exclusivas, por tipo de deficiência, transtorno global do desenvolvimento ou altas habilidades/superdotação. A tabela 1.3 traz o total de matrículas da educação básica.

Em 2021, a categoria aparece como **"Autismo"**; a partir de 2022, como **"Transtorno do Espectro Autista"**. A comparação assume que se trata da mesma categoria conceitual.

## 2. Série nacional

| Ano | TEA | AH/SD | Total educação básica | % TEA | % AH/SD | Razão TEA/AH/SD |
|---|---:|---:|---:|---:|---:|---:|
| 2021 | 294.394 | 23.758 | 46.668.401 | 0,631 | 0,051 | 12,4 |
| 2022 | 429.521 | 26.815 | 47.382.074 | 0,907 | 0,057 | 16,0 |
| 2023 | 636.202 | 38.019 | 47.304.632 | 1,345 | 0,080 | 16,7 |
| 2024 | 918.877 | 44.171 | 47.088.922 | 1,951 | 0,094 | 20,8 |

**Crescimento 2021–2024:** TEA +212%; AH/SD +86%.

## 3. Dados regionais (2024)

| Região | TEA | AH/SD | Razão TEA/AH/SD | Total educação especial |
|---|---:|---:|---:|---:|
| Norte | 89.150 | 3.671 | 24,3 | 198.915 |
| Nordeste | 282.410 | 6.253 | 45,2 | 649.724 |
| Sudeste | 340.751 | 11.584 | 29,4 | 701.764 |
| Sul | 144.536 | 17.985 | 8,0 | 361.307 |
| Centro-Oeste | 62.030 | 4.678 | 13,3 | 165.115 |
| **Brasil** | **918.877** | **44.171** | **20,8** | **2.076.825** |

## 4. Ajuste linear e cenários

**Ajuste linear (2021–2024):**

- TEA: inclinação de 208.013 matrículas/ano; R² = 0,9755.
- AH/SD: inclinação de 7.244 matrículas/ano; R² = 0,9594.

**Cenários para 2025–2027:**

| Cenário | TEA 2025 | AH/SD 2025 | TEA 2027 | AH/SD 2027 | Razão 2027 |
|---|---:|---:|---:|---:|---:|
| Linear | 1.089.781 | 51.301 | 1.505.807 | 65.790 | 22,9 |
| Moderado (TEA +20%/ano; AH/SD +15%/ano) | 1.102.652 | 50.797 | 1.587.819 | 67.179 | 23,6 |
| Convergência (TEA +10%/ano; AH/SD +25%/ano) | 1.010.765 | 55.214 | 1.223.025 | 86.271 | 14,2 |

Os cenários são **condicionais e exploratórios**. Não são previsões. O modelo log-linear para o TEA foi testado, mas produziu projeções incompatíveis com o tamanho da educação básica (cerca de 9 milhões em 2030) e foi descartado.

### 4.1 Extremos estaduais (2024)

| UF | TEA | AH/SD | Razão TEA/AH/SD |
|---|---:|---:|---:|
| Ceará | 69.888 | 574 | 121,8 |
| Pernambuco | 44.133 | 558 | 79,1 |
| São Paulo | 161.502 | 4.388 | 36,8 |
| Minas Gerais | 86.371 | 2.574 | 33,6 |
| Espírito Santo | 26.224 | 1.506 | 17,4 |
| Santa Catarina | 45.739 | 2.836 | 16,1 |
| Distrito Federal | 11.806 | 2.795 | 4,2 |
| Paraná | 50.586 | 12.807 | 3,9 |

Fonte: elaborado pelo autor com base em INEP (2024). Tabelas 1.44 e 1.50.

O contraste entre Ceará e Paraná é o mais expressivo: os dois estados têm ordens de grandeza semelhantes de matrículas de TEA, mas o Paraná identifica 12.807 matrículas de AH/SD, contra 574 no Ceará. A diferença sugere que a identificação depende de critérios, instrumentos e prioridades locais, e não apenas da prevalência.

## 5. Limitações dos dados

1. **Categorias não exclusivas:** a soma das categorias de deficiência, transtorno global do desenvolvimento e AH/SD supera o total de matrículas da educação especial, indicando que um mesmo estudante pode ser contabilizado em mais de uma categoria.
2. **Ausência de cruzamento TEA × AH/SD:** o Censo não publica a tabulação conjunta; não é possível estimar a dupla excepcionalidade.
3. **Matrículas, não pessoas:** os números são de matrículas, não de estudantes únicos.
4. **Série curta:** quatro pontos anuais limitam a robustez dos modelos.
5. **Mudança de nomenclatura:** "Autismo" (2021) e "Transtorno do Espectro Autista" (2022–2024).
6. **Declaração escolar:** os dados dependem do registro realizado pelas escolas; subnotificação e diferenças de critério são possíveis.

## 6. Reprodução

```bash
python3 scripts/analise_dados.py
```

O script gera:

- `dados/serie_nacional.csv`
- `dados/estados_2024.csv`
- `dados/regioes_2024.csv`
- `dados/cenarios.csv`
- `dados/resumo_analise.json`

## 7. Referências das fontes

INEP. **Sinopse Estatística da Educação Básica 2021**. Brasília, DF: Inep, 2021. Disponível em: https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopses_estatisticas_censo_escolar_2021.zip. Acesso em: 5 nov. 2026.

INEP. **Sinopse Estatística da Educação Básica 2022**. Brasília, DF: Inep, 2022. Disponível em: https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopses_estatisticas_censo_escolar_2022.zip. Acesso em: 5 nov. 2026.

INEP. **Sinopse Estatística da Educação Básica 2023**. Brasília, DF: Inep, 2023. Disponível em: https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopse_estatistica_censo_escolar_2023.zip. Acesso em: 5 nov. 2026.

INEP. **Sinopse Estatística da Educação Básica 2024**. Brasília, DF: Inep, 2024. Disponível em: https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopse_estatistica_censo_escolar_2024.zip. Acesso em: 5 nov. 2026.
