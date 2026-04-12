"""
Music Library for Hermes Music Plugin

Browse, search, favorite, and play songs from the music library.
"""

import logging
from typing import Any, Dict, List, Optional

from .tasks import MusicTaskManager, TaskStatus

logger = logging.getLogger(__name__)


def browse_library(
    manager: MusicTaskManager,
    agent_id: Optional[str] = None,
    favorites_only: bool = False,
    status: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """Browse the music library with optional filters."""
    try:
        sorted_tasks = sorted(
            manager.tasks.values(),
            key=lambda t: t.created_at,
            reverse=True,
        )

        filtered = []
        for task in sorted_tasks:
            if agent_id and task.agent_id != agent_id:
                continue
            if favorites_only and not task.favorite:
                continue
            if status and task.status.value != status:
                continue
            filtered.append(task)
            if len(filtered) >= limit:
                break

        total_duration = sum(t.duration for t in filtered if t.duration)
        completed_count = sum(1 for t in filtered if t.status == TaskStatus.COMPLETED)

        songs = []
        for t in filtered:
            songs.append({
                "task_id": t.task_id,
                "title": t.title or "Untitled",
                "agent_id": t.agent_id,
                "status": t.status.value,
                "favorite": t.favorite,
                "play_count": t.play_count,
                "duration": t.duration,
                "audio_file": t.audio_file,
                "is_instrumental": t.is_instrumental,
                "created_at": t.created_at,
            })

        return {
            "songs": songs,
            "count": len(songs),
            "completed_count": completed_count,
            "total_duration": total_duration,
            "total_in_library": len(manager.tasks),
        }

    except Exception as e:
        logger.error("Error browsing library: %s", e)
        return {"error": str(e)}


def search_songs(
    manager: MusicTaskManager,
    query: str,
    limit: int = 10,
) -> Dict[str, Any]:
    """Search songs by title, prompt, or style."""
    try:
        query_lower = query.lower()
        matches = []

        for task in manager.tasks.values():
            searchable = f"{task.title} {task.prompt} {task.style}".lower()
            if query_lower in searchable:
                matches.append((task, searchable.count(query_lower)))

        matches.sort(key=lambda x: (-x[1], x[0].created_at), reverse=True)

        results = []
        for task, _score in matches[:limit]:
            results.append({
                "task_id": task.task_id,
                "title": task.title or "Untitled",
                "agent_id": task.agent_id,
                "status": task.status.value,
                "favorite": task.favorite,
                "duration": task.duration,
                "audio_file": task.audio_file,
                "prompt_preview": task.prompt[:100] + ("..." if len(task.prompt) > 100 else ""),
                "created_at": task.created_at,
            })

        return {
            "results": results,
            "count": len(results),
            "query": query,
            "total_searched": len(manager.tasks),
        }

    except Exception as e:
        logger.error("Error searching music: %s", e)
        return {"error": str(e)}


def toggle_favorite(
    manager: MusicTaskManager,
    task_id: str,
    favorite: Optional[bool] = None,
) -> Dict[str, Any]:
    """Toggle or set favorite status for a song."""
    try:
        task = manager.get_task(task_id)
        if not task:
            return {"success": False, "error": f"Task {task_id} not found"}

        if favorite is not None:
            task.favorite = favorite
        else:
            task.favorite = not task.favorite

        manager._save_tasks()

        return {
            "success": True,
            "task_id": task_id,
            "title": task.title,
            "favorite": task.favorite,
            "message": f"{'⭐ Favorited' if task.favorite else '☆ Unfavorited'}: {task.title}",
        }

    except Exception as e:
        logger.error("Error toggling favorite: %s", e)
        return {"success": False, "error": str(e)}


def play_song(
    manager: MusicTaskManager,
    task_id: str,
) -> Dict[str, Any]:
    """Mark a song as played and return file path."""
    try:
        task = manager.get_task(task_id)
        if not task:
            return {"success": False, "error": f"Task {task_id} not found"}

        if task.status != TaskStatus.COMPLETED:
            return {
                "success": False,
                "error": f"Song not ready. Status: {task.status.value}",
            }

        task.play_count += 1
        manager._save_tasks()

        return {
            "success": True,
            "task_id": task_id,
            "title": task.title,
            "audio_file": task.audio_file,
            "duration": task.duration,
            "play_count": task.play_count,
            "message": f"Now playing: {task.title}",
        }

    except Exception as e:
        logger.error("Error playing music: %s", e)
        return {"success": False, "error": str(e)}
