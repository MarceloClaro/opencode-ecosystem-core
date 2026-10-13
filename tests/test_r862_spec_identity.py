"""Contrapróvas da identidade formal, sem usar o singleton persistido do projeto."""
from pathlib import Path
import collections

from sdd.spec_engine import SpecRegistry, Specification, _parse_spec_frontmatter


def registry():
    reg=object.__new__(SpecRegistry)
    reg.specs={}
    reg._initialized=True
    return reg


def write_spec(directory,name,title='Primeira'):
    directory.mkdir(parents=True,exist_ok=True)
    path=directory/name
    path.write_text('---\nspec_id: SPEC-LOCAL-DUP\ntitle: '+title+'\ncomponent: local\ntest_file: tests/test_local.py\nstatus: proposed\n---\n\n## Critérios de Aceitação Executáveis\n- `contrato` — Resultado local.\n')
    return path


def test_identidade_duplicada_no_mesmo_diretorio_nao_seleciona_ultima(tmp_path):
    a=write_spec(tmp_path,'SPEC-a.md');b=write_spec(tmp_path,'SPEC-b.md','Segunda')
    reg=registry();count=reg.load_formal_specs(str(tmp_path))
    assert count==0 and reg.get('SPEC-LOCAL-DUP') is None
    assert set(getattr(reg,'ambiguous_spec_sources',{}).get('SPEC-LOCAL-DUP',()))=={str(a.resolve()),str(b.resolve())}


def test_identidade_duplicada_entre_diretorios_nao_sobrescreve(tmp_path):
    write_spec(tmp_path/'a','SPEC-a.md');write_spec(tmp_path/'b','SPEC-b.md','Segunda')
    reg=registry();assert reg.load_formal_specs(str(tmp_path/'a'))==1
    reg.load_formal_specs(str(tmp_path/'b'))
    assert reg.get('SPEC-LOCAL-DUP') is None


def test_mesmo_arquivo_pode_ser_recarregado(tmp_path):
    write_spec(tmp_path,'SPEC-a.md')
    reg=registry();assert reg.load_formal_specs(str(tmp_path))==1
    write_spec(tmp_path,'SPEC-a.md','Atualizada')
    assert reg.load_formal_specs(str(tmp_path))==1
    assert reg.get('SPEC-LOCAL-DUP').title=='Atualizada'


def test_remover_duplicata_reabilita_definicao_unica(tmp_path):
    write_spec(tmp_path,'SPEC-a.md');b=write_spec(tmp_path,'SPEC-b.md','Segunda')
    reg=registry();reg.load_formal_specs(str(tmp_path));b.unlink()
    assert reg.load_formal_specs(str(tmp_path))==1
    assert reg.get('SPEC-LOCAL-DUP').title=='Primeira'
    assert not getattr(reg,'ambiguous_spec_sources',{})


def test_especificacao_dinamica_nao_e_removida(tmp_path):
    reg=registry();dynamic=Specification('TSPEC-LOCAL','Dinâmica','Objetivo local')
    reg.specs[dynamic.spec_id]=dynamic
    write_spec(tmp_path,'SPEC-a.md');write_spec(tmp_path,'SPEC-b.md')
    reg.load_formal_specs(str(tmp_path))
    assert reg.get(dynamic.spec_id) is dynamic


def test_repositorio_nao_tem_ids_formais_duplicados():
    root=Path(__file__).resolve().parents[1];ids=collections.defaultdict(list)
    for path in (root/'specs').glob('SPEC-*.md'):
        meta=_parse_spec_frontmatter(path.read_text())
        if isinstance(meta.get('spec_id'),str):ids[meta['spec_id']].append(path.name)
    assert not {key:value for key,value in ids.items() if len(value)>1}
