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
