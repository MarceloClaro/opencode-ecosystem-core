"""R1266: page tabs AT-SPI selecionáveis, sob a aprovação local existente."""
from __future__ import annotations

import json
from types import SimpleNamespace

from integrations.desktop_operator import approvals, atspi_backend, policy, runtime


APP = "Burp Suite Community Edition v2026.11.2 - Temporary Project"


class _FakeSelection:
    def __init__(self):
        self.selected = []

    def select_child(self, index):
        self.selected.append(index)
        return True


class _FakeNode:
    def __init__(self, role, name="", children=(), *, selection=None):
        self.role = role
        self.name = name
        self.children = list(children)
        self.selection = selection

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
        return None

    def get_selection_iface(self):
        return self.selection

    def is_text(self):
        return False

    def is_value(self):
        return False

    def is_editable_text(self):
        return False

    def get_editable_text_iface(self):
        return None


def _atspi_stub():
    return SimpleNamespace(StateType=SimpleNamespace(ENABLED=1, VISIBLE=2, FOCUSED=3))


def _app_tree(*, with_selection=True):
    selection = _FakeSelection() if with_selection else None
    first = _FakeNode("page tab", "Installed")
    bapp = _FakeNode("page tab", "BApp Store")
    tab_list = _FakeNode("page tab list", "Extensions", (first, bapp), selection=selection)
    app = _FakeNode("application", APP, (tab_list,))
    return app, selection


def _snapshot(monkeypatch, tmp_path, app_tree):
    root, selection = app_tree
    monkeypatch.setattr(atspi_backend, "_atspi", _atspi_stub)
    monkeypatch.setattr(atspi_backend, "_find_app", lambda _atspi, _app, pid=None: root)
    config = policy.PolicyConfig(allowed_apps=(APP,), backend="atspi", state_dir=str(tmp_path))
    result = atspi_backend.snapshot(config, APP, max_depth=12)
    return config, result, selection


def _find_named(node, role, name):
    if node.get("role") == role and node.get("name") == name:
        return node
    for child in node.get("children", []):
        found = _find_named(child, role, name)
        if found:
            return found
    return None


def test_snapshot_qualifies_page_tab_with_parent_selection(tmp_path, monkeypatch):
    _, result, selection = _snapshot(monkeypatch, tmp_path, _app_tree())

    assert result["ok"] is True
    tab = _find_named(result["data"]["tree"], "page tab", "BApp Store")
    assert tab is not None
    assert tab.get("ref_id") == f"@{result['data']['snapshot_id']}:e2"
    stored = json.loads(
        (tmp_path / "atspi-refs" / f"{result['data']['snapshot_id']}.json").read_text()
    )
    assert stored["refs"][tab["ref_id"]]["selectable"] is True
    assert stored["refs"][tab["ref_id"]]["path"] == [0, 1]
    assert selection.selected == []


def test_page_tab_without_selection_iface_is_not_clickable(tmp_path, monkeypatch):
    _, result, _ = _snapshot(monkeypatch, tmp_path, _app_tree(with_selection=False))

    assert result["ok"] is True
    tab = _find_named(result["data"]["tree"], "page tab", "BApp Store")
    assert tab is not None
    assert "ref_id" not in tab


def test_click_selects_tab_only_after_one_time_approval(tmp_path, monkeypatch):
    app_tree = _app_tree()
    config, result, selection = _snapshot(monkeypatch, tmp_path, app_tree)
    tab = _find_named(result["data"]["tree"], "page tab", "BApp Store")
    assert tab is not None
    ref = tab.get("ref_id")
    assert ref is not None

    denied = runtime.run("click", config, app=APP, ref=ref)
    assert denied["ok"] is False
    assert denied["error"]["code"] == "approval_required"
    assert selection.selected == []

    issued = approvals.issue_approval(config, "click", APP, ref, ttl_seconds=60)
    clicked = runtime.run("click", config, app=APP, ref=ref,
                          approval_token=issued["token"])

    assert clicked["ok"] is True
    assert clicked["policy"]["approval_used"] is True
    assert clicked["data"]["disposition"] == {
        "delivery": "delivered_unverified",
        "retry": "unsafe",
    }
    assert selection.selected == [1]
