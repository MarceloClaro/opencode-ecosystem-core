"""R1265: alcance limitado de snapshots AT-SPI, sem autorizar ações."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from integrations.desktop_operator import atspi_backend, policy


class _FakeAction:
    def get_n_actions(self):
        return 1


class _FakeNode:
    def __init__(self, role, name="", children=(), actionable=False):
        self.role = role
        self.name = name
        self.children = list(children)
        self.actionable = actionable

    def get_role_name(self):
        return self.role

    def get_name(self):
        return self.name

    def get_process_id(self):
        return 6737

    def get_child_count(self):
        return len(self.children)

    def get_child_at_index(self, index):
        return self.children[index]

    def get_state_set(self):
        return None

    def get_action_iface(self):
        return _FakeAction() if self.actionable else None

    def is_text(self):
        return False

    def is_value(self):
        return False

    def is_editable_text(self):
        return False

    def get_editable_text_iface(self):
        return None


def _tree_with_button_at_depth_12():
    node = _FakeNode("push button", "Continue with Burp Suite Community Edition", actionable=True)
    for _ in range(11):
        node = _FakeNode("panel", children=(node,))
    return _FakeNode("application", "Burp Suite", children=(node,))


def test_policy_accepts_depth_12_and_rejects_depth_13():
    config = policy.PolicyConfig(allowed_apps=("Burp Suite",))

    try:
        argv = policy.build_argv("snapshot", config, app="Burp Suite", max_depth=12)
    except policy.PolicyDenied:
        argv = None
    assert argv is not None, "profundidade 12 deve ser aceita"
    assert argv[argv.index("--max-depth") + 1] == "12"

    with pytest.raises(policy.PolicyDenied) as error:
        policy.build_argv("snapshot", config, app="Burp Suite", max_depth=13)
    assert error.value.code == "max_depth_invalid"


def test_atspi_snapshot_returns_qualified_ref_at_depth_12(tmp_path, monkeypatch):
    fake_atspi = SimpleNamespace(
        StateType=SimpleNamespace(ENABLED=1, VISIBLE=2, FOCUSED=3)
    )
    root = _tree_with_button_at_depth_12()
    monkeypatch.setattr(atspi_backend, "_atspi", lambda: fake_atspi)
    monkeypatch.setattr(atspi_backend, "_find_app", lambda _atspi, _app: root)
    config = SimpleNamespace(state_dir=str(tmp_path))

    result = atspi_backend.snapshot(config, "Burp Suite", max_depth=12)

    assert result["ok"] is True
    assert result["data"]["ref_count"] == 1
    assert result["data"]["truncated"] is False
    node = result["data"]["tree"]
    while node.get("children"):
        node = node["children"][0]
    assert node["name"] == "Continue with Burp Suite Community Edition"
    assert node["ref_id"] == f"@{result['data']['snapshot_id']}:e1"


def test_deep_snapshot_only_reads_tree_and_does_not_activate_action(tmp_path, monkeypatch):
    actions = []

    class TrackingAction(_FakeAction):
        def do_action(self, index):
            actions.append(index)
            return True

    class TrackingNode(_FakeNode):
        def get_action_iface(self):
            return TrackingAction() if self.actionable else None

    button = TrackingNode("push button", "Continue with Burp Suite Community Edition", actionable=True)
    for _ in range(11):
        button = TrackingNode("panel", children=(button,))
    root = TrackingNode("application", "Burp Suite", children=(button,))
    fake_atspi = SimpleNamespace(
        StateType=SimpleNamespace(ENABLED=1, VISIBLE=2, FOCUSED=3)
    )
    monkeypatch.setattr(atspi_backend, "_atspi", lambda: fake_atspi)
    monkeypatch.setattr(atspi_backend, "_find_app", lambda _atspi, _app: root)
    config = SimpleNamespace(state_dir=str(tmp_path))

    result = atspi_backend.snapshot(config, "Burp Suite", max_depth=12)

    assert result["ok"] is True
    assert result["data"]["ref_count"] == 1
    assert actions == []
