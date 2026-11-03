"""R916: origem real do atlas, limites de leitura e ausência de circularidade."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest


@pytest.fixture
def builder():
    path = Path(__file__).resolve().parents[1] / 'scripts/build_architecture_maps.py'
    spec = importlib.util.spec_from_file_location('r916_maps', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def repo(tmp_path):
    subprocess.run(['git','init','-q',str(tmp_path)],check=True)
    files={'pkg/__init__.py':'','pkg/core.py':'from . import helper\ndef run():\n    return helper.value\n',
           'pkg/helper.py':'value=1\n','README.md':'old documentation\n',
           'opencode.json':json.dumps({'agent':{'primary':{}},'mcp':{},'command':{}})}
    for name,text in files.items():
        path=tmp_path/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
    subprocess.run(['git','-C',str(tmp_path),'add','.'],check=True)
    subprocess.run(['git','-C',str(tmp_path),'-c','user.name=fixture','-c','user.email=fixture@example.invalid','commit','-qm','fixture'],check=True)
    return tmp_path


def test_worktree_samples_current_sources_and_removed_modules(builder,repo):
    index=(repo/'.git/index').read_bytes()
    (repo/'pkg/core.py').write_text('def changed():\n    return 7\n')
    (repo/'pkg/helper.py').unlink()
    result=builder.build_snapshot(repo,source='worktree')
    modules={row['module']:row for row in result['modules']}
    assert set(modules)=={'pkg','pkg.core'}
    assert modules['pkg.core']['symbols'][0]['name']=='changed'
    assert modules['pkg.core']['sha256']==hashlib.sha256((repo/'pkg/core.py').read_bytes()).hexdigest()
    assert 'pkg/helper.py' in result['git']['deleted_paths']
    assert 'pkg/core.py' in result['git']['changed_paths']
    assert result['git']['source']=='worktree'
    assert len(result['git']['worktree_sha256'])==64
    assert (repo/'.git/index').read_bytes()==index
    assert result['git']['commit'][:12] in builder._dot(result,False)
    assert result['git']['worktree_sha256'][:12] in builder._dot(result,False)
    from scripts.build_mermaid_architecture import render_mermaid
    mermaid=render_mermaid(result)
    assert result['git']['worktree_sha256'][:12] in mermaid
    assert 'removidos omitidos' in mermaid


def test_untracked_sources_never_read_or_counted(builder,repo,monkeypatch):
    secret=repo/'private.py';secret.write_text('NEVER_READ_PRIVATE')
    original=Path.read_bytes
    def guarded(path):
        assert path!=secret,'Untracked source was read'
        return original(path)
    monkeypatch.setattr(Path,'read_bytes',guarded)
    result=builder.build_snapshot(repo,source='worktree')
    assert 'private.py' not in {row['path'] for row in result['files']}
    assert 'NEVER_READ_PRIVATE' not in json.dumps(result)


def test_current_symlink_and_parent_symlink_are_never_followed(builder,repo,tmp_path):
    outside=tmp_path.parent/(tmp_path.name+'-external')
    outside.mkdir();(outside/'core.py').write_text('SECRET_OUTSIDE')
    (repo/'pkg/core.py').unlink();(repo/'pkg/core.py').symlink_to(outside/'core.py')
    result=builder.build_snapshot(repo,source='worktree')
    assert 'pkg.core' not in {row['module'] for row in result['modules']}
    assert 'SECRET_OUTSIDE' not in json.dumps(result)
    (repo/'pkg/core.py').unlink();(repo/'pkg/helper.py').unlink();(repo/'pkg/__init__.py').unlink()
    (repo/'pkg').rmdir();(repo/'pkg').symlink_to(outside,target_is_directory=True)
    result=builder.build_snapshot(repo,source='worktree')
    assert not result['modules']
    assert 'SECRET_OUTSIDE' not in json.dumps(result)


def test_generated_docs_do_not_make_source_identity_circular(builder,repo):
    first=builder.build_snapshot(repo,source='worktree')
    (repo/'README.md').write_text('new generated documentation\n')
    second=builder.build_snapshot(repo,source='worktree')
    assert first==second
    entry=next(row for row in second['files'] if row['path']=='README.md')
    assert entry['content_source']=='git_base'


def test_configuration_uses_current_names_without_exporting_secrets(builder,repo):
    (repo/'opencode.json').write_text(json.dumps({'agent':{'current':{'prompt':'PRIVATE_PROMPT'}},
       'mcp':{'new':{'env':{'API_KEY':'PRIVATE_KEY'}}},'command':{},'provider':{'apiKey':'PRIVATE_PROVIDER'}}))
    result=builder.build_snapshot(repo,source='worktree')
    assert result['configurations'][0]['agents']==['current']
    assert result['configurations'][0]['mcp_servers']==['new']
    assert not any(value in json.dumps(result) for value in ('PRIVATE_PROMPT','PRIVATE_KEY','PRIVATE_PROVIDER'))


def test_concurrent_source_change_invalidates_collection(builder,repo,monkeypatch):
    original=builder._parse_python
    def mutate(snapshot,texts):
        original(snapshot,texts)
        (repo/'pkg/helper.py').write_text('value=999\n')
    monkeypatch.setattr(builder,'_parse_python',mutate)
    with pytest.raises(ValueError,match='Fonte alterada'):
        builder.build_snapshot(repo,source='worktree')


def test_git_default_still_ignores_local_changes(builder,repo):
    first=builder.build_snapshot(repo)
    (repo/'pkg/core.py').write_text('raise RuntimeError("not executed")\n')
    assert first==builder.build_snapshot(repo)


def test_worktree_cli_check_detects_source_tampering(builder,repo,tmp_path):
    output=tmp_path/'maps'
    builder.write_artifacts(builder.build_snapshot(repo,source='worktree'),output,render=False)
    args=['--root',str(repo),'--source','worktree','--output',str(output),'--check']
    assert builder.main(args)==0
    (repo/'pkg/core.py').write_text('def next_version():\n    return 9\n')
    assert builder.main(args)==1


@pytest.mark.parametrize('line,symbol',[(2,'run'),(1,'missing')])
def test_readme_sync_rejects_wrong_source_anchor(tmp_path,line,symbol):
    from scripts.sync_readme_flowcharts import synchronize
    folder=tmp_path/'docs/architecture/flows';folder.mkdir(parents=True)
    (tmp_path/'source.py').write_text('def run():\n    return 1\n')
    (folder/'one.mmd').write_text('flowchart LR\n  A --> B\n')
    (folder/'one.svg').write_text('<svg/>')
    entry={'id':'one','title':'Example','description':'Example','file':'flows/one.mmd',
           'sources':[{'path':'source.py','line':line,'symbol':symbol}],'limitations':['Local']}
    (tmp_path/'docs/architecture/flows.json').write_text(json.dumps({'flows':[entry]}))
    readme=tmp_path/'README.md';readme.write_text('# Example\n\n## Limites de segurança e operação\n')
    original=readme.read_bytes()
    with pytest.raises(ValueError,match='Âncora'):
        synchronize(tmp_path,'README.md')
    assert readme.read_bytes()==original


def test_refresh_flow_anchors_binds_to_worktree_inventory(builder,repo,tmp_path):
    from scripts.sync_readme_flowcharts import refresh_source_anchors

    (repo/'pkg/core.py').write_text('def run():\n    return 2\n')
    snapshot=builder.build_snapshot(repo,ref='HEAD',source='worktree')
    architecture=repo/'docs/architecture';architecture.mkdir(parents=True)
    (architecture/'architecture-inventory.json').write_text(json.dumps(snapshot))
    catalog={'version':2,'flows':[{'id':'sample','title':'Sample','description':'Sample',
        'file':'flows/sample.mmd','sources':[{'path':'pkg/core.py','symbol':'run','line':99,'sha256':'stale'}],
        'limitations':['Static source only.']}]}
    (architecture/'flows.json').write_text(json.dumps(catalog))

    result=refresh_source_anchors(repo)
    refreshed=json.loads((architecture/'flows.json').read_text())
    source=refreshed['flows'][0]['sources'][0]
    assert source['line']==1
    assert source['sha256']==hashlib.sha256((repo/'pkg/core.py').read_bytes()).hexdigest()
    assert source['origin']=='worktree_tracked'
    assert refreshed['source']['base_commit']==snapshot['git']['commit']
    assert refreshed['source']['worktree_sha256']==snapshot['git']['worktree_sha256']
    assert result['updated_anchors']==1


def test_refresh_flow_anchors_rejects_source_not_in_worktree_manifest(builder,repo):
    from scripts.sync_readme_flowcharts import refresh_source_anchors

    snapshot=builder.build_snapshot(repo,ref='HEAD',source='worktree')
    architecture=repo/'docs/architecture';architecture.mkdir(parents=True)
    (architecture/'architecture-inventory.json').write_text(json.dumps(snapshot))
    catalog={'version':2,'flows':[{'id':'sample','sources':[{'path':'untracked.py','symbol':'secret','line':1}],
        'limitations':['Static source only.']}]}
    target=architecture/'flows.json';original=json.dumps(catalog);target.write_text(original)
    (repo/'untracked.py').write_text('secret = 42\n')

    with pytest.raises(ValueError,match='manifest'):
        refresh_source_anchors(repo)
    assert target.read_text()==original


def test_worktree_readme_anchor_does_not_link_modified_bytes_to_base(tmp_path):
    from scripts.sync_readme_flowcharts import render_block

    folder=tmp_path/'docs/architecture/flows';folder.mkdir(parents=True)
    (folder/'one.mmd').write_text('flowchart LR\n  A --> B\n')
    (folder/'one.svg').write_text('<svg/>')
    (tmp_path/'source.py').write_text('def run():\n    return 1\n')
    source={'path':'source.py','line':1,'symbol':'run',
        'sha256':hashlib.sha256((tmp_path/'source.py').read_bytes()).hexdigest(),
        'origin':'worktree_tracked'}
    flow={'id':'one','title':'Example','description':'Example','file':'flows/one.mmd',
        'sources':[source],'limitations':['Local']}
    catalog={'flows':[flow],'source':{'mode':'worktree','base_commit':'b'*40,
        'worktree_sha256':'c'*64,'changed_paths':['source.py'],'deleted_paths':['old.py']}}
    (tmp_path/'docs/architecture/flows.json').write_text(json.dumps(catalog))

    block=render_block(tmp_path)
    assert 'fonte local modificada; não é permalink da base' in block
    assert 'blob/' + 'b'*40 + '/source.py' not in block
    assert 'worktree `' + 'c'*64 + '`' in block


def test_model_guide_matches_local_config_and_does_not_change_default():
    root=Path(__file__).resolve().parents[1]
    config=json.loads((root/'opencode.json').read_text(encoding='utf-8'))
    catalog=json.loads((root/'integrations/opencode_provider_models.json').read_text(encoding='utf-8'))
    guide=(root/'docs/architecture/MODELOS_E_ECONOMIA_DE_TOKENS_R916.md').read_text(encoding='utf-8')
    assert config['model']=='ollama-local/llama3.2'
    assert 'gpt-6-luna' not in catalog
    assert 'gpt-5.6-luna' in catalog and 'gemini-3.8-flash' in catalog
    assert 'catalog_is_not_entitlement' in guide
    assert 'não verificaram a identidade do modelo respondente' in guide
    assert 'gpt-6-luna' in guide and 'gpt-5.6-luna' in guide
    assert 'não é preço da assinatura' in guide
    assert 'custo por tarefa aceita' in guide
    assert 'sem trocar o padrão automaticamente' in guide


def test_quantized_github_research_pins_sources_and_limits():
    root=Path(__file__).resolve().parents[1]
    guide=(root/'docs/architecture/QUANTIZACAO_LOCAL_GITHUB_R916.md').read_text(encoding='utf-8')
    for repo in ('ggml-org/llama.cpp','ollama/ollama','unslothai/unsloth'):
        assert f'github.com/{repo}/tree/' in guide
    assert 'Q4_K_M' in guide and 'imatrix' in guide
    assert 'não realizados' in guide
    assert 'weights' in guide.lower() and 'licença' in guide.lower()


def test_viewer_page_discloses_hash_of_actual_template():
    from scripts.render_architecture_page import render_page

    root=Path(__file__).resolve().parents[1]
    template=(root/'docs/architecture/viewer-template.html').read_bytes()
    digest=hashlib.sha256(template).hexdigest()
    inventory={'git':{'commit':'a'*40,'source':'worktree','worktree_sha256':'b'*64,
        'changed_paths':[],'deleted_paths':[]},'counts':{},'modules':[],'files':[],
        'edges':[],'surfaces':[],'limitations':[]}
    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"></svg>'
    page=render_page(inventory,svg,svg,[])
    assert digest in page
    assert '__VIEWER_TEMPLATE_SHA256__' not in page


def test_current_r916_receipt_matches_map_and_flow_artifacts():
    root=Path(__file__).resolve().parents[1]
    path=root/'docs/verification-documentation-r916-ollama-quantizacao.json'
    assert path.is_file(), 'Recibo documental atual ausente'
    receipt=json.loads(path.read_text())
    inventory=json.loads((root/'docs/architecture/architecture-inventory.json').read_text())
    catalog=json.loads((root/'docs/architecture/flows.json').read_text())
    assert receipt['source']['worktree_sha256']==inventory['git']['worktree_sha256']
    assert receipt['source']['commit']==inventory['git']['commit']
    assert receipt['counts']['flows']==len(catalog['flows'])==22
    indexed={item['id']:item for item in receipt['render_manifest']}
    assert set(indexed)=={flow['id'] for flow in catalog['flows']}
    for flow in catalog['flows']:
        row=indexed[flow['id']]
        source=root/'docs/architecture'/flow['file']
        svg=source.with_suffix('.svg')
        assert row['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
        assert row['svg_sha256']==hashlib.sha256(svg.read_bytes()).hexdigest()
    assert receipt['externally_validated'] is False
    assert receipt['model_default_changed'] is False


@pytest.mark.parametrize('changed',[True,False])
def test_worktree_source_links_never_misattribute_changed_bytes(tmp_path,changed):
    from scripts.sync_readme_flowcharts import render_block
    folder=tmp_path/'docs/architecture/flows';folder.mkdir(parents=True)
    (tmp_path/'source.py').write_text('def run():\n    return 1\n')
    (folder/'one.mmd').write_text('flowchart LR\n  A --> B\n')
    (folder/'one.svg').write_text('<svg/>')
    entry={'id':'one','title':'Example','description':'Example','file':'flows/one.mmd',
           'sources':[{'path':'source.py','line':1,'symbol':'run'}],'limitations':['Local']}
    base='a'*40
    catalog={'flows':[entry],'source':{'mode':'worktree','base_commit':base,
        'worktree_sha256':'b'*64,'changed_paths':['source.py'] if changed else [],'deleted_paths':[]}}
    (tmp_path/'docs/architecture/flows.json').write_text(json.dumps(catalog))
    block=render_block(tmp_path)
    permalink=f'https://github.com/MarceloClaro/opencode-ecosystem-core/blob/{base}/source.py#L1'
    if changed:
        assert permalink not in block
        assert '`source.py:1` (fonte local modificada; não é permalink da base)' in block
    else:
        assert f'[source.py:1]({permalink})' in block
