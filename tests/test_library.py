"""Tests for the music library functions."""

import pytest
from pathlib import Path

from hermes_music.tasks import MusicTaskManager, TaskStatus
from hermes_music.library import browse_library, search_songs, toggle_favorite, play_song


@pytest.fixture
def manager(tmp_path):
    mgr = MusicTaskManager(tmp_path / "music")
    # Create some test tasks
    t1 = mgr.create_task(prompt="ambient electronic vibes", style="ambient electronic", title="Chill Waves", agent_id="CLAUDE-OPUS")
    t1.status = TaskStatus.COMPLETED
    t1.duration = 120.0
    t1.audio_file = "/tmp/chill_waves.mp3"

    t2 = mgr.create_task(prompt="epic orchestral battle", style="cinematic", title="Battle Theme", agent_id="CLAUDE-HAILO")
    t2.status = TaskStatus.COMPLETED
    t2.duration = 180.0
    t2.audio_file = "/tmp/battle_theme.mp3"
    t2.favorite = True

    t3 = mgr.create_task(prompt="jazz improv", style="jazz piano", title="Night Jazz")
    t3.status = TaskStatus.FAILED
    t3.error = "API timeout"

    mgr._save_tasks()
    return mgr


class TestBrowseLibrary:
    def test_browse_all(self, manager):
        result = browse_library(manager)
        assert result["count"] == 3
        assert result["total_in_library"] == 3

    def test_browse_by_agent(self, manager):
        result = browse_library(manager, agent_id="CLAUDE-OPUS")
        assert result["count"] == 1
        assert result["songs"][0]["title"] == "Chill Waves"

    def test_browse_favorites_only(self, manager):
        result = browse_library(manager, favorites_only=True)
        assert result["count"] == 1
        assert result["songs"][0]["title"] == "Battle Theme"

    def test_browse_by_status(self, manager):
        result = browse_library(manager, status="failed")
        assert result["count"] == 1
        assert result["songs"][0]["title"] == "Night Jazz"

    def test_browse_limit(self, manager):
        result = browse_library(manager, limit=2)
        assert result["count"] == 2


class TestSearchSongs:
    def test_search_by_title(self, manager):
        result = search_songs(manager, "battle")
        assert result["count"] == 1
        assert result["results"][0]["title"] == "Battle Theme"

    def test_search_by_style(self, manager):
        result = search_songs(manager, "jazz")
        assert result["count"] == 1

    def test_search_by_prompt(self, manager):
        result = search_songs(manager, "ambient")
        assert result["count"] == 1

    def test_search_no_results(self, manager):
        result = search_songs(manager, "reggaeton")
        assert result["count"] == 0

    def test_search_case_insensitive(self, manager):
        result = search_songs(manager, "BATTLE")
        assert result["count"] == 1


class TestToggleFavorite:
    def test_toggle_on(self, manager):
        tasks = manager.list_tasks()
        non_fav = [t for t in tasks if not t.favorite][0]
        result = toggle_favorite(manager, non_fav.task_id)
        assert result["success"] is True
        assert result["favorite"] is True

    def test_toggle_off(self, manager):
        tasks = manager.list_tasks()
        fav = [t for t in tasks if t.favorite][0]
        result = toggle_favorite(manager, fav.task_id)
        assert result["success"] is True
        assert result["favorite"] is False

    def test_set_explicit(self, manager):
        tasks = manager.list_tasks()
        result = toggle_favorite(manager, tasks[0].task_id, favorite=True)
        assert result["favorite"] is True

    def test_not_found(self, manager):
        result = toggle_favorite(manager, "nonexistent")
        assert result["success"] is False


class TestPlaySong:
    def test_play_completed(self, manager):
        tasks = manager.list_tasks()
        completed = [t for t in tasks if t.status == TaskStatus.COMPLETED][0]
        result = play_song(manager, completed.task_id)
        assert result["success"] is True
        assert result["play_count"] == 1

        # Play again
        result2 = play_song(manager, completed.task_id)
        assert result2["play_count"] == 2

    def test_play_failed_song(self, manager):
        tasks = manager.list_tasks()
        failed = [t for t in tasks if t.status == TaskStatus.FAILED][0]
        result = play_song(manager, failed.task_id)
        assert result["success"] is False

    def test_play_not_found(self, manager):
        result = play_song(manager, "nonexistent")
        assert result["success"] is False
