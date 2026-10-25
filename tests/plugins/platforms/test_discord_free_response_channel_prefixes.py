"""Regression coverage for Discord free-response channel-name prefixes."""

from gateway.config import Platform, PlatformConfig


def _adapter(extra):
    from plugins.platforms.discord.adapter import DiscordAdapter

    adapter = object.__new__(DiscordAdapter)
    adapter.platform = Platform.DISCORD
    adapter.config = PlatformConfig(enabled=True, token="x", extra=dict(extra))
    adapter._gate_env_snapshot = None
    return adapter


def test_free_response_channel_prefix_matches_bare_and_hash_names():
    adapter = _adapter({"free_response_channel_prefixes": ["hermes-"]})

    assert adapter._discord_channel_is_free_response({"123", "hermes-ops", "#hermes-ops"})
    assert not adapter._discord_channel_is_free_response({"456", "general", "#general"})


def test_free_response_exact_channel_and_wildcard_still_work():
    exact = _adapter({"free_response_channels": ["123"]})
    wildcard = _adapter({"free_response_channels": ["*"]})

    assert exact._discord_channel_is_free_response({"123", "general", "#general"})
    assert wildcard._discord_channel_is_free_response({"456", "general", "#general"})
