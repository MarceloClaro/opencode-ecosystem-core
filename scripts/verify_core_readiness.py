#!/usr/bin/env python3
"""Release gate for OpenCode Ecosystem Core WSL integration (SPEC-CORE-CHATGPT-013).

Read-only by design: no network, subprocesses, command execution or credentials.
Reports are evidence *claims* from separately executed probes, not an attestation
by this script. Live readiness requires coordinator and fleet reports with
matching inventory and successful transport observation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

SCHEMA = 'opencode-core-chatgpt-readiness/v1'
DEFAULT_ROOT = '/home/marceloclaro/opencode-ecosystem-core'
REQUIRED_PRIMARY = 'marceloclaro'
CONFIG = 'opencode.json'
SPEC = 'specs/SPEC-006-agents.md'
TEST = 'tests/test_sdd_tdd.py'


def sha256(path: Path) -> str:
    with path.open('rb') as stream:
        digest = hashlib.sha256()
        for chunk in iter(lambda: stream.read(65536), b''):
            digest.update(chunk)
        return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(data, dict):
        raise ValueError(f'{path.name}: JSON root must be an object')
    return data


def flatten_mcps(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError('mcp must be an object')
    flat: dict[str, Any] = {}
    for name, entry in value.items():
        if name == 'servers' and isinstance(entry, dict) and 'type' not in entry:
            rows = entry.items()
        else:
            rows = [(name, entry)]
        for key, server in rows:
            if key in flat:
                raise ValueError(f'duplicate MCP name: {key}')
            flat[key] = server
    return flat


def static_inventory(root: Path) -> dict[str, Any]:
    data = read_json(root / CONFIG)
    agents = data.get('agent')
    if not isinstance(agents, dict) or not agents:
        raise ValueError('agent must be a nonempty object')
    primary = data.get('default_agent')
    if primary != REQUIRED_PRIMARY or primary not in agents:
        raise ValueError('required primary marceloclaro is not configured')
    servers = flatten_mcps(data.get('mcp'))
    issues: list[str] = []
    names: list[str] = []
    enabled_names: list[str] = []
    for name, entry in servers.items():
        names.append(name)
        if not isinstance(entry, dict):
            issues.append(f'{name}: not an object')
            continue
        if entry.get('enabled') is False:
            continue
        enabled_names.append(name)
        transport = entry.get('type')
        if transport == 'local':
            command = entry.get('command')
            if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
                issues.append(f'{name}: invalid local command')
        elif transport == 'remote':
            url = entry.get('url')
            if not isinstance(url, str) or not (url.startswith('https://') or url.startswith('http://127.0.0.1:') or url.startswith('http://localhost:')):
                issues.append(f'{name}: invalid remote URL policy')
        else:
            issues.append(f'{name}: unsupported transport')
    # The declared SDD contract is a necessary precondition, not evidence tests ran.
    if not (root / SPEC).is_file():
        issues.append('missing SPEC-006')
    elif 'tests/test_sdd_tdd.py' not in (root / SPEC).read_text(encoding='utf-8'):
        issues.append('SPEC-006 does not reference TDD test')
    if not (root / TEST).is_file():
        issues.append('missing SDD/TDD tests')
    return {
        'primary': primary,
        'agent_count': len(agents),
        'mcp_count': len(servers),
        'enabled_count': len(enabled_names),
        'mcp_names': sorted(names),
        'enabled_names': sorted(enabled_names),
        'issues': issues,
        'config_sha256': sha256(root / CONFIG),
        'spec_sha256': sha256(root / SPEC) if (root / SPEC).is_file() else None,
        'test_sha256': sha256(root / TEST) if (root / TEST).is_file() else None,
    }


def evaluate(root: Path, reports: Path | None = None) -> dict[str, Any]:
    report: dict[str, Any] = {
        'schema': SCHEMA,
        'observed': {'local_executor_in_this_chat': False},
        'criteria': {},
        'limitations': [
            'Static inspection does not execute pytest or establish MCP connectivity.',
            'Probe reports are provided files, not independent cryptographic attestations.',
            'MCP initialization does not establish authentication or actual agent inference.',
        ],
    }
    try:
        inventory = static_inventory(root)
        report['inventory'] = inventory
        report['criteria']['C1_static_contract'] = not inventory['issues']
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report['inventory'] = {'issues': [f'{type(exc).__name__}: {str(exc)[:250]}']}
        report['criteria']['C1_static_contract'] = False
    report['criteria']['C2_coordinator_initialized'] = False
    report['criteria']['C3_fleet_initialized'] = False
    report['criteria']['C4_inventory_consistent'] = False
    evidence = {}
    if reports is not None and reports.is_dir() and report['criteria']['C1_static_contract']:
        try:
            coordinator = read_json(reports / 'coordinator.json')
            fleet = read_json(reports / 'fleet.json')
            evidence['coordinator_sha256'] = sha256(reports / 'coordinator.json')
            evidence['fleet_sha256'] = sha256(reports / 'fleet.json')
            live = coordinator.get('live')
            # A successful read of a coordinator tool must be recorded.
            report['criteria']['C2_coordinator_initialized'] = (
                isinstance(live, dict)
                and live.get('coordinator_transport') == 'initialized'
                and live.get('integration_status_called') is True
                and live.get('status_tool_declared') is True
            )
            rows = fleet.get('results')
            valid_rows = isinstance(rows, list) and all(isinstance(row, dict) and isinstance(row.get('name'), str) for row in rows)
            initialized = [] if not valid_rows else [row['name'] for row in rows if row.get('status') == 'initialized' and isinstance(row.get('tool_count'), int) and row['tool_count'] >= 0]
            report['criteria']['C3_fleet_initialized'] = bool(fleet.get('probe_performed') is True and initialized)
            expected = set(report['inventory']['mcp_names'])
            actual = set(row['name'] for row in rows) if valid_rows else set()
            report['criteria']['C4_inventory_consistent'] = (
                valid_rows and len(actual) == len(rows)
                and actual == expected
                and fleet.get('mcp_configured') == len(expected)
                and fleet.get('primary_agent') == REQUIRED_PRIMARY
                and fleet.get('agents_configured') == report['inventory']['agent_count']
                and set(initialized).issubset(set(report['inventory']['enabled_names']))
            )
            evidence['initialized_mcp_names'] = sorted(initialized)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            evidence['error_type'] = type(exc).__name__
    report['evidence'] = evidence
    criteria = report['criteria']
    if not criteria['C1_static_contract']:
        report['state'] = 'CONFIG_INVALID'
    elif all(criteria.values()):
        report['state'] = 'TRANSPORT_OBSERVED'
    else:
        report['state'] = 'CONFIG_ONLY'
    report['accepted_static'] = bool(criteria['C1_static_contract'])
    report['accepted_live'] = report['state'] == 'TRANSPORT_OBSERVED'
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core-root', type=Path, default=Path(DEFAULT_ROOT))
    parser.add_argument('--reports', type=Path, help='directory containing coordinator.json and fleet.json')
    parser.add_argument('--require-live', action='store_true', help='fail unless actual probe receipts report working transport')
    args = parser.parse_args(argv)
    result = evaluate(args.core_root, args.reports)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if (result['accepted_live'] if args.require_live else result['accepted_static']) else 2


if __name__ == '__main__':
    raise SystemExit(main())
