"""Launchd start must not report success when the registered job never spawns."""

from types import SimpleNamespace

import hermes_cli.gateway as gateway_cli
from hermes_cli.gateway_launchd import _launchd_confirm_started_or_fallback


def test_launchd_start_verification_falls_back_when_spawn_never_produces_pid(monkeypatch):
    bootouts = []
    fallbacks = []

    monkeypatch.setattr(gateway_cli, "_launchd_domain", lambda: "gui/501")
    monkeypatch.setattr(
        gateway_cli,
        "_wait_for_launchd_service_pid",
        lambda label, old_pid, timeout, domain: False,
    )
    monkeypatch.setattr(
        gateway_cli,
        "_launchd_fallback_to_detached",
        lambda reason: fallbacks.append(reason) or True,
    )
    monkeypatch.setattr(
        "hermes_cli.gateway_launchd.subprocess.run",
        lambda command, **kwargs: bootouts.append(command) or SimpleNamespace(returncode=0),
    )

    assert _launchd_confirm_started_or_fallback("ai.hermes.gateway", timeout=0.1) is False
    assert bootouts == [["launchctl", "bootout", "gui/501/ai.hermes.gateway"]]
    assert fallbacks == ["launchd registered the job but could not spawn it"]


def test_launchd_start_verification_keeps_supervised_process(monkeypatch):
    monkeypatch.setattr(gateway_cli, "_launchd_domain", lambda: "gui/501")
    monkeypatch.setattr(
        gateway_cli,
        "_wait_for_launchd_service_pid",
        lambda label, old_pid, timeout, domain: True,
    )
    monkeypatch.setattr(
        gateway_cli,
        "_launchd_fallback_to_detached",
        lambda reason: (_ for _ in ()).throw(AssertionError(reason)),
    )

    assert _launchd_confirm_started_or_fallback("ai.hermes.gateway", timeout=0.1) is True
