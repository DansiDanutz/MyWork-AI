# Workflow: Autocoder Feature Verification

## Problem This Solves

**The Marketplace Bug:** The Autocoder initializer agent created 56 features
from a *gaming platform* spec instead of the *marketplace* spec. This caused:

- Agents building wrong features
- Wasted compute on skipping irrelevant features
- Confusion about actual progress
- Manual intervention required to complete project

## Root Cause

The initializer agent reads `prompts/app_spec.txt` to create features in
`features.db`. If:

1. The spec is ambiguous or incomplete
2. The agent has context from a previous project
3. The agent hallucinates feature requirements

...the wrong features get created, and all subsequent coding agents work on the
wrong things.

---

## Prevention: Verification Workflow

### Step 1: Create Clear App Spec

Before running Autocoder, ensure `prompts/app_spec.txt` has:

```xml

<project_specification>
  <project_name>EXACT PROJECT NAME</project_name>

  <overview>

```text

2-3 sentences describing EXACTLY what this project is.
Be specific about the domain (e-commerce, gaming, SaaS, etc.)

```html

  </overview>

  <core_features>

```html

<!-- List actual features, not categories -->
<feature>User can sign up with email</feature>
<feature>User can create a product listing</feature>
<feature>Buyer can checkout with Stripe</feature>
<!-- Be explicit - don't assume anything -->

```html

  </core_features>

  <feature_count>45</feature_count>
  <!-- Explicit count prevents agent from guessing -->
</project_specification>

```yaml

**Anti-patterns to avoid:**

- ❌ Generic descriptions like "users can do things"
- ❌ Referencing other projects ("like the gaming platform")
- ❌ Vague feature categories without specifics
- ❌ Leaving feature_count blank

### Step 2: Run Initializer

```bash
python tools/autocoder_api.py start {project-name}

```markdown

The initializer runs first (creates features.db).

### Step 3: VERIFY Before Continuing

**CRITICAL: Always verify features.db after initializer completes!**

```bash

# Check feature count

sqlite3 projects/{name}/features.db "SELECT COUNT(*) FROM features"

# Check feature categories match your project

sqlite3 projects/{name}/features.db "SELECT DISTINCT category FROM features"

# Sample features - do they make sense?

sqlite3 projects/{name}/features.db "SELECT id, name FROM features LIMIT 10"

# Check for wrong-project indicators

sqlite3 projects/{name}/features.db "SELECT * FROM features WHERE name LIKE '%game%' OR name LIKE '%room%' OR name LIKE '%lobby%'"

```yaml

**Red Flags:**

- ⚠️ Categories don't match your project domain
- ⚠️ Feature names reference other projects
- ⚠️ Feature count is way off from spec
- ⚠️ Features reference concepts not in your spec

### Step 4: Fix If Wrong

If features are wrong, **regenerate before agents start coding:**

```bash

# Option 1: Delete and re-run initializer

sqlite3 projects/{name}/features.db "DELETE FROM features"
python tools/autocoder_api.py start {project-name}

# Option 2: Delete database entirely

rm projects/{name}/features.db
python tools/autocoder_api.py start {project-name}

```markdown

### Step 5: Add Verification to Workflow

Update `tools/autocoder_api.py` to include verification step:

```python
def verify_features(project_name: str) -> bool:

```yaml

"""Verify features.db matches app_spec.txt"""
db_path = MYWORK_PROJECTS / project_name / "features.db"
spec_path = MYWORK_PROJECTS / project_name / "prompts" / "app_spec.txt"

if not db_path.exists():

```
return True  # No features yet

```markdown

# Read spec

spec = spec_path.read_text()
project_name_from_spec = extract_project_name(spec)

# Read features

conn = sqlite3.connect(str(db_path))
features = conn.execute("SELECT name FROM features LIMIT 5").fetchall()
categories = conn.execute("SELECT DISTINCT category FROM features").fetchall()
conn.close()

# Basic sanity checks

warnings = []

# Check for gaming-specific terms in non-gaming project

gaming_terms = ['game', 'lobby', 'room', 'player', 'match', 'XP', 'credits']
for feature in features:

```yaml
for term in gaming_terms:

```

if term.lower() in feature[0].lower():

```
if 'game' not in project_name_from_spec.lower():
    warnings.append(f"Feature '{feature[0]}' contains gaming term
    '{term}'")

```

```yaml

```yaml

if warnings:

```
print("⚠️  FEATURE VERIFICATION WARNINGS:")
for w in warnings:

```python

print(f"   - {w}")

```
return False

```text

return True

```markdown

```markdown

---

## Quick Verification Checklist

Before letting coding agents run:

- [ ] `features.db` exists and has features
- [ ] Feature count matches `<feature_count>` in spec
- [ ] Categories match project domain
- [ ] Sample features make sense for this project
- [ ] No cross-project contamination (gaming terms in marketplace, etc.)

---

## Recovery If You Catch It Late

If agents have already started building wrong features:

1. **Stop agents:**

   ```bash
   python tools/autocoder_api.py stop {project-name}

```yaml

2. **Assess damage:**
   - Check what's actually built vs what features say
   - Often agents adapt and build correct things anyway
   - Review `claude-progress.txt` for actual work done

3. **Options:**
   - **Continue manually** with GSD (like we did with marketplace)
   - **Regenerate features** and restart (loses some progress)
   - **Mark mismatched features as skipped** in database

4. **Update STATE.md:**

   Document what happened and decision made.

---

## Prevention Summary

| Step | Action | When |
| ------ | -------- | ------ |
| 1 | Write explicit app_spec.txt | Before starting Autocoder |
| 2 | Run initializer | First Autocoder session |
| 3 | **VERIFY features.db** | After initializer, before coding |
| 4 | Fix if wrong | Before any coding agents run |
| 5 | Monitor first features | First few coding sessions |

**The key insight:** Verify features.db immediately after initialization. Don't
assume the agent understood your spec correctly.

---

## Adding to MyWork Framework

Consider adding this to `CLAUDE.md` decision tree:

```yaml
┌─────────────────────────────────────────────────────────────────┐
│  After Autocoder initializer completes:                        │
│     → ALWAYS run feature verification                          │
│     → Check: sqlite3 features.db "SELECT DISTINCT category..." │
│     → If wrong: DELETE and re-run initializer                  │
└─────────────────────────────────────────────────────────────────┘

```markdown

---

## Example: What Went Wrong with Marketplace

**Spec said:** MyWork Marketplace - e-commerce for developers
**Features created:** Gaming platform features

| Feature ID | Created (Wrong) | Should Have Been |
| ------------ | ----------------- | ------------------ |
| 14 | "Create XP game room" | "Create product listing" |
| 15 | "Create Credits game room" | "Checkout with Stripe" |
| 19 | "Lobby shows player list" | "Orders list page" |
| 27 | "Server validates game moves" | "Validate checkout" |

**Why it happened:** Unclear. Possibly:

- Agent had context from GamesAI project
- Spec wasn't explicit enough
- Database was copied from another project

**How we recovered:**

1. Agents started skipping gaming features automatically
2. Agents built correct marketplace pages based on app_spec.txt
3. We completed manually with GSD when discovered
4. Marketplace is now 95% complete

**Lesson:** Always verify features.db after initialization.
