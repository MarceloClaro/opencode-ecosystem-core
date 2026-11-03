# SPEC-935-EDUC-DIRETOR: Sistema Educacional Simulado de Gestão e Diretoria Escolar

## 1. Visão Geral e Objetivo
Este documento especifica o desenvolvimento do **Sistema Educacional Simulado de Gestão e Diretoria Escolar**, um aplicativo web full-stack educativo e de simulação (Clean Room), projetado para atender a todos os módulos essenciais de um painel de direção escolar (autenticação, dashboard executivo, gestão de turmas/alunos, frequência, notas e relatórios gerenciais), construído sob os rigorosos padrões SDD (Specification-Driven Development) e TDD (Test-Driven Development) do OpenCode Ecosystem Core.

---

## 2. Módulos do Sistema

### Módulo 1: Autenticação e Controle de Sessão
- **Descrição**: Tela de login com validação de credenciais simuladas (ex: CPF do gestor e senha).
- **Recursos**:
  - Emissão de token de sessão simulado (JWT / SessionStorage).
  - Controle de perfil (Diretor, Coordenador, Professor).
  - Rota protegida `/sistema/diretor/home`.

### Módulo 2: Dashboard Executivo / Home
- **Descrição**: Painel principal com indicadores-chave (KPIs) da escola.
- **Recursos**:
  - Total de alunos matriculados, turmas ativas, corpo docente.
  - Taxa média de frequência geral e desempenho acadêmico.
  - Alertas recentes (alunos em risco de evasão ou baixa frequência).
  - Atalhos rápidos para diário de classe e lançamentos.

### Módulo 3: Gestão de Turmas e Alunos
- **Descrição**: Listagem e detalhamento das turmas da unidade escolar.
- **Recursos**:
  - Filtros por turno (Manhã, Tarde, Noite) e série/ano.
  - Lista de alunos por turma com dados de contato e situação escolar.

### Módulo 4: Controle de Frequência Escolar
- **Descrição**: Registro e acompanhamento diário da presença dos alunos.
- **Recursos**:
  - Visualização de diários de classe por turma e data.
  - Lançamento e edição de faltas/presenças.
  - Relatório automático de alerta de infrequência (< 75%).

### Módulo 5: Notas e Avaliações
- **Descrição**: Lançamento de notas por unidade/trimestre e acompanhamento de boletins.
- **Recursos**:
  - Lançamento de notas de avaliações (AV1, AV2, Recuperação).
  - Cálculo automático de médias ponderadas.
  - Painel de desempenho por disciplina.

### Módulo 6: Relatórios de Gestão e Indicadores
- **Descrição**: Geração de relatórios consolidados para a Secretaria / Diretoria.
- **Recursos**:
  - Relatório de Evasão e Frequência Crítica.
  - Desempenho acadêmico consolidado (Aprovados, Reprovados, Recuperação).
  - Exportação de dados simulados (CSV / PDF).

---

## 3. Critérios de Aceitação (SDD)
1. **Autenticação**: O acesso negado a rotas protegidas sem token válido; redirecionamento correto para o dashboard ao autenticar.
2. **Integridade de Dados**: Todos os cálculos de médias e frequências devem ser precisos e testados via TDD.
3. **Responsividade**: Interface limpa e acessível em desktop e dispositivos móveis.
