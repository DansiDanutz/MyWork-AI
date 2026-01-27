# MyWork Strategy Alignment

This document aligns the MyWork Framework, Brain, and Marketplace into one system.
It defines the project taxonomy, the Brain contribution pipeline, and the path from
project to marketplace product.

## Core System

MyWork is composed of three engines:

- Framework Engine: tooling, workflows, and automation that improve delivery speed.
- Brain Engine: knowledge vault that captures patterns, fixes, and reusable solutions.
- Marketplace Engine: distribution and monetization of production-ready projects.

The loop: build -> capture -> package -> sell -> feedback -> improve.

## Project Taxonomy (Two Groups)

All projects in `projects/` must be classified as one of:

1) `framework` projects

   - Purpose: Improve MyWork core capabilities.
   - Examples: CLI tools, Autocoder, workflow automation, Brain services.
   - Output: Enables faster, more reliable delivery.

2) `product` projects

   - Purpose: Standalone products or templates that can be sold.
   - Examples: Marketplace, task-tracker, ai-dashboard, SaaS templates.
   - Output: Revenue and user value.

If a project is not directly improving the framework, it is a product project.

## Required Project Metadata

Each project should include a `project.yaml` in its root:

- name: display name
- type: framework | product
- owner: team or maintainer
- status: planned | active | archived
- marketplace: true | false
- brain_contribution: true | false
- stack: short tech list
- tags: discovery tags
- description: 1-2 lines

This metadata allows indexing, automation, and marketplace readiness checks.

## Brain -> Marketplace Pipeline

1) Capture

   - Add summaries to `.planning/BRAIN.md`
   - Add reusable patterns to Brain entries

2) Validate

   - Minimum tests or smoke checks pass
   - Docs exist (README + usage + setup)

3) Package

   - Versioned release notes
   - Stable assets (demo, screenshots, package)

4) Publish

   - Marketplace listing meets quality gate
   - Pricing and license defined

## Marketplace Readiness Checklist

Minimum to list:

- README with setup + usage
- Basic tests or smoke test
- License and pricing
- Demo URL or screenshots
- Package artifact (downloadable)
- Changelog for versions

Optional but recommended:

- Performance benchmarks
- Support policy
- Roadmap or upgrade plan

## Governance and Signals

To keep the marketplace high quality:

- Require metadata in `project.yaml`
- Use Brain contributions as a quality signal
- Track defects per release (lower is better)
- Track time-to-fix (faster is better)

## Implementation Roadmap

1) Add `project.yaml` template
2) Classify existing projects
3) Automate project registry generation
4) Use registry to power marketplace onboarding
