# 50 Production Tasks — MyWork-AI Framework

Generated: 2026-02-15 | Priority: P0 (critical) → P3 (nice-to-have)

---

## 🔴 P0 — MUST FIX (Blocking Production)

### 1. Marketplace publish is manual-only
**Q:** Can a user actually run `mw marketplace publish` and have their product listed?
**A:** No. It creates a zip but says "Manual Upload Required". Need to wire it to the API with Clerk auth.
**Task:** Automate `mw marketplace publish` to upload to R2 + create product via marketplace API.

### 2. Stripe payments not integrated
**Q:** Can someone BUY a product on the marketplace?
**A:** No. Stripe keys are `sk_test_xxxxx` placeholders. No checkout flow works.
**Task:** Configure real Stripe test keys, test checkout → payment → repo access flow.

### 3. `mw n8n` needs .env auto-config
**Q:** After `mw n8n setup`, does the user have to manually edit .env?
**A:** Yes. Setup installs n8n but doesn't write N8N_API_URL/KEY to .env.
**Task:** After setup, auto-detect n8n URL and prompt user to save API key to .env.

### 4. AutoForge import fails
**Q:** Does `mw af start` actually work?
**A:** No. `autoforge_api.py` fails to import. Missing dependencies or broken code.
**Task:** Fix autoforge_api.py imports, test `mw af start/status/queue`.

### 5. PyPI package doesn't include n8n commands
**Q:** Does `pip install mywork-ai && mw n8n --help` work?
**A:** The PyPI package (v2.3.3) doesn't have the n8n integration yet. Need to publish v2.4.0.
**Task:** Bump version, publish to PyPI with n8n + GSD + all fixes.

### 6. No buyer repo access automation
**Q:** When someone buys a product, do they get repo access automatically?
**A:** No. It's manual. Need GitHub API integration to grant collaborator access on purchase.
**Task:** Build webhook: Stripe payment → grant GitHub repo access to buyer's account.

### 7. `mw setup` doesn't work outside MyWork-AI dir
**Q:** Can a new user run `pip install mywork-ai && mw setup` in any directory?
**A:** The `mw` entry point works but setup expects the framework directory.
**Task:** Make `mw setup` work from any directory — create project structure wherever called.

---

## 🟠 P1 — HIGH PRIORITY (User Experience)

### 8. Missing docs/ai-features.md
**Q:** Does the AI features documentation exist?
**A:** No. README links to `docs/ai-features.md` which doesn't exist.
**Task:** Write docs/ai-features.md covering mw ai generate/refactor/review/optimize.

### 9. Missing DEPLOYMENT_GUIDE.md
**Q:** Is there a deployment guide?
**A:** No. README links to it but it doesn't exist.
**Task:** Write DEPLOYMENT_GUIDE.md with Vercel, Railway, Docker, and manual deploy steps.

### 10. mw.py is 10,501 lines — needs splitting
**Q:** Is the codebase maintainable?
**A:** No. 10.5K lines in one file is a maintenance nightmare. 134 imports.
**Task:** Split mw.py into modules: core.py, n8n.py, marketplace.py, gsd.py, git_cmds.py, etc.

### 11. `mw new` scaffolded projects need real sample code
**Q:** When user runs `mw new my-app`, does the generated project actually work?
**A:** Needs testing. Verify scaffolded projects have working sample code that runs.
**Task:** Test all scaffold templates (fastapi, react, node, python). Fix any broken ones.

### 12. `.mcp.json` not configured
**Q:** Is n8n-mcp integration actually working?
**A:** n8n-mcp npx command exists but `.mcp.json` config file isn't created.
**Task:** Generate .mcp.json during `mw n8n setup` with proper n8n MCP server config.

### 13. n8n skills not installed
**Q:** Are n8n-skills (expert workflow guidance) available?
**A:** No. They're referenced in CLAUDE.md but never installed.
**Task:** Bundle or auto-install n8n-skills during `mw n8n setup`.

### 14. Marketplace frontend Clerk auth not working for new users
**Q:** Can a new user sign up on the marketplace?
**A:** Needs testing. Clerk publishable key might be misconfigured.
**Task:** Test full signup → browse → purchase flow on frontend-hazel-ten-17.vercel.app.

### 15. No product screenshots/preview images
**Q:** Do marketplace products have visual previews?
**A:** SportsAI has screenshot URLs but images might not exist. Smart Lead Nurture has none.
**Task:** Create actual screenshots for both products, upload to GitHub/R2.

### 16. WAT workflow template references missing tool
**Q:** Do all WAT workflows reference existing tools?
**A:** No. `_template.md` references `tools/example_tool.py` which doesn't exist.
**Task:** Fix _template.md and audit all 13 workflow files for broken references.

### 17. No integration tests for n8n commands
**Q:** Are n8n commands tested?
**A:** Only manual testing. No pytest tests for n8n import/export/list/status.
**Task:** Add tests/test_n8n.py with mocked API responses.

### 18. 22 placeholder values in .env.example
**Q:** Is .env.example helpful for new users?
**A:** It has 22 "xxxxx" or "your-" placeholders. Needs clear comments for each.
**Task:** Rewrite .env.example with clear descriptions and which are required vs optional.

---

## 🟡 P2 — MEDIUM PRIORITY (Quality & Polish)

### 19. `mw tour` — test the interactive tour
**Q:** Does the interactive tour work end-to-end?
**A:** Needs testing. Tour should guide through setup → first project → deploy.
**Task:** Run through tour, fix any broken steps.

### 20. `mw selftest` — verify all 8 diagnostic checks
**Q:** Does selftest catch real issues?
**A:** Needs testing. Verify it checks: Python, pip, git, node, npm, docker, mw version, config.
**Task:** Run selftest, verify each check, fix any false positives/negatives.

### 21. `mw deploy` — test all platforms
**Q:** Does deploy work for Vercel, Railway, Docker?
**A:** Partially. Vercel deploy was fixed with API workaround. Railway/Docker untested.
**Task:** Test `mw deploy --platform=vercel/railway/docker` for each platform.

### 22. `mw ci generate` — test CI pipeline generation
**Q:** Does it generate working GitHub Actions?
**A:** Needs testing. Generated CI should run tests, lint, and deploy.
**Task:** Run `mw ci generate`, push to a test repo, verify Actions pass.

### 23. Brain knowledge vault — test CRUD
**Q:** Does `mw brain add/search/stats` work?
**A:** Has code but needs testing with actual data.
**Task:** Test brain add "lesson", brain search "lesson", brain stats, brain review.

### 24. Credits system — does it track anything?
**Q:** What does `mw credits` actually do?
**A:** Likely a stub. Need to verify if it tracks API usage or marketplace credits.
**Task:** Test credits balance/history, document what it tracks.

### 25. `mw changelog` — auto-generate from git
**Q:** Does changelog generation work from git history?
**A:** Needs testing. Should parse conventional commits.
**Task:** Test `mw changelog` on the MyWork-AI repo, verify output quality.

### 26. `mw release` — full release pipeline
**Q:** Does `mw release` handle version bump + changelog + tag + push?
**A:** Needs testing end-to-end.
**Task:** Test `mw release patch/minor/major` in a safe environment.

### 27. `mw monitor` — what does it monitor?
**Q:** Does monitoring work?
**A:** Likely needs an API server running. Test what it does.
**Task:** Test `mw monitor`, document what it monitors, fix if broken.

### 28. `mw pair` — pair programming mode
**Q:** Does pair session work?
**A:** Needs testing. Should enable collaborative coding sessions.
**Task:** Test pair session start/stop, document the feature.

### 29. `mw bench self` — benchmark tracking
**Q:** Does `mw bench self` save historical data for comparison?
**A:** Just added it. Needs testing of the history tracking feature.
**Task:** Run bench self 3 times, verify historical comparison works.

### 30. `mw plugin` — plugin management
**Q:** Can users install/remove plugins?
**A:** Needs testing. Plugin system should handle third-party extensions.
**Task:** Test plugin list/install/remove with a sample plugin.

### 31. Error messages need consistency audit
**Q:** Do all commands show "❌ Error + 💡 Try" format consistently?
**A:** Most do from the audit, but some edge cases might slip through.
**Task:** Test 10 error scenarios (bad args, missing files, network errors), verify format.

### 32. `mw env audit` — environment security
**Q:** Does it catch exposed secrets in .env files?
**A:** Needs testing. Should flag API keys in .env that aren't gitignored.
**Task:** Test with a .env containing test secrets, verify detection.

### 33. `mw depgraph` — dependency visualization
**Q:** Does it produce a useful dependency graph?
**A:** Needs testing. Should output a visual or text-based dep graph.
**Task:** Test on MyWork-AI itself, verify output is useful.

### 34. `mw test-coverage` — test gap analysis
**Q:** Does it identify files missing tests?
**A:** Needs testing. Should report which source files have no corresponding tests.
**Task:** Run on MyWork-AI, compare output to actual test coverage.

### 35. `mw insights` — tech debt analysis
**Q:** Does insights give actionable recommendations?
**A:** Needs testing. Should identify hotspots, complexity, and debt.
**Task:** Run on a real project, verify insights are accurate and actionable.

---

## 🟢 P3 — NICE TO HAVE (Enhancement)

### 36. Add `mw n8n templates` — browse n8n template library
**Q:** Can users browse 2,709 n8n templates from the CLI?
**A:** Not yet. n8n-mcp has template search but it's not wired to `mw n8n`.
**Task:** Add `mw n8n templates <query>` to search n8n template library.

### 37. Add `mw n8n create` — AI-assisted workflow creation
**Q:** Can users create n8n workflows from natural language?
**A:** Not yet. Should use LLM + n8n node catalog to build workflows.
**Task:** Implement `mw n8n create "send weekly email report"` using AI.

### 38. Marketplace product reviews
**Q:** Can buyers leave reviews?
**A:** API has review endpoints but not tested.
**Task:** Test review create/list/respond flow via API.

### 39. Marketplace seller dashboard
**Q:** Can sellers see their sales/revenue?
**A:** API has payout/balance endpoints but untested.
**Task:** Test seller dashboard: sales count, revenue, payout requests.

### 40. `mw marketplace search` — search products
**Q:** Can users search for specific products?
**A:** `mw marketplace browse` lists all but no search/filter.
**Task:** Add `mw marketplace search <query>` with category/tag filtering.

### 41. SportsAI — live odds not working
**Q:** Does SportsAI show real-time betting odds?
**A:** No. The Odds API key is out of credits (401 errors). Only team/league data works.
**Task:** Either get new Odds API key or document the limitation clearly.

### 42. SportsAI — GitHub auth on frontend
**Q:** Can users sign in with GitHub on sports-ai-one.vercel.app?
**A:** Needs testing. OAuth callback might not be configured.
**Task:** Test GitHub OAuth flow on SportsAI frontend.

### 43. Add `mw doctor --fix` auto-fix
**Q:** Does `mw doctor --fix` actually fix issues?
**A:** Doctor recommends fixes but --fix flag might not implement them.
**Task:** Verify --fix actually resolves reported issues.

### 44. Marketplace CI/CD smoke tests
**Q:** Do the smoke test workflows actually run?
**A:** There are 3 smoke test workflow files but they might not be configured to run.
**Task:** Verify GitHub Actions smoke tests trigger and pass.

### 45. `mw upgrade` — self-upgrade from PyPI
**Q:** Can users upgrade MyWork-AI with one command?
**A:** Should run `pip install --upgrade mywork-ai`. Needs testing.
**Task:** Test `mw upgrade` from an older version, verify it pulls latest.

### 46. Add version check on startup
**Q:** Does `mw` tell users when a new version is available?
**A:** No. Should check PyPI on startup (with cache to avoid slowdown).
**Task:** Add optional version check that notifies of updates.

### 47. `mw config` — persistent configuration
**Q:** Does config persist between sessions?
**A:** Needs testing. Should save preferences to ~/.mywork/config.json.
**Task:** Test config set/get/list, verify persistence.

### 48. Add `mw quickstart` — guided first experience
**Q:** Is there a single command that walks through everything?
**A:** `mw tour` exists but `mw quickstart` would be more intuitive.
**Task:** Create `mw quickstart` as alias/wrapper for the best onboarding flow.

### 49. Marketplace — R2 file upload for product packages
**Q:** Can sellers upload product zip files?
**A:** R2 is configured but upload flow not implemented in CLI.
**Task:** Implement R2 upload in `mw marketplace publish` using R2 credentials.

### 50. End-to-end integration test script
**Q:** Is there one script that tests the ENTIRE user journey?
**A:** No. Need: `pip install → mw setup → mw new → mw doctor → mw n8n setup → mw marketplace publish`
**Task:** Create `tests/e2e/test_full_journey.py` that runs the complete flow in a temp directory.

---

## Summary

| Priority | Count | Description |
|----------|-------|-------------|
| 🔴 P0 | 7 | Blocking production — must fix |
| 🟠 P1 | 11 | User experience — high impact |
| 🟡 P2 | 17 | Quality & polish — medium impact |
| 🟢 P3 | 15 | Enhancements — nice to have |
| **Total** | **50** | |
