#!/usr/bin/env python3
"""
Error Handling Improvements for MyWork-AI
=========================================

This module provides enhanced error handling with user-friendly messages
and actionable guidance for common issues discovered in batch 3 testing.

Author: Subagent for OpenClaw
Created: 2026-02-09
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Tuple


class MyWorkErrorHandler:
    """Enhanced error handling with user-friendly messages"""
    
    @staticmethod
    def check_permissions(path: Path) -> Tuple[bool, str]:
        """Check if we have read/write permissions to a path"""
        try:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
            
            # Test write permissions
            test_file = path / ".permission_test"
            test_file.write_text("test")
            test_file.unlink()
            
            return True, ""
        except PermissionError as e:
            error_msg = f"""
🔒 Permission Error: {path}

Cannot write to {path}. This is likely a permission issue.

Quick fixes:
  1. Fix ownership: sudo chown -R $USER:$USER {path}
  2. Fix permissions: chmod -R u+w {path}
  3. Or run: sudo chmod 755 {path}

If this is a system directory, consider using a different location.
"""
            return False, error_msg.strip()
        except Exception as e:
            return False, f"Unexpected error checking permissions: {str(e)}"

    @staticmethod
    def check_disk_space(path: Path, required_mb: int = 100) -> Tuple[bool, str]:
        """Check if we have enough disk space for operations"""
        try:
            stat = shutil.disk_usage(path)
            free_mb = stat.free // (1024 * 1024)
            
            if free_mb < required_mb:
                error_msg = f"""
💾 Disk Space Error

Not enough disk space available:
  Required: {required_mb} MB
  Available: {free_mb} MB
  
To free up space:
  1. Clean temp files: sudo apt clean && sudo apt autoremove
  2. Empty trash: rm -rf ~/.local/share/Trash/*
  3. Find large files: du -h {path} | sort -rh | head -10
  
After freeing space, try your command again.
"""
                return False, error_msg.strip()
            
            return True, ""
        except Exception as e:
            return False, f"Could not check disk space: {str(e)}"

    @staticmethod
    def handle_file_operation_error(operation: str, file_path: Path, error: Exception) -> str:
        """Generate helpful error messages for file operation failures"""
        
        if isinstance(error, PermissionError):
            return f"""
🔒 Permission denied for {operation}

File: {file_path}

Quick fixes:
  1. Check ownership: ls -la {file_path.parent}
  2. Fix permissions: chmod u+w {file_path}
  3. Fix ownership: sudo chown $USER {file_path}
  
If this persists, run: sudo chown -R $USER:$USER {file_path.parent}
"""
        
        elif isinstance(error, FileNotFoundError):
            return f"""
📁 File not found: {file_path}

The {operation} operation failed because the file doesn't exist.

Possible solutions:
  1. Check the path: {file_path}
  2. Create parent directory: mkdir -p {file_path.parent}
  3. Initialize if needed: mw setup
"""
        
        elif isinstance(error, OSError) and "No space left" in str(error):
            return f"""
💾 No space left on device

The {operation} operation failed due to insufficient disk space.

To resolve:
  1. Free up space: df -h (check usage)
  2. Clean temporary files: rm -rf /tmp/*
  3. Remove old logs: sudo journalctl --vacuum-size=100M
  4. Run: sudo apt clean && sudo apt autoremove

After freeing space, retry your command.
"""
        
        else:
            return f"Error during {operation}: {str(error)}"

    @staticmethod
    def safe_file_write(file_path: Path, content: str, backup: bool = True) -> Tuple[bool, str]:
        """Safely write to a file with proper error handling"""
        
        # Check disk space first (estimate 2x content size)
        required_mb = len(content.encode()) * 2 // (1024 * 1024) + 1
        has_space, space_error = MyWorkErrorHandler.check_disk_space(
            file_path.parent, required_mb
        )
        
        if not has_space:
            return False, space_error
        
        # Check permissions
        has_perms, perm_error = MyWorkErrorHandler.check_permissions(file_path.parent)
        if not has_perms:
            return False, perm_error
        
        try:
            # Create backup if requested and file exists
            if backup and file_path.exists():
                backup_path = file_path.with_suffix(file_path.suffix + '.backup')
                backup_path.write_text(file_path.read_text())
            
            # Write the content
            file_path.write_text(content)
            return True, f"Successfully wrote {len(content)} characters to {file_path}"
            
        except Exception as e:
            error_msg = MyWorkErrorHandler.handle_file_operation_error(
                "write", file_path, e
            )
            return False, error_msg

    @staticmethod
    def format_error_message(title: str, message: str, suggestions: list = None) -> str:
        """Format a consistent error message with suggestions"""
        
        formatted = f"\n🚨 {title}\n\n{message}\n"
        
        if suggestions:
            formatted += "\n💡 Suggestions:\n"
            for i, suggestion in enumerate(suggestions, 1):
                formatted += f"  {i}. {suggestion}\n"
        
        formatted += "\nFor more help, run: mw doctor\n"
        return formatted


def enhanced_error_decorator(func):
    """Decorator to add enhanced error handling to functions"""
    
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PermissionError as e:
            file_path = getattr(e, 'filename', 'unknown file')
            error_msg = MyWorkErrorHandler.handle_file_operation_error(
                func.__name__, Path(file_path), e
            )
            print(error_msg)
            return 1
        except OSError as e:
            if "No space left" in str(e):
                print(MyWorkErrorHandler.format_error_message(
                    "Disk Full",
                    "Not enough disk space to complete the operation.",
                    [
                        "Run 'df -h' to check disk usage",
                        "Free up space with 'sudo apt clean'",
                        "Remove large files from ~/Downloads or /tmp",
                        "Move projects to external storage"
                    ]
                ))
            else:
                print(f"System error: {str(e)}")
            return 1
        except Exception as e:
            print(f"Unexpected error in {func.__name__}: {str(e)}")
            return 1
    
    return wrapper


if __name__ == "__main__":
    # Quick test of error handling
    test_path = Path("/tmp/mw_error_test")
    
    # Test permission check
    has_perms, msg = MyWorkErrorHandler.check_permissions(test_path)
    print(f"Permission check: {has_perms}")
    if not has_perms:
        print(msg)
    
    # Test disk space check
    has_space, msg = MyWorkErrorHandler.check_disk_space(test_path, 1)  # 1MB
    print(f"Disk space check: {has_space}")
    if not has_space:
        print(msg)
    
    # Test safe file write
    test_file = test_path / "test.txt"
    success, msg = MyWorkErrorHandler.safe_file_write(test_file, "Test content")
    print(f"File write test: {success}")
    print(msg)
    
    # Cleanup
    if test_path.exists():
        shutil.rmtree(test_path)
        
    print("\n✅ Error handling improvements module is ready!")
    print("To integrate with mw.py, import MyWorkErrorHandler and use the safe_file_write method.")