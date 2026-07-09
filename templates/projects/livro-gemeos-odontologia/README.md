# Gêmeos Digitais na Odontologia

> Fundamentos, Aplicações e Impacto Social no Brasil com o OpenCode Ecosystem

Este repositório contém os fontes LaTeX da obra científica **Gêmeos Digitais na Odontologia**, bem como os motores de simulação e orquestração do **OpenCode Ecosystem** e suas integrações com o framework **MIRA (Metáforas Inteligentes Responsivas e Animadas)**.

---

## 📖 Sobre a Obra

O livro explora a transição paradigmática da Odontologia Analógica tradicional para a era da **Odontologia de Precisão e Preditiva**, impulsionada pelo desenvolvimento de **Gêmeos Digitais (Digital Twins)**. Ele aborda os fundamentos biomecânicos e de captura tridimensional (tomografia CBCT, scanners intraorais) e deságua em soluções robustas orientadas a dados:
- **Medicina P4:** Personalizada, Preditiva, Preventiva e Participativa aplicada à saúde bucal.
- **Inteligência Artificial e Vision Transformers (ViT):** Mecanismos de Auto-Atenção para segmentação anatômica em imagens tridimensionais (nnU-Net).
- **Simulação Mecânica Periodontal (LPD):** Modelagem viscoelástica e anisotrópica não-linear para prever e mitigar traumas periodontais sob carregamentos mastigatórios.
- **Segurança Forense de Telemetria:** Arquiteturas baseadas em **Zero-Knowledge Proofs (ZKP)** para preservação absoluta de privacidade.
- **Conformidade Regulatória (SAMD):** Processo de validação clínica e certificação de software como dispositivo médico.

---

## 🛠️ O OpenCode Ecosystem

O **OpenCode Ecosystem** é uma arquitetura multiagente descentralizada composta por **128 agentes autônomos**, **155 skills** e **46 Model Context Protocol (MCP) servers** coordenados por um motor de orquestração determinístico e auditável via TDD/SDD.

### O Pipeline de Produção Científica (ScientificProductionAgent)
O ecossistema implementa uma esteira metodológica de 8 estágios contínuos para a orquestração e redação de manuscritos científicos e apresentações interativas:
1. **Hypothesis Formation:** Formulação de hipóteses científicas testáveis e falseáveis com o `MultiReasoningEngine`.
2. **Literature Review:** Revisão sistemática da literatura com construção de gráficos de citação.
3. **Methodology Design:** Desenho metodológico contendo portões de qualidade para conformidade SAMD, privacidade baseada em ZKP e modelagem mecânica de LPD.
4. **Data Analysis:** Processamento estocástico e inserção do cálculo de **Social Return on Investment (SROI)**.
5. **Scientific Writing:** Redação automática do artigo utilizando templates estruturados (Markdown, LaTeX e BibTeX).
6. **Peer Review:** Simulação de revisão por pares baseada em enxame (*ensemble*) avaliando originalidade, rigor e integridade científica.
7. **Publication:** Atribuição e validação de DOIs e relatórios públicos de impacto no SUS.
8. **Presentation Generation (MIRA):** Geração de apresentações animadas interativas no formato configurado pelo `mira-animator`.

---

## 🚀 Como Compilar o Livro

A obra está disponível em dois temas altamente premium (Claro e Escuro).

### Pré-requisitos
Certifique-se de possuir uma distribuição LaTeX completa (como o TeX Live) e o utilitário `wsl` ou terminal bash Linux.

### Comandos de Compilação
```bash
# Limpa arquivos auxiliares e compila o tema Light
rm -f *.aux && pdflatex -interaction=nonstopmode light.tex
bibtex light
pdflatex -interaction=nonstopmode light.tex
pdflatex -interaction=nonstopmode light.tex

# Limpa e compila o tema Dark
rm -f *.aux && pdflatex -interaction=nonstopmode dark.tex
bibtex dark
pdflatex -interaction=nonstopmode dark.tex
pdflatex -interaction=nonstopmode dark.tex
```
Os PDFs de saída `light.pdf` e `dark.pdf` serão gerados no diretório raiz.

---

## 🧪 Como Executar a Suíte de Testes (TDD/SDD)

A suíte de testes unitários valida os invariantes formais estabelecidos no *Software Design Document (SDD)* do ecossistema.

### Execução dos Testes da Esteira de Produção Científica
```bash
# Executa o runner nativo
node .tdd-sdd/tests/test_scientific_production.js
```

---

## 🌟 Apoio Financeiro e Contribuição

Se este ecossistema open-source e esta obra didática agregaram valor ao seu trabalho ou pesquisa, apoie o desenvolvedor:

<div align="center">
  <a href="https://www.buymeacoffee.com/GEOMAKER" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Ofereça-me um café" style="height: 60px !important;width: 217px !important;" >
  </a>
</div>

<div align="center">
  <img src="livro-opencode/capa_dark.jpg" alt="OpenCode Ecosystem Architecture" width="100%"/>
</div>
