"""R913: servidor MCP fino, com duas ferramentas por componente local."""
from __future__ import annotations
import argparse
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from integrations.component_actions import validate_component_request
from integrations.component_plugins import COMPONENTS
from integrations.ecosystem_mcp import _knowledge_operation
from integrations.execution_control import run_cancellable

def create_server(component):
    if component not in COMPONENTS: raise ValueError('Componente desconhecido')
    server=FastMCP(f'core-{component}')
    async def status() -> dict:
        return await run_cancellable(_knowledge_operation,'local_component_action',{'component':component,'config':{'operation':'status'}})
    async def action(config: dict) -> dict:
        validated=validate_component_request(component,config)
        return await run_cancellable(_knowledge_operation,'local_component_action',{'component':component,'config':validated})
    action_name={'rea':'rea_action','mirofish':'mirofish_run','lean4':'lean4_verify'}[component]
    server.tool(name=f'{component}_status',description=f'Consulta instalação de {component} pelo MarceloClaro; não comprova inferência.',annotations=ToolAnnotations(readOnlyHint=False,destructiveHint=False,openWorldHint=False))(status)
    server.tool(name=action_name,description=COMPONENTS[component][3],annotations=ToolAnnotations(readOnlyHint=False,destructiveHint=False,openWorldHint=component=='mirofish'))(action)
    return server

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--component',required=True,choices=COMPONENTS)
    create_server(parser.parse_args().component).run(transport='stdio')

if __name__=='__main__': main()
