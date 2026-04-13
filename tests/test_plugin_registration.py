"""Tests for the plugin registration entry point."""

import json
import pytest
from unittest.mock import MagicMock, patch

import hermes_music


class TestRegister:
    def test_register_all_tools(self):
        """register() should register all 10 tools."""
        ctx = MagicMock()
        hermes_music.register(ctx)
        assert ctx.register_tool.call_count == 12

    def test_register_tool_names(self):
        """All expected tool names are registered."""
        ctx = MagicMock()
        hermes_music.register(ctx)

        registered_names = {call.kwargs["name"] for call in ctx.register_tool.call_args_list}
        expected = {
            "music_generate", "music_status", "music_result", "music_list",
            "music_favorite", "music_library", "music_search", "music_play",
            "music_stop", "music_delete", "midi_create", "music_compose",
        }
        assert registered_names == expected

    def test_register_toolset(self):
        """All tools are in the 'music' toolset."""
        ctx = MagicMock()
        hermes_music.register(ctx)

        for call in ctx.register_tool.call_args_list:
            assert call.kwargs["toolset"] == "music"

    def test_midi_create_no_suno_key(self):
        """midi_create uses a different check_fn (no SUNO_API_KEY needed)."""
        ctx = MagicMock()
        hermes_music.register(ctx)

        for call in ctx.register_tool.call_args_list:
            if call.kwargs["name"] == "midi_create":
                assert call.kwargs["requires_env"] == []
                break

    def test_suno_tools_require_api_key(self):
        """All Suno-dependent tools require SUNO_API_KEY."""
        ctx = MagicMock()
        hermes_music.register(ctx)

        for call in ctx.register_tool.call_args_list:
            if call.kwargs["name"] not in ("midi_create", "music_stop"):
                assert "SUNO_API_KEY" in call.kwargs["requires_env"]

    def test_schemas_have_required_fields(self):
        """All tool schemas have name, description, and parameters."""
        for name, schema in hermes_music.TOOL_SCHEMAS.items():
            assert "name" in schema, f"{name} missing 'name'"
            assert "description" in schema, f"{name} missing 'description'"
            assert "parameters" in schema, f"{name} missing 'parameters'"
            assert schema["parameters"]["type"] == "object"


class TestCheckFunctions:
    def test_check_suno_available_with_key(self, monkeypatch):
        monkeypatch.setenv("SUNO_API_KEY", "test_key")
        assert hermes_music._check_suno_available() is True

    def test_check_suno_available_without_key(self, monkeypatch):
        monkeypatch.delenv("SUNO_API_KEY", raising=False)
        assert hermes_music._check_suno_available() is False


class TestToolHandlers:
    """Test that handlers return valid JSON strings."""

    def test_music_list_empty(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hermes_music, "_manager", None)
        monkeypatch.setattr(hermes_music, "_get_data_dir", lambda: tmp_path / "music")
        result = json.loads(hermes_music._handle_music_list({}, task_id="test"))
        assert "tasks" in result
        assert result["count"] == 0

    def test_music_status_not_found(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hermes_music, "_manager", None)
        monkeypatch.setattr(hermes_music, "_get_data_dir", lambda: tmp_path / "music")
        result = json.loads(hermes_music._handle_music_status({"task_id": "nope"}, task_id="test"))
        assert "error" in result

    def test_music_result_not_found(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hermes_music, "_manager", None)
        monkeypatch.setattr(hermes_music, "_get_data_dir", lambda: tmp_path / "music")
        result = json.loads(hermes_music._handle_music_result({"task_id": "nope"}, task_id="test"))
        assert "error" in result

    def test_music_search_empty(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hermes_music, "_manager", None)
        monkeypatch.setattr(hermes_music, "_get_data_dir", lambda: tmp_path / "music")
        result = json.loads(hermes_music._handle_music_search({"query": "anything"}, task_id="test"))
        assert result["count"] == 0
