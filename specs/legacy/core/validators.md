# Spec: Validators (core/validators.py)

**Versao:** 1.0.0 | **Status:** active | **SWEBOK:** corretiva | **Revisao:** 2026-05-27

## 1. Comportamento
Funcoes de validacao reutilizaveis para inputs e schemas. Valida identificadores, caminhos, intervalos numericos, schemas JSON e tipos basicos. Integra-se com Pydantic para validacao de modelos.

## 2. Usuarios
- Usuarios: todos os modulos que recebem input externo (API, CLI, config)
- Volume: alta frequencia (cada operacao valida inputs)
- Ambiente: Python 3.11+, Pydantic V2

## 3. Restricoes
- Funcoes puras (sem efeitos colaterais)
- Retornam bool ou levantam ValidationError
- Compatibilidade com Pydantic V2
- Mensagens de erro descritivas

## 4. Bordas
- Input None: levanta ValidationError
- String vazia: depende do contexto (pode ser valido ou nao)
- Unicode/emoji: validado contra whitelist de caracteres

## 5. Criterios
- [ ] validar_identificador() rejeita strings com caracteres especiais
- [ ] validar_caminho() rejeita path traversal (../)
- [ ] validar_json_schema() valida contra schema JSON
- [ ] Integracao com Pydantic funciona
