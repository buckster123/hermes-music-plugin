"""
Music Task Manager for Hermes Music Plugin

Manages the lifecycle of music generation tasks:
create → submit → poll → download → complete/fail

Persists task state to JSON for durability across sessions.
"""

import json
import logging
import random
import re
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import suno

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class MusicTask:
    """Represents a music generation task."""
    task_id: str
    prompt: str
    style: str = ""
    title: str = ""
    model: str = "V5"
    is_instrumental: bool = True
    status: TaskStatus = TaskStatus.PENDING
    progress: str = "Queued"
    suno_task_id: Optional[str] = None
    audio_url: Optional[str] = None
    audio_file: Optional[str] = None
    duration: float = 0.0
    clip_id: Optional[str] = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    # Curation fields
    agent_id: Optional[str] = None
    favorite: bool = False
    play_count: int = 0
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "prompt": self.prompt,
            "style": self.style,
            "title": self.title,
            "model": self.model,
            "is_instrumental": self.is_instrumental,
            "status": self.status.value,
            "progress": self.progress,
            "suno_task_id": self.suno_task_id,
            "audio_url": self.audio_url,
            "audio_file": self.audio_file,
            "duration": self.duration,
            "clip_id": self.clip_id,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "agent_id": self.agent_id,
            "favorite": self.favorite,
            "play_count": self.play_count,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MusicTask":
        try:
            status = TaskStatus(data.get("status", "pending"))
        except ValueError:
            status = TaskStatus.PENDING

        return cls(
            task_id=data["task_id"],
            prompt=data.get("prompt", ""),
            style=data.get("style", ""),
            title=data.get("title", ""),
            model=data.get("model", "V5"),
            is_instrumental=data.get("is_instrumental", True),
            status=status,
            progress=data.get("progress", "Queued"),
            suno_task_id=data.get("suno_task_id"),
            audio_url=data.get("audio_url"),
            audio_file=data.get("audio_file"),
            duration=data.get("duration", 0.0),
            clip_id=data.get("clip_id"),
            error=data.get("error"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            agent_id=data.get("agent_id"),
            favorite=data.get("favorite", False),
            play_count=data.get("play_count", 0),
            tags=data.get("tags", []),
        )


class MusicTaskManager:
    """Manages music generation tasks with JSON persistence."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.music_dir = data_dir / "audio"
        self.midi_dir = data_dir / "midi"
        self.tasks_file = data_dir / "tasks.json"
        self.tasks: Dict[str, MusicTask] = {}
        self._lock = threading.Lock()

        # Ensure directories exist
        self.music_dir.mkdir(parents=True, exist_ok=True)
        self.midi_dir.mkdir(parents=True, exist_ok=True)

        self._load_tasks()

    def _load_tasks(self):
        """Load tasks from JSON file."""
        try:
            if self.tasks_file.exists():
                with open(self.tasks_file, "r") as f:
                    data = json.load(f)
                for task_id, task_data in data.items():
                    self.tasks[task_id] = MusicTask.from_dict(task_data)
                logger.info("Loaded %d music tasks", len(self.tasks))
        except Exception as e:
            logger.error("Error loading music tasks: %s", e)

    def _save_tasks(self):
        """Save tasks to JSON file."""
        try:
            self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
            data = {tid: t.to_dict() for tid, t in self.tasks.items()}
            with open(self.tasks_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error("Error saving music tasks: %s", e)

    def create_task(
        self,
        prompt: str,
        style: str = "",
        title: str = "",
        model: str = "V5",
        is_instrumental: bool = True,
        agent_id: Optional[str] = None,
    ) -> MusicTask:
        """Create a new music task."""
        task_id = f"music_{int(datetime.now().timestamp() * 1000)}_{random.randint(100, 999)}"
        task = MusicTask(
            task_id=task_id,
            prompt=prompt,
            style=style,
            title=title,
            model=model,
            is_instrumental=is_instrumental,
            agent_id=agent_id,
        )
        with self._lock:
            self.tasks[task_id] = task
            self._save_tasks()
        logger.info("Created music task %s: %s...", task_id, prompt[:50])
        return task

    def get_task(self, task_id: str) -> Optional[MusicTask]:
        return self.tasks.get(task_id)

    def list_tasks(self, limit: int = 10) -> List[MusicTask]:
        sorted_tasks = sorted(
            self.tasks.values(),
            key=lambda t: t.created_at,
            reverse=True,
        )
        return sorted_tasks[:limit]

    def run_task(self, task_id: str) -> Dict[str, Any]:
        """Run a music generation task (blocking). Downloads all tracks."""
        task = self.get_task(task_id)
        if not task:
            return {"error": f"Task {task_id} not found"}

        task.status = TaskStatus.GENERATING
        task.started_at = datetime.now().isoformat()
        task.progress = "Starting generation..."
        self._save_tasks()

        try:
            # Submit to Suno (skip if already submitted, e.g. music_compose)
            if task.suno_task_id:
                suno_task_id = task.suno_task_id
            else:
                task.progress = "Submitting to Suno API..."
                self._save_tasks()
                suno_task_id = suno.submit_generation(
                    prompt=task.prompt,
                    style=task.style,
                    title=task.title,
                    model=task.model,
                    is_instrumental=task.is_instrumental,
                )
                task.suno_task_id = suno_task_id

            task.progress = "Queued at Suno..."
            self._save_tasks()

            # Poll for completion
            result = suno.poll_completion(suno_task_id)

            if not result.get("success"):
                raise Exception(result.get("error", "Unknown error"))

            tracks = result.get("tracks", [])
            track_count = len(tracks)
            task.progress = f"Downloading {track_count} track(s)..."
            self._save_tasks()

            # Download all tracks
            downloaded_files = []
            all_tracks_info = []

            for i, track_info in enumerate(tracks):
                try:
                    safe_title = re.sub(r"[^\w\-]", "_", track_info.get("title", f"track_{i+1}"))
                    filename = f"{safe_title}_{task_id[-8:]}_{i+1}.mp3"
                    output_path = str(self.music_dir / filename)

                    audio_file = suno.download_audio(track_info["audio_url"], output_path)
                    downloaded_files.append(audio_file)
                    all_tracks_info.append({
                        "file": audio_file,
                        "title": track_info.get("title"),
                        "duration": track_info.get("duration", 0),
                        "clip_id": track_info.get("clip_id"),
                        "audio_url": track_info.get("audio_url"),
                    })
                except Exception as e:
                    logger.error("Failed to download track %d: %s", i + 1, e)

            if not downloaded_files:
                raise Exception("Failed to download any tracks")

            # Store first track as primary
            first = all_tracks_info[0]
            task.audio_file = first["file"]
            task.audio_url = first.get("audio_url")
            task.duration = first.get("duration", 0.0)
            task.clip_id = first.get("clip_id")
            task.title = first.get("title", task.title) or f"Track_{task_id[-8:]}"
            task.status = TaskStatus.COMPLETED
            task.progress = f"Complete ({track_count} tracks)"
            task.completed_at = datetime.now().isoformat()
            self._save_tasks()

            logger.info("Music task %s completed: %d tracks", task_id, track_count)
            return {
                "success": True,
                "audio_file": first["file"],
                "audio_files": downloaded_files,
                "tracks": all_tracks_info,
                "track_count": track_count,
            }

        except Exception as e:
            logger.error("Music task %s failed: %s", task_id, e)
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.progress = f"Failed: {str(e)[:100]}"
            task.completed_at = datetime.now().isoformat()
            self._save_tasks()
            return {"success": False, "error": str(e)}
