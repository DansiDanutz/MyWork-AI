# Modules

Each subdirectory is a self-contained business domain module.

## Module Structure

```
module-name/
├── components/    # Module-specific UI components
├── lib/           # Business logic and server actions
├── types/         # TypeScript types
└── index.ts       # Public API (only export what other modules need)

```

## Rules

- Import from module index only: `@/modules/tasks` not `@/modules/tasks/lib/internal`
- Each module owns its data and logic
- Shared code goes in `@/shared/`
