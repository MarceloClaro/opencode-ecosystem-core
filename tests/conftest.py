# -*- coding: utf-8 -*-
"""
conftest.py raiz da suíte — isola o estado persistido do MCI (MetaBus)
de qualquer execução real, antes que qualquer módulo de teste seja
importado.

Causa raiz do bug corrigido aqui: `mci/metabus.py::MetacognitiveMemory`
carrega e grava `.mci_state/shared_memory.json` de verdade — o mesmo
arquivo usado pelo CLI/orquestrador em uso real (`marceloclaro/cli.py`).
Como o módulo só é importado uma vez por processo Python, apenas o
*primeiro* import define `STATE_DIR` permanentemente. Vários arquivos
de teste tentavam isolar isso individualmente
(`os.environ["MCI_STATE_DIR"] = tempfile.mkdtemp(...)` antes de seus
próprios imports), mas essa tentativa só tem efeito se aquele arquivo
específico for, por acaso, o primeiro a ser coletado pelo pytest em
toda a sessão — o que não é garantido numa suíte com 100+ arquivos, e
na prática quase nunca acontecia.

Consequência real: toda rodada completa da suíte corrompia
permanentemente o `confidence_ledger` de produção. Como a fórmula EMA
de falha (`mci/reflexion.py`: `score=0.2` em falhas) tem ponto fixo
matemático em 0.2 (`novo = antigo*0.7 + 0.2*0.3` ⇒ estável quando
`antigo == 0.2`), a confiança de agentes específicos foi convergindo,
ao longo de centenas de execuções históricas da suíte, para perto
desse piso — e uma vez ali, uma nova falha deixa de reduzir a
confiança (por design da fórmula). Isso fazia
`tests/test_ecosystem.py::test_failed_task_lowers_confidence` falhar
de forma intermitente sempre que o agente designado já partia de
confiança ≤ 0.2.

`conftest.py` é sempre importado pelo pytest antes de qualquer módulo
de teste do mesmo diretório/subdiretórios — por isso, e só aqui, a
variável de ambiente tem efeito garantido sobre `mci.metabus`.
"""

import os
import tempfile

os.environ["MCI_STATE_DIR"] = tempfile.mkdtemp(prefix="mci_test_state_")
