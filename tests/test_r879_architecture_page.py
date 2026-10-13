import json

import pytest

from scripts.render_architecture_page import render_page

SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50"><text>Core</text></svg>'


def inventory():
    return {
        "git": {"commit": "a" * 40, "tree": "b" * 40, "requested_ref": "HEAD"},
        "counts": {}, "modules": [], "files": [], "edges": [],
        "configurations": {}, "limitations": ["Estático"],
    }


def test_dados_json_nao_encerram_script_inerte():
    data = inventory()
    data["limitations"] = ['</script><script>alert("fora")</script>']
    page = render_page(data, SVG, SVG, [])
    assert '</script><script>alert("fora")</script>' not in page
    encoded = page.split('<script id="inventory-data" type="application/json">')[1].split('</script>')[0]
    assert json.loads(encoded)["limitations"] == data["limitations"]


@pytest.mark.parametrize("svg", [
    '<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"/>',
    '<svg xmlns="http://www.w3.org/2000/svg"><image href="https://externo.invalid/imagem"/></svg>',
])
def test_svg_ativo_ou_recurso_externo_e_recusado(svg):
    with pytest.raises(ValueError):
        render_page(inventory(), svg, SVG, [])


def test_pagina_local_tem_navegacao_e_nao_carrega_cdns():
    page = render_page(inventory(), SVG, SVG, [])
    assert '<!doctype html>' in page.lower()
    assert 'lang="pt-BR"' in page
    assert 'id="module-search"' in page
    assert 'id="diagram-stage"' in page
    assert 'src="https://' not in page
    assert '__SNAPSHOT_JSON__' not in page


def test_rotulo_fluxo_e_escapado_sem_perder_texto():
    flow = {"id": "test", "title": '<img src=x onerror="alert(1)">',
            "description": "Fonte local", "svg": SVG, "sources": [], "limitations": []}
    page = render_page(inventory(), SVG, SVG, [flow])
    assert '<img src=x onerror="alert(1)">' not in page
    assert '&lt;img src=x' in page
