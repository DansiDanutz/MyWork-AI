#!/usr/bin/env python3
"""
Simple Task Manager CLI - Built with MyWork Framework

A command-line task manager demonstrating GSD development workflow
and CLI best practices.

Usage:
    python task_manager.py add "Task title" [--priority high] [--due 2024-12-31]
    python task_manager.py list [--status pending|completed] [--priority low|normal|high]
    python task_manager.py complete <task_id>
    python task_manager.py delete <task_id>
    python task_manager.py search <query>
    python task_manager.py stats
"""

import click
from datetime import datetime
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from models import Task, Priority, Status
from storage import TaskStorage

# Initialize rich console for colored output
console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--version", is_flag=True, help="Show version information")
def cli(ctx, version):
    """🚀 Simple Task Manager - Built with MyWork Framework

    A command-line tool for managing your personal tasks and todos.
    """
    if version:
        console.print("📱 Task Manager CLI v1.0.0")
        console.print("🚀 Built with MyWork Framework")
        return

    # If no command provided, show help
    if ctx.invoked_subcommand is None:
        console.print(
            Panel(
                "Welcome to Task Manager CLI!\n\n"
                "Try: [bold cyan]python task_manager.py --help[/bold cyan]\n"
                "Or: [bold green]python task_manager.py add 'My first task'[/bold green]",
                title="🚀 Task Manager",
                border_style="blue",
            )
        )


@cli.command()
@click.argument("title")
@click.option(
    "--priority",
    type=click.Choice(["low", "normal", "high"], case_sensitive=False),
    default="normal",
    help="Task priority level",
)
@click.option(
    "--due", type=click.DateTime(formats=["%Y-%m-%d", "%Y/%m/%d"]), help="Due date (YYYY-MM-DD)"
)
def add(title: str, priority: str, due: Optional[datetime]):
    """📝 Add a new task to your list.

    Examples:
        python task_manager.py add "Learn Python"
        python task_manager.py add "Finish project" --priority high --due 2024-12-31
    """
    storage = TaskStorage()

    try:
        task = Task(
            id=storage.get_next_id(),
            title=title.strip(),
            priority=Priority(priority.lower()),
            due_date=due,
        )

        storage.add_task(task)

        # Success message with task details
        priority_color = {"high": "red", "normal": "white", "low": "dim"}[priority.lower()]
        console.print(f"✅ Added task: [bold]{title}[/bold]", style=priority_color)
        if due:
            console.print(f"📅 Due: {due.strftime('%Y-%m-%d')}")

    except Exception as e:
        console.print(f"❌ Error adding task: {str(e)}", style="bold red")
        raise click.Abort()


@cli.command()
@click.option(
    "--status",
    type=click.Choice(["pending", "completed", "all"], case_sensitive=False),
    default="all",
    help="Filter by task status",
)
@click.option(
    "--priority",
    type=click.Choice(["low", "normal", "high"], case_sensitive=False),
    help="Filter by priority level",
)
@click.option("--overdue", is_flag=True, help="Show only overdue tasks")
def list(status: str, priority: Optional[str], overdue: bool):
    """📋 List your tasks.

    Examples:
        python task_manager.py list
        python task_manager.py list --status pending
        python task_manager.py list --priority high
        python task_manager.py list --overdue
    """
    storage = TaskStorage()
    tasks = storage.get_tasks()

    # Apply filters
    if status != "all":
        tasks = [
            t
            for t in tasks
            if (t.completed and status == "completed") or (not t.completed and status == "pending")
        ]

    if priority:
        tasks = [t for t in tasks if t.priority.value == priority.lower()]

    if overdue:
        now = datetime.now()
        tasks = [t for t in tasks if t.due_date and t.due_date < now and not t.completed]

    if not tasks:
        console.print("📭 No tasks found matching your criteria.", style="yellow")
        return

    # Create rich table
    table = Table(title="📋 Your Tasks" + (f" ({status.title()})" if status != "all" else ""))

    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center", width=8)
    table.add_column("Title", style="white")
    table.add_column("Priority", justify="center", width=10)
    table.add_column("Due Date", justify="center", width=12)

    for task in sorted(tasks, key=lambda t: (t.completed, t.created_at)):
        status_icon = "✅" if task.completed else "⏳"
        priority_color = {"high": "red", "normal": "white", "low": "dim"}[task.priority.value]

        # Due date formatting with overdue highlighting
        due_str = ""
        due_style = ""
        if task.due_date:
            due_str = task.due_date.strftime("%Y-%m-%d")
            if task.due_date < datetime.now() and not task.completed:
                due_style = "bold red"
            elif task.due_date.date() == datetime.now().date():
                due_style = "bold yellow"

        table.add_row(
            str(task.id),
            status_icon,
            task.title,
            task.priority.value.title(),
            due_str,
            style=priority_color if not task.completed else "dim",
            end_section=False,
        )

    console.print(table)


@cli.command()
@click.argument("task_id", type=int)
def complete(task_id: int):
    """✅ Mark a task as completed.

    Example:
        python task_manager.py complete 1
    """
    storage = TaskStorage()

    try:
        task = storage.get_task(task_id)
        if not task:
            console.print(f"❌ Task with ID {task_id} not found.", style="bold red")
            return

        if task.completed:
            console.print(f"ℹ️  Task '{task.title}' is already completed.", style="yellow")
            return

        storage.complete_task(task_id)
        console.print(f"✅ Completed: [bold]{task.title}[/bold]", style="bold green")

    except Exception as e:
        console.print(f"❌ Error completing task: {str(e)}", style="bold red")
        raise click.Abort()


@cli.command()
@click.argument("task_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this task?")
def delete(task_id: int):
    """🗑️  Delete a task permanently.

    Example:
        python task_manager.py delete 1
    """
    storage = TaskStorage()

    try:
        task = storage.get_task(task_id)
        if not task:
            console.print(f"❌ Task with ID {task_id} not found.", style="bold red")
            return

        storage.delete_task(task_id)
        console.print(f"🗑️  Deleted: [dim]{task.title}[/dim]", style="red")

    except Exception as e:
        console.print(f"❌ Error deleting task: {str(e)}", style="bold red")
        raise click.Abort()


@cli.command()
@click.argument("query")
@click.option("--case-sensitive", is_flag=True, help="Case-sensitive search")
def search(query: str, case_sensitive: bool):
    """🔍 Search tasks by title.

    Example:
        python task_manager.py search "python"
        python task_manager.py search "Python" --case-sensitive
    """
    storage = TaskStorage()
    tasks = storage.search_tasks(query, case_sensitive=case_sensitive)

    if not tasks:
        console.print(f"🔍 No tasks found matching '{query}'", style="yellow")
        return

    console.print(f"🔍 Found {len(tasks)} task(s) matching '[bold]{query}[/bold]':")

    # Reuse list display logic
    ctx = click.get_current_context()
    ctx.invoke(list, status="all", priority=None, overdue=False)


@cli.command()
def stats():
    """📊 Show task statistics.

    Example:
        python task_manager.py stats
    """
    storage = TaskStorage()
    tasks = storage.get_tasks()

    if not tasks:
        console.print("📭 No tasks found. Add some tasks to see statistics!", style="yellow")
        return

    # Calculate statistics
    total = len(tasks)
    completed = len([t for t in tasks if t.completed])
    pending = total - completed

    priority_stats = {
        "high": len([t for t in tasks if t.priority == Priority.HIGH]),
        "normal": len([t for t in tasks if t.priority == Priority.NORMAL]),
        "low": len([t for t in tasks if t.priority == Priority.LOW]),
    }

    # Overdue tasks
    now = datetime.now()
    overdue = len([t for t in tasks if t.due_date and t.due_date < now and not t.completed])

    # Create stats panel
    stats_text = f"""[bold]Total:[/bold] {total} tasks
[bold]Completed:[/bold] {completed} ({completed/total*100:.1f}%) [green]{'█' * int(completed/total*10)}[/green]
[bold]Pending:[/bold] {pending} ({pending/total*100:.1f}%) [yellow]{'█' * int(pending/total*10)}[/yellow]

[bold]Priority Breakdown:[/bold]
• High: {priority_stats['high']} tasks [red]({'█' * min(priority_stats['high'], 10)})[/red]
• Normal: {priority_stats['normal']} tasks [white]({'█' * min(priority_stats['normal'], 10)})[/white]
• Low: {priority_stats['low']} tasks [dim]({'█' * min(priority_stats['low'], 10)})[/dim]
"""

    if overdue > 0:
        stats_text += f"\n[bold red]⚠️  Overdue:[/bold red] {overdue} tasks"

    console.print(Panel(stats_text, title="📊 Task Statistics", border_style="blue"))


@cli.command()
@click.argument("task_id", type=int)
@click.option("--title", help="New task title")
@click.option("--priority", type=click.Choice(["low", "normal", "high"]), help="New priority")
@click.option("--due", type=click.DateTime(formats=["%Y-%m-%d"]), help="New due date (YYYY-MM-DD)")
def edit(task_id: int, title: Optional[str], priority: Optional[str], due: Optional[datetime]):
    """✏️  Edit an existing task.

    Examples:
        python task_manager.py edit 1 --title "Updated title"
        python task_manager.py edit 1 --priority high
        python task_manager.py edit 1 --due 2024-12-31
    """
    storage = TaskStorage()

    try:
        task = storage.get_task(task_id)
        if not task:
            console.print(f"❌ Task with ID {task_id} not found.", style="bold red")
            return

        # Apply updates
        changes = []
        if title:
            task.title = title.strip()
            changes.append(f"title → '{title}'")

        if priority:
            task.priority = Priority(priority.lower())
            changes.append(f"priority → {priority}")

        if due:
            task.due_date = due
            changes.append(f"due date → {due.strftime('%Y-%m-%d')}")

        if not changes:
            console.print(
                "ℹ️  No changes specified. Use --title, --priority, or --due options.",
                style="yellow",
            )
            return

        storage.update_task(task)
        console.print(f"✏️  Updated task {task_id}: {', '.join(changes)}", style="bold green")

    except Exception as e:
        console.print(f"❌ Error editing task: {str(e)}", style="bold red")
        raise click.Abort()


if __name__ == "__main__":
    cli()
