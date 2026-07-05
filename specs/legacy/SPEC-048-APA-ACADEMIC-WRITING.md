# SPEC-048: Normas APA para Escrita Acadêmica

## 1. Visão Geral
Especificação de Desenvolvimento Orientado a Documentação (SDD) para implementação de normas APA 7ª edição no ecossistema OpenCode, com foco em Projetos Finais (PF) e documentos acadêmicos.

## 2. Objetivos
- Formalizar as regras de formatação APA para geração automática de documentos
- Implementar validadores de conformidade para citações e referências
- Criar agentes especializados em revisão bibliográfica APA
- Integrar com o pipeline de produção acadêmica existente

## 3. Escopo

### 3.1 Componentes Afetados
- **Skills**: `apa-academic-writing`, `edicao-cirurgica`, `potentiality-estimator-v2`
- **Agentes**: `12_agente_auditoria_bibliografica_abnt`, `44_agente_correcao_textual_qualis`
- **MCPs**: `sequential-thinking`, `memory`, `websearch`
- **Templates**: Modelos LaTeX para documentos acadêmicos

### 3.2 Requisitos Funcionais

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-01 | Validação de formatação de página (margens, espaçamento) | Alta |
| RF-02 | Conversão automática de citações para formato APA | Alta |
| RF-03 | Geração de referências bibliográficas | Alta |
| RF-04 | Validação de estrutura de documento | Média |
| RF-05 | Verificação de conformidade com normas institucionais | Alta |
| RF-06 | Suporte a múltiplos estilos (APA, Vancouver) | Média |
| RF-07 | Integração com gestores de referência (Zotero, Mendeley) | Baixa |

### 3.3 Requisitos Não-Funcionais

| ID | Requisito | Métrica |
|----|-----------|---------|
| RNF-01 | Performance | Validação completa em < 5 segundos |
| RNF-02 | Precisão | 99% de acerto na formatação |
| RNF-03 | Disponibilidade | 99.9% de uptime |
| RNF-04 | Usabilidade | Interface intuitiva para acadêmicos |

## 4. Arquitetura

### 4.1 Componentes Principais

```
┌─────────────────────────────────────────────┐
│         APA Academic Writing Engine         │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Validator  │  │  Formatter Engine   │  │
│  │  Module     │  │                     │  │
│  │             │  │  • Citation Parser   │  │
│  │  • Page     │  │  • Reference Gen    │  │
│  │  • Margin   │  │  • Style Converter  │  │
│  │  • Spacing  │  │  • Template Engine  │  │
│  │  • Font     │  │                     │  │
│  └─────────────┘  └─────────────────────┘  │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │       Compliance Checker           │   │
│  │                                     │   │
│  │  • Institutional Rules             │   │
│  │  • APA 7th Edition                 │   │
│  │  • Vancouver (Optional)            │   │
│  └─────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

### 4.2 Fluxo de Dados

```
Documento de Entrada → Parser → Validador → Formatador → Documento de Saída
         ↓                ↓           ↓           ↓              ↓
    (PDF/DOCX)    (Extrair texto) (Verificar) (Corrigir)   (PDF/DOCX/LaTeX)
```

## 5. Especificações Técnicas

### 5.1 Validação de Formatação

```python
class APAValidator:
    def validate_page_setup(self, document):
        """Valida configurações de página"""
        # Margens: 2.54 cm em todos os lados
        # Espaçamento: Duplo
        # Fonte: Times New Roman 12pt
        # Alinhamento: Justificado
        pass
    
    def validate_citations(self, text):
        """Valida citações no texto"""
        # Padrões aceitos:
        # (Autor, Ano)
        # (Autor1 & Autor2, Ano)
        # (Autor et al., Ano)
        pass
    
    def validate_references(self, references):
        """Valida lista de referências"""
        # Formato: Autor, A. A. (Ano). Título. Fonte. DOI/URL
        # Ordenação alfabética
        # Hanging indent
        pass
```

### 5.2 Formatação Automática

```python
class APAFormatter:
    def format_citation(self, citation_type, authors, year, title, source):
        """Formata citação according to APA 7"""
        if citation_type == "narrative":
            return f"{authors} ({year})"
        elif citation_type == "parenthetical":
            return f"({authors}, {year})"
        pass
    
    def format_reference(self, ref_type, **kwargs):
        """Formata referência according to APA 7"""
        # Implementação por tipo de fonte
        pass
    
    def generate_hanging_indent(self, text):
        """Gera hanging indent para referências"""
        pass
```

### 5.3 Validação de Conformidade Institucional

```python
class InstitutionalCompliance:
    def check_pf_requirements(self, document):
        """Verifica requisitos do Projeto Final"""
        # Estrutura obrigatória
        # Modelos de memória
        # Prazos e entregas
        pass
    
    def check_program_rules(self, program, document):
        """Verifica regras específicas do programa"""
        # APA vs Vancouver
        # Exigências adicionais
        pass
```

## 6. Cenários de Teste (TDD)

| ID | Descrição | Critério de Aceite | Arquivo |
|----|-----------|-------------------|---------|
| CT-4801 | Validação de margens | Margens = 2.54 cm | `tests/apa/test_validator.py` |
| CT-4802 | Validação de espaçamento | Espaçamento = duplo | `tests/apa/test_validator.py` |
| CT-4803 | Validação de fonte | Fonte = Times New Roman 12pt | `tests/apa/test_validator.py` |
| CT-4804 | Validação de citação narrativa | Formato correto | `tests/apa/test_validator.py` |
| CT-4805 | Validação de citação parentética | Formato correto | `tests/apa/test_validator.py` |
| CT-4806 | Formatação de referência (livro) | Formato APA completo | `tests/apa/test_formatter.py` |
| CT-4807 | Formatação de referência (artigo) | Formato APA completo | `tests/apa/test_formatter.py` |
| CT-4808 | Formatação de referência (website) | Formato APA completo | `tests/apa/test_formatter.py` |
| CT-4809 | Validação de estrutura PF | Estrutura conforme normas | `tests/apa/test_compliance.py` |
| CT-4810 | Verificação de hanging indent | Indentação correta | `tests/apa/test_formatter.py` |

## 7. Integração

### 7.1 Agentes Existentes
- `12_agente_auditoria_bibliografica_abnt`: Usar módulo APA para validação
- `44_agente_correcao_textual_qualis`: Incorporar verificações APA
- `15_agente_resumo_abstract_palavras_chave`: Formatar conforme APA

### 7.2 Skills Existentes
- `edicao-cirurgica`: Combinar com verificações APA
- `potentiality-estimator-v2`: Análise de qualidade acadêmica

### 7.3 MCPs Disponíveis
- `sequential-thinking`: Raciocínio para validação complexa
- `memory`: Armazenar regras institucionais
- `websearch`: Buscar referências atualizadas

## 8. Roadmap de Implementação

### Fase 1: Fundamentos (Semanas 1-2)
- [ ] Implementar `APAValidator` básico
- [ ] Criar testes unitários
- [ ] Documentar APIs

### Fase 2: Formatação (Semanas 3-4)
- [ ] Implementar `APAFormatter`
- [ ] Suporte a múltiplos tipos de referência
- [ ] Integração com templates LaTeX

### Fase 3: Conformidade (Semanas 5-6)
- [ ] Implementar `InstitutionalCompliance`
- [ ] Regras para diferentes programas
- [ ] Validação de estrutura PF

### Fase 4: Integração (Semanas 7-8)
- [ ] Conectar com agentes existentes
- [ ] Criar hooks de validação
- [ ] Testes end-to-end

## 9. Métricas de Sucesso

| Métrica | Meta | Método de Medição |
|---------|------|-------------------|
| Precisão de formatação | 99% | Testes automatizados |
| Cobertura de tipos de referência | 90% | Análise de documentos reais |
| Tempo de validação | < 5s | Benchmark de performance |
| Satisfação do usuário | 9/10 | Pesquisa de feedback |

## 10. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Complexidade das regras APA | Alta | Média | Implementação incremental |
| Variações institucionais | Média | Alta | Configuração por programa |
| Performance de validação | Baixa | Média | Otimização de algoritmos |
| Adoção pelos usuários | Média | Alta | Treinamento e documentação |

## 11. Dependências

- **Especificações APA**: 7ª edição oficial
- **Normas Institucionais**: Documento de normas PF
- **Templates LaTeX**: Modelos existentes no ecossistema
- **Agentes de Revisão**: Módulos existentes

## 12. Critérios de Aceite Finais

- [ ] 10 CTs implementados e passando
- [ ] Cobertura de código ≥ 80%
- [ ] Documentação completa da API
- [ ] Integração com 3+ agentes existentes
- [ ] Validação com 10+ documentos reais
- [ ] Performance dentro das métricas definidas

---

**Status**: Em desenvolvimento  
**Versão**: 1.0  
**Data**: 22/06/2026  
**Autor**: Marcelo Claro (Orquestrador Supremo)