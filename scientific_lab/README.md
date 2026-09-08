# Scientific Lab bridge

Esta pasta é a fachada nativa que conecta o OpenCode Ecosystem Core à instalação
completa do Pesquisador Universal Marcelo Claro v4.1.

Ela foi desenhada para evitar duplicação do runtime científico dentro do kernel.
O instalador v4.1 usa por padrão:

```text
~/.local/share/pesquisador-universal/skill
```

Também é possível definir:

```bash
export PESQUISADOR_UNIVERSAL_HOME=/caminho/para/skill
```

Comandos:

```bash
python -m marceloclaro.scientific_lab status
python -m marceloclaro.scientific_lab doctor
python -m marceloclaro.scientific_lab research harvest "tema" --workspace .
```

O `doctor` distingue a compatibilidade estrutural do Core da disponibilidade da
supercamada. Ausência da instalação nunca é apresentada como sucesso.
