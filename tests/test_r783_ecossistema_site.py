"""Aceite funcional do percurso ilustrativo do ecossistema, sem rede."""

import json
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "artigos" / "pucrs-roteamento-atencao" / "site" / "ecosystem.mjs"


def execute_node(body, *, check=True):
    node = shutil.which("node")
    assert node, "Node.js é necessário para conferir o percurso do navegador."
    script = (
        "import { ECOSYSTEM_STEPS, ECOSYSTEM_SCOPES, createTourState, transitionTour, getTourView } "
        f"from {json.dumps(MODULE.as_uri())};\n" + body
    )
    return subprocess.run(
        [node, "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
        check=check,
    )


def test_initial_state_and_legible_content():
    output = execute_node(
        "const state=createTourState(); process.stdout.write(JSON.stringify({"
        "state,view:getTourView(state),steps:ECOSYSTEM_STEPS,scopes:ECOSYSTEM_SCOPES}));"
    )
    result = json.loads(output.stdout)
    assert result["state"] == {"step": 0, "scope": "ecosystem"}
    assert len(result["steps"]) == 4
    assert len(result["scopes"]) == 3
    assert len({step["id"] for step in result["steps"]}) == 4
    assert {scope["id"] for scope in result["scopes"]} == {"ecosystem", "research", "mira"}
    for step in result["steps"]:
        assert all(isinstance(step[key], str) and step[key].strip() for key in ("id", "title", "text", "takeaway"))
    for scope in result["scopes"]:
        assert all(isinstance(scope[key], str) and scope[key].strip() for key in ("id", "title", "text", "tag"))
    assert result["view"]["step"] == result["steps"][0]
    assert result["view"]["scope"]["id"] == "ecosystem"
    assert result["view"]["canPrevious"] is False
    assert result["view"]["canNext"] is True
    assert result["view"]["isResearchStep"] is False


def test_next_and_previous_visit_every_step_without_changing_perspective():
    output = execute_node(
        "let state=transitionTour(createTourState(),{type:'scope',value:'research'});"
        "const forward=[state]; for(let i=0;i<3;i++){state=transitionTour(state,{type:'next'});forward.push(state);}"
        "const backward=[]; for(let i=0;i<3;i++){state=transitionTour(state,{type:'previous'});backward.push(state);}"
        "process.stdout.write(JSON.stringify({forward,backward}));"
    )
    result = json.loads(output.stdout)
    assert [state["step"] for state in result["forward"]] == [0, 1, 2, 3]
    assert [state["step"] for state in result["backward"]] == [2, 1, 0]
    assert all(state["scope"] == "research" for state in result["forward"] + result["backward"])


def test_navigation_saturates_at_limits_and_view_reports_available_directions():
    output = execute_node(
        "const initial=createTourState(); const start=transitionTour(initial,{type:'previous'});"
        "const last=transitionTour(initial,{type:'step',value:3}); const end=transitionTour(last,{type:'next'});"
        "process.stdout.write(JSON.stringify({initial,start,last,end,startView:getTourView(start),endView:getTourView(end)}));"
    )
    result = json.loads(output.stdout)
    assert result["start"] == result["initial"]
    assert result["end"] == result["last"] == {"step": 3, "scope": "ecosystem"}
    assert result["startView"]["canPrevious"] is False
    assert result["startView"]["canNext"] is True
    assert result["endView"]["canPrevious"] is True
    assert result["endView"]["canNext"] is False


def test_perspectives_are_independent_of_step_and_research_highlight():
    output = execute_node(
        "let state=transitionTour(createTourState(),{type:'step',value:2}); const views=[];"
        "for(const value of ['ecosystem','research','mira']) {state=transitionTour(state,{type:'scope',value});views.push({state,view:getTourView(state)});}"
        "const moved=transitionTour(state,{type:'step',value:1});"
        "process.stdout.write(JSON.stringify({views,moved,movedView:getTourView(moved)}));"
    )
    result = json.loads(output.stdout)
    assert [entry["state"]["scope"] for entry in result["views"]] == ["ecosystem", "research", "mira"]
    assert all(entry["state"]["step"] == 2 for entry in result["views"])
    assert all(entry["view"]["isResearchStep"] is True for entry in result["views"])
    assert all(entry["view"]["canNext"] and entry["view"]["canPrevious"] for entry in result["views"])
    assert result["moved"] == {"step": 1, "scope": "mira"}
    assert result["movedView"]["isResearchStep"] is False


def test_restart_restores_initial_step_and_perspective_without_changing_input():
    output = execute_node(
        "const state=Object.freeze({step:3,scope:'mira'}); const restart=transitionTour(state,{type:'restart'});"
        "process.stdout.write(JSON.stringify({state,restart,view:getTourView(restart)}));"
    )
    result = json.loads(output.stdout)
    assert result["state"] == {"step": 3, "scope": "mira"}
    assert result["restart"] == {"step": 0, "scope": "ecosystem"}
    assert result["view"]["scope"]["id"] == "ecosystem"


def test_all_transitions_and_views_leave_frozen_input_intact():
    output = execute_node(
        "const state=Object.freeze({step:1,scope:'research'});"
        "const actions=[{type:'next'},{type:'previous'},{type:'restart'},{type:'step',value:3},{type:'scope',value:'mira'}];"
        "const outputs=actions.map(action=>transitionTour(state,Object.freeze(action))); getTourView(state);"
        "const another=createTourState();another.step=3;"
        "process.stdout.write(JSON.stringify({state,outputs,fresh:createTourState()}));"
    )
    result = json.loads(output.stdout)
    assert result["state"] == {"step": 1, "scope": "research"}
    assert result["outputs"] == [
        {"step": 2, "scope": "research"},
        {"step": 0, "scope": "research"},
        {"step": 0, "scope": "ecosystem"},
        {"step": 3, "scope": "research"},
        {"step": 1, "scope": "mira"},
    ]
    assert result["fresh"] == {"step": 0, "scope": "ecosystem"}


def test_execution_is_conditional_and_scopes_explain_their_distinct_limits():
    output = execute_node("process.stdout.write(JSON.stringify({steps:ECOSYSTEM_STEPS,scopes:ECOSYSTEM_SCOPES}));")
    result = json.loads(output.stdout)
    execution = result["steps"][3]["text"].lower()
    assert "preparada" in execution and "disponível" in execution and "pode ser realizada" in execution
    research = next(scope for scope in result["scopes"] if scope["id"] == "research")["text"].lower()
    assert "provas" in research and "cenários simulados" in research
    mira = next(scope for scope in result["scopes"] if scope["id"] == "mira")["text"].lower()
    assert "conformidade interna" in mira and "apresentação" in mira


@pytest.mark.parametrize("state,error", [
    ("null", "TypeError"), ("[]", "TypeError"), ("{}", "TypeError"),
    ("{step:'0',scope:'ecosystem'}", "TypeError"),
    ("{step:0.5,scope:'ecosystem'}", "TypeError"),
    ("{step:NaN,scope:'ecosystem'}", "TypeError"),
    ("{step:-1,scope:'ecosystem'}", "RangeError"),
    ("{step:4,scope:'ecosystem'}", "RangeError"),
    ("{step:0,scope:null}", "TypeError"),
    ("{step:0,scope:'unknown'}", "RangeError"),
])
def test_invalid_states_are_rejected_by_both_apis(state, error):
    for call in (f"getTourView({state})", f"transitionTour({state},{{type:'restart'}})"):
        output = execute_node(f"{call};", check=False)
        assert output.returncode != 0
        assert error in output.stderr


@pytest.mark.parametrize("action,error", [
    ("null", "TypeError"), ("[]", "TypeError"), ("{}", "TypeError"),
    ("{type:7}", "TypeError"), ("{type:'unknown'}", "RangeError"),
    ("{type:'step'}", "TypeError"), ("{type:'step',value:'2'}", "TypeError"),
    ("{type:'step',value:1.5}", "TypeError"),
    ("{type:'step',value:-1}", "RangeError"), ("{type:'step',value:4}", "RangeError"),
    ("{type:'scope'}", "TypeError"), ("{type:'scope',value:2}", "TypeError"),
    ("{type:'scope',value:'unknown'}", "RangeError"),
])
def test_invalid_actions_are_rejected(action, error):
    output = execute_node(f"transitionTour(createTourState(),{action});", check=False)
    assert output.returncode != 0
    assert error in output.stderr
