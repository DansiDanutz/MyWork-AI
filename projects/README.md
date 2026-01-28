# Projects

This directory contains all MyWork Framework projects - isolated applications built using GSD orchestration.

## Production Projects

| Project | Status | Live URL | Stack |
|---------|--------|----------|-------|
| [task-tracker](task-tracker/) | **Live** | [task-tracker-weld-delta.vercel.app](https://task-tracker-weld-delta.vercel.app) | Next.js 15 + Prisma + PostgreSQL |
| [ai-dashboard](ai-dashboard/) | Ready | - | Next.js 14 + FastAPI + APScheduler |

## External Projects (Symlinks)

These projects are symlinked from external locations:

| Project | Status | Live URL | Description |
|---------|--------|----------|-------------|
| sports-ai | **Live** | [sports-ai-one.vercel.app](https://sports-ai-one.vercel.app) | Sports betting analytics platform |
| games | **Live** | - | Gaming platform (326 features) |

## Creating New Projects

### Using CLI (Recommended)

```bash
# From MyWork root
python tools/mw.py new my-project fastapi

# Available templates: basic, fastapi, nextjs, fullstack, cli, automation
```

### Using GSD

```bash
# Navigate to new project
cd projects/my-project

# Initialize with GSD
/gsd:new-project
```

### Manual Creation

Copy the template directory:

```bash
cp -r _template my-new-project
cd my-new-project
```

## Project Structure

Each project follows this standard structure:

```
project-name/
├── .planning/              # GSD state for this project
│   ├── PROJECT.md          # Vision and scope
│   ├── ROADMAP.md          # Phases and progress
│   ├── STATE.md            # Current context
│   └── phases/             # Phase plans and summaries
├── src/                    # Source code (varies by template)
├── README.md               # Project documentation
└── start.sh / start.bat    # Launch scripts
```

## Project Isolation

Each project is **fully isolated**:

- Own `.planning/` directory (separate from framework)
- Own dependencies (`package.json`, `requirements.txt`)
- Own environment (`.env.local`)
- Own deployment configuration

This means you can work on multiple projects simultaneously without interference.

## Linking External Projects

To add an existing project to MyWork:

```bash
# Create symlink
ln -s /path/to/your/project projects/project-name

# The project should have its own .planning/ directory
# GSD commands will work normally
```

## Best Practices

1. **One project per folder** - Keep projects isolated
2. **Use templates** - Start with `mw new` for consistent structure
3. **Track state** - GSD creates `.planning/` automatically
4. **Separate concerns** - Framework state stays in root `.planning/`, project state in `projects/[name]/.planning/`
