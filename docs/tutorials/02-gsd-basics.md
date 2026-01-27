# Tutorial 2: Understanding GSD Workflow

**Goal:** Master the GSD planning and execution system by building a todo web app with authentication.

**What you'll learn:**
- ✅ Advanced GSD planning techniques
- ✅ Breaking down complex features into phases
- ✅ Working with multiple phases and dependencies
- ✅ Understanding verification and quality gates
- ✅ Managing project state across sessions

**Time:** 20 minutes
**Skill level:** Beginner → Intermediate
**Prerequisite:** [Tutorial 1: Your First Project](01-first-project.md)

---

## 📋 **What We're Building**

A web-based todo application with:
- **User Authentication** - Sign up, login, sessions
- **Task Management** - CRUD operations for tasks
- **Categories** - Organize tasks by project/category
- **Responsive UI** - Works on desktop and mobile
- **Data Persistence** - SQLite database storage

**Technologies:** Next.js + TypeScript + Tailwind + SQLite

---

## 🎯 **Understanding GSD Philosophy**

Before we start building, let's understand what makes GSD different:

### **Traditional Approach:**
```
💭 "I want a todo app"
   ↓
🔨 Start coding immediately
   ↓
😵 Get lost in implementation details
   ↓
🐛 Discover missing features late
   ↓
🔄 Endless refactoring
```

### **GSD Approach:**
```
💭 "I want a todo app"
   ↓
🧠 Research domain and best practices
   ↓
📋 Generate comprehensive requirements
   ↓
🗺️ Create phased roadmap
   ↓
⚡ Execute phases systematically
   ↓
✅ Verify each phase before continuing
```

**Result:** Faster development, higher quality, fewer bugs.

---

## ⚡ **Step 1: Create and Plan Project** *(5 minutes)*

### **1.1 Create the project**
```bash
cd /Users/dansidanutz/Desktop/MyWork
mw new todo-web-app nextjs
cd projects/todo-web-app
```

### **1.2 Initialize GSD planning**
```bash
mw gsd new-project
```

**Follow the prompts with these responses:**

**Project description:**
```
A modern web-based todo application with user authentication, task categories, and responsive design. Users can sign up, create tasks, organize them by category, and manage their personal productivity.
```

**Target audience:**
```
Individual users who want a clean, fast todo app accessible from any device. Power users who need categories and organization features.
```

**Key features:**
```
User registration and authentication, task CRUD operations, task categories/projects, responsive mobile-first design, data persistence, search and filtering, task due dates, priority levels.
```

**Success criteria:**
```
Users can register, log in, create and manage tasks with categories, and use the app effectively on both desktop and mobile devices. App should be fast, intuitive, and reliable.
```

### **1.3 Review the generated roadmap**
```bash
cat .planning/ROADMAP.md
```

**Expected roadmap structure:**
```markdown
Phase 1: Foundation & Authentication (5-7 features)
Phase 2: Core Task Management (6-8 features)
Phase 3: Categories & Organization (4-6 features)
Phase 4: UI/UX & Responsiveness (5-7 features)
Phase 5: Advanced Features (3-5 features)
```

**Check requirements traceability:**
```bash
cat .planning/REQUIREMENTS.md
```

---

## 🔄 **Step 2: The GSD Cycle in Action** *(12 minutes)*

### **2.1 Discuss Phase 1 (Optional but Recommended)**

Before planning, let's gather context about authentication decisions:

```bash
mw gsd discuss-phase 1
```

**GSD will ask about gray areas like:**
- Authentication method (email/password vs social login)
- Session management (cookies vs JWT)
- User profile requirements
- Password requirements
- Registration flow

**Example responses:**
- Choose email/password for simplicity
- Use cookies for session management
- Minimal user profile (email + name)
- Standard password requirements
- Simple registration with email verification

### **2.2 Plan Phase 1**
```bash
mw gsd plan-phase 1
```

**Watch GSD work:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GSD ► RESEARCHING PHASE 1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

◆ Spawning researcher...
```

**The researcher will:**
- Study Next.js authentication patterns
- Research best practices for session management
- Identify security requirements
- Find recommended libraries (NextAuth, bcrypt, etc.)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GSD ► PLANNING PHASE 1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

◆ Spawning planner...
```

**The planner will create specific plans like:**
- `01-01-PLAN.md` - Database schema and models
- `01-02-PLAN.md` - Authentication API routes
- `01-03-PLAN.md` - Login/register UI components

### **2.3 Execute Phase 1**
```bash
mw gsd execute-phase 1
```

**Watch parallel execution:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GSD ► EXECUTING WAVE 1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

◆ Plan 01-01: Database setup and user model... ✅ (commit a1b2c3d)
◆ Plan 01-02: Authentication API routes... ✅ (commit e4f5g6h)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GSD ► EXECUTING WAVE 2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

◆ Plan 01-03: Login and register UI... ✅ (commit i7j8k9l)
```

### **2.4 Verify Phase 1**

GSD automatically runs verification, but you can also test manually:

```bash
# Start the development server
npm run dev

# Test in browser at http://localhost:3000
# Try registration and login flows
```

**Verification checks:**
- ✅ User can register with email/password
- ✅ User can log in successfully
- ✅ Session persists across page reloads
- ✅ Protected routes redirect to login
- ✅ UI is clean and functional

### **2.5 Continue to Phase 2**

If verification passes:

```bash
mw gsd progress  # Check status
mw gsd execute-phase 2  # Build core task management
```

**Phase 2 will add:**
- Task model and database tables
- CRUD API endpoints for tasks
- Task list and creation UI
- Task editing and deletion

---

## 🧠 **Step 3: Understanding GSD State Management** *(3 minutes)*

### **3.1 Project state tracking**
```bash
cat .planning/STATE.md
```

**You'll see:**
```markdown
## Current Position
- **Phase:** 2 of 5
- **Status:** Executing plans
- **Last completed:** Phase 1 - Foundation & Authentication

## Decisions Made
- Authentication: Email/password with sessions
- Database: SQLite with Prisma ORM
- UI Framework: Tailwind CSS
- Session management: HTTP-only cookies

## Current Blockers
None

## Next Steps
Complete Phase 2 execution, then move to Phase 3 (Categories)
```

### **3.2 Cross-session memory**

**If you need to pause work:**
```bash
mw gsd pause-work
```

**This creates a handoff document with:**
- Current context and decisions
- What's in progress
- Next steps when resuming

**When you return:**
```bash
mw gsd resume-work
```

### **3.3 Progress tracking**
```bash
mw gsd progress
```

**Shows:**
- Overall project completion percentage
- Current phase status
- What's next
- Any blockers or issues

---

## 🔍 **Understanding the Generated Code**

### **3.1 Explore the structure**
```bash
tree src/ -I node_modules  # See the generated structure
```

**You'll find:**
```
src/
├── app/
│   ├── api/auth/           # Authentication endpoints
│   ├── auth/               # Auth pages (login, register)
│   ├── dashboard/          # Protected dashboard
│   └── layout.tsx          # App layout with nav
├── components/
│   ├── auth/               # Auth-related components
│   ├── tasks/              # Task management components
│   └── ui/                 # Reusable UI components
├── lib/
│   ├── auth.ts             # Authentication utilities
│   ├── db.ts               # Database connection
│   └── validations.ts      # Form validation schemas
└── types/
    └── index.ts            # TypeScript type definitions
```

### **3.2 Key design patterns**

**GSD follows consistent patterns:**

1. **Separation of concerns** - Auth, tasks, UI are separate
2. **Type safety** - Full TypeScript throughout
3. **Validation** - Zod schemas for forms and APIs
4. **Error handling** - Consistent error patterns
5. **Testing** - Test files alongside implementation

### **3.3 Review specific implementations**
```bash
# Authentication middleware
cat src/lib/auth.ts

# Task management API
cat src/app/api/tasks/route.ts

# Main dashboard component
cat src/app/dashboard/page.tsx
```

---

## ✅ **Verification & Quality Gates**

### **Understanding GSD verification**

GSD has multiple verification levels:

1. **Automatic verification** - Runs after each phase
2. **Manual verification** - `mw gsd verify-work`
3. **User acceptance testing** - You test the actual app

### **Quality gates checklist**

For each phase, GSD checks:
- ✅ All planned features implemented
- ✅ Code follows established patterns
- ✅ Tests pass (if applicable)
- ✅ No obvious bugs or errors
- ✅ Meets phase objectives

### **Manual testing**
```bash
# Start the app
npm run dev

# Test each major feature:
# 1. Register a new account
# 2. Log in and out
# 3. Create, edit, delete tasks
# 4. Try different categories
# 5. Test mobile responsiveness
```

---

## 🚀 **Advanced GSD Techniques**

### **4.1 Phase dependencies**

Some phases must complete before others can start. GSD automatically handles this:

```markdown
Phase 1: Authentication (prerequisite for all others)
Phase 2: Core tasks (depends on Phase 1)
Phase 3: Categories (depends on Phase 2)
Phase 4: UI polish (depends on Phases 1-3)
```

### **4.2 Parallel execution**

Within phases, GSD runs independent tasks in parallel:

```
Wave 1: Database setup + API routes (parallel)
Wave 2: UI components (after Wave 1)
Wave 3: Integration tests (after Wave 2)
```

### **4.3 Adaptive planning**

If execution reveals new requirements:

```bash
# Add an urgent phase between existing ones
mw gsd insert-phase 2.5

# Add a phase at the end
mw gsd add-phase

# Remove a phase that's no longer needed
mw gsd remove-phase 5
```

---

## 🎓 **Key GSD Concepts Mastered**

### **Planning Layer:**
- ✅ **Research** - Automatic domain investigation
- ✅ **Requirements** - Traceability from idea to code
- ✅ **Roadmap** - Phased delivery planning
- ✅ **Context** - Implementation decision capture

### **Execution Layer:**
- ✅ **Waves** - Parallel task execution
- ✅ **Atomic commits** - Clean git history
- ✅ **Verification** - Quality gates between phases
- ✅ **State management** - Cross-session continuity

### **Intelligence Layer:**
- ✅ **Brain learning** - Pattern recognition and reuse
- ✅ **Module registry** - Code reuse acceleration
- ✅ **Adaptive planning** - Dynamic requirement changes

---

## 🚀 **What's Next?**

### **Option A: Complete Your Todo App**
```bash
# Continue with remaining phases
mw gsd execute-phase 3  # Categories & Organization
mw gsd execute-phase 4  # UI/UX Polish
mw gsd execute-phase 5  # Advanced Features
```

### **Option B: Try Autocoder for Larger Projects**
Ready for autonomous coding? → [**Tutorial 3: Autocoder Basics →**](03-autocoder-basics.md)

### **Option C: Explore Advanced Features**
- **Customize phases:** Add your own requirements
- **Debug issues:** `mw gsd debug` for problem solving
- **Branch management:** Work on features in parallel
- **Deploy:** Add a deployment phase

---

## 🆘 **Troubleshooting**

### **❌ "Phase verification failed"**
```bash
# Check what failed
cat .planning/phases/[phase]/[phase]-VERIFICATION.md

# Fix manually or create gap closure plans
mw gsd plan-phase [phase] --gaps
```

### **❌ "Want to change requirements mid-project"**
```bash
# Pause current work
mw gsd pause-work

# Update requirements
# Edit .planning/REQUIREMENTS.md

# Create new phases for changes
mw gsd add-phase

# Resume with new plan
mw gsd resume-work
```

### **❌ "Generated code doesn't match my preferences"**
```bash
# Discuss implementation preferences
mw gsd discuss-phase [next-phase]

# Set coding standards in context
# Then plan and execute normally
```

---

## 🎉 **Congratulations!**

You now understand the core GSD workflow and can:

- ✅ **Plan complex projects** systematically
- ✅ **Execute phases** with parallel task management
- ✅ **Verify quality** at each step
- ✅ **Manage state** across sessions
- ✅ **Handle changing requirements** adaptively

### **Time Comparison:**

| Traditional Web App Dev | GSD Approach |
|------------------------|--------------|
| ⏱️ **1-2 weeks** planning + coding | ⚡ **2-3 hours** guided execution |
| 🐛 **Debug auth issues** for days | ✅ **Proven patterns** auto-applied |
| 📝 **Write tests** manually | 🧪 **Auto-generated** test coverage |
| 🔄 **Refactor** when requirements change | 🎯 **Adaptive planning** built-in |

---

**Ready for Tutorial 3?** → [**Autocoder Integration →**](03-autocoder-basics.md)

*💡 You've now mastered 40% of MyWork's capabilities. Tutorial 3 will show you how to scale up to larger projects with autonomous coding agents.*