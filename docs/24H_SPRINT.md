# 24-Hour Production Sprint
**Deadline:** 2026-02-15 18:00 UTC (Dan tests as user)

## Critical Path (Must Ship)
- [ ] Fix `pip install mywork-ai && mw setup` flow end-to-end
- [ ] Publish v2.3.0 to PyPI with all fixes
- [ ] README: professional, clear getting-started, demo GIF placeholder
- [ ] `mw tour` must work flawlessly for first-time users
- [ ] `mw doctor` security score fixed (shows real score, not 0)
- [ ] All 67 commands: no crashes, clear error messages
- [ ] Shell completion (`mw completion bash/zsh/fish`)
- [ ] `mw changelog` auto-generates from git history

## Important (Should Ship)
- [ ] Fix `mw deploy` to actually work (Vercel/Railway/Render)
- [ ] `mw ai` commands work with OpenRouter key
- [ ] Performance: CLI startup < 1 second
- [ ] Clean CHANGELOG.md for v2.3.0
- [ ] GitHub Actions CI passing (green badge)

## Nice to Have
- [ ] `mw marketplace` browse/install plugins
- [ ] `mw bench` benchmarks
- [ ] Documentation site redeployed properly

## Test Protocol (What Dan Will Test)
1. `pip install mywork-ai`
2. `mw setup` → guided setup
3. `mw tour` → see what it can do
4. `mw new my-project` → scaffold
5. `cd my-project && mw doctor` → diagnostics
6. `mw ai ask "help me build X"` → AI works
7. `mw brain add/search` → knowledge management
8. `mw check` → quality gate
9. `mw deploy --dry-run` → deployment
10. Overall: is it polished? professional? intuitive?
