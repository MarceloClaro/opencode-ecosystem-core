"""R922: contraprovas independentes e ponte pelo primário; caches artificiais."""
import importlib.util
import json
from pathlib import Path

import pytest

from integrations import local_plugin_extraction as extraction
from integrations.scientific_plugins import ScientificPluginService


@pytest.fixture
def cache(tmp_path):
    helper_path=Path(__file__).with_name('test_r921_local_plugin_extraction.py')
    spec=importlib.util.spec_from_file_location('r922_fixture_helpers',helper_path)
    helpers=importlib.util.module_from_spec(spec); spec.loader.exec_module(helpers)
    root=tmp_path/'cache'; package=helpers.package(root)
    return root,package


def test_restricted_frontmatter_is_not_split_by_internal_dashes(cache):
    root,package=cache
    skill=package/'skills/curate/SKILL.md'
    skill.write_text('---\nname: curate\ndescription: a---b\nlicense: Proprietary\n---\nCORPO_RESTRITO\n')
    report=extraction.inventory_local_plugins(root)['plugins'][0]
    assert report['disposition']=='reference_only'
    assert 'skills/curate/SKILL.md' not in report['files']


def test_punctuated_quoted_secret_is_rejected_without_leak(cache):
    root,package=cache
    secret='!Aa1!Bb2!Cc3!Dd4'
    (package/'skills/curate/references/guide.md').write_text('api_key: "'+secret+'"\n')
    try:
        extraction.inventory_local_plugins(root)
    except ValueError as exc:
        assert 'secret_material' in str(exc) and secret not in str(exc)
    else:
        assert False, 'Atribuição explícita de chave foi aceita'


def test_canonical_service_rejects_lexical_symlink_root(cache,tmp_path):
    root,_=cache
    repo=tmp_path/'repo'; repo.mkdir()
    link=tmp_path/'repo-link'; link.symlink_to(repo,target_is_directory=True)
    try:
        ScientificPluginService(link).extract_eligible(cache_root=root,plugin_ids=['zotero'])
    except ValueError:
        pass
    else:
        assert False, 'Raiz lexical simbólica aceita pelo serviço canônico'
    assert not (repo/'.opencode').exists()


def selected_api():
    fn=getattr(extraction,'inventory_selected_plugins',None)
    assert callable(fn), 'Inventário de escopo selecionado ausente'
    return fn


def test_selected_inventory_does_not_touch_unrelated_packages(cache):
    root,_=cache
    private=root/'claude-cowork/unrelated/1.0.0'
    private.mkdir(parents=True); (private/'auth.json').write_text('DO_NOT_READ')
    report=selected_api()(root,['zotero'])
    assert [p['id'] for p in report['plugins']]==['zotero']
    assert report['scope']=='explicit_catalogued_packages'
    for bad in ([],['unknown'],['zotero','zotero'],['../zotero']):
        with pytest.raises(ValueError): selected_api()(root,bad)


@pytest.mark.parametrize('projected',[False,True])
def test_drvfs_projection_is_data_only_and_requires_observed_mount(cache,tmp_path,monkeypatch,projected):
    root,package=cache
    fn=selected_api()
    helper=getattr(extraction,'_drvfs_synthetic_modes',None)
    assert callable(helper), 'Detecção de montagem ausente'
    monkeypatch.setattr(extraction,'_drvfs_synthetic_modes',lambda _root:projected)
    for path in package.rglob('*'):
        if path.is_file(): path.chmod(0o777)
    (package/'scripts').mkdir(); (package/'scripts/never.py').write_text('raise RuntimeError("NEVER")')
    report=fn(root,['zotero'])
    row=report['plugins'][0]
    assert row['permission_projection']==('drvfs_synthetic_bits_data_only' if projected else 'posix_mode_bits')
    if projected:
        assert row['disposition']=='eligible'
        assert 'scripts/never.py' not in row['files']
        service=ScientificPluginService(tmp_path/'repo')
        assert callable(getattr(service,'extract_selected',None))
        result=service.extract_selected(cache_root=root,plugin_ids=['zotero'])
        assert result['executed'] is False and result['hooks_executed'] is False
        destination=tmp_path/'repo/.opencode/scientific-plugins/packages/zotero/0.1.2'
        assert all(not (p.stat().st_mode&0o111) for p in destination.rglob('*') if p.is_file())
    else:
        assert row['disposition']=='reference_only'


def test_primary_facade_validates_and_dispatches_selected_operations(cache,tmp_path,monkeypatch):
    root,_=cache
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    from marceloclaro.runtime_actions import validate_action
    from integrations import scientific_plugins
    selected_api()
    service=ScientificPluginService(tmp_path/'repo')
    monkeypatch.setattr(scientific_plugins,'ScientificPluginService',lambda _root:service)
    primary=object.__new__(MarceloClaroOrchestrator)
    observations=[]
    primary._record_knowledge_outcome=lambda *args: observations.append(args) or {'persisted':True}
    config={'operation':'inventory_local','cache_root':str(root),'plugin_ids':['zotero']}
    assert validate_action('plugins',config)==config
    report=primary.scientific_plugin_action('inventory_local',cache_root=str(root),plugin_ids=['zotero'])
    assert report['plugins'][0]['id']=='zotero' and not (tmp_path/'repo/.opencode').exists()
    imported=primary.scientific_plugin_action('extract_selected',cache_root=str(root),plugin_ids=['zotero'])
    assert imported['executed'] is False and imported['metacognition']['confidence_promoted'] is False
    assert len(observations)==2
    for bad in ({'operation':'extract_selected','cache_root':str(root)},
                {**config,'destination_root':'/tmp/not-permitted'},
                {**config,'ignore_modes':True}):
        with pytest.raises(ValueError): validate_action('plugins',bad)


def test_selected_extraction_uses_canonical_registry_without_runtime(cache,tmp_path,monkeypatch):
    root,package=cache
    import subprocess,urllib.request
    def forbidden(*_a,**_kw): raise AssertionError('Execução indevida')
    monkeypatch.setattr(subprocess,'Popen',forbidden)
    monkeypatch.setattr(urllib.request,'urlopen',forbidden)
    service=ScientificPluginService(tmp_path/'repo')
    assert callable(getattr(service,'extract_selected',None))
    first=service.extract_selected(cache_root=root,plugin_ids=['zotero'])
    assert first['executed'] is False and first['credentials_copied'] is False
    registry=json.loads((tmp_path/'repo/.opencode/scientific-plugins/registry.json').read_text())
    assert registry['zotero']['source_root']==str(package)
    assert registry['zotero']['skills']==['curate']
    assert service.extract_selected(cache_root=root,plugin_ids=['zotero'])['executed'] is False
