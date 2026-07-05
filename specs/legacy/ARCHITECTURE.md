# Arquitetura do Projeto de Mestrado

## Topologia
O projeto estrutura-se em dois planos paralelos:
1. **Plano de Submissão** (curto prazo, deadline 01/06/2026): documentação para o processo seletivo
2. **Plano de Execução** (24 meses): fases da pesquisa conforme cronograma PPGTE

## Estrutura de diretórios
```
Antiprojeto UFC/
├── specs/                    # Spec-Driven Development
│   ├── AGENTS.md             # Regras para agentes de IA
│   ├── PRD.md                # Visão do produto
│   ├── RULES.md              # Regras invariantes (R1..V3)
│   ├── ARCHITECTURE.md       # Este arquivo
│   ├── TASKS.md              # Backlog operacional
│   ├── API_SPEC.md           # Contratos dos artefatos
│   └── TESTS_SPEC.md         # Estratégia de validação
├── anteprojeto/              # Artefatos da submissão
│   ├── ANTEPROJETO_PPGTE_2026.md
│   ├── ANTEPROJETO_PPGTE_2026.tex
│   └── ANTEPROJETO_PPGTE_2026.pdf
├── guia-pratico/             # Produto educacional (Fase 2)
│   ├── modulo-a-etica/
│   ├── modulo-b-bibliografia/
│   ├── modulo-c-redacao/
│   └── modulo-d-lgpd/
├── estudo-caso/              # Dados da Fase 3
│   ├── tcle/
│   ├── questionarios/
│   ├── transcricoes/
│   └── analise/
├── dissertacao/              # Fase 4
├── figuras/                  # Diagramas e ilustrações
├── Curriculos/               # Documentos pessoais
├── Certificados/             # Comprovantes
└── Documentos/               # Diplomas e declarações
```

## Camadas do projeto
- **Especificação**: arquivos em specs/ — fonte da verdade
- **Produção textual**: anteprojeto, guia, dissertação (LaTeX + Markdown)
- **Validação**: testes de conformidade, checklists, análise de grupo focal
- **Evidência**: PDFs, logs de auditoria, questionários assinados

## Componentes principais
- **Pipeline de Submissão**: produz o PDF único ≤ 15MB para o SIGAA
- **Pipeline de Escrita**: produz textos acadêmicos com auditoria TSAC
- **Pipeline de Validação**: checklist ABNT, verificador de plágio, corretor LGPD
- **Pipeline de Pesquisa**: busca bibliográfica com rastreabilidade DOI

## Decisões arquiteturais (ADRs)

### ADR-001: Markdown como formato fonte, LaTeX para PDF
- **Contexto**: anteprojeto exige PDF formatado em ABNT
- **Opções**: (a) Word, (b) LaTeX puro, (c) Markdown → LaTeX
- **Escolha**: Markdown → LaTeX (pandoc + template ABNT)
- **Consequências**: edição leve em MD, compilação profissional em LaTeX. Curva de aprendizado do template.

### ADR-002: Processamento local para conformidade LGPD
- **Contexto**: dados de participantes do grupo focal são sensíveis
- **Opções**: (a) nuvem (Google Forms), (b) local (Python + SQLite)
- **Escolha**: processamento local com SQLite criptografado
- **Consequências**: sem dependência de internet, conformidade LGPD total, mas exige backup manual.

### ADR-003: Agentes como assistentes, não autores
- **Contexto**: Anexo IV do edital exige declaração de uso de IA
- **Opções**: (a) não usar IA, (b) usar IA sem declarar, (c) usar IA com transparência total
- **Escolha**: uso transparente com declaração formal + logs de auditoria
- **Consequências**: rastreabilidade completa, alinhamento com Resolução 39/2025, diferencial competitivo.

## Trade-offs aceitos
- Markdown → LaTeX tem fricção de compilação, mas garante formatação ABNT precisa
- SQLite local é menos conveniente que Google Forms, mas garante LGPD
- Pipeline de auditoria adiciona tempo de revisão, mas elimina risco de plágio inadvertido
