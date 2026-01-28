#!/usr/bin/env python3
"""
Perfect Auto-Linting Agent - NEVER SLEEPS!
Forces immediate markdown fixing without any delays.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class PerfectMarkdownHandler(FileSystemEventHandler):
    """Immediately fixes ANY markdown file that changes"""

    def __init__(self):
        self.root_dir = Path.cwd()
        print(f"🔥 PERFECT AGENT ACTIVATED - Watching: {self.root_dir}")

    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process markdown files
        if file_path.suffix.lower() != ".md":
            return

        # Skip ignored paths
        rel_path = str(file_path.relative_to(self.root_dir))
        if any(skip in rel_path for skip in ["node_modules", ".git", ".tmp", "__pycache__"]):
            return

        print(f"🔧 MARKDOWN CHANGED: {file_path}")

        # FORCE IMMEDIATE FIX
        try:
            result = subprocess.run(
                [sys.executable, "tools/auto_lint_fixer.py", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                print(f"✅ FIXED: {file_path}")
            else:
                print(f"⚠️  Issue with {file_path}: {result.stderr}")

        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")

    def on_created(self, event):
        # Also handle newly created markdown files
        self.on_modified(event)


def main():
    """Start the perfect agent that NEVER sleeps"""
    print("🚀 Starting PERFECT Auto-Linting Agent...")
    print("🎯 This agent NEVER sleeps and fixes markdown IMMEDIATELY!")
    print("📁 Monitoring ALL markdown files")
    print("⚡ Press Ctrl+C to stop")

    event_handler = PerfectMarkdownHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping Perfect Agent...")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
