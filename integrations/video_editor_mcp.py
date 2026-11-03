"""MCP R1042 do editor universal: projeto, plano e render sob aprovação.

Superfície pequena: sem shell, sem URL, sem caminho do cliente fora da raiz.
Render real exige arquivo de aprovação criado pelo operador; dry-run é livre.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from integrations import video_editor

ID = re.compile(r'[A-Za-z0-9_-]{1,80}')


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def create_server(root=None):
    value = root if root is not None else os.environ.get('EDITOR_PROJECT_ROOT')
    if not value or not Path(value).is_dir():
        raise ValueError('EDITOR_PROJECT_ROOT must be an existing directory')
    root = Path(value).absolute()
    if root.is_symlink() or any(p.is_symlink() for p in root.parents):
        raise ValueError('symlink root not allowed')
    server = FastMCP('video-editor')
    read = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)
    write = ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False,
                            idempotentHint=True)

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
            raise ValueError('params object required')
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
        """Contagens locais; não executa render nem aprova qualidade."""
        projects = root / 'editor-projects'
        plans = root / 'editor-plans'
        approvals = root / 'editor-approvals'
        return {'projects': len(list(projects.glob('*.json'))) if projects.is_dir() else 0,
                'plans': len(list(plans.glob('*.json'))) if plans.is_dir() else 0,
                'approvals': len(list(approvals.glob('*.json'))) if approvals.is_dir() else 0,
                'backends': sorted(video_editor.BACKENDS),
                'render_executed': False}

    return server


if __name__ == '__main__':
    create_server().run(transport='stdio')
