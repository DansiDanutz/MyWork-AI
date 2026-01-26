# Projects Overview

All projects live under `projects/`. Each project must belong to one of two groups:

- `framework`: Improves the MyWork Framework itself.
- `product`: Standalone product or template that can be sold.

## Required Metadata

Every project should include a `project.yaml` file with the fields listed in
`projects/_template/project.yaml`. This enables indexing, automation, and marketplace
readiness checks.

## Examples

- `projects/task-tracker` -> product
- `projects/ai-dashboard` -> product

Core framework tools live outside of `projects/` in `tools/` and `workflows/`.

Marketplace lives in a private repo: `DansiDanutz/Marketplace`.
