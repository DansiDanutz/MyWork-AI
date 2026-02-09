# Error Handling Integration Guide

This guide shows how to integrate the enhanced error handling from batch 3 testing into the MyWork-AI tool.

## Issues Found in Batch 3 Testing

### SIM25: Disk Full Error Handling (FAILED)
- **Problem**: No graceful handling when disk is full
- **Solution**: Add disk space checks before large operations

### SIM26: Permission Error Handling (FAILED) 
- **Problem**: Poor error messages for permission issues
- **Solution**: Provide specific commands to fix permissions

### SIM21: SQL Injection (FALSE POSITIVE)
- **Review**: The tool actually handles this correctly - test was overly aggressive

## Integration Steps

### 1. Import the Error Handler

```python
# Add to top of mw.py
from error_handling_improvements import MyWorkErrorHandler, enhanced_error_decorator
```

### 2. Enhance File Operations

```python
# Replace basic file writes with safe writes
def save_brain_data(data):
    brain_file = Path(".planning/brain_data.json")
    success, message = MyWorkErrorHandler.safe_file_write(
        brain_file, 
        json.dumps(data, indent=2)
    )
    if not success:
        print(message)
        return False
    return True
```

### 3. Add Disk Space Checks

```python
@enhanced_error_decorator
def cmd_new(args):
    """Create new project with disk space check"""
    # Check disk space before creating project
    project_root = PROJECTS_DIR / project_name
    has_space, error_msg = MyWorkErrorHandler.check_disk_space(
        project_root, 50  # 50MB for new project
    )
    if not has_space:
        print(error_msg)
        return 1
    
    # Continue with project creation...
```

### 4. Improve Permission Errors

```python
def ensure_planning_directory():
    """Ensure .planning directory exists with proper permissions"""
    planning_dir = MYWORK_ROOT / ".planning"
    
    has_perms, error_msg = MyWorkErrorHandler.check_permissions(planning_dir)
    if not has_perms:
        print(error_msg)
        return False
    
    return True
```

## Quick Wins

Apply these decorators to high-risk functions:

```python
@enhanced_error_decorator
def cmd_new(args):
    # Project creation

@enhanced_error_decorator 
def cmd_brain_add(args):
    # Brain data operations

@enhanced_error_decorator
def save_project_registry():
    # Registry saves
```

## Testing the Fixes

After integration, re-run batch 3 tests:

```bash
cd tools/simulation/scenarios
python3 batch_3_advanced.py
```

Expected improvements:
- SIM25 should pass with disk space checks
- SIM26 should pass with better permission messages
- Overall grade should improve from B to A-

## Implementation Priority

1. **High Priority**: Disk space checks for `cmd_new` and brain operations
2. **Medium Priority**: Permission error messages for setup operations  
3. **Low Priority**: Review and adjust SQL injection test criteria

---

**Next Steps**: Implement these changes and re-run the test suite to validate improvements.