# Data Card — Template (Gebru et al. 2021)

> **Baseado em:** Gebru T, et al. *Datasheets for Datasets.* Communications of the ACM, 2021. DOI: 10.1145/3458723
> **Aplicação no OdontoIA:** Todos os datasets referenciados no livro

---

## 1. Motivation

### 1.1 Para que o dataset foi criado?
- **Finalidade:** (pesquisa, validação de modelo, benchmark)
- **Tarefa de IA:** (segmentação, classificação, etc.)
- **Problema clínico:**

### 1.2 Quem criou o dataset?
- **Instituição:**
- **Pesquisadores principais:**
- **Financiamento:**

### 1.3 Quem financiou a criação do dataset?
- **Fonte de financiamento:** (grant, agência, etc.)
- **Conflitos de interesse:**

## 2. Composition

### 2.1 O que há em cada instância?
- **Tipo de dado:** (radiografia, foto, texto, etc.)
- **Anotações:** (segmentação, classificação, etc.)
- **Formato:** (DICOM, JPG, COCO, etc.)
- **Metadados:**

### 2.2 Quantas instâncias?
- **Total:** (N imagens, N pacientes)
- **Por classe:**
- **Por subgrupo demográfico:**

### 2.3 O dataset contém todas as instâncias possíveis?
- [ ] Sim, é exaustivo
- [ ] Não, é amostragem (descrever método)

### 2.4 Que dados foram coletados?
- **Período:** (datas de coleta)
- **Setting:** (hospital X, ambulatório Y)
- **Equipamento:** (modelo do scanner, parâmetros)

### 2.5 Quem foi incluído?
- **Critérios de inclusão:**
- **Critérios de exclusão:**
- **Consentimento:** (escrito, verbal, etc.)
- **Aprovação ética:** (IRB number)

## 3. Collection Process

### 3.1 Como os dados foram coletados?
- **Método:** (retrospectivo, prospectivo, scraping)
- **Ferramentas:**
- **Tempo de coleta:**

### 3.2 Quem coletou?
- **Anotadores:** (número, qualificação)
- **Treinamento dos anotadores:**
- **Validação inter-anotador:** (Cohen's Kappa, ICC)

### 3.3 Medidas de qualidade
- **Kappa inter-anotador:**
- **Procedência de resolução de conflitos:**

## 4. Preprocessing

### 4.1 Os dados foram preprocessados?
- [ ] Não
- [ ] Sim (descrever)

### 4.2 Software usado:
### 4.3 Parâmetros:
### 4.4 A versão raw está disponível?

## 5. Uses

### 5.1 O dataset foi usado para?
- **Artigos publicados:**
- **Modelos treinados:**
- **Benchmarks:**

### 5.2 Usos recomendados
- ✅ **Aplicações para as quais foi projetado**
- ✅ **Aplicações similares razoáveis**

### 5.3 Usos NÃO recomendados
- ❌ **Populações fora do dataset de treino**
- ❌ **Decisões clínicas autônomas (sem revisão humana)**
- ❌ **Detecção de condições raras não representadas**

## 6. Distribution

### 6.1 Como o dataset será distribuído?
- **Licença:**
- **URL de acesso:**
- **DOI:**
- **Registro necessário:** (sim/não)

### 6.2 Quando?
- **Data de lançamento:**
- **Manutenção:** (frequência de atualizações)

### 6.3 Restrições
- **Uso comercial:** (permitido/proibido)
- **Redistribuição:** (permitida/proibida)
- **Atribuição obrigatória:** (sim/não)

## 7. Maintenance

### 7.1 Quem mantém?
- **Mantenedor:**
- **Contato:**

### 7.2 Como reportar problemas?
- **Email:**
- **GitHub Issues:**

### 7.3 Atualizações
- **Frequência:**
- **Versionamento:**

## 8. Ethics & Privacy

### 8.1 Aprovação ética
- **Comitê:** (nome, número)
- **Data:**

### 8.2 LGPD/GDPR
- **Conformidade:**
- **Anonimização:** (técnica, software)
- **Retenção:** (período)

### 8.3 Consent
- **Tipo:** (informado, presumido, etc.)
- **Revogação:** (como exercer)

## 9. Impact

### 9.1 Benefícios potenciais
- **Para prática clínica:**
- **Para pesquisa:**

### 9.2 Riscos potenciais
- **Viés:**
- **Uso indevido:**
- **Mitigação:**

---

**Auditor:** OpenCode Ecosystem
**Data:** 2026-07-09
**Versão:** 1.0
