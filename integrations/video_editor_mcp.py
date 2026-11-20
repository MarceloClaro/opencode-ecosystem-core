"""MCP R1042 do editor universal: projeto, plano e render sob aprovação.

Superfície pequena: sem shell, sem URL, sem caminho do cliente fora da raiz.
Render real exige arquivo de aprovação criado pelo operador; dry-run é livre.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from integrations import video_analysis, video_editor

ID = re.compile(r'[A-Za-z0-9_-]{1,80}')


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def create_server(root=None, *, mpt_output_root=None):
    value = root if root is not None else os.environ.get('EDITOR_PROJECT_ROOT')
    if not value or not Path(value).is_dir():
        raise ValueError('EDITOR_PROJECT_ROOT must be an existing directory')
    root = Path(value).absolute()
    if root.is_symlink() or any(p.is_symlink() for p in root.parents):
        raise ValueError('symlink root not allowed')
    configured_mpt_root = mpt_output_root
    if configured_mpt_root is None:
        configured_mpt_root = os.environ.get('MPT_OUTPUT_ROOT')
    if configured_mpt_root is None and os.environ.get('MPT_HOME'):
        configured_mpt_root = Path(os.environ['MPT_HOME']) / 'storage' / 'tasks'
    if configured_mpt_root is not None:
        configured_mpt_root = Path(configured_mpt_root).expanduser().absolute()
        if (configured_mpt_root.is_symlink()
                or any(p.is_symlink() for p in configured_mpt_root.parents)
                or not configured_mpt_root.is_dir()):
            raise ValueError('MPT_OUTPUT_ROOT must be an existing non-symlink directory')
    server = FastMCP('video-editor')
    read = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)
    write = ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False,
                            idempotentHint=True)
    create_only = ToolAnnotations(readOnlyHint=False, destructiveHint=False,
                                  openWorldHint=False, idempotentHint=False)

    def confined(relative, *, must_exist=False, directory=False):
        if not isinstance(relative, str) or not relative:
            raise ValueError('path required')
        p = Path(relative)
        if p.is_absolute() or any(part in ('.', '..') for part in p.parts):
            raise ValueError('relative confined path required')
        target = root / p
        for node in (target, *target.parents):
            if node.is_symlink():
                raise ValueError('symlink blocked')
        if not target.resolve().is_relative_to(root.resolve()):
            raise ValueError('path escape blocked')
        if must_exist and not target.exists():
            raise ValueError('path missing')
        if directory and not target.is_dir():
            raise ValueError('directory required')
        return target

    def compact(value):
        text = json.dumps(value, ensure_ascii=False, allow_nan=False)
        if len(text) > 7000:
            return {'status': value.get('status', 'detail_in_artifact'),
                    'artifact': value.get('artifact'), 'truncated': True}
        return value

    def load_project(project_id):
        if not isinstance(project_id, str) or not ID.fullmatch(project_id):
            raise ValueError('invalid project_id')
        path = confined(f'editor-projects/{project_id}.json', must_exist=True)
        project = video_editor.load_project(path.read_text())
        project['root'] = str(root)
        for source in project['sources'].values():
            raw = Path(source['path'])
            if raw.is_absolute():
                try:
                    raw = raw.relative_to(root)
                except ValueError as exc:
                    raise ValueError('project source outside MCP root') from exc
            source['path'] = str(confined(str(raw), must_exist=True))
        return project

    def registered_source(project_id, source_id):
        """Resolve only a source already recorded in the confined project."""
        project = load_project(project_id)
        if not isinstance(source_id, str) or not source_id:
            raise ValueError('registered source_id required')
        source_key = Path(source_id)
        if source_key.is_absolute() or any(part in ('.', '..') for part in source_key.parts):
            raise ValueError('registered relative source_id required')
        record = project['sources'].get(source_id)
        if record is None:
            raise ValueError('source_id is not registered in project')
        if not isinstance(record, dict):
            raise TypeError('registered project source must be an object')
        source = Path(record['path'])
        try:
            relative = source.relative_to(root)
        except ValueError as exc:
            raise ValueError('project source outside MCP root') from exc
        target = confined(str(relative), must_exist=True)
        if target.is_symlink() or not target.is_file():
            raise ValueError('registered source must be a regular non-symlink file')
        expected = record.get('sha256')
        if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{64}', expected):
            raise ValueError('registered source hash required')
        if _sha(target) != expected:
            raise ValueError('registered source hash mismatch; reopen project after review')
        return project, target

    def persist_analysis(folder_name, result, id_key):
        raw = json.dumps(result, ensure_ascii=False, sort_keys=True,
                         separators=(',', ':'), allow_nan=False).encode('utf-8')
        artifact_hash = hashlib.sha256(raw).hexdigest()
        relative = f'{folder_name}/{artifact_hash}.json'
        target = confined(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target = confined(relative)
        if target.exists():
            if target.is_symlink() or not target.is_file() or target.read_bytes() != raw:
                raise ValueError('content-addressed artifact collision or integrity mismatch')
            status = 'cached'
        else:
            try:
                with target.open('xb') as stream:
                    stream.write(raw)
                status = 'created'
            except FileExistsError:
                if target.is_symlink() or not target.is_file() or target.read_bytes() != raw:
                    raise ValueError('content-addressed artifact collision or integrity mismatch')
                status = 'cached'
        return {'status': status, id_key: artifact_hash,
                'sha256': artifact_hash, 'artifact': str(target.relative_to(root))}

    @server.tool(annotations=write)
    def editor_open(media_path: str, project_id: str, allow_silent: bool = False) -> dict:
        """Abre um vídeo local e grava o projeto; não edita, não renderiza."""
        if not ID.fullmatch(project_id):
            raise ValueError('invalid project_id')
        media = confined(media_path, must_exist=True)
        info = (video_editor.probe_media(media, allow_silent=True) if allow_silent
                else video_editor.probe_media(media))
        project = video_editor.project_from_probe(media_path, info, project_id=project_id,
                                                  allow_silent=allow_silent)
        project['root'] = str(root)
        text = video_editor.dumps_project(project)
        target = confined(f'editor-projects/{project_id}.json')
        target.parent.mkdir(exist_ok=True)
        if target.exists():
            if target.read_text() != text:
                raise ValueError('project exists with different content')
            return {'status': 'cached', 'project_id': project_id,
                    'artifact': str(target.relative_to(root))}
        with target.open('x', encoding='utf-8') as stream:
            stream.write(text)
        return {'status': 'opened', 'project_id': project_id,
                'frames': info['video']['frames'], 'fps': info['video']['fps'],
                'artifact': str(target.relative_to(root))}

    if configured_mpt_root is not None:
        @server.tool(annotations=create_only)
        def editor_import_mpt_output(media_path: str, project_id: str,
                                     allow_silent: bool = False) -> dict:
            """Importa somente um MP4 final local de MPT; não inicia MPT nem renderiza."""
            from integrations.moneyprinterturbo import import_task_output

            return import_task_output(
                configured_mpt_root, root, media_path, project_id,
                allow_silent=allow_silent)

    @server.tool(annotations=read)
    def editor_list_projects() -> dict:
        """Lista projetos por ID; não lê a timeline inteira."""
        folder = root / 'editor-projects'
        ids = sorted(p.stem for p in folder.glob('*.json')) if folder.is_dir() else []
        return {'projects': ids[:200], 'count': len(ids), 'truncated': len(ids) > 200}

    @server.tool(annotations=write)
    def editor_plan(project_id: str, operation: str, params: dict) -> dict:
        """Cria plano auditável. Caminhos ficam confinados à raiz do projeto."""
        project = load_project(project_id)
        if not isinstance(params, dict):
            raise TypeError('params object required')
        clean = dict(params)
        for key in ('output',):
            if key not in clean:
                raise ValueError('output required')
            clean[key] = str(confined(clean[key]))
        for key in ('file',):
            if key in clean:
                target = confined(clean[key], must_exist=True)
                clean[key] = str(target.relative_to(root))
        for key in ('video', 'audio'):
            if key in clean:
                clean[key] = str(confined(clean[key], must_exist=True))
        if 'project_path' in clean:
            clean['project_path'] = str(confined(clean['project_path'],
                                                 must_exist=True, directory=True))
        if 'sources' in clean:
            rows = clean['sources']
            if not isinstance(rows, list):
                raise ValueError('sources list required')
            clean['sources'] = [{**row, 'path': str(confined(row['path'], must_exist=True))}
                                for row in rows]
        result = video_editor.plan(project, operation, clean)
        plan_id = result['plan_sha256'][:16]
        target = confined(f'editor-plans/{plan_id}.json')
        target.parent.mkdir(exist_ok=True)
        if target.exists():
            existing = json.loads(target.read_text())
            if existing.get('plan_sha256') != result['plan_sha256']:
                raise ValueError('plan ID collision/integrity mismatch')
            status = 'cached'
        else:
            with target.open('x', encoding='utf-8') as stream:
                stream.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
            status = 'planned'
        return {'status': status, 'plan_id': plan_id, 'operation': operation,
                'backend': result['backend'], 'expected_frames': result['expected_frames'],
                'warnings': result['warnings'], 'limitations': result['limitations'],
                'artifact': str(target.relative_to(root))}

    @server.tool(annotations=write)
    def editor_analyze_scenes(project_id: str, source_id: str,
                              threshold: float = 27.0,
                              min_scene_len: int = 15) -> dict:
        """Gera marcadores de cena revisáveis para uma fonte registrada; não edita."""
        _project, source = registered_source(project_id, source_id)
        result = video_analysis.detect_scene_markers(
            source, threshold=threshold, min_scene_len=min_scene_len)
        artifact = persist_analysis('editor-analysis', result, 'analysis_id')
        artifact['kind'] = result['kind']
        artifact['marker_count'] = len(result['markers'])
        artifact['review_required'] = True
        return artifact

    @server.tool(annotations=write)
    def editor_propose_auto_cuts(project_id: str, source_id: str,
                                 timeout: int = 300) -> dict:
        """Salva export Auto-Editor como proposta pendente; nunca renderiza."""
        if isinstance(timeout, bool) or not isinstance(timeout, int) or not 1 <= timeout <= 600:
            raise ValueError('timeout must be an integer between 1 and 600 seconds')
        _project, source = registered_source(project_id, source_id)
        result = video_analysis.propose_auto_editor_cuts(source, timeout=timeout)
        if result.get('approval_state') != 'pending' or result.get('rendered') is not False:
            raise ValueError('cut adapter returned a non-reviewable result')
        artifact = persist_analysis('editor-proposals', result, 'proposal_id')
        artifact['kind'] = result['kind']
        artifact['segment_count'] = len(result['segments'])
        artifact['approval_state'] = 'pending'
        artifact['review_required'] = True
        artifact['rendered'] = False
        return artifact

    @server.tool(annotations=read)
    def editor_render(plan_id: str, dry_run: bool = True) -> dict:
        """Mostra o comando (dry-run) ou executa plano aprovado pelo operador."""
        if not isinstance(plan_id, str) or not ID.fullmatch(plan_id):
            raise ValueError('invalid plan_id')
        path = confined(f'editor-plans/{plan_id}.json', must_exist=True)
        plan = json.loads(path.read_text())
        if plan.get('plan_sha256', '')[:16] != plan_id:
            raise ValueError('plan integrity mismatch')
        if dry_run:
            return compact(video_editor.render(plan, dry_run=True))
        approval = confined(f'editor-approvals/{plan_id}.json', must_exist=True)
        data = json.loads(approval.read_text())
        if (data.get('approved') is not True or not isinstance(data.get('reviewer'), str)
                or not data['reviewer'].strip()
                or data.get('plan_sha256') != plan['plan_sha256']):
            raise ValueError('operator approval required and must bind the plan hash')
        return compact(video_editor.render(plan))

    @server.tool(annotations=read)
    def editor_status() -> dict:
        """Contagens e versões locais; não analisa mídia nem executa render."""
        folders = {name: confined(name) for name in (
            'editor-projects', 'editor-plans', 'editor-approvals',
            'editor-analysis', 'editor-proposals')}

        def count_json(folder):
            if not folder.is_dir():
                return 0
            return sum(1 for item in folder.glob('*.json')
                       if not item.is_symlink() and item.is_file())

        return {'projects': count_json(folders['editor-projects']),
                'plans': count_json(folders['editor-plans']),
                'approvals': count_json(folders['editor-approvals']),
                'analyses': count_json(folders['editor-analysis']),
                'cut_proposals': count_json(folders['editor-proposals']),
                'backends': sorted(video_editor.BACKENDS),
                'toolchain': video_analysis.diagnose_tools(),
                'render_executed': False}

    return server


if __name__ == '__main__':
    create_server().run(transport='stdio')
