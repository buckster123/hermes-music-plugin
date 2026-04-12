"""Tests for the MusicTaskManager."""

import json
import pytest
from pathlib import Path

from hermes_music.tasks import MusicTaskManager, MusicTask, TaskStatus


@pytest.fixture
def manager(tmp_path):
    """Create a fresh MusicTaskManager with temp storage."""
    return MusicTaskManager(tmp_path / "music")


class TestTaskCreation:
    def test_create_task(self, manager):
        task = manager.create_task(prompt="ambient vibes", style="electronic")
        assert task.task_id.startswith("music_")
        assert task.prompt == "ambient vibes"
        assert task.style == "electronic"
        assert task.status == TaskStatus.PENDING
        assert task.is_instrumental is True

    def test_create_task_with_agent_id(self, manager):
        task = manager.create_task(prompt="test", agent_id="CLAUDE-OPUS")
        assert task.agent_id == "CLAUDE-OPUS"

    def test_create_task_persists(self, manager, tmp_path):
        task = manager.create_task(prompt="persist test")
        # Reload from disk
        manager2 = MusicTaskManager(tmp_path / "music")
        loaded = manager2.get_task(task.task_id)
        assert loaded is not None
        assert loaded.prompt == "persist test"

    def test_create_task_with_all_fields(self, manager):
        task = manager.create_task(
            prompt="epic orchestral battle",
            style="cinematic orchestral",
            title="Battle Theme",
            model="V4_5",
            is_instrumental=False,
            agent_id="CLAUDE-HAILO",
        )
        assert task.title == "Battle Theme"
        assert task.model == "V4_5"
        assert task.is_instrumental is False


class TestTaskSerialization:
    def test_to_dict_roundtrip(self):
        task = MusicTask(
            task_id="music_123",
            prompt="test prompt",
            style="jazz",
            title="Test Song",
            favorite=True,
            play_count=5,
            tags=["chill", "study"],
        )
        d = task.to_dict()
        restored = MusicTask.from_dict(d)
        assert restored.task_id == "music_123"
        assert restored.prompt == "test prompt"
        assert restored.favorite is True
        assert restored.play_count == 5
        assert restored.tags == ["chill", "study"]

    def test_from_dict_handles_invalid_status(self):
        task = MusicTask.from_dict({
            "task_id": "music_456",
            "status": "invalid_status",
        })
        assert task.status == TaskStatus.PENDING

    def test_from_dict_defaults(self):
        task = MusicTask.from_dict({"task_id": "music_789"})
        assert task.model == "V5"
        assert task.is_instrumental is True
        assert task.favorite is False
        assert task.play_count == 0


class TestTaskListing:
    def test_list_tasks_empty(self, manager):
        assert manager.list_tasks() == []

    def test_list_tasks_ordered(self, manager):
        t1 = manager.create_task(prompt="first")
        import time; time.sleep(0.01)
        t2 = manager.create_task(prompt="second")
        tasks = manager.list_tasks(limit=10)
        assert tasks[0].task_id == t2.task_id  # Most recent first
        assert tasks[1].task_id == t1.task_id

    def test_list_tasks_limit(self, manager):
        for i in range(5):
            manager.create_task(prompt=f"task {i}")
        assert len(manager.list_tasks(limit=3)) == 3


class TestDirectories:
    def test_directories_created(self, tmp_path):
        manager = MusicTaskManager(tmp_path / "new_music")
        assert (tmp_path / "new_music" / "audio").is_dir()
        assert (tmp_path / "new_music" / "midi").is_dir()
