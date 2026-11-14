#!/usr/bin/env python3
"""Conservative MCP fleet probe; default tests ONLY the primary coordinator.

Does not call tools. Does not run npx/uvx unless explicitly opted in.
"""
from __future__ import annotations
import argparse
import asyncio
import json
import os
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import urlsplit

PRIMARY_NAME = 'ecosystem-network'
MANAGERS = {'npx','uvx','npm','yarn','pnpm'}

def flatten(mcps):
    if not isinstance(mcps, dict):
        raise ValueError('mcp must be object')
    out = {}
    for key, val in mcps.items():
        rows = val.items() if key == 'servers' and isinstance(val,dict) and 'type' not in val else [(key,val)]
        for name, item in rows:
            if name in out:
                raise ValueError('duplicate MCP ' + name)
            out[name] = item
    return out


def classify(name, item, root, allow_managers=False):
    row = {'name':name,'status':'not_probed','declared':True}
    if not isinstance(item,dict) or item.get('type') not in ('local','remote'):
        row['status'] = 'invalid_definition'; return row
    if item.get('enabled') is False:
        row['status'] = 'disabled'; return row
    if item['type'] == 'remote':
        url = item.get('url')
        if not isinstance(url,str):
            row['status'] = 'invalid_url'; return row
        p = urlsplit(url)
        if p.username or p.password or p.query or p.fragment or not p.hostname or (p.scheme != 'https' and not (p.scheme == 'http' and p.hostname in ('localhost','127.0.0.1','::1'))):
            row['status'] = 'unsafe_url'; return row
        row['transport'] = 'remote'; return row
    argv = item.get('command')
    if not isinstance(argv,list) or not argv or any(not isinstance(v,str) or not v for v in argv):
        row['status']='invalid_command'; return row
    program=argv[0]
    if Path(program).name in MANAGERS and not allow_managers:
        row['status']='deferred_package_manager'; return row
    cwd = item.get('cwd') or str(root)
    if not isinstance(cwd,str):
        row['status']='invalid_cwd'; return row
    cwdpath=Path(cwd) if Path(cwd).is_absolute() else root/cwd
    if not cwdpath.is_dir():
        row['status']='missing_cwd';return row
    binary = Path(program) if Path(program).is_absolute() else cwdpath/program
    found = (binary.is_file() and os.access(binary,os.X_OK)) if '/' in program else bool(shutil.which(program))
    row['status']='ready_for_probe' if found else 'missing_executable'
    row['transport']='stdio'
    return row


def environment_for(entry):
    env=os.environ.copy()
    settings=entry.get('environment',{})
    if not isinstance(settings,dict):
        raise ValueError('invalid environment')
    for key, value in settings.items():
        if not isinstance(key,str) or not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',key) or not isinstance(value,str):
            raise ValueError('invalid environment')
        match=re.fullmatch(r'\{env:([A-Za-z_][A-Za-z_0-9]*)\}',value)
        if match:
            if match.group(1) not in env:
                raise ValueError('missing environment variable')
            value=env[match.group(1)]
        env[key]=value
    return env

async def probe(name,entry,root,timeout):
    status={'name':name,'status':'probe_failed'}
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        async with asyncio.timeout(timeout):
            if entry['type'] == 'local':
                cmd=list(entry['command'])
                cwd=Path(entry.get('cwd') or root)
                if not cwd.is_absolute(): cwd=root/cwd
                if '/' in cmd[0] and not Path(cmd[0]).is_absolute(): cmd[0]=str(cwd/cmd[0])
                params=StdioServerParameters(command=cmd[0],args=cmd[1:],cwd=str(cwd),env=environment_for(entry))
                with open(os.devnull,'w') as stderr:
                    async with stdio_client(params,errlog=stderr) as (reader,writer):
                        async with ClientSession(reader,writer) as client:
                            await client.initialize()
                            tools=await client.list_tools()
                            status.update(status='initialized',tool_count=len(tools.tools),tools=sorted(t.name for t in tools.tools))
            else:
                from mcp.client.streamable_http import streamablehttp_client
                async with streamablehttp_client(entry['url']) as streams:
                    async with ClientSession(streams[0],streams[1]) as client:
                        await client.initialize()
                        tools=await client.list_tools()
                        status.update(status='initialized',tool_count=len(tools.tools),tools=sorted(t.name for t in tools.tools))
    except Exception as exc:
        status.update(status='probe_failed',error_type=type(exc).__name__)
    return status

async def inspect(rows,entries,root,names,timeout,concurrency):
    sem=asyncio.Semaphore(concurrency)
    async def work(row):
        if row['name'] not in names or row['status'] != 'ready_for_probe': return
        async with sem:
            row.update(await probe(row['name'],entries[row['name']],root,timeout))
    await asyncio.gather(*(work(r) for r in rows))


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--probe',action='store_true')
    ap.add_argument('--all',action='store_true',help='Explicitly probe every eligible server; starts many child processes')
    ap.add_argument('--allow-package-managers',action='store_true')
    ap.add_argument('--timeout',type=float,default=15)
    ap.add_argument('--concurrency',type=int,default=2)
    args=ap.parse_args(argv)
    if not 2 <= args.timeout <= 120 or not 1 <= args.concurrency <= 6:
        ap.error('timeout 2..120; concurrency 1..6')
    root=args.root.resolve()
    try:
        config=json.loads((root/'opencode.json').read_text(encoding='utf-8-sig'))
        entries=flatten(config.get('mcp'))
    except Exception as exc:
        print(json.dumps({'error_type':type(exc).__name__,'error':str(exc)[:250]},ensure_ascii=True))
        return 2
    rows=[classify(name,item,root,args.allow_package_managers) for name,item in entries.items()]
    requested=set(entries) if args.all else {PRIMARY_NAME}
    if args.probe:
        asyncio.run(inspect(rows,entries,root,requested,args.timeout,args.concurrency))
    result={
        'schema':'core-click-fleet/v1',
        'primary_agent':config.get('default_agent'),
        'agents_configured':len(config.get('agent',{})),
        'mcp_configured':len(entries),
        'mcp_initialized':sum(x['status']=='initialized' for x in rows),
        'probe_performed':args.probe,
        'probe_scope':'all_eligible' if args.all else 'primary_only',
        'results':rows,
        'limitations':['Initialization is only MCP transport, not execution, authentication or inference.'],
    }
    print(json.dumps(result,ensure_ascii=True,sort_keys=True,indent=2))
    return 0

if __name__=='__main__':
    sys.exit(main())
