# MyWork Framework - Example Projects

This folder contains working example projects that demonstrate how to use the MyWork framework.

## Available Now

### CLI Task Manager (Python)
- Path: `examples/cli-task-manager/`
- Tutorial: `../docs/tutorials/01-first-project.md`
- Focus: GSD basics, CLI patterns, JSON persistence

## Quick Start the Example

```bash
cd /Users/dansidanutz/Desktop/MyWork
cp -r examples/cli-task-manager projects/my-task-cli
cd projects/my-task-cli
pip install -r requirements.txt
python src/task_manager.py --help
```

## Notes

- More examples will be added over time.
- You can scaffold additional examples using the framework CLI:

```bash
mw gsd start my-new-example
```
