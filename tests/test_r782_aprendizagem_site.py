"""Aceite funcional dos desafios e das perguntas didáticas, sem rede."""

import json
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "artigos" / "pucrs-roteamento-atencao" / "site"


def execute_node(body, *, check=True):
    node = shutil.which("node")
    assert node, "Node.js é necessário para conferir os módulos do navegador."
    script = (
        f"import {{ rankCandidates }} from {json.dumps((SITE / 'router.mjs').as_uri())};\n"
        f"import {{ MISSIONS, QUESTIONS, evaluateMission, gradeAnswer }} from {json.dumps((SITE / 'learning.mjs').as_uri())};\n"
        + body
    )
    return subprocess.run(
        [node, "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
        check=check,
    )


def candidate(identifier, **changes):
    row = {
        "id": identifier,
        "status": "available",
        "capabilities": ["pesquisa", "sintese"],
        "semantic": 0.8417 if identifier == "ana" else 0.7703,
        "trust": 0.9 if identifier == "ana" else 0.7,
        "load": 0.1 if identifier == "ana" else 0.4,
    }
    row.update(changes)
    return row


def mission(index, candidates):
    output = execute_node(
        f"const result = rankCandidates({json.dumps(candidates)}, ['pesquisa', 'sintese']);"
        f"process.stdout.write(JSON.stringify({{result, feedback: evaluateMission({index}, result)}}));"
    )
    return json.loads(output.stdout)


def test_content_has_three_complete_missions_and_questions():
    output = execute_node("process.stdout.write(JSON.stringify({MISSIONS, QUESTIONS}));")
    content = json.loads(output.stdout)
    assert len(content["MISSIONS"]) == len(content["QUESTIONS"]) == 3
    for key in ("MISSIONS", "QUESTIONS"):
        assert len({entry["id"] for entry in content[key]}) == 3
        for entry in content[key]:
            assert entry["prompt"].strip() and entry["explanation"].strip()
    for entry in content["MISSIONS"]:
        assert entry["title"].strip() and entry["hint"].strip()
    for entry in content["QUESTIONS"]:
        options = entry["options"]
        assert len(options) >= 2
        assert len({option["id"] for option in options}) == len(options)
        assert all(option["text"].strip() for option in options)
        assert entry["correctId"] in {option["id"] for option in options}


def test_first_mission_requires_cid_to_win_with_ana_still_eligible():
    original = mission(0, [candidate("ana"), candidate("cid")])
    assert original["result"]["ranked"][0]["id"] == "ana"
    assert original["feedback"]["complete"] is False
    changed = mission(0, [candidate("ana", trust=0.1), candidate("cid")])
    assert changed["result"]["ranked"][0]["id"] == "cid"
    assert {row["id"] for row in changed["result"]["ranked"]} == {"ana", "cid"}
    assert changed["feedback"]["complete"] is True
    assert "confian" in changed["feedback"]["message"].lower()
    assert "ana" in changed["feedback"]["message"].lower()


def test_excluding_ana_is_not_a_valid_shortcut_for_first_mission():
    feedback = mission(0, [candidate("ana", status="busy"), candidate("cid")])["feedback"]
    assert feedback["complete"] is False
    assert "ana" in feedback["message"].lower()
    assert mission(0, [candidate("cid")])["feedback"]["complete"] is False


def test_second_mission_requires_ana_excluded_and_cid_as_only_eligible():
    output = mission(1, [candidate("ana", status="busy"), candidate("cid")])
    assert output["feedback"]["complete"] is True
    assert output["result"]["ranked"][0]["weight"] == 1
    assert "100%" in output["feedback"]["message"]
    assert "sucesso" in output["feedback"]["message"].lower()


def test_second_mission_rejects_cid_winning_with_ana_or_a_third_eligible():
    assert mission(1, [candidate("ana", trust=0.1), candidate("cid")])["feedback"]["complete"] is False
    assert mission(1, [candidate("ana", status="busy"), candidate("cid"), candidate("bia")])["feedback"]["complete"] is False
    assert mission(1, [candidate("cid")])["feedback"]["complete"] is False
    assert mission(1, [candidate("ana"), candidate("cid", status="busy")])["feedback"]["complete"] is False


def test_third_mission_requires_an_actual_exclusion_and_no_eligible_candidate():
    assert mission(2, [])["feedback"]["complete"] is False
    output = mission(2, [candidate("ana", status="busy"), candidate("cid", status="busy")])
    assert output["feedback"]["complete"] is True
    assert "ninguém" in output["feedback"]["message"].lower()
    assert mission(2, [candidate("ana", status="busy"), candidate("cid")])["feedback"]["complete"] is False


@pytest.mark.parametrize("result", ["null", "{}", "{ranked:[],excluded:null}", "{ranked:null,excluded:[]}", "{ranked:[],excluded:[null]}", "{ranked:[],excluded:[{}]}", "{ranked:[{}],excluded:[]}"])
def test_malformed_routing_results_are_rejected(result):
    output = execute_node(f"evaluateMission(2, {result});", check=False)
    assert output.returncode != 0
    assert "TypeError" in output.stderr


@pytest.mark.parametrize("index,error", [("-1", "RangeError"), ("3", "RangeError"), ("0.5", "TypeError"), ("'0'", "TypeError"), ("null", "TypeError"), ("NaN", "TypeError")])
def test_invalid_indexes_are_rejected_by_both_apis(index, error):
    for call in (f"evaluateMission({index}, {{ranked:[],excluded:[]}})", f"gradeAnswer({index}, 'a')"):
        output = execute_node(f"{call};", check=False)
        assert output.returncode != 0
        assert error in output.stderr


@pytest.mark.parametrize("index", [0, 1, 2])
def test_question_feedback_explains_every_correct_and_incorrect_option(index):
    output = execute_node(
        f"const question = QUESTIONS[{index}];"
        "process.stdout.write(JSON.stringify(question.options.map(option => ({"
        f"id:option.id, expected:option.id===question.correctId, feedback:gradeAnswer({index},option.id)"
        "}))));"
    )
    responses = json.loads(output.stdout)
    assert sum(row["feedback"]["correct"] for row in responses) == 1
    for row in responses:
        assert row["feedback"]["correct"] is row["expected"]
        assert row["feedback"]["message"].strip()
        message = row["feedback"]["message"].lower()
        if index == 0:
            assert "indisponível" in message and "compar" in message
            assert "carga alta" in message and "nota" in message
        elif index == 1:
            assert "53%" in message and ("chance" in message or "probabilidade" in message)
        else:
            assert "matemát" in message and "execução" in message


def test_high_load_reduces_score_without_excluding_an_available_candidate():
    output = execute_node(
        "const low = rankCandidates(["
        + json.dumps(candidate("ana", load=0.1))
        + "], ['pesquisa', 'sintese']);"
        "const high = rankCandidates(["
        + json.dumps(candidate("ana", load=1))
        + "], ['pesquisa', 'sintese']);"
        "process.stdout.write(JSON.stringify({low, high, question: QUESTIONS[0]}));"
    )
    result = json.loads(output.stdout)
    assert result["high"]["excluded"] == []
    assert result["high"]["ranked"][0]["id"] == "ana"
    assert result["high"]["ranked"][0]["utility"] < result["low"]["ranked"][0]["utility"]
    assert "está indisponível para novas tarefas" in result["question"]["prompt"]


@pytest.mark.parametrize("answer,error", [("null", "TypeError"), ("1", "TypeError"), ("{}", "TypeError"), ("''", "RangeError"), ("'unknown'", "RangeError")])
def test_invalid_answers_are_rejected(answer, error):
    output = execute_node(f"gradeAnswer(0, {answer});", check=False)
    assert output.returncode != 0
    assert error in output.stderr


def test_learning_does_not_mutate_the_calculation_or_question_content():
    output = execute_node(
        "const result=rankCandidates(["
        + json.dumps(candidate("ana", trust=0.1))
        + ","
        + json.dumps(candidate("cid"))
        + "],['pesquisa','sintese']);"
        "const before=JSON.stringify({result,MISSIONS,QUESTIONS});"
        "evaluateMission(0,result); gradeAnswer(0,QUESTIONS[0].correctId);"
        "process.stdout.write(JSON.stringify(before===JSON.stringify({result,MISSIONS,QUESTIONS})));"
    )
    assert json.loads(output.stdout) is True
