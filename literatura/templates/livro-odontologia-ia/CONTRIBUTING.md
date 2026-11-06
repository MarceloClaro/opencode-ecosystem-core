# Contribuindo para o OdontoIA Book

Obrigado pelo interesse em contribuir! Este documento explica o processo.

## 📋 Checklist de Contribuição

### Para novas citações/artigos
- [ ] Possui DOI ou link auditável (PubMed, arXiv, DOI.org)
- [ ] Foi verificado que o link está ativo
- [ ] O artigo é relevante para Odontologia + IA
- [ ] A citação segue formato ABNT

### Para novo código
- [ ] Implementado com metodologia **SDD** (spec antes do código)
- [ ] **Testes TDD** estão presentes e passam (`pytest tests/ -v`)
- [ ] Código comentado em português
- [ ] Compatível com Google Colab (CPU e GPU)
- [ ] `requirements.txt` atualizado se houver nova dependência

### Para figuras/imagens
- [ ] Licença verificada e compatível
- [ ] Legenda completa: autor, ano, artigo, DOI, figura original
- [ ] Arquivo salvo em `imagens/figuras/capXX/`

## 🔧 Fluxo de Trabalho

1. **Fork** o repositório
2. Crie uma **branch**: `feat/nova-secao` ou `fix/correcao-typo`
3. Implemente com **TDD**: RED → GREEN → REFACTOR
4. Execute **todos os testes**: `cd odontoia-pkg && PYTHONPATH=src:$PYTHONPATH pytest tests/ -v`
5. **Commit** com mensagem clara: `feat: adiciona seção X com CNN para Y`
6. **Push** e abra um **Pull Request**

## 📝 Padrão de Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` nova funcionalidade
- `fix:` correção de bug
- `docs:` documentação
- `test:` testes
- `refactor:` refatoração
- `style:` formatação
- `chore:` manutenção

## 🧪 Testes

```bash
# Todos os testes CPU
cd odontoia-pkg
PYTHONPATH=src:$PYTHONPATH python -m pytest tests/ -v

# Apenas métricas
PYTHONPATH=src:$PYTHONPATH python -m pytest tests/test_metrics.py -v

# Apenas SDD
PYTHONPATH=src:$PYTHONPATH python -m pytest tests/test_sdd.py -v
```

## 📧 Dúvidas?

Abra uma [Issue](https://github.com/edsonlaranjeiras/odontoia-book/issues) ou entre em contato via [odontoia.com.br](https://odontoia.com.br/contato).
