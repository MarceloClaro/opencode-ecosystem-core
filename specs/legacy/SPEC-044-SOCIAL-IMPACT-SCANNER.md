# SPEC-044: Social Impact Scanner — Avaliação de Impacto Social, Ambiental e Econômico

## 1. Visão Geral
O `SocialImpactScanner` é uma nova camada analítica para avaliar o **impacto social, ambiental e econômico** de pesquisas científicas, manuscritos e projetos no OpenCode Ecosystem. Integra 6 metodologias internacionais padronizadas para gerar um **parecer consolidado de impacto social**.

Este scanner funciona como um **raciocínio metacognitivo** (habilidade de 4ª ordem) que analisa não apenas o conteúdo técnico-científico, mas sua **relevância social, retorno para a sociedade e alinhamento com agendas globais de desenvolvimento sustentável**.

## 2. Metodologias Integradas

### 2.1 SROI (Social Return on Investment) — ISO 26000
- **Ratio SROI**: Valor social criado por unidade de investimento
- **Stakeholder Mapping**: Identificação e priorização de partes interessadas
- **Materialidade**: Temas sociais mais relevantes para cada stakeholder
- **ISO 26000**: 7 temas centrais: Governança, Direitos Humanos, Práticas Trabalhistas, Meio Ambiente, Práticas Justas, Consumidores, Comunidade

### 2.2 Social Value International — Deadweight/Attribution/Displacement
- **Deadweight**: O que teria acontecido sem a intervenção (contrafactual)
- **Attribution**: Percentual do resultado atribuível à intervenção
- **Displacement**: Efeitos de deslocamento (o que foi deslocado/sacrificado)
- **Drop-off**: Declínio do impacto ao longo do tempo
- **Duration**: Duração esperada do impacto

### 2.3 Theory of Change (ToC)
- **Inputs**: Recursos investidos (financeiros, humanos, materiais)
- **Activities**: Atividades realizadas
- **Outputs**: Produtos diretos gerados
- **Outcomes**: Mudanças de curto/médio prazo
- **Impact**: Mudanças de longo prazo (atribuíveis)

### 2.4 IRIS+ (GIIN) — 4 Indicadores Padronizados
1. **OD01**: Descrição do Produto/Serviço Social
2. **OD02**: Objetivo Social Declarado
3. **OD03**: Beneficiários Diretos
4. **OD04**: Beneficiários Indiretos
- *Nota: IRIS+ possui centenas de indicadores; estes 4 são o núcleo mínimo padronizado para investidores de impacto*

### 2.5 B Impact Assessment (B Lab)
- **Governança**: Missão, transparência, prestação de contas
- **Trabalhadores**: Remuneração, benefícios, saúde e segurança
- **Comunidade**: Engajamento local, diversidade, impacto social
- **Meio Ambiente**: Gestão ambiental, uso de recursos, emissões
- **Clientes**: Qualidade, privacidade, benefício ao cliente

### 2.6 SDG (UN Agenda 2030) — Rastreamento de ODS
- Mapeamento dos 17 ODS com indicadores relevantes
- Alinhamento temático entre a pesquisa e cada ODS
- Score de contribuição projetada por ODS
- Rastreamento de metas específicas

## 3. Arquitetura

### 3.1 Classe Principal
- **`SocialImpactScanner`** em `skills/system/academic-audit/social_impact_scanner.py`

### 3.2 Sub-módulos
| Sub-módulo | Responsabilidade | Framework |
|-----------|-----------------|-----------|
| `SROIAnalyzer` | Cálculo de ratio SROI, stakeholder mapping, ISO 26000 | SROI + ISO 26000 |
| `SocialValueEngine` | Deadweight, attribution, displacement, drop-off | Social Value Intl. |
| `TheoryOfChangeBuilder` | ToC framework input→impact | Theory of Change |
| `IRISPlusReport` | 4 indicadores padronizados GIIN | IRIS+/GIIN |
| `BImpactAssessor` | 5 dimensões de avaliação | B Lab |
| `SDGTracker` | Mapeamento ODS + score de contribuição | UN Agenda 2030 |

### 3.3 Saídas
- `SocialImpactReport`: Relatório consolidado com:
  - Resumo executivo do impacto social
  - Ratios e scores por metodologia
  - Parecer de impacto social qualitativo
  - Recomendações de melhoria
  - Score consolidado (0-100)

## 4. Casos de Teste (TDD)

### CT-4401 (SROI Ratio Analysis)
Garante que o cálculo do SROI ratio:
- Aceite inputs financeiros e sociais
- Calcule corretamente o ratio = valor social / investimento
- Identifique e aplique deadweight, attribution e displacement
- Valide a sanidade do resultado (ratio >= 0)

### CT-4402 (Theory of Change Framework)
Garante que a ToC:
- Construa a cadeia input→activities→outputs→outcomes→impact
- Associe indicadores verificáveis a cada elo
- Gere a narrativa de mudança (change narrative)
- Identifique preconditions e assumptions

### CT-4403 (B Impact Assessment Scoring)
Garante que o BIA:
- Calcule scores para 5 dimensões (G, W, C, E, C)
- Pondere corretamente (Governança 20%, Trabalhadores 20%, Comunidade 25%, Meio Ambiente 20%, Clientes 15%)
- Gere score total (0-200)
- Identifique pontos fortes e fracos por dimensão

### CT-4404 (IRIS+ Standard Indicators)
Garante que o relatório IRIS+:
- Preencha os 4 indicadores obrigatórios (OD01-OD04)
- Valide formato padronizado GIIN
- Inclua metadados de verificação
- Gere saída compatível com IRIS+ Catalog

### CT-4405 (SDG Alignment Tracking)
Garante que o SDG Tracker:
- Mapeie corretamente temas de pesquisa para ODS
- Calcule score de alinhamento (0-100)
- Identifique os 3 ODS mais relevantes
- Projeta contribuição por meta específica

### CT-4406 (Consolidated Social Impact Report)
Garante que o relatório final:
- Integre todas as 6 metodologias
- Gere parecer qualitativo fundamentado
- Calcule score consolidado de impacto social
- Inclua diagnóstico de ratio (custos vs. benefícios sociais)
- Seja exportável em formato JSON legível
