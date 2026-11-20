"""R1261: nomes de aplicações AT-SPI com espaços, sem relaxar a allowlist."""
from __future__ import annotations

import pytest

from integrations.desktop_operator import policy


def test_allowlisted_app_name_with_spaces_is_preserved_as_one_argv_value():
    config = policy.PolicyConfig(allowed_apps=("Burp Suite",))

    assert policy.require_app(config, "Burp Suite") == "Burp Suite"
    argv = policy.build_argv("snapshot", config, app="Burp Suite")

    assert argv[:3] == ["snapshot", "--app", "Burp Suite"]
    assert argv.count("Burp Suite") == 1


def test_app_name_still_requires_exact_allowlist_match():
    config = policy.PolicyConfig(allowed_apps=("Burp Suite",))

    assert policy.require_app(config, "burp suite") == "burp suite"
    with pytest.raises(policy.PolicyDenied) as error:
        policy.require_app(config, "Other Suite")

    assert error.value.code == "app_not_allowed"


@pytest.mark.parametrize(
    "app",
    [
        " Burp Suite",
        "Burp Suite ",
        "Burp\tSuite",
        "Burp\nSuite",
        "Burp\x00Suite",
        "Burp Suite;id",
        "A" * 121,
    ],
)
def test_app_name_rejects_boundary_whitespace_controls_and_shell_syntax(app):
    config = policy.PolicyConfig(allowed_apps=(app,))

    with pytest.raises(policy.PolicyDenied) as error:
        policy.require_app(config, app)

    assert error.value.code == "app_invalid"
