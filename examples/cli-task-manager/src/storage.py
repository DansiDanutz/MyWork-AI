"""
Task storage and persistence layer for the CLI Task Manager.

This module handles saving and loading tasks from JSON files,
providing a simple file-based database solution.
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import shutil

from models import Task, Priority, TaskStats


class TaskStorage:
    """
    File-based storage for tasks using JSON format.

    This class provides a simple persistence layer that saves tasks
    to a JSON file in the user's home directory or current directory.
    """

    def __init__(self, file_path: Optional[str] = None):
        """
        Initialize storage with optional custom file path.

        Args:
            file_path: Optional custom path for the tasks file.
                      Defaults to 'tasks.json' in current directory.
        """
        if file_path:
            self.file_path = Path(file_path)
        else:
            # Default to tasks.json in current directory
            self.file_path = Path("tasks.json")

        self._ensure_file_exists()
        self._backup_interval = 10  # Backup every 10 operations

    def _ensure_file_exists(self) -> None:
        """Ensure the tasks file exists, creating it if necessary."""
        if not self.file_path.exists():
            # Create empty tasks file
            self._save_tasks_to_file([])

    def _save_tasks_to_file(self, tasks: List[Task]) -> None:
        """Save tasks to the JSON file with error handling."""
        try:
            # Convert tasks to dictionaries for JSON serialization
            tasks_data = [task.to_dict() for task in tasks]

            # Create backup before writing
            self._create_backup_if_needed()

            # Write to temporary file first, then move (atomic operation)
            temp_path = self.file_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "tasks": tasks_data,
                        "metadata": {
                            "last_updated": datetime.now().isoformat(),
                            "version": "1.0",
                            "task_count": len(tasks),
                        },
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            # Atomic move
            temp_path.replace(self.file_path)

        except Exception as e:
            # Clean up temp file if it exists
            temp_path = self.file_path.with_suffix(".tmp")
            if temp_path.exists():
                temp_path.unlink()
            raise RuntimeError(f"Failed to save tasks: {str(e)}") from e

    def _load_tasks_from_file(self) -> List[Task]:
        """Load tasks from the JSON file with error handling."""
        try:
            if not self.file_path.exists() or self.file_path.stat().st_size == 0:
                return []

            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle both old format (direct list) and new format (with metadata)
            if isinstance(data, list):
                tasks_data = data
            elif isinstance(data, dict) and "tasks" in data:
                tasks_data = data["tasks"]
            else:
                raise ValueError("Invalid file format")

            # Convert dictionaries back to Task objects
            tasks = []
            for task_data in tasks_data:
                try:
                    task = Task.from_dict(task_data)
                    tasks.append(task)
                except Exception as e:
                    # Log corrupted task but continue loading others
                    print(f"Warning: Skipped corrupted task: {e}")

            return tasks

        except (json.JSONDecodeError, ValueError) as e:
            # Try to restore from backup
            backup_path = self.file_path.with_suffix(".backup")
            if backup_path.exists():
                print(f"Warning: Corrupted tasks file, restoring from backup...")
                shutil.copy(backup_path, self.file_path)
                return self._load_tasks_from_file()

            # If no backup or backup also fails, start fresh
            print(f"Warning: Could not load tasks file ({e}), starting with empty list")
            return []

    def _create_backup_if_needed(self) -> None:
        """Create a backup copy of the tasks file."""
        if self.file_path.exists():
            backup_path = self.file_path.with_suffix(".backup")
            shutil.copy(self.file_path, backup_path)

    def get_tasks(self, include_completed: bool = True) -> List[Task]:
        """
        Retrieve all tasks from storage.

        Args:
            include_completed: Whether to include completed tasks

        Returns:
            List of Task objects sorted by creation date
        """
        tasks = self._load_tasks_from_file()

        if not include_completed:
            tasks = [task for task in tasks if not task.completed]

        # Sort by completion status first (pending first), then by creation date
        return sorted(tasks, key=lambda t: (t.completed, t.created_at))

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a single task by ID.

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            Task object if found, None otherwise
        """
        tasks = self._load_tasks_from_file()
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    def add_task(self, task: Task) -> None:
        """
        Add a new task to storage.

        Args:
            task: Task object to add
        """
        tasks = self._load_tasks_from_file()

        # Ensure unique ID
        if any(t.id == task.id for t in tasks):
            raise ValueError(f"Task with ID {task.id} already exists")

        tasks.append(task)
        self._save_tasks_to_file(tasks)

    def update_task(self, updated_task: Task) -> bool:
        """
        Update an existing task in storage.

        Args:
            updated_task: Task object with updated data

        Returns:
            True if task was found and updated, False otherwise
        """
        tasks = self._load_tasks_from_file()

        for i, task in enumerate(tasks):
            if task.id == updated_task.id:
                tasks[i] = updated_task
                self._save_tasks_to_file(tasks)
                return True

        return False

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task from storage.

        Args:
            task_id: ID of the task to delete

        Returns:
            True if task was found and deleted, False otherwise
        """
        tasks = self._load_tasks_from_file()
        initial_count = len(tasks)

        tasks = [task for task in tasks if task.id != task_id]

        if len(tasks) < initial_count:
            self._save_tasks_to_file(tasks)
            return True

        return False

    def complete_task(self, task_id: int) -> bool:
        """
        Mark a task as completed.

        Args:
            task_id: ID of the task to complete

        Returns:
            True if task was found and completed, False otherwise
        """
        task = self.get_task(task_id)
        if task and not task.completed:
            task.complete()
            return self.update_task(task)

        return False

    def uncomplete_task(self, task_id: int) -> bool:
        """
        Mark a task as not completed.

        Args:
            task_id: ID of the task to uncomplete

        Returns:
            True if task was found and uncompleted, False otherwise
        """
        task = self.get_task(task_id)
        if task and task.completed:
            task.uncomplete()
            return self.update_task(task)

        return False

    def search_tasks(self, query: str, case_sensitive: bool = False) -> List[Task]:
        """
        Search for tasks matching a query string.

        Args:
            query: Search query string
            case_sensitive: Whether search should be case-sensitive

        Returns:
            List of matching Task objects
        """
        if not query.strip():
            return []

        tasks = self._load_tasks_from_file()
        return [task for task in tasks if task.matches_query(query, case_sensitive)]

    def get_next_id(self) -> int:
        """
        Get the next available task ID.

        Returns:
            Next available ID (1-based)
        """
        tasks = self._load_tasks_from_file()
        if not tasks:
            return 1

        max_id = max(task.id for task in tasks)
        return max_id + 1

    def get_stats(self) -> TaskStats:
        """
        Get statistics about all tasks.

        Returns:
            TaskStats object with calculated statistics
        """
        tasks = self._load_tasks_from_file()
        return TaskStats.from_tasks(tasks)

    def get_overdue_tasks(self) -> List[Task]:
        """
        Get all overdue tasks.

        Returns:
            List of overdue Task objects
        """
        tasks = self._load_tasks_from_file()
        return [task for task in tasks if task.is_overdue]

    def get_due_today(self) -> List[Task]:
        """
        Get all tasks due today.

        Returns:
            List of Task objects due today
        """
        tasks = self._load_tasks_from_file()
        today = datetime.now().date()
        return [
            task
            for task in tasks
            if task.due_date and task.due_date.date() == today and not task.completed
        ]

    def get_tasks_by_priority(self, priority: Priority) -> List[Task]:
        """
        Get all tasks with a specific priority.

        Args:
            priority: Priority level to filter by

        Returns:
            List of Task objects with the specified priority
        """
        tasks = self._load_tasks_from_file()
        return [task for task in tasks if task.priority == priority]

    def clear_completed_tasks(self) -> int:
        """
        Remove all completed tasks from storage.

        Returns:
            Number of tasks that were removed
        """
        tasks = self._load_tasks_from_file()
        completed_count = len([task for task in tasks if task.completed])

        tasks = [task for task in tasks if not task.completed]
        self._save_tasks_to_file(tasks)

        return completed_count

    def export_to_json(self, export_path: str) -> None:
        """
        Export tasks to a different JSON file.

        Args:
            export_path: Path where to save the exported tasks
        """
        tasks = self._load_tasks_from_file()
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "source_file": str(self.file_path),
            "task_count": len(tasks),
            "tasks": [task.to_dict() for task in tasks],
        }

        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    def import_from_json(self, import_path: str, merge: bool = True) -> int:
        """
        Import tasks from a JSON file.

        Args:
            import_path: Path to the JSON file to import
            merge: Whether to merge with existing tasks or replace them

        Returns:
            Number of tasks imported
        """
        with open(import_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Handle different export formats
        if "tasks" in data:
            import_tasks_data = data["tasks"]
        else:
            import_tasks_data = data

        imported_tasks = []
        for task_data in import_tasks_data:
            try:
                task = Task.from_dict(task_data)
                imported_tasks.append(task)
            except Exception as e:
                print(f"Warning: Skipped invalid task during import: {e}")

        if merge:
            existing_tasks = self._load_tasks_from_file()
            # Update IDs to avoid conflicts
            max_existing_id = max((task.id for task in existing_tasks), default=0)
            for i, task in enumerate(imported_tasks):
                task.id = max_existing_id + i + 1

            all_tasks = existing_tasks + imported_tasks
        else:
            all_tasks = imported_tasks

        self._save_tasks_to_file(all_tasks)
        return len(imported_tasks)

    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the storage file.

        Returns:
            Dictionary with file metadata
        """
        if not self.file_path.exists():
            return {"exists": False, "path": str(self.file_path)}

        stat = self.file_path.stat()
        task_count = len(self._load_tasks_from_file())

        return {
            "exists": True,
            "path": str(self.file_path.absolute()),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "task_count": task_count,
        }
