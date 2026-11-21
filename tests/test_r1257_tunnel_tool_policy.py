"""R1257: fronteira real do bridge, filho/autorizações simulados, sem rede."""
from __future__ import annotations

import asyncio
import hashlib
import importlib
import json
import os
from pathlib import Path
import time

import pytest


CORE_NAMES = {
    'ecosystem_agent_profile', 'ecosystem_local_ci', 'ecosystem_knowledge_plan',
    'ecosystem_scientific_run', 'ecosystem_scientific_verify',
    'ecosystem_integration_status', 'ecosystem_rea', 'ecosystem_production',
    'ecosystem_code_context', 'ecosystem_browser', 'ecosystem_scientific_runtime',
    'ecosystem_dataset_download', 'ecosystem_dataset_custom',
    'ecosystem_scientific_plugins', 'ecosystem_gemini_notebook',
    'ecosystem_artifact_handoff', 'ecosystem_skill_plan',
    'ecosystem_claude_bughunter_plan', 'ecosystem_library_search',
    'ecosystem_quantum_catalog', 'ecosystem_knowledge_query',
    'ecosystem_text_spec', 'ecosystem_status', 'ecosystem_route',
    'ecosystem_run', 'ecosystem_workflow', 'ecosystem_workflow_status',
}
READ_NAMES = {
    'ecosystem_integration_status', 'ecosystem_artifact_handoff',
    'ecosystem_skill_plan', 'ecosystem_claude_bughunter_plan',
    'ecosystem_library_search', 'ecosystem_quantum_catalog',
    'ecosystem_knowledge_query', 'ecosystem_status', 'ecosystem_route',
    'ecosystem_workflow_status',
}


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def request(name='ecosystem_integration_status', args=None, rid=1, auth=None):
    params = {'name': name, 'arguments': {} if args is None else args}
    if auth is not None:
        params['_meta'] = {'authorization': auth}
    return {'jsonrpc': '2.0', 'id': rid, 'method': 'tools/call', 'params': params}


@pytest.fixture
def bridge():
    return importlib.import_module('integrations.ecosystem_mcp_tunnel')


@pytest.fixture
def harness(bridge, tmp_path):
    assert hasattr(bridge, 'TunnelBridge'), 'falta fronteira persistente de política'
    root = tmp_path / 'core'
    (root / 'specs').mkdir(parents=True)
    spec = root / 'specs/SPEC-935-R1257-test.md'
    spec.write_text('---\nspec_id: SPEC-935-R1257\n---\nAutorização de teste local.\n')
    private = tmp_path / 'private'
    private.mkdir(mode=0o700)
    authfile = private / 'authorizations.json'
    policy = bridge.ToolPolicy(root=root, authorizations=authfile)
    session = bridge.TunnelBridge(policy)
    child, client = [], []

    async def send_child(line):
        child.append(json.loads(line))

    async def send_client(line):
        client.append(json.loads(line))

    def send(payload):
        asyncio.run(session.process_line(payload if isinstance(payload, str) else encode(payload), send_child, send_client))

    def reply(payload):
        asyncio.run(session.process_child_line(encode(payload), send_client))

    return session, root, spec, authfile, child, client, send, reply


def grant(h, name='ecosystem_text_spec', args=None, operation='call', effects=None, targets=None):
    _, root, spec, authfile, *_ = h
    args = {'task': 'revisar texto', 'criteria': ['explicar limites']} if args is None else args
    scope = {'workspace': str(root), 'operation': operation,
             'effects': ['local_write'] if effects is None else effects,
             'targets': [str(root)] if targets is None else targets}
    record = {'grant_id': 'approval-1', 'tool': name, 'spec_id': 'SPEC-935-R1257',
              'spec_sha256': hashlib.sha256(spec.read_bytes()).hexdigest(),
              'arguments_sha256': hashlib.sha256(encode(args).encode()).hexdigest(),
              'scope': scope, 'expires_at': int(time.time()) + 1800, 'used': False}
    authfile.write_text(encode({'version': 1, 'grants': [record]}))
    authfile.chmod(0o600)
    selection = {k: record[k] for k in ('grant_id', 'spec_id', 'scope')}
    return args, record, selection


def test_current_bridge_must_not_forward_unknown_tools(bridge):
    child, client = [], []
    async def to_child(line): child.append(line)
    async def to_client(line): client.append(json.loads(line))
    asyncio.run(bridge.process_line(encode(request('future_admin')), to_child, to_client))
    assert child == [], 'chamada desconhecida atravessou a fronteira'
    assert client[0]['error']['code'] == -32602


@pytest.mark.parametrize('wire', [
    'not-json', '[]', '[{"jsonrpc":"2.0","id":1,"method":"tools/call"}]',
    '{"jsonrpc":"2.0","id":1,"id":2,"method":"tools/call"}',
    '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"ecosystem_status","arguments":{"x":NaN}}}',
    {'jsonrpc':'2.0','method':'tools/call','params':{'name':'ecosystem_status','arguments':{}}},
    {'jsonrpc':'2.0','id':1,'method':'resources/read','params':{'uri':'file:///secret'}},
    {'jsonrpc':'2.0','id':1,'method':'prompts/get'},
    {'jsonrpc':'2.0','id':1,'method':'arbitrary/dispatch'},
    {'jsonrpc':'2.0','id':True,'method':'tools/list'},
    {'jsonrpc':'2.0','id':1,'method':'tools/list','params':{'cursor':'bypass'}},
    {'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'ecosystem_status','arguments':{},'bypass':True}},
])
def test_invalid_or_alternative_requests_never_reach_child(harness, wire):
    *_, child, client, send, reply = harness
    send(wire)
    assert child == []


@pytest.mark.parametrize('name,args', [
    ('ecosystem_status', {'confirm':True}),
    ('ecosystem_quantum_catalog', {'config':{'operation':'import'}}),
    ('ecosystem_quantum_catalog', {'config':{'operation':'status','url':'https://target'}}),
    ('ecosystem_knowledge_query', {'config':{'operation':'sql','query':'DROP TABLE x'}}),
    ('ecosystem_library_search', {'query':'x','top_k':True}),
    ('ecosystem_route', {'task':'x','required_capabilities':'burp'}),
    ('ecosystem_skill_plan', {'skill_name':'../../etc/passwd'}),
    ('ecosystem_workflow_status', {'workflow_id':'../../secret'}),
    ('ecosystem_text_spec', {'task':'x','criteria':['x'],'confirm':True}),
    ('ecosystem_agent_profile', {'config':{'operation':'create','consent':True}}),
    ('burp_scan', {}), ('ecosystem_status_extra', {}),
])
def test_unauthorized_or_malformed_calls_are_denied(harness, name, args):
    *_, child, client, send, reply = harness
    send(request(name,args))
    assert child == []
    assert client[0]['error']['code'] == -32602


@pytest.mark.parametrize('name,args', [
    ('ecosystem_integration_status', {}),
    ('ecosystem_claude_bughunter_plan', {}),
    ('ecosystem_library_search', {'query':'MCP','top_k':2}),
    ('ecosystem_quantum_catalog', {'config':{'operation':'status'}}),
    ('ecosystem_knowledge_query', {'config':{'operation':'sources'}}),
    ('ecosystem_route', {'task':'explicar MCP','required_capabilities':['text']}),
])
def test_explicit_read_calls_preserve_arguments_and_correlate_results(harness,name,args):
    _,_,_,_,child,client,send,reply = harness
    send(request(name,args,rid='client-id'))
    assert len(child) == 1
    assert child[0]['params'] == {'name':name,'arguments':args}
    reply({'jsonrpc':'2.0','id':child[0]['id'],'result':{'content':[{'type':'text','text':'local'}]}})
    assert client == [{'jsonrpc':'2.0','id':'client-id','result':{'content':[{'type':'text','text':'local'}]}}]


def test_list_filters_unknown_and_effects_from_child_even_with_readonly_hint(harness):
    _,_,_,_,child,client,send,reply = harness
    send({'jsonrpc':'2.0','id':7,'method':'tools/list','params':{}})
    tools = [{'name':n,'inputSchema':{'type':'object'},'annotations':{'readOnlyHint':True}} for n in sorted(CORE_NAMES|{'future_admin','burp_scan'})]
    reply({'jsonrpc':'2.0','id':child[0]['id'],'result':{'tools':tools}})
    assert {t['name'] for t in client[0]['result']['tools']} == READ_NAMES
    assert client[0]['id'] == 7


@pytest.mark.parametrize('result', [
    {'tools':[{'name':'ecosystem_status'},{'name':'ecosystem_status'}]},
    {'tools':'bad'}, {'tools':[{'name':[]} ]},
    {'tools':[],'nextCursor':'hidden-page'},
])
def test_malformed_or_paginated_child_listing_fails_closed(harness,result):
    _,_,_,_,child,client,send,reply = harness
    send({'jsonrpc':'2.0','id':1,'method':'tools/list'})
    reply({'jsonrpc':'2.0','id':child[0]['id'],'result':result})
    assert 'result' not in client[0]
    assert 'error' in client[0]


def test_orphan_child_messages_do_not_escape_and_duplicate_client_id_keeps_original(harness):
    _,_,_,_,child,client,send,reply = harness
    send({'jsonrpc':'2.0','id':1,'method':'tools/list'})
    send(request(rid=1))
    assert len(child) == 1
    reply({'jsonrpc':'2.0','id':'orphan','result':{'secret':True}})
    assert len(client) == 1 and 'error' in client[0]
    reply({'jsonrpc':'2.0','id':child[0]['id'],'result':{'tools':[]}})
    assert client[-1] == {'jsonrpc':'2.0','id':1,'result':{'tools':[]}}


def test_exact_local_authorization_is_consumed_durably_before_dispatch(harness,bridge):
    session,root,_,authfile,child,client,send,reply = harness
    args,record,selection = grant(harness)
    send(request('ecosystem_text_spec',args,auth=selection))
    assert len(child) == 1 and child[0]['params'] == {'name':'ecosystem_text_spec','arguments':args}
    assert json.loads(authfile.read_text())['grants'][0]['used'] is True
    restarted = bridge.TunnelBridge(bridge.ToolPolicy(root=root,authorizations=authfile))
    async def capture(line): child.append(json.loads(line))
    async def client_send(line): client.append(json.loads(line))
    asyncio.run(restarted.process_line(encode(request('ecosystem_text_spec',args,auth=selection)),capture,client_send))
    assert len(child) == 1 and 'error' in client[-1]


@pytest.mark.parametrize('change', ['args','type','scope','spec','spec_hash','expired','future','used','mode','parent_mode','symlink','missing','duplicate_grant'])
def test_modified_or_untrusted_authorizations_are_denied(harness,change):
    _,_,spec,authfile,child,client,send,reply = harness
    args,record,selection = grant(harness)
    if change == 'args': args['task'] = 'executar outra tarefa'
    if change == 'type': args['criteria'] = [True]
    if change == 'scope': selection = {**selection,'scope':{**selection['scope'],'targets':['/elsewhere']}}
    if change == 'spec': selection['spec_id'] = 'SPEC-935-R1'
    if change == 'spec_hash': spec.write_text('spec alterada')
    if change == 'expired': record['expires_at'] = int(time.time())-1
    if change == 'future': record['expires_at'] = int(time.time())+7200
    if change == 'used': record['used'] = True
    if change in {'expired','future','used','duplicate_grant'}:
        authfile.write_text(encode({'version':1,'grants':[record,record] if change == 'duplicate_grant' else [record]}))
    if change == 'mode': authfile.chmod(0o644)
    if change == 'parent_mode': authfile.parent.chmod(0o755)
    if change == 'symlink':
        target=authfile.with_name('target'); authfile.rename(target); authfile.symlink_to(target)
    if change == 'missing': authfile.unlink()
    send(request('ecosystem_text_spec',args,auth=selection))
    assert child == [] and 'error' in client[0]


@pytest.mark.parametrize('name,args,operation', [
    ('burp_scan',{},'call'),
    ('ecosystem_gemini_notebook',{'config':{'operation':'mcp','tool':'burp_scan','arguments':{}}},'mcp'),
    ('ecosystem_scientific_plugins',{'config':{'operation':'request','tool':'burp_scan'}},'request'),
    ('ecosystem_rea',{'config':{'operation':'analyze','path':'/target'}},'analyze'),
    ('ecosystem_production',{'config':{'operation':'run','consent':True}},'run'),
    ('ecosystem_run',{'task':'chamar Burp'},'call'),
    ('ecosystem_workflow',{'nodes':[]},'call'),
])
def test_grant_cannot_enable_unknown_burp_or_generic_dispatch(harness,name,args,operation):
    *_,child,client,send,reply = harness
    _,_,selection = grant(harness,name,args,operation)
    send(request(name,args,auth=selection))
    assert child == [] and 'error' in client[0]


def test_effects_visible_only_while_valid_grant_exists(harness):
    _,_,_,authfile,child,client,send,reply = harness
    args,_,selection = grant(harness)
    def listing(rid):
        send({'jsonrpc':'2.0','id':rid,'method':'tools/list'})
        reply({'jsonrpc':'2.0','id':child[-1]['id'],'result':{'tools':[{'name':'ecosystem_text_spec','inputSchema':{'type':'object'}}]}})
        return client[-1]['result']['tools']
    assert len(listing(1)) == 1
    send(request('ecosystem_text_spec',args,rid=2,auth=selection))
    assert listing(3) == []


def test_initialize_removes_alternate_capabilities(harness):
    _,_,_,_,child,client,send,reply = harness
    send({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'local','version':'1'}}})
    reply({'jsonrpc':'2.0','id':child[0]['id'],'result':{'protocolVersion':'2025-11-25','capabilities':{'tools':{},'resources':{},'prompts':{}},'serverInfo':{'name':'fixture','version':'1'}}})
    assert client[0]['result']['capabilities'] == {'tools':{'listChanged':False}}


def test_authorization_cannot_be_inside_workspace(harness,bridge):
    _,root,_,_,child,client,send,reply = harness
    path=root/'authorizations.json'
    policy=bridge.ToolPolicy(root=root,authorizations=path)
    assert policy.visible('ecosystem_text_spec') is False
