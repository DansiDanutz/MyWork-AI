# MyWork Module Registry

> Auto-generated on 2026-01-24 16:08:46
> Total Modules: 1283

## Overview

This registry contains all reusable modules discovered across MyWork projects.
Use it to find existing implementations before building new ones.

## Quick Search Commands

```bash

# Search for modules

python tools/module_registry.py search "auth"
python tools/module_registry.py search "api endpoint"

# List by type

python tools/module_registry.py list api_endpoint
python tools/module_registry.py list component

```

## Statistics

### By Type

| Type | Count |
|------|-------|
| utility | 779 |
| component | 236 |
| schema | 149 |
| api_endpoint | 57 |
| hook | 52 |
| service | 8 |
| middleware | 2 |

### By Project

| Project | Modules |
|---------|--------|
| my-games | 1197 |
| ai-dashboard | 86 |

## Modules by Type

### Api Endpoint

- **/api/videos** (ai-dashboard)
  - File: `backend/main.py:173`
  - API root endpoint
  - Tags: api, backend, main.py, videos, api_endpoint

- **/api/automation/{automation_id}** (ai-dashboard)
  - File: `backend/main.py:311`
  - Create a new video automation from prompt
  - Tags: api, backend, automation, main.py, api_endpoint

- **/api/videos/scrape** (ai-dashboard)
  - File: `backend/main.py:185`
  - Get top AI videos
  - Tags: api, backend, main.py, scrape, videos

- **/api/scheduler/run/{job_id}** (ai-dashboard)
  - File: `backend/main.py:381`
  - Get scheduler job status
  - Tags: api, job, backend, main.py, api_endpoint

- **/api/news/trending** (ai-dashboard)
  - File: `backend/main.py:210`
  - Get latest AI news
  - Tags: api, trending, backend, main.py, news

- **/api/projects/scrape** (ai-dashboard)
  - File: `backend/main.py:257`
  - Get trending AI GitHub projects
  - Tags: api, projects, backend, main.py, scrape

- **/api/automation/{automation_id}/generate-video** (ai-dashboard)
  - File: `backend/main.py:328`
  - Update a video automation draft
  - Tags: api, backend, automation, generate, main.py

- **/api/news** (ai-dashboard)
  - File: `backend/main.py:198`
  - Manually trigger YouTube scraper
  - Tags: api, backend, main.py, news, api_endpoint

- **/api/automation** (ai-dashboard)
  - File: `backend/main.py:293`
  - Get a specific automation
  - Tags: api, backend, automation, main.py, api_endpoint

- **/api/automation/{automation_id}/approve** (ai-dashboard)
  - File: `backend/main.py:353`
  - Check HeyGen video generation status
  - Tags: api, backend, automation, main.py, approve

- **/api/projects** (ai-dashboard)
  - File: `backend/main.py:234`
  - Manually trigger news aggregator
  - Tags: api, projects, backend, main.py, api_endpoint

- **/api/scheduler/status** (ai-dashboard)
  - File: `backend/main.py:375`
  - ---------- Scheduler ----------
  - Tags: api, status, backend, main.py, api_endpoint

- **/api/projects/trending** (ai-dashboard)
  - File: `backend/main.py:246`
  - Get top AI GitHub projects
  - Tags: api, projects, trending, backend, main.py

- **/api/news/scrape** (ai-dashboard)
  - File: `backend/main.py:221`
  - Get latest AI news
  - Tags: api, backend, main.py, scrape, news

- **/api/automation/{automation_id}/video-status** (ai-dashboard)
  - File: `backend/main.py:343`
  - Generate HeyGen video for automation
  - Tags: api, status, backend, automation, main.py

- **/api/stats** (ai-dashboard)
  - File: `backend/main.py:395`
  - Manually trigger a scheduled job
  - Tags: api, backend, main.py, stats, api_endpoint

- **/next** (my-games)
  - File: `autocoder/server/routers/schedules.py:204`
  - Tags: next, autocoder, schedules.py, api_endpoint, server

- **/sessions** (my-games)
  - File: `autocoder/server/routers/expand_project.py:61`
  - Status of an expansion session.
  - Tags: sessions, expand_project.py, autocoder, api_endpoint, server

- **/{name}/prompts** (my-games)
  - File: `autocoder/server/routers/projects.py:312`
  - Tags: name, routers, projects.py, autocoder, api_endpoint

- **/{path:path}** (my-games)
  - File: `autocoder/server/main.py:201`
  - Serve the React app index.html.
  - Tags: path, main.py, autocoder, api_endpoint, server

- **/{feature_id}/dependencies** (my-games)
  - File: `autocoder/server/routers/features.py:680`
  - Tags: routers, feature, features.py, autocoder, api_endpoint

- **/create-directory** (my-games)
  - File: `autocoder/server/routers/filesystem.py:432`
  - Tags: filesystem.py, create, autocoder, directory, api_endpoint

- **/sessions/{project_name}** (my-games)
  - File: `autocoder/server/routers/spec_creation.py:86`
  - Tags: name, sessions, spec_creation.py, autocoder, project

- **/status/{project_name}** (my-games)
  - File: `autocoder/server/routers/spec_creation.py:109`
  - Status of spec files on disk (from .spec_status.json).
  - Tags: name, status, spec_creation.py, autocoder, project

- **/pause** (my-games)
  - File: `autocoder/server/routers/agent.py:163`
  - Notify scheduler of manual stop (to prevent auto-start during scheduled window)
  - Tags: agent.py, pause, autocoder, api_endpoint, server

- **/status** (my-games)
  - File: `autocoder/server/routers/agent.py:85`
  - Get the process manager for a project.
  - Tags: status, agent.py, autocoder, api_endpoint, server

- **/{feature_id}** (my-games)
  - File: `autocoder/server/routers/features.py:477`
  - Compute passing IDs for response
  - Tags: feature, features.py, autocoder, api_endpoint, server

- **/bulk** (my-games)
  - File: `autocoder/server/routers/features.py:224`
  - ============================================================================
  - Tags: bulk, features.py, autocoder, api_endpoint, server

- **/{schedule_id}** (my-games)
  - File: `autocoder/server/routers/schedules.py:348`
  - Tags: schedule, autocoder, schedules.py, api_endpoint, server

- **/{project_name}/{terminal_id}** (my-games)
  - File: `autocoder/server/routers/terminal.py:199`
  - Tags: name, terminal.py, autocoder, project, terminal

- **/sessions** (my-games)
  - File: `autocoder/server/routers/assistant_chat.py:178`
  - ============================================================================
  - Tags: sessions, autocoder, api_endpoint, server, assistant_chat.py

- **/sessions** (my-games)
  - File: `autocoder/server/routers/spec_creation.py:62`
  - Validate project name to prevent path traversal.
  - Tags: sessions, spec_creation.py, autocoder, api_endpoint, server

- **/start** (my-games)
  - File: `autocoder/server/routers/devserver.py:136`
  - Run healthcheck to detect crashed processes
  - Tags: start, autocoder, api_endpoint, server, devserver.py

- **/api/health** (my-games)
  - File: `autocoder/server/main.py:153`
  - WebSocket endpoint for real-time project updates.
  - Tags: api, main.py, autocoder, health, api_endpoint

- **/conversations/{project_name}/{conversation_id}** (my-games)
  - File: `autocoder/server/routers/assistant_chat.py:157`
  - Tags: name, routers, conversation, autocoder, project

- **/{project_name}** (my-games)
  - File: `autocoder/server/routers/terminal.py:139`
  - If no terminals exist, create a default one
  - Tags: name, terminal.py, autocoder, project, api_endpoint

- **/config** (my-games)
  - File: `autocoder/server/routers/devserver.py:232`
  - Tags: config, autocoder, api_endpoint, server, devserver.py

- **/{feature_id}/skip** (my-games)
  - File: `autocoder/server/routers/features.py:528`
  - Tags: feature, features.py, autocoder, skip, api_endpoint

- **/{name}/stats** (my-games)
  - File: `autocoder/server/routers/projects.py:342`
  - Tags: name, projects.py, stats, autocoder, api_endpoint

- **/start** (my-games)
  - File: `autocoder/server/routers/agent.py:105`
  - Run healthcheck to detect crashed processes
  - Tags: agent.py, start, autocoder, api_endpoint, server

- **/list** (my-games)
  - File: `autocoder/server/routers/filesystem.py:187`
  - for pattern in HIDDEN_PATTERNS:

        if re.match(pattern, name, re.IGNORECASE):
            retur

  - Tags: list, autocoder, filesystem.py, api_endpoint, server

- **/models** (my-games)
  - File: `autocoder/server/routers/settings.py:46`
  - Parse YOLO mode string to boolean.
  - Tags: models, autocoder, api_endpoint, server, settings.py

- **/sessions/{project_name}** (my-games)
  - File: `autocoder/server/routers/assistant_chat.py:201`
  - Get information about an active session.
  - Tags: name, sessions, autocoder, project, api_endpoint

- **/stop** (my-games)
  - File: `autocoder/server/routers/devserver.py:180`
  - Now command is definitely str
  - Tags: stop, autocoder, api_endpoint, server, devserver.py

- **/stop** (my-games)
  - File: `autocoder/server/routers/agent.py:142`
  - Notify scheduler of manual start (to prevent auto-stop during scheduled window)
  - Tags: agent.py, stop, autocoder, api_endpoint, server

- **/api/setup/status** (my-games)
  - File: `autocoder/server/main.py:159`
  - WebSocket endpoint for real-time project updates.
  - Tags: api, status, setup, main.py, autocoder

- **/api/test/slow** (my-games)
  - File: `apps/api/src/index.ts:154`
  - Health check routes (must be registered before other routes)
  - Tags: api, slow, api_endpoint, test, index.ts

- **/validate** (my-games)
  - File: `autocoder/server/routers/filesystem.py:358`
  - Check if drive is accessible
  - Tags: validate, autocoder, filesystem.py, api_endpoint, server

- **/status** (my-games)
  - File: `autocoder/server/routers/devserver.py:114`
  - ============================================================================
  - Tags: status, autocoder, api_endpoint, server, devserver.py

- **/resume** (my-games)
  - File: `autocoder/server/routers/agent.py:177`
  - Pause the agent for a project.
  - Tags: resume, agent.py, autocoder, api_endpoint, server

- **/drives** (my-games)
  - File: `autocoder/server/routers/filesystem.py:303`
  - Not at root
  - Tags: drives, autocoder, filesystem.py, api_endpoint, server

- **/{name}** (my-games)
  - File: `autocoder/server/routers/projects.py:237`
  - Tags: name, projects.py, autocoder, api_endpoint, server

- **/{feature_id}/dependencies/{dep_id}** (my-games)
  - File: `autocoder/server/routers/features.py:644`
  - Tags: routers, feature, features.py, autocoder, dep

- **/conversations/{project_name}** (my-games)
  - File: `autocoder/server/routers/assistant_chat.py:136`
  - Tags: name, routers, autocoder, project, api_endpoint

- **/home** (my-games)
  - File: `autocoder/server/routers/filesystem.py:505`
  - Tags: autocoder, filesystem.py, api_endpoint, server, home

- **/graph** (my-games)
  - File: `autocoder/server/routers/features.py:313`
  - Tags: graph, features.py, autocoder, api_endpoint, server

- **/sessions/{project_name}** (my-games)
  - File: `autocoder/server/routers/expand_project.py:85`
  - Tags: name, sessions, expand_project.py, autocoder, project

### Component

- **Dashboard** (ai-dashboard)
  - File: `frontend/app/page.tsx:8`
  - Tags: component, page.tsx, frontend, dashboard

- **YouTubeBotPage** (ai-dashboard)
  - File: `frontend/app/youtube-bot/page.tsx:8`
  - Tags: frontend, bot, page, tube, component

- **Sidebar** (ai-dashboard)
  - File: `frontend/components/Sidebar.tsx:23`
  - Tags: frontend, sidebar, components, sidebar.tsx, component

- **AutomationDetailPage** (ai-dashboard)
  - File: `frontend/app/youtube-bot/[id]/page.tsx:12`
  - Tags: frontend, detail, automation, [id], page

- **VideosPage** (ai-dashboard)
  - File: `frontend/app/videos/page.tsx:7`
  - Tags: frontend, page, component, videos, page.tsx

- **RootLayout** (ai-dashboard)
  - File: `frontend/app/layout.tsx:13`
  - Tags: root, frontend, layout.tsx, layout, component

- **NewsPage** (ai-dashboard)
  - File: `frontend/app/news/page.tsx:7`
  - Tags: frontend, page, component, news, page.tsx

- **ProjectsPage** (ai-dashboard)
  - File: `frontend/app/projects/page.tsx:7`
  - Tags: frontend, projects, page, component, page.tsx

- **PromotionDialog** (my-games)
  - File: `apps/web/src/pages/ChessPawnPromotionTestPage.tsx:492`
  - Pawn on d7
  - Tags: dialog, chesspawnpromotiontestpage.tsx, pages, component, apps

- **CheckersBoardTestPage** (my-games)
  - File: `apps/web/src/pages/CheckersBoardTestPage.tsx:318`
  - ===========================================
  - Tags: checkersboardtestpage.tsx, pages, web, page, component

- **TurboSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:333`
  - Turbo - rocket character
  - Tags: components, component, turbo, autocoder, ui

- **RoomLobbyPage** (my-games)
  - File: `apps/web/src/pages/RoomLobbyPage.tsx:62`
  - Tags: roomlobbypage.tsx, pages, page, component, room

- **ChessMoveTestPage** (my-games)
  - File: `apps/web/src/pages/ChessMoveTestPage.tsx:339`
  - ===========================================
  - Tags: chess, pages, page, component, chessmovetestpage.tsx

- **ChessPreviewPage** (my-games)
  - File: `apps/web/src/pages/ChessPreviewPage.tsx:95`
  - Count pieces by color
  - Tags: chess, pages, page, component, preview

- **GamesPage** (my-games)
  - File: `apps/admin/src/pages/Games.tsx:10`
  - Tags: page, component, games, admin, games.tsx

- **ViewToggle** (my-games)
  - File: `autocoder/ui/src/components/ViewToggle.tsx:13`
  - Toggle button to switch between Kanban and Graph views
  - Tags: components, component, view, autocoder, toggle

- **UsersPage** (my-games)
  - File: `apps/admin/src/pages/Users.tsx:10`
  - Tags: page, component, users, admin, apps

- **AuthProvider** (my-games)
  - File: `apps/web/src/context/AuthContext.tsx:29`
  - Tags: context, component, auth, provider, authcontext.tsx

- **OptimizedBackground** (my-games)
  - File: `apps/web/src/components/OptimizedImage.tsx:267`
  - OptimizedBackground Component
  - Tags: components, optimized, component, background, apps

- **StreakResetTestPage** (my-games)
  - File: `apps/web/src/pages/StreakResetTestPage.tsx:28`
  - Use imported API_URL
  - Tags: reset, pages, page, component, streakresettestpage.tsx

- **TriviaGameTestPage** (my-games)
  - File: `apps/web/src/pages/TriviaGameTestPage.tsx:388`
  - ===========================================
  - Tags: game, triviagametestpage.tsx, pages, page, component

- **AgentLogModal** (my-games)
  - File: `autocoder/ui/src/components/AgentCard.tsx:156`
  - Log viewer modal component
  - Tags: log, components, agentcard.tsx, modal, component

- **ToastContainer** (my-games)
  - File: `apps/web/src/components/ToastContainer.tsx:61`
  - Tags: toastcontainer.tsx, components, toast, component, apps

- **TriviaBoard** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:1226`
  - Tags: pages, gameplaypage.tsx, component, board, trivia

- **InvitePage** (my-games)
  - File: `apps/web/src/pages/InvitePage.tsx:62`
  - Tags: invite, pages, page, component, invitepage.tsx

- **ProtectedRoute** (my-games)
  - File: `apps/web/src/components/ProtectedRoute.tsx:12`
  - ProtectedRoute component that redirects unauthenticated users to login.
  - Tags: components, protectedroute.tsx, component, route, protected

- **SkeletonTestPage** (my-games)
  - File: `apps/web/src/pages/SkeletonTestPage.tsx:17`
  - Tags: skeleton, pages, page, component, skeletontestpage.tsx

- **ReferralCommissionTestPage** (my-games)
  - File: `apps/web/src/pages/ReferralCommissionTestPage.tsx:43`
  - Tags: referral, pages, referralcommissiontestpage.tsx, page, component

- **NeonSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:376`
  - Neon - glowing character
  - Tags: components, neon, component, autocoder, ui

- **SuccessAlert** (my-games)
  - File: `apps/web/src/components/ui/SuccessAlert.tsx:7`
  - Tags: ui, components, component, alert, success

- **ChatPanel** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:1898`
  - Chat Panel Component
  - Tags: panel, pages, gameplaypage.tsx, component, apps

- **SetupWizard** (my-games)
  - File: `autocoder/ui/src/components/SetupWizard.tsx:9`
  - Tags: setupwizard.tsx, components, setup, component, autocoder

- **DevServerControl** (my-games)
  - File: `autocoder/ui/src/components/DevServerControl.tsx:62`
  - DevServerControl provides start/stop controls for a project's development server.
  - Tags: dev, control, components, devservercontrol.tsx, component

- **Layout** (my-games)
  - File: `apps/web/src/components/Layout.tsx:40`
  - Tags: layout.tsx, layout, components, component, apps

- **AssistantChat** (my-games)
  - File: `autocoder/ui/src/components/AssistantChat.tsx:26`
  - Tags: components, assistantchat.tsx, component, autocoder, ui

- **TypingIndicator** (my-games)
  - File: `autocoder/ui/src/components/TypingIndicator.tsx:8`
  - Typing Indicator Component
  - Tags: components, typingindicator.tsx, typing, indicator, component

- **OfflineIndicator** (my-games)
  - File: `apps/web/src/components/OfflineIndicator.tsx:13`
  - Displays an offline/online status indicator banner
  - Tags: components, offline, indicator, component, offlineindicator.tsx

- **HomePage** (my-games)
  - File: `apps/web/src/pages/HomePage.tsx:76`
  - Tags: homepage.tsx, pages, page, component, apps

- **EmailVerifyPage** (my-games)
  - File: `apps/web/src/pages/EmailVerifyPage.tsx:7`
  - Tags: pages, verify, email, page, component

- **App** (my-games)
  - File: `apps/web/src/App.tsx:61`
  - Development-only test pages
  - Tags: app, app.tsx, component, apps, web

- **MaintenancePage** (my-games)
  - File: `apps/web/src/pages/errors/MaintenancePage.tsx:3`
  - Tags: errors, pages, maintenancepage.tsx, page, component

- **Breadcrumbs** (my-games)
  - File: `apps/web/src/components/Breadcrumbs.tsx:95`
  - Fetch tournament details from API
  - Tags: breadcrumbs.tsx, components, component, breadcrumbs, apps

- **Modal** (my-games)
  - File: `apps/admin/src/components/ui/Modal.tsx:11`
  - Tags: ui, components, modal, component, modal.tsx

- **SparkSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:47`
  - Indigo
  - Tags: spark, components, component, autocoder, ui

- **AgentThought** (my-games)
  - File: `autocoder/ui/src/components/AgentThought.tsx:51`
  - Extracts the latest agent thought from logs
  - Tags: agentthought.tsx, components, component, autocoder, agent

- **LeaderboardRowSkeletonInline** (my-games)
  - File: `apps/web/src/components/Skeleton.tsx:411`
  - Inline skeleton for leaderboard rows (used within table)
  - Tags: inline, skeleton, components, leaderboard, component

- **HealthPage** (my-games)
  - File: `apps/admin/src/pages/Health.tsx:6`
  - Tags: health.tsx, page, component, health, admin

- **OptimizedImage** (my-games)
  - File: `apps/web/src/components/OptimizedImage.tsx:28`
  - e.g., "16/9", "4/3", "1/1"
  - Tags: image, optimized, components, component, apps

- **ToastTestPage** (my-games)
  - File: `apps/web/src/pages/ToastTestPage.tsx:3`
  - Tags: pages, toast, toasttestpage.tsx, page, component

- **TicTacToeBoard** (my-games)
  - File: `apps/web/src/pages/TicTacToeBoardTestPage.tsx:94`
  - ===========================================
  - Tags: tac, tictactoeboardtestpage.tsx, pages, component, board

- **FeatureCard** (my-games)
  - File: `autocoder/ui/src/components/FeatureCard.tsx:35`
  - Tags: feature, components, component, autocoder, ui

- **PWAInstallPrompt** (my-games)
  - File: `apps/web/src/components/PWAInstallPrompt.tsx:16`
  - Define the beforeinstallprompt event type
  - Tags: pwainstallprompt.tsx, components, install, component, apps

- **TableHeader** (my-games)
  - File: `apps/admin/src/components/ui/Table.tsx:20`
  - Tags: table.tsx, table, ui, components, component

- **SettingsPage** (my-games)
  - File: `apps/web/src/pages/SettingsPage.tsx:21`
  - Tags: pages, page, component, settingspage.tsx, settings

- **TransactionItemSkeleton** (my-games)
  - File: `apps/web/src/components/Skeleton.tsx:139`
  - Skeleton loader for wallet quick stats
  - Tags: skeleton, components, component, item, transaction

- **MatchReplayPage** (my-games)
  - File: `apps/web/src/pages/MatchReplayPage.tsx:67`
  - Tags: match, replay, pages, page, component

- **SubscriptionRenewalTestPage** (my-games)
  - File: `apps/web/src/pages/SubscriptionRenewalTestPage.tsx:37`
  - Tags: test, subscription, pages, page, subscriptionrenewaltestpage.tsx

- **PageLoader** (my-games)
  - File: `apps/web/src/App.tsx:47`
  - Error pages (loaded synchronously for faster error display)
  - Tags: app.tsx, page, component, loader, apps

- **TableCell** (my-games)
  - File: `apps/admin/src/components/ui/Table.tsx:47`
  - Tags: table.tsx, table, ui, components, component

- **AuditLogPage** (my-games)
  - File: `apps/admin/src/App.tsx:11`
  - Tags: log, app.tsx, page, component, admin

- **TicTacToeBoardTestPage** (my-games)
  - File: `apps/web/src/pages/TicTacToeBoardTestPage.tsx:271`
  - ===========================================
  - Tags: test, tac, tictactoeboardtestpage.tsx, pages, page

- **HostGameModal** (my-games)
  - File: `apps/web/src/pages/GameDetailPage.tsx:141`
  - Tags: game, host, pages, modal, component

- **GamePlayPage** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:2429`
  - Tags: game, pages, gameplaypage.tsx, page, component

- **HealthCard** (my-games)
  - File: `apps/admin/src/components/HealthCard.tsx:8`
  - Tags: components, component, health, admin, apps

- **MiseryCardComponent** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:1697`
  - Render a misery card
  - Tags: pages, gameplaypage.tsx, component, apps, web

- **AuditLog** (my-games)
  - File: `apps/admin/src/components/AuditLog.tsx:24`
  - Tags: log, components, audit, component, auditlog.tsx

- **PrivacyPolicyPage** (my-games)
  - File: `apps/web/src/pages/PrivacyPolicyPage.tsx:4`
  - Tags: privacy, pages, page, component, apps

- **ConnectionIndicator** (my-games)
  - File: `autocoder/ui/src/components/ExpandProjectChat.tsx:151`
  - Connection status indicator
  - Tags: expandprojectchat.tsx, ui, components, indicator, component

- **ChessCheckTestPage** (my-games)
  - File: `apps/web/src/pages/ChessCheckTestPage.tsx:403`
  - Tags: chess, pages, page, component, chesschecktestpage.tsx

- **NotificationsDropdown** (my-games)
  - File: `apps/web/src/components/NotificationsDropdown.tsx:20`
  - Tags: components, notificationsdropdown.tsx, component, notifications, apps

- **SpectatorViewPage** (my-games)
  - File: `apps/web/src/pages/SpectatorViewPage.tsx:421`
  - Tags: spectator, pages, page, component, view

- **GameCard** (my-games)
  - File: `apps/admin/src/components/GameCard.tsx:10`
  - Tags: game, components, gamecard.tsx, component, admin

- **BoltSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:255`
  - Bolt - lightning character
  - Tags: components, component, bolt, autocoder, ui

- **ReferralsPage** (my-games)
  - File: `apps/web/src/pages/ReferralsPage.tsx:163`
  - Tags: pages, page, component, referrals, referralspage.tsx

- **ChessBoard** (my-games)
  - File: `apps/web/src/pages/ChessPawnPromotionTestPage.tsx:545`
  - ===========================================
  - Tags: chesspawnpromotiontestpage.tsx, chess, pages, component, board

- **TerminalTabs** (my-games)
  - File: `autocoder/ui/src/components/TerminalTabs.tsx:28`
  - Tags: components, component, tabs, autocoder, terminal

- **ChatMessage** (my-games)
  - File: `autocoder/ui/src/components/ChatMessage.tsx:19`
  - Chat Message Component
  - Tags: components, chatmessage.tsx, component, message, autocoder

- **Layout** (my-games)
  - File: `apps/admin/src/components/Layout.tsx:8`
  - Tags: layout.tsx, layout, components, component, admin

- **DailyLoginBonusTestPage** (my-games)
  - File: `apps/web/src/pages/DailyLoginBonusTestPage.tsx:34`
  - Tags: login, test, pages, page, component

- **InfiniteScroll** (my-games)
  - File: `apps/web/src/components/ui/InfiniteScroll.tsx:13`
  - Tags: ui, components, scroll, component, infinite

- **TableRow** (my-games)
  - File: `apps/admin/src/components/ui/Table.tsx:32`
  - Tags: table.tsx, table, ui, components, component

- **AssistantFAB** (my-games)
  - File: `autocoder/ui/src/components/AssistantFAB.tsx:12`
  - Floating Action Button for toggling the Assistant panel
  - Tags: assistantfab.tsx, components, component, autocoder, ui

- **EmptyState** (my-games)
  - File: `apps/web/src/components/ui/EmptyState.tsx:12`
  - Tags: ui, emptystate.tsx, components, state, component

- **ActivityFeed** (my-games)
  - File: `autocoder/ui/src/components/ActivityFeed.tsx:30`
  - Tags: feed, activityfeed.tsx, components, component, activity

- **GameCatalogPage** (my-games)
  - File: `apps/web/src/pages/GameCatalogPage.tsx:111`
  - Tags: game, pages, page, component, catalog

- **DashboardPage** (my-games)
  - File: `apps/admin/src/pages/Dashboard.tsx:7`
  - Tags: page, component, admin, apps, dashboard

- **UnknownSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:480`
  - Unknown agent fallback - simple question mark icon
  - Tags: components, component, agentavatar.tsx, autocoder, ui

- **FeatureNode** (my-games)
  - File: `autocoder/ui/src/components/DependencyGraph.tsx:96`
  - Custom node component
  - Tags: feature, node, components, dependencygraph.tsx, component

- **UserProfilePage** (my-games)
  - File: `apps/web/src/pages/UserProfilePage.tsx:46`
  - Tags: userprofilepage.tsx, profile, pages, page, component

- **HootSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:121`
  - Tags: hoot, components, component, autocoder, ui

- **CheckersBoard** (my-games)
  - File: `apps/web/src/pages/CheckersMultiJumpTestPage.tsx:447`
  - ===========================================
  - Tags: pages, web, component, board, checkersmultijumptestpage.tsx

- **RegisterPage** (my-games)
  - File: `apps/web/src/pages/RegisterPage.tsx:22`
  - Tags: registerpage.tsx, pages, page, component, register

- **StorePage** (my-games)
  - File: `apps/web/src/pages/StorePage.tsx:63`
  - Tags: storepage.tsx, pages, page, store, component

- **TriviaScoringTestPage** (my-games)
  - File: `apps/web/src/pages/TriviaScoringTestPage.tsx:348`
  - ===========================================
  - Tags: triviascoringtestpage.tsx, pages, page, component, trivia

- **CardGameBoard** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:1433`
  - Card Game Board Component
  - Tags: game, pages, gameplaypage.tsx, component, board

- **GameCardSkeleton** (my-games)
  - File: `apps/web/src/components/Skeleton.tsx:59`
  - Skeleton loader for game cards in the catalog
  - Tags: game, skeleton, components, component, apps

- **ChessCastlingTestPage** (my-games)
  - File: `apps/web/src/pages/ChessCastlingTestPage.tsx:663`
  - ===========================================
  - Tags: chess, pages, page, component, castling

- **ShitHappensBoard** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:1648`
  - ===========================================
  - Tags: shit, happens, pages, gameplaypage.tsx, component

- **ByteSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:197`
  - Byte - data cube character
  - Tags: byte, components, component, autocoder, ui

- **WalletStatCardSkeleton** (my-games)
  - File: `apps/web/src/components/Skeleton.tsx:127`
  - Skeleton loader for wallet quick stats
  - Tags: skeleton, components, wallet, component, skeleton.tsx

- **TicTacToeBoard** (my-games)
  - File: `apps/web/src/pages/SpectatorViewPage.tsx:22`
  - Tic-Tac-Toe Board Component (view only)
  - Tags: tac, pages, component, board, toe

- **AgentMissionControl** (my-games)
  - File: `autocoder/ui/src/components/AgentMissionControl.tsx:23`
  - Tags: mission, control, components, component, autocoder

- **ChipSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:232`
  - Chip - circuit board character
  - Tags: chip, components, component, autocoder, ui

- **TipNotification** (my-games)
  - File: `apps/web/src/pages/SpectatorViewPage.tsx:254`
  - Tip notification component
  - Tags: pages, spectatorviewpage.tsx, component, notification, tip

- **ToastItem** (my-games)
  - File: `apps/web/src/components/ToastContainer.tsx:5`
  - Tags: toastcontainer.tsx, components, toast, component, item

- **PlacementSlot** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:1731`
  - Render slot between cards or at edges
  - Tags: pages, slot, gameplaypage.tsx, component, placement

- **CelebrationOverlay** (my-games)
  - File: `autocoder/ui/src/components/CelebrationOverlay.tsx:24`
  - Generate random confetti particles
  - Tags: celebrationoverlay.tsx, components, component, overlay, autocoder

- **AgentAvatar** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:579`
  - Tags: avatar, components, component, autocoder, agent

- **RateLimitPage** (my-games)
  - File: `apps/web/src/pages/errors/RateLimitPage.tsx:3`
  - Tags: errors, pages, page, component, limit

- **AssistantPanel** (my-games)
  - File: `autocoder/ui/src/components/AssistantPanel.tsx:45`
  - Invalid stored data, ignore
  - Tags: panel, components, component, assistantpanel.tsx, autocoder

- **ResetPasswordPage** (my-games)
  - File: `apps/web/src/pages/ResetPasswordPage.tsx:7`
  - Tags: reset, resetpasswordpage.tsx, password, pages, page

- **TermsOfServicePage** (my-games)
  - File: `apps/web/src/pages/TermsOfServicePage.tsx:4`
  - Tags: service, pages, terms, page, termsofservicepage.tsx

- **TournamentDetailPage** (my-games)
  - File: `apps/web/src/pages/TournamentDetailPage.tsx:119`
  - Tags: detail, pages, page, component, tournament

- **WalletPageSkeleton** (my-games)
  - File: `apps/web/src/components/Skeleton.tsx:293`
  - Full page skeleton for wallet
  - Tags: skeleton, components, page, wallet, component

- **CheckersBoard** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:1037`
  - Tags: pages, web, gameplaypage.tsx, component, board

- **NotFoundPage** (my-games)
  - File: `apps/web/src/pages/errors/NotFoundPage.tsx:4`
  - Tags: errors, pages, found, notfoundpage.tsx, not

- **FinancialsPage** (my-games)
  - File: `apps/admin/src/pages/Financials.tsx:8`
  - Tags: financials.tsx, page, component, financials, admin

- **ConnectionIndicator** (my-games)
  - File: `autocoder/ui/src/components/SpecCreationChat.tsx:192`
  - Connection status indicator
  - Tags: ui, components, speccreationchat.tsx, indicator, component

- **StreakMultiplierTestPage** (my-games)
  - File: `apps/web/src/pages/StreakMultiplierTestPage.tsx:38`
  - Tags: streakmultipliertestpage.tsx, pages, page, multiplier, component

- **SpecCreationChat** (my-games)
  - File: `autocoder/ui/src/components/SpecCreationChat.tsx:50`
  - Exit to project without starting agent
  - Tags: components, speccreationchat.tsx, component, creation, spec

- **TableBody** (my-games)
  - File: `apps/admin/src/components/ui/Table.tsx:26`
  - Tags: table.tsx, table, ui, components, component

- **TournamentChat** (my-games)
  - File: `apps/web/src/components/TournamentChat.tsx:11`
  - Tags: components, component, tournament, tournamentchat.tsx, apps

- **ExpandProjectChat** (my-games)
  - File: `autocoder/ui/src/components/ExpandProjectChat.tsx:25`
  - Image upload validation constants
  - Tags: expandprojectchat.tsx, components, component, expand, autocoder

- **GameCatalogSkeleton** (my-games)
  - File: `apps/web/src/components/Skeleton.tsx:261`
  - Full page skeleton for game catalog
  - Tags: game, skeleton, components, component, catalog

- **AgentControl** (my-games)
  - File: `autocoder/ui/src/components/AgentControl.tsx:18`
  - Tags: agentcontrol.tsx, control, components, component, autocoder

- **CheckersBoard** (my-games)
  - File: `apps/web/src/pages/CheckersBoardTestPage.tsx:73`
  - ===========================================
  - Tags: checkersboardtestpage.tsx, pages, web, component, board

- **Level3ReferralTestPage** (my-games)
  - File: `apps/web/src/pages/Level3ReferralTestPage.tsx:22`
  - Tags: level3referraltestpage.tsx, level, pages, page, component

- **ProfilePage** (my-games)
  - File: `apps/web/src/pages/ProfilePage.tsx:84`
  - Tags: profile, pages, profilepage.tsx, page, component

- **AdminDashboardPage** (my-games)
  - File: `apps/web/src/pages/AdminDashboardPage.tsx:250`
  - Tags: admindashboardpage.tsx, pages, page, component, admin

- **Skeleton** (my-games)
  - File: `apps/web/src/components/Skeleton.tsx:15`
  - Skeleton loader component for showing loading placeholders
  - Tags: skeleton, components, component, apps, skeleton.tsx

- **ChessPawnPromotionTestPage** (my-games)
  - File: `apps/web/src/pages/ChessPawnPromotionTestPage.tsx:671`
  - ===========================================
  - Tags: chesspawnpromotiontestpage.tsx, chess, pages, page, component

- **LoginPage** (my-games)
  - File: `apps/web/src/pages/LoginPage.tsx:15`
  - Use imported FRONTEND_URL
  - Tags: login, pages, page, component, apps

- **MatchHistoryPage** (my-games)
  - File: `apps/web/src/pages/MatchHistoryPage.tsx:59`
  - Tags: match, pages, history, page, component

- **KanbanColumn** (my-games)
  - File: `autocoder/ui/src/components/KanbanColumn.tsx:26`
  - Callback to start spec creation
  - Tags: column, components, component, kanbancolumn.tsx, autocoder

- **TableHeaderCell** (my-games)
  - File: `apps/admin/src/components/ui/Table.tsx:38`
  - Tags: table.tsx, table, ui, components, component

- **LoadingSpinner** (my-games)
  - File: `apps/admin/src/components/ui/LoadingSpinner.tsx:1`
  - Tags: spinner, ui, components, loadingspinner.tsx, component

- **ChessBoard** (my-games)
  - File: `apps/web/src/pages/ChessEnPassantTestPage.tsx:607`
  - Initially no en passant
  - Tags: chess, pages, chessenpassanttestpage.tsx, component, board

- **LeaderboardPageSkeleton** (my-games)
  - File: `apps/web/src/components/Skeleton.tsx:342`
  - Full page skeleton for leaderboard
  - Tags: skeleton, components, leaderboard, page, component

- **DebugLogViewer** (my-games)
  - File: `autocoder/ui/src/components/DebugLogViewer.tsx:39`
  - Tags: log, components, debug, debuglogviewer.tsx, component

- **EditFeatureForm** (my-games)
  - File: `autocoder/ui/src/components/EditFeatureForm.tsx:18`
  - Tags: form, feature, components, component, editfeatureform.tsx

- **ChessBoard** (my-games)
  - File: `apps/web/src/pages/ChessCastlingTestPage.tsx:537`
  - ===========================================
  - Tags: chess, pages, component, board, chesscastlingtestpage.tsx

- **SetupItem** (my-games)
  - File: `autocoder/ui/src/components/SetupWizard.tsx:134`
  - Tags: setupwizard.tsx, components, setup, component, item

- **NovaSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:215`
  - Nova - star character
  - Tags: components, component, autocoder, ui, nova

- **LeaderboardPage** (my-games)
  - File: `apps/web/src/pages/LeaderboardPage.tsx:72`
  - Tags: leaderboardpage.tsx, pages, leaderboard, page, component

- **ForgotPasswordPage** (my-games)
  - File: `apps/web/src/pages/ForgotPasswordPage.tsx:7`
  - Tags: forgotpasswordpage.tsx, forgot, password, pages, page

- **ChessMoveHistory** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:330`
  - Capture
  - Tags: chess, pages, history, gameplaypage.tsx, component

- **ChessBoard** (my-games)
  - File: `apps/web/src/pages/SpectatorViewPage.tsx:129`
  - File and rank labels
  - Tags: chess, pages, component, board, spectatorviewpage.tsx

- **CheckersMultiJumpTestPage** (my-games)
  - File: `apps/web/src/pages/CheckersMultiJumpTestPage.tsx:565`
  - ===========================================
  - Tags: pages, jump, web, page, component

- **TimeoutTestPage** (my-games)
  - File: `apps/web/src/pages/TimeoutTestPage.tsx:8`
  - Configurable timeout (in ms)
  - Tags: timeouttestpage.tsx, pages, page, component, timeout

- **WalletPage** (my-games)
  - File: `apps/web/src/pages/WalletPage.tsx:81`
  - Tags: pages, page, wallet, component, walletpage.tsx

- **WidgetSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:397`
  - Widget - UI component character
  - Tags: components, widget, component, autocoder, ui

- **DependencyGraph** (my-games)
  - File: `autocoder/ui/src/components/DependencyGraph.tsx:416`
  - Wrapper component with error boundary for stability
  - Tags: graph, components, dependencygraph.tsx, component, autocoder

- **HostBonusTestPage** (my-games)
  - File: `apps/web/src/pages/HostBonusTestPage.tsx:66`
  - Tags: hostbonustestpage.tsx, host, pages, page, component

- **CheckersKingPromotionTestPage** (my-games)
  - File: `apps/web/src/pages/CheckersKingPromotionTestPage.tsx:392`
  - No promotion expected
  - Tags: checkerskingpromotiontestpage.tsx, pages, web, page, component

- **MilestonesPage** (my-games)
  - File: `apps/web/src/pages/MilestonesPage.tsx:79`
  - Tags: pages, page, milestones, component, apps

- **BlipSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:356`
  - Blip - radar dot character
  - Tags: blip, components, component, autocoder, ui

- **MetricCard** (my-games)
  - File: `apps/admin/src/components/MetricCard.tsx:8`
  - Tags: components, metriccard.tsx, component, admin, metric

- **ChessBoard** (my-games)
  - File: `games/chess/client/ChessBoard.tsx:380`
  - ===========================================
  - Tags: chess, component, board, client, games

- **ToastProvider** (my-games)
  - File: `apps/web/src/context/ToastContext.tsx:21`
  - Tags: context, toastcontext.tsx, toast, component, provider

- **LoadingSpinner** (my-games)
  - File: `apps/web/src/components/ui/LoadingSpinner.tsx:6`
  - Tags: spinner, ui, components, loadingspinner.tsx, component

- **Table** (my-games)
  - File: `apps/admin/src/components/ui/Table.tsx:7`
  - Tags: table.tsx, table, ui, components, component

- **ZippySVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:419`
  - Zippy - fast bunny-like character
  - Tags: zippy, components, component, autocoder, ui

- **VerificationChecklist** (my-games)
  - File: `apps/web/src/pages/TicTacToeBoardTestPage.tsx:192`
  - ===========================================
  - Tags: tictactoeboardtestpage.tsx, pages, web, component, checklist

- **SubscriptionsPage** (my-games)
  - File: `apps/web/src/pages/SubscriptionsPage.tsx:98`
  - Tags: subscriptionspage.tsx, pages, page, subscriptions, component

- **GameDetailPage** (my-games)
  - File: `apps/web/src/pages/GameDetailPage.tsx:486`
  - Tags: game, detail, pages, page, component

- **OctoSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:99`
  - Tags: components, component, autocoder, ui, octo

- **OrchestratorStatusCard** (my-games)
  - File: `autocoder/ui/src/components/OrchestratorStatusCard.tsx:61`
  - Format timestamp to relative time
  - Tags: ui, components, component, autocoder, orchestratorstatuscard.tsx

- **OrchestratorAvatar** (my-games)
  - File: `autocoder/ui/src/components/OrchestratorAvatar.tsx:151`
  - Tags: avatar, components, component, orchestratoravatar.tsx, autocoder

- **ProjectSelector** (my-games)
  - File: `autocoder/ui/src/components/ProjectSelector.tsx:16`
  - Tags: projectselector.tsx, selector, components, component, autocoder

- **XpWinTestPage** (my-games)
  - File: `apps/web/src/pages/XpWinTestPage.tsx:26`
  - Tags: win, pages, page, component, apps

- **MatchPage** (my-games)
  - File: `apps/web/src/pages/MatchPage.tsx:74`
  - Tags: matchpage.tsx, match, pages, page, component

- **DependencyGraphInner** (my-games)
  - File: `autocoder/ui/src/components/DependencyGraph.tsx:209`
  - Tags: graph, components, dependencygraph.tsx, component, inner

- **DependencyBadge** (my-games)
  - File: `autocoder/ui/src/components/DependencyBadge.tsx:17`
  - Badge component showing dependency status for a feature.
  - Tags: badge, components, dependencybadge.tsx, component, autocoder

- **CreditDeductionTestPage** (my-games)
  - File: `apps/web/src/pages/CreditDeductionTestPage.tsx:26`
  - Tags: pages, credit, page, creditdeductiontestpage.tsx, component

- **GoogleAuthCallbackPage** (my-games)
  - File: `apps/web/src/pages/GoogleAuthCallbackPage.tsx:7`
  - Tags: google, pages, googleauthcallbackpage.tsx, page, component

- **TicTacToeBoard** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:32`
  - Tic-Tac-Toe Board Component
  - Tags: tac, pages, gameplaypage.tsx, component, board

- **BuzzSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:147`
  - Tags: components, component, buzz, autocoder, ui

- **QuirkSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:442`
  - Quirk - question mark character
  - Tags: components, quirk, component, autocoder, ui

- **NewProjectModal** (my-games)
  - File: `autocoder/ui/src/components/NewProjectModal.tsx:31`
  - Tags: components, modal, component, newprojectmodal.tsx, autocoder

- **KeyboardShortcutsHelp** (my-games)
  - File: `autocoder/ui/src/components/KeyboardShortcutsHelp.tsx:26`
  - Tags: shortcuts, keyboard, components, component, autocoder

- **ProgressBar** (my-games)
  - File: `apps/web/src/components/ui/ProgressBar.tsx:9`
  - Tags: ui, components, component, progress, bar

- **ZapSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:291`
  - Zap - electric orb
  - Tags: components, component, autocoder, ui, zap

- **PlayingCard** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:1373`
  - Card suit symbols and colors
  - Tags: playing, pages, gameplaypage.tsx, component, apps

- **ServerErrorPage** (my-games)
  - File: `apps/web/src/pages/errors/ServerErrorPage.tsx:4`
  - Tags: errors, pages, web, page, component

- **LeaderboardRowSkeleton** (my-games)
  - File: `apps/web/src/components/Skeleton.tsx:160`
  - Skeleton loader for leaderboard rows
  - Tags: skeleton, components, leaderboard, component, apps

- **ChessBoard** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:797`
  - Chess Board Component
  - Tags: chess, pages, gameplaypage.tsx, component, board

- **ConfirmDialog** (my-games)
  - File: `apps/web/src/components/ui/ConfirmDialog.tsx:12`
  - Tags: confirm, dialog, ui, components, confirmdialog.tsx

- **TournamentPrizeTestPage** (my-games)
  - File: `apps/web/src/pages/TournamentPrizeTestPage.tsx:62`
  - Tags: tournamentprizetestpage.tsx, pages, page, component, tournament

- **TriviaCard** (my-games)
  - File: `apps/web/src/pages/TriviaGameTestPage.tsx:279`
  - Tags: triviagametestpage.tsx, pages, component, trivia, apps

- **PlayerInfo** (my-games)
  - File: `apps/web/src/pages/TicTacToeBoardTestPage.tsx:156`
  - ===========================================
  - Tags: tictactoeboardtestpage.tsx, pages, component, info, player

- **ProgressDashboard** (my-games)
  - File: `autocoder/ui/src/components/ProgressDashboard.tsx:10`
  - Tags: components, component, progress, autocoder, progressdashboard.tsx

- **MilestonesPageSkeleton** (my-games)
  - File: `apps/web/src/components/Skeleton.tsx:447`
  - Full page skeleton for milestones
  - Tags: skeleton, components, page, milestones, component

- **OptimizedAvatar** (my-games)
  - File: `apps/web/src/components/OptimizedImage.tsx:163`
  - OptimizedAvatar Component
  - Tags: avatar, components, optimized, component, apps

- **UITestPage** (my-games)
  - File: `apps/web/src/pages/UITestPage.tsx:12`
  - Tags: pages, page, component, uitestpage.tsx, apps

- **DependencyIndicator** (my-games)
  - File: `autocoder/ui/src/components/DependencyBadge.tsx:94`
  - Small inline indicator for dependency status
  - Tags: components, dependencybadge.tsx, indicator, component, autocoder

- **Scoreboard** (my-games)
  - File: `apps/web/src/pages/TriviaGameTestPage.tsx:353`
  - Tags: triviagametestpage.tsx, pages, scoreboard, component, apps

- **UnsavedChangesDialog** (my-games)
  - File: `apps/web/src/components/UnsavedChangesDialog.tsx:18`
  - Dialog component that warns users about unsaved changes
  - Tags: dialog, changes, components, web, component

- **FolderBrowser** (my-games)
  - File: `autocoder/ui/src/components/FolderBrowser.tsx:29`
  - Tags: ui, components, component, autocoder, folderbrowser.tsx

- **FizzSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:71`
  - Tags: fizz, components, component, autocoder, ui

- **SettingsModal** (my-games)
  - File: `autocoder/ui/src/components/SettingsModal.tsx:9`
  - Tags: components, modal, component, autocoder, settings

- **VerificationItem** (my-games)
  - File: `apps/web/src/pages/CheckersMultiJumpTestPage.tsx:935`
  - Verification item component
  - Tags: pages, web, component, item, checkersmultijumptestpage.tsx

- **ChessClock** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:729`
  - Format time for chess clock display (mm:ss)
  - Tags: chess, clock, pages, gameplaypage.tsx, component

- **ProfileSkeleton** (my-games)
  - File: `apps/web/src/components/Skeleton.tsx:177`
  - Skeleton loader for profile page
  - Tags: skeleton, profile, components, component, apps

- **ScheduleModal** (my-games)
  - File: `autocoder/ui/src/components/ScheduleModal.tsx:33`
  - Tags: components, schedule, modal, schedulemodal.tsx, component

- **TournamentCardSkeleton** (my-games)
  - File: `apps/web/src/components/Skeleton.tsx:235`
  - Skeleton loader for tournament cards
  - Tags: skeleton, components, component, tournament, apps

- **FeedbackPage** (my-games)
  - File: `apps/web/src/pages/FeedbackPage.tsx:85`
  - Tags: pages, feedback, feedbackpage.tsx, page, component

- **TournamentsPage** (my-games)
  - File: `apps/web/src/pages/TournamentsPage.tsx:101`
  - Tags: tournamentspage.tsx, tournaments, pages, page, component

- **MilestoneCardSkeleton** (my-games)
  - File: `apps/web/src/components/Skeleton.tsx:212`
  - Skeleton loader for milestone cards
  - Tags: skeleton, milestone, components, component, apps

- **FluxSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:461`
  - Flux - flowing wave character
  - Tags: components, component, autocoder, ui, flux

- **TipModal** (my-games)
  - File: `apps/web/src/pages/SpectatorViewPage.tsx:285`
  - Tip modal component
  - Tags: pages, spectatorviewpage.tsx, modal, component, tip

- **TriviaCard** (my-games)
  - File: `apps/web/src/pages/TriviaScoringTestPage.tsx:223`
  - Tags: triviascoringtestpage.tsx, pages, component, trivia, apps

- **ConfirmDialog** (my-games)
  - File: `autocoder/ui/src/components/ConfirmDialog.tsx:23`
  - Tags: confirm, dialog, components, confirmdialog.tsx, component

- **AddFeatureForm** (my-games)
  - File: `autocoder/ui/src/components/AddFeatureForm.tsx:15`
  - Tags: form, feature, components, component, autocoder

- **QuestionOptions** (my-games)
  - File: `autocoder/ui/src/components/QuestionOptions.tsx:18`
  - Question Options Component
  - Tags: components, questionoptions.tsx, question, component, autocoder

- **TournamentsPage** (my-games)
  - File: `apps/admin/src/pages/Tournaments.tsx:9`
  - Tags: tournaments, page, tournaments.tsx, component, admin

- **WalletBalanceCardSkeleton** (my-games)
  - File: `apps/web/src/components/Skeleton.tsx:93`
  - Skeleton loader for wallet balance cards
  - Tags: skeleton, components, wallet, component, balance

- **GizmoSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:311`
  - Gizmo - gear character
  - Tags: gizmo, components, component, autocoder, ui

- **AgentCard** (my-games)
  - File: `autocoder/ui/src/components/AgentCard.tsx:70`
  - Get agent type badge config
  - Tags: components, agentcard.tsx, component, autocoder, agent

- **KanbanBoard** (my-games)
  - File: `autocoder/ui/src/components/KanbanBoard.tsx:14`
  - Callback to start spec creation
  - Tags: components, kanbanboard.tsx, component, board, autocoder

- **MaestroSVG** (my-games)
  - File: `autocoder/ui/src/components/OrchestratorAvatar.tsx:24`
  - Maestro color scheme - Deep violet
  - Tags: maestro, components, component, orchestratoravatar.tsx, autocoder

- **Terminal** (my-games)
  - File: `autocoder/ui/src/components/Terminal.tsx:73`
  - Reconnection configuration
  - Tags: components, component, autocoder, terminal.tsx, terminal

- **ChessEnPassantTestPage** (my-games)
  - File: `apps/web/src/pages/ChessEnPassantTestPage.tsx:736`
  - ===========================================
  - Tags: chess, passant, pages, chessenpassanttestpage.tsx, page

- **PixelSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:176`
  - Pixel - cute pixel art style character
  - Tags: components, component, autocoder, ui, agentavatar.tsx

- **FeatureModal** (my-games)
  - File: `autocoder/ui/src/components/FeatureModal.tsx:33`
  - pink (accent)
  - Tags: feature, components, modal, component, featuremodal.tsx

- **ExpandProjectModal** (my-games)
  - File: `autocoder/ui/src/components/ExpandProjectModal.tsx:17`
  - Expand Project Modal
  - Tags: expandprojectmodal.tsx, components, modal, component, expand

- **Level2ReferralTestPage** (my-games)
  - File: `apps/web/src/pages/Level2ReferralTestPage.tsx:36`
  - Tags: level, pages, page, component, level2referraltestpage.tsx

- **ErrorAlert** (my-games)
  - File: `apps/web/src/components/ui/ErrorAlert.tsx:7`
  - Tags: ui, components, component, alert, erroralert.tsx

- **App** (my-games)
  - File: `autocoder/ui/src/App.tsx:35`
  - Tags: app, app.tsx, component, autocoder, ui

- **StatusIcon** (my-games)
  - File: `autocoder/ui/src/components/DependencyGraph.tsx:104`
  - Custom node component
  - Tags: ui, icon, components, dependencygraph.tsx, component

- **ChessCheckmateTestPage** (my-games)
  - File: `apps/web/src/pages/ChessCheckmateTestPage.tsx:611`
  - Tags: chess, pages, checkmate, page, component

- **ConversationHistory** (my-games)
  - File: `autocoder/ui/src/components/ConversationHistory.tsx:45`
  - Tags: conversationhistory.tsx, components, history, conversation, component

- **CheckersBoard** (my-games)
  - File: `apps/web/src/pages/CheckersKingPromotionTestPage.tsx:210`
  - ===========================================
  - Tags: checkerskingpromotiontestpage.tsx, pages, web, component, board

- **NotFoundPage** (my-games)
  - File: `apps/web/src/pages/NotFoundPage.tsx:4`
  - Tags: pages, found, notfoundpage.tsx, not, page

- **DashSVG** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:271`
  - Dash - speedy character
  - Tags: components, component, dash, autocoder, ui

- **Scoreboard** (my-games)
  - File: `apps/web/src/pages/TriviaScoringTestPage.tsx:300`
  - Tags: triviascoringtestpage.tsx, pages, scoreboard, component, apps

- **App** (my-games)
  - File: `apps/admin/src/App.tsx:20`
  - Tags: app, app.tsx, component, admin, apps

### Hook

- **useUpdateSettings** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:263`
  - Cache for 5 minutes - models don't change often
  - Tags: hook, update, useprojects.ts, autocoder, hooks

- **useCreateFeature** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:64`
  - ============================================================================
  - Tags: feature, hook, useprojects.ts, create, autocoder

- **useAuthStore** (my-games)
  - File: `apps/web/src/stores/authStore.ts:4`
  - Simple auth store that reads from localStorage
  - Tags: hook, store, authstore.ts, auth, apps

- **useAvailableModels** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:243`
  - Default models response for placeholder (until API responds)
  - Tags: hook, useprojects.ts, models, autocoder, hooks

- **useHealthCheck** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:185`
  - ============================================================================
  - Tags: hook, useprojects.ts, check, health, autocoder

- **useSchedules** (my-games)
  - File: `autocoder/ui/src/hooks/useSchedules.ts:16`
  - React Query hooks for schedule data
  - Tags: hook, useschedules.ts, autocoder, schedules, hooks

- **useCreateProject** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:28`
  - ============================================================================
  - Tags: hook, useprojects.ts, create, autocoder, project

- **useSettings** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:253`
  - Cache for 5 minutes - models don't change often
  - Tags: hook, useprojects.ts, autocoder, hooks, settings

- **useProjectWebSocket** (my-games)
  - File: `autocoder/ui/src/hooks/useWebSocket.ts:61`
  - Celebration queue to handle rapid successes without race conditions
  - Tags: usewebsocket.ts, hook, socket, autocoder, project

- **useProject** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:20`
  - ============================================================================
  - Tags: hook, useprojects.ts, autocoder, project, hooks

- **useAssistantChat** (my-games)
  - File: `autocoder/ui/src/hooks/useAssistantChat.ts:30`
  - Tags: hook, use, autocoder, hooks, ui

- **useI18n** (my-games)
  - File: `apps/web/src/hooks/useI18n.ts:11`
  - Hook for internationalization/localization
  - Tags: usei18n.ts, hook, hooks, apps, web

- **useListDirectory** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:197`
  - Cache for 1 minute
  - Tags: hook, useprojects.ts, list, autocoder, hooks

- **useStopDevServer** (my-games)
  - File: `autocoder/ui/src/components/DevServerControl.tsx:32`
  - Internal hook to stop the dev server for a project.
  - Tags: dev, hook, components, devservercontrol.tsx, stop

- **useSpectatorSocket** (my-games)
  - File: `apps/web/src/hooks/useSpectatorSocket.ts:64`
  - Tags: hook, spectator, socket, hooks, apps

- **useDeleteConversation** (my-games)
  - File: `autocoder/ui/src/hooks/useConversations.ts:35`
  - Get a single conversation with all its messages
  - Tags: delete, hook, conversation, autocoder, hooks

- **useUpdateSchedule** (my-games)
  - File: `autocoder/ui/src/hooks/useSchedules.ts:53`
  - Hook to create a new schedule.
  - Tags: hook, useschedules.ts, update, schedule, autocoder

- **useNextScheduledRun** (my-games)
  - File: `autocoder/ui/src/hooks/useSchedules.ts:105`
  - Hook to fetch the next scheduled run for a project.
  - Tags: hook, useschedules.ts, scheduled, next, autocoder

- **useSetupStatus** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:177`
  - ============================================================================
  - Tags: hook, useprojects.ts, ui, setup, autocoder

- **usePresence** (my-games)
  - File: `apps/web/src/hooks/usePresence.ts:11`
  - Presence hook for tracking user online status and receiving friend online notifications
  - Tags: hook, usepresence.ts, presence, hooks, apps

- **useAuth** (my-games)
  - File: `apps/web/src/context/AuthContext.tsx:156`
  - Enable presence tracking when authenticated
  - Tags: context, hook, auth, authcontext.tsx, apps

- **useTournamentChat** (my-games)
  - File: `apps/web/src/hooks/useTournamentChat.ts:29`
  - Tags: hook, usetournamentchat.ts, tournament, hooks, apps

- **useValidatePath** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:217`
  - Invalidate parent directory listing
  - Tags: validate, hook, useprojects.ts, path, autocoder

- **useSpecChat** (my-games)
  - File: `autocoder/ui/src/hooks/useSpecChat.ts:34`
  - Tags: hook, usespecchat.ts, spec, autocoder, hooks

- **useResumeAgent** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:162`
  - Invalidate schedule status to reflect manual stop override
  - Tags: resume, hook, useprojects.ts, autocoder, agent

- **useDeleteFeature** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:75`
  - Refetch every 5 seconds for real-time updates
  - Tags: delete, hook, feature, useprojects.ts, autocoder

- **useSound** (my-games)
  - File: `apps/web/src/hooks/useSound.ts:171`
  - Hook for playing sound effects based on user settings.
  - Tags: hook, usesound.ts, hooks, apps, web

- **useCreateSchedule** (my-games)
  - File: `autocoder/ui/src/hooks/useSchedules.ts:38`
  - Hook to fetch a single schedule.
  - Tags: hook, useschedules.ts, schedule, create, autocoder

- **useConversations** (my-games)
  - File: `autocoder/ui/src/hooks/useConversations.ts:11`
  - React Query hooks for assistant conversation management
  - Tags: hook, autocoder, hooks, useconversations.ts, ui

- **useCelebration** (my-games)
  - File: `autocoder/ui/src/hooks/useCelebration.ts:148`
  - Check if all features are complete (none pending or in progress, at least one done)
  - Tags: usecelebration.ts, hook, autocoder, hooks, celebration

- **useAgentStatus** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:113`
  - ============================================================================
  - Tags: hook, useprojects.ts, ui, autocoder, agent

- **useCreateDirectory** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:204`
  - ============================================================================
  - Tags: hook, useprojects.ts, create, autocoder, hooks

- **useSkipFeature** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:86`
  - Tags: hook, feature, useprojects.ts, autocoder, hooks

- **useStartAgent** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:122`
  - ============================================================================
  - Tags: hook, useprojects.ts, ui, autocoder, agent

- **useExpandChat** (my-games)
  - File: `autocoder/ui/src/hooks/useExpandChat.ts:38`
  - Tags: hook, expand, autocoder, hooks, useexpandchat.ts

- **useToast** (my-games)
  - File: `apps/web/src/context/ToastContext.tsx:56`
  - Tags: context, hook, toastcontext.tsx, toast, apps

- **usePauseAgent** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:151`
  - Invalidate schedule status to reflect manual stop override
  - Tags: hook, useprojects.ts, pause, autocoder, agent

- **useProjects** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:13`
  - React Query hooks for project data
  - Tags: projects, hook, useprojects.ts, autocoder, hooks

- **useUnsavedChanges** (my-games)
  - File: `apps/web/src/hooks/useUnsavedChanges.ts:32`
  - Hook to warn users about unsaved changes when navigating away from a form
  - Tags: hook, changes, web, useunsavedchanges.ts, hooks

- **useFeatures** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:55`
  - ============================================================================
  - Tags: hook, useprojects.ts, features, autocoder, hooks

- **useDeleteSchedule** (my-games)
  - File: `autocoder/ui/src/hooks/useSchedules.ts:69`
  - Hook to delete a schedule.
  - Tags: delete, hook, useschedules.ts, schedule, autocoder

- **useConversation** (my-games)
  - File: `autocoder/ui/src/hooks/useConversations.ts:23`
  - List all conversations for a project
  - Tags: hook, conversation, autocoder, hooks, useconversations.ts

- **useStartDevServer** (my-games)
  - File: `autocoder/ui/src/components/DevServerControl.tsx:17`
  - Internal hook to start the dev server for a project.
  - Tags: dev, hook, ui, components, devservercontrol.tsx

- **useToggleSchedule** (my-games)
  - File: `autocoder/ui/src/hooks/useSchedules.ts:84`
  - Hook to delete a schedule.
  - Tags: hook, useschedules.ts, schedule, autocoder, hooks

- **useStopAgent** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:138`
  - Poll every 3 seconds
  - Tags: hook, useprojects.ts, stop, autocoder, agent

- **usePWAInstall** (my-games)
  - File: `apps/web/src/components/PWAInstallPrompt.tsx:177`
  - Hook for programmatic install prompt
  - Tags: pwainstallprompt.tsx, hook, components, install, apps

- **useMatchSocket** (my-games)
  - File: `apps/web/src/hooks/useSocket.ts:122`
  - Tags: hook, match, socket, hooks, usesocket.ts

- **useFeatureSound** (my-games)
  - File: `autocoder/ui/src/hooks/useFeatureSound.ts:69`
  - Audio not supported or blocked, fail silently
  - Tags: hook, feature, usefeaturesound.ts, autocoder, hooks

- **useOnlineStatus** (my-games)
  - File: `apps/web/src/hooks/useOnlineStatus.ts:13`
  - Hook to track online/offline status
  - Tags: hook, hooks, useonlinestatus.ts, status, web

- **useDeleteProject** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:40`
  - Tags: delete, hook, useprojects.ts, autocoder, project

- **useUpdateFeature** (my-games)
  - File: `autocoder/ui/src/hooks/useProjects.ts:97`
  - Tags: feature, hook, update, useprojects.ts, autocoder

- **useSchedule** (my-games)
  - File: `autocoder/ui/src/hooks/useSchedules.ts:27`
  - Hook to fetch all schedules for a project.
  - Tags: hook, useschedules.ts, schedule, autocoder, hooks

### Middleware

- **metricsMiddleware** (my-games)
  - File: `apps/api/src/middleware/metricsMiddleware.ts:4`
  - Tags: metricsmiddleware.ts, api, metrics, apps, middleware

- **http** (my-games)
  - File: `autocoder/server/main.py:110`
  - Vite dev server
  - Tags: main.py, autocoder, http, middleware, server

### Schema

- **ScraperLog** (ai-dashboard)
  - File: `backend/database/models.py:154`
  - Status
  - Tags: log, backend, models.py, scraper, schema

- **AutomationCreate** (ai-dashboard)
  - File: `backend/main.py:120`
  - Tags: backend, automation, main.py, create, schema

- **YouTubeAutomation** (ai-dashboard)
  - File: `backend/database/models.py:116`
  - Calculate trending score based on stars growth and activity
  - Tags: backend, automation, database, tube, models.py

- **AutomationResponse** (ai-dashboard)
  - File: `backend/main.py:134`
  - Tags: response, backend, automation, main.py, schema

- **VideoResponse** (ai-dashboard)
  - File: `backend/main.py:71`
  - Create FastAPI app
  - Tags: response, backend, main.py, schema, video

- **ProjectResponse** (ai-dashboard)
  - File: `backend/main.py:102`
  - Tags: response, backend, main.py, project, schema

- **AutomationUpdate** (ai-dashboard)
  - File: `backend/main.py:126`
  - Tags: update, backend, automation, main.py, schema

- **YouTubeVideo** (ai-dashboard)
  - File: `backend/database/models.py:10`
  - AI Dashboard - Database Models
  - Tags: backend, database, tube, models.py, video

- **GitHubProject** (ai-dashboard)
  - File: `backend/database/models.py:74`
  - TechCrunch, Verge, HackerNews, etc.
  - Tags: backend, git, models.py, project, schema

- **AINews** (ai-dashboard)
  - File: `backend/database/models.py:55`
  - Normalize values (log scale to handle large numbers)
  - Tags: backend, models.py, news, schema, database

- **NewsResponse** (ai-dashboard)
  - File: `backend/main.py:86`
  - ============ Pydantic Models ============
  - Tags: response, backend, main.py, news, schema

- **FeatureListResponse** (my-games)
  - File: `autocoder/server/schemas.py:114`
  - Response schema for a feature.
  - Tags: response, feature, schemas.py, list, autocoder

- **AgentStatus** (my-games)
  - File: `autocoder/server/schemas.py:201`
  - Validate testing_agent_ratio is between 0 and 3.
  - Tags: schemas.py, autocoder, agent, schema, status

- **ExpandSessionStatus** (my-games)
  - File: `autocoder/server/routers/expand_project.py:52`
  - Get project path from registry.
  - Tags: expand_project.py, session, expand, autocoder, schema

- **ImageAttachment** (my-games)
  - File: `autocoder/server/schemas.py:298`
  - One of AGENT_MASCOTS
  - Tags: attachment, schemas.py, image, autocoder, schema

- **PieceType** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:4003`
  - Real initialization with shuffling happens in rooms.ts when match is created
  - Tags: api, socket, piece, matchhandler.ts, schema

- **PieceType** (my-games)
  - File: `games/chess/ai/index.ts:10`
  - Chess AI Engine
  - Tags: chess, games, piece, schema, type

- **ProjectDetail** (my-games)
  - File: `autocoder/server/schemas.py:50`
  - Project statistics.
  - Tags: detail, schemas.py, autocoder, project, schema

- **MilestoneType** (my-games)
  - File: `packages/shared/src/types/index.ts:283`
  - ===========================================
  - Tags: types, milestone, packages, shared, schema

- **FeatureCreate** (my-games)
  - File: `autocoder/server/schemas.py:86`
  - Base feature attributes.
  - Tags: feature, schemas.py, create, autocoder, schema

- **verifyEmailSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:56`
  - Tags: api, verify, email, validators.ts, schema

- **SettingsUpdate** (my-games)
  - File: `autocoder/server/schemas.py:394`
  - Information about an available model.
  - Tags: update, schemas.py, autocoder, schema, settings

- **AgentStartRequest** (my-games)
  - File: `autocoder/server/schemas.py:168`
  - Response for dependency graph visualization.
  - Tags: schemas.py, request, autocoder, agent, schema

- **SpecialMoveType** (my-games)
  - File: `apps/api/src/game-engines/chess/types.ts:43`
  - Piece on the board
  - Tags: api, special, chess, schema, game-engines

- **createTournamentSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:152`
  - ============================================
  - Tags: api, create, validators.ts, tournament, schema

- **RenameTerminalRequest** (my-games)
  - File: `autocoder/server/routers/terminal.py:92`
  - Validate terminal ID format.

    Args:
        terminal_id: The terminal ID to validate

    Return

  - Tags: rename, terminal.py, request, autocoder, schema

- **registerSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:12`
  - Centralized input validation schemas
  - Tags: api, validators.ts, register, schema, apps

- **banUserSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:192`
  - ============================================
  - Tags: api, ban, validators.ts, user, schema

- **ProjectStats** (my-games)
  - File: `autocoder/server/schemas.py:34`
  - Request schema for creating a new project.
  - Tags: schemas.py, stats, autocoder, project, schema

- **PieceType** (my-games)
  - File: `apps/web/src/pages/ChessPawnPromotionTestPage.tsx:7`
  - ===========================================
  - Tags: chesspawnpromotiontestpage.tsx, pages, piece, schema, type

- **DevServerConfigResponse** (my-games)
  - File: `autocoder/server/schemas.py:441`
  - Current dev server status.
  - Tags: response, config, dev, schemas.py, autocoder

- **ConversationDetail** (my-games)
  - File: `autocoder/server/routers/assistant_chat.py:77`
  - Summary of a conversation.
  - Tags: detail, conversation, autocoder, schema, server

- **createRoomSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:91`
  - Game-specific move data
  - Tags: api, create, validators.ts, room, schema

- **FeatureBulkCreate** (my-games)
  - File: `autocoder/server/schemas.py:121`
  - id: int

    priority: int
    passes: bool
    in_progress: bool
    blocked: bool = False  # Comput

  - Tags: feature, bulk, schemas.py, create, autocoder

- **WSLogMessage** (my-games)
  - File: `autocoder/server/schemas.py:252`
  - WebSocket message for progress updates.
  - Tags: log, schemas.py, message, autocoder, schema

- **ScheduleListResponse** (my-games)
  - File: `autocoder/server/schemas.py:556`
  - Response schema for a schedule.
  - Tags: response, schemas.py, schedule, list, autocoder

- **FeatureCreateItem** (my-games)
  - File: `autocoder/mcp_server/feature_mcp.py:82`
  - Input for clearing in-progress status.
  - Tags: mcp_server, feature, create, feature_mcp.py, item

- **PieceType** (my-games)
  - File: `games/chess/server/index.ts:10`
  - Chess Server-Side Game Engine
  - Tags: chess, games, piece, schema, type

- **ConversationMessage** (my-games)
  - File: `autocoder/server/services/assistant_database.py:44`
  - Optional title, derived from first message
  - Tags: services, conversation, assistant_database.py, message, autocoder

- **PieceType** (my-games)
  - File: `apps/web/src/pages/ChessCastlingTestPage.tsx:7`
  - ===========================================
  - Tags: pages, piece, chesscastlingtestpage.tsx, schema, type

- **Settings** (my-games)
  - File: `autocoder/registry.py:90`
  - SQLAlchemy model for registered projects.
  - Tags: settings, registry.py, autocoder, schema

- **ScheduleResponse** (my-games)
  - File: `autocoder/server/schemas.py:538`
  - Validate model is in the allowed list.
  - Tags: response, schemas.py, schedule, autocoder, schema

- **joinAsGuestSchema** (my-games)
  - File: `apps/api/src/routes/invites.ts:26`
  - Helper function to check if a user is blocked by another user
  - Tags: api, guest, invites.ts, schema, join

- **FeatureUpdate** (my-games)
  - File: `autocoder/server/schemas.py:91`
  - Base feature attributes.
  - Tags: feature, update, schemas.py, autocoder, schema

- **updateProfileSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:127`
  - ============================================
  - Tags: api, update, profile, validators.ts, schema

- **ProjectSummary** (my-games)
  - File: `autocoder/server/schemas.py:42`
  - Request schema for creating a new project.
  - Tags: summary, schemas.py, autocoder, project, schema

- **CreateDirectoryRequest** (my-games)
  - File: `autocoder/server/schemas.py:361`
  - Response for directory listing.
  - Tags: schemas.py, request, create, autocoder, schema

- **PieceType** (my-games)
  - File: `apps/api/src/game-engines/chess/types.ts:10`
  - Chess Engine Types
  - Tags: api, chess, piece, schema, game-engines

- **PieceType** (my-games)
  - File: `games/chess/client/ChessBoard.tsx:10`
  - Chess Board Component
  - Tags: chess, games, client, piece, chessboard.tsx

- **CheckersPieceType** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:5394`
  - Checkers types and helpers
  - Tags: api, socket, piece, matchhandler.ts, schema

- **forgotPasswordSchema** (my-games)
  - File: `apps/api/src/routes/auth.ts:1136`
  - In development mode, include the link in response for testing
  - Tags: api, forgot, password, schema, auth.ts

- **CheckersPieceType** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:1016`
  - ===========================================
  - Tags: pages, web, gameplaypage.tsx, piece, schema

- **PieceType** (my-games)
  - File: `apps/web/src/pages/CheckersKingPromotionTestPage.tsx:12`
  - Checkers King Promotion Test Page
  - Tags: checkerskingpromotiontestpage.tsx, pages, piece, schema, type

- **SpecFileStatus** (my-games)
  - File: `autocoder/server/routers/spec_creation.py:100`
  - Cancel and remove a spec creation session.
  - Tags: file, spec_creation.py, spec, autocoder, schema

- **registerSchema** (my-games)
  - File: `apps/api/src/routes/auth.ts:31`
  - localhost:5180',
  - Tags: api, register, schema, auth.ts, apps

- **WSAgentStatusMessage** (my-games)
  - File: `autocoder/server/schemas.py:261`
  - WebSocket message for feature status updates.
  - Tags: schemas.py, message, autocoder, agent, schema

- **PieceType** (my-games)
  - File: `apps/web/src/pages/ChessPreviewPage.tsx:9`
  - ===========================================
  - Tags: pages, chesspreviewpage.tsx, piece, schema, type

- **ModelInfo** (my-games)
  - File: `autocoder/server/schemas.py:374`
  - Request to create a new directory.
  - Tags: schemas.py, info, autocoder, model, schema

- **WSDevServerStatusMessage** (my-games)
  - File: `autocoder/server/schemas.py:466`
  - custom_command: str | None = None  # None clears the custom command


# ============================

  - Tags: dev, schemas.py, message, autocoder, schema

- **joinTournamentSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:164`
  - Tags: api, validators.ts, tournament, schema, join

- **WinnerType** (my-games)
  - File: `packages/shared/src/types/index.ts:182`
  - ===========================================
  - Tags: winner, types, packages, shared, schema

- **resetPasswordSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:46`
  - Tags: api, reset, password, validators.ts, schema

- **Project** (my-games)
  - File: `autocoder/registry.py:81`
  - Registry file doesn't exist.
  - Tags: registry.py, autocoder, project, schema

- **DriveInfo** (my-games)
  - File: `autocoder/server/schemas.py:326`
  - ============================================================================
  - Tags: schemas.py, drive, info, autocoder, schema

- **RegressionInput** (my-games)
  - File: `autocoder/mcp_server/feature_mcp.py:77`
  - Input for marking a feature as in-progress.
  - Tags: mcp_server, input, feature_mcp.py, autocoder, regression

- **TerminalInfoResponse** (my-games)
  - File: `autocoder/server/routers/terminal.py:98`
  - Validate terminal ID format.

    Args:
        terminal_id: The terminal ID to validate

    Return

  - Tags: response, terminal.py, info, autocoder, schema

- **forgotPasswordSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:40`
  - Tags: api, forgot, password, validators.ts, schema

- **submitFeedbackSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:173`
  - ============================================
  - Tags: api, submit, feedback, validators.ts, schema

- **updatePasswordSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:138`
  - Tags: api, update, password, validators.ts, schema

- **loginSchema** (my-games)
  - File: `apps/api/src/routes/auth.ts:45`
  - Optional guest session to convert
  - Tags: api, login, schema, auth.ts, apps

- **DevServerConfigUpdate** (my-games)
  - File: `autocoder/server/schemas.py:449`
  - Response for dev server control actions.
  - Tags: config, dev, update, schemas.py, autocoder

- **Feature** (my-games)
  - File: `autocoder/api/database.py:38`
  - Return current UTC time. Replacement for deprecated _utc_now().
  - Tags: api, feature, database.py, autocoder, schema

- **WSFeatureUpdateMessage** (my-games)
  - File: `autocoder/server/schemas.py:245`
  - System setup status.
  - Tags: feature, update, schemas.py, message, autocoder

- **ProjectPrompts** (my-games)
  - File: `autocoder/server/schemas.py:59`
  - Project statistics.
  - Tags: schemas.py, autocoder, project, schema, server

- **ConversationSummary** (my-games)
  - File: `autocoder/server/routers/assistant_chat.py:59`
  - Validate project name to prevent path traversal.
  - Tags: summary, conversation, autocoder, schema, server

- **createMatchSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:70`
  - ============================================
  - Tags: api, match, create, validators.ts, schema

- **DependencyGraphNode** (my-games)
  - File: `autocoder/server/schemas.py:137`
  - Request schema for bulk creating features.
  - Tags: graph, schemas.py, node, autocoder, schema

- **joinRoomSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:102`
  - ROOM VALIDATION
  - Tags: api, validators.ts, room, schema, join

- **PieceType** (my-games)
  - File: `apps/web/src/pages/SpectatorViewPage.tsx:95`
  - Chess piece types
  - Tags: pages, piece, schema, spectatorviewpage.tsx, type

- **MarkInProgressInput** (my-games)
  - File: `autocoder/mcp_server/feature_mcp.py:67`
  - Input for marking a feature as passing.
  - Tags: mcp_server, feature_mcp.py, progress, mark, autocoder

- **twoFactorVerifySchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:60`
  - Tags: api, two, verify, validators.ts, factor

- **resetPasswordSchema** (my-games)
  - File: `apps/api/src/routes/auth.ts:1140`
  - In development mode, include the link in response for testing
  - Tags: api, reset, password, schema, auth.ts

- **FeatureBulkCreateResponse** (my-games)
  - File: `autocoder/server/schemas.py:127`
  - Response containing list of features organized by status.
  - Tags: response, feature, bulk, schemas.py, create

- **WSMessageType** (my-games)
  - File: `autocoder/ui/src/lib/types.ts:241`
  - Orchestrator status for Mission Control
  - Tags: ui, message, autocoder, schema, type

- **TabType** (my-games)
  - File: `autocoder/ui/src/components/DebugLogViewer.tsx:22`
  - Tags: tab, ui, components, debuglogviewer.tsx, autocoder

- **PieceType** (my-games)
  - File: `apps/web/src/pages/CheckersMultiJumpTestPage.tsx:12`
  - Checkers Multi-Jump Test Page
  - Tags: pages, piece, schema, checkersmultijumptestpage.tsx, type

- **SetupStatus** (my-games)
  - File: `autocoder/server/schemas.py:224`
  - Response for agent control actions.
  - Tags: schemas.py, setup, autocoder, schema, status

- **PieceType** (my-games)
  - File: `apps/web/src/pages/ChessCheckTestPage.tsx:9`
  - ===========================================
  - Tags: pages, chesschecktestpage.tsx, piece, schema, type

- **joinMatchSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:77`
  - ============================================
  - Tags: api, match, validators.ts, schema, join

- **SkipFeatureInput** (my-games)
  - File: `autocoder/mcp_server/feature_mcp.py:62`
  - Input for marking a feature as passing.
  - Tags: mcp_server, feature, feature_mcp.py, autocoder, schema

- **ScheduleUpdate** (my-games)
  - File: `autocoder/server/schemas.py:516`
  - Validate model is in the allowed list.
  - Tags: update, schemas.py, schedule, autocoder, schema

- **WebhookEventType** (my-games)
  - File: `apps/api/src/routes/webhooks.ts:27`
  - Webhook event types we handle
  - Tags: api, webhooks.ts, webhook, schema, type

- **googleAuthSchema** (my-games)
  - File: `apps/api/src/routes/auth.ts:1336`
  - Google OAuth validation schema
  - Tags: google, api, auth, schema, auth.ts

- **Conversation** (my-games)
  - File: `autocoder/server/services/assistant_database.py:31`
  - Return current UTC time. Replacement for deprecated datetime.utcnow().
  - Tags: services, conversation, assistant_database.py, autocoder, schema

- **makeMoveSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:82`
  - GAME VALIDATION
  - Tags: api, make, validators.ts, schema, apps

- **PieceType** (my-games)
  - File: `apps/web/src/pages/ChessCheckmateTestPage.tsx:9`
  - ===========================================
  - Tags: pages, piece, schema, type, web

- **updateWalletSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:202`
  - ============================================
  - Tags: api, update, wallet, validators.ts, schema

- **loginSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:33`
  - Tags: api, login, validators.ts, schema, apps

- **fileUploadSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:239`
  - ============================================
  - Tags: api, file, validators.ts, upload, schema

- **transferCreditsSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:118`
  - ============================================
  - Tags: api, validators.ts, schema, transfer, apps

- **ScheduleOverride** (my-games)
  - File: `autocoder/api/database.py:150`
  - Check if schedule is active on given weekday (0=Monday, 6=Sunday).
  - Tags: api, database.py, schedule, autocoder, schema

- **createRoomSchema** (my-games)
  - File: `apps/api/src/routes/rooms.ts:16`
  - Validation schemas
  - Tags: api, create, room, schema, apps

- **purchaseCreditsSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:111`
  - ============================================
  - Tags: api, validators.ts, schema, apps, purchase

- **DependencyUpdate** (my-games)
  - File: `autocoder/server/schemas.py:159`
  - Edge in the dependency graph.
  - Tags: update, schemas.py, autocoder, schema, server

- **FeatureResponse** (my-games)
  - File: `autocoder/server/schemas.py:101`
  - Request schema for creating a new feature.
  - Tags: response, feature, schemas.py, autocoder, schema

- **WSDevLogMessage** (my-games)
  - File: `autocoder/server/schemas.py:459`
  - Request schema for updating dev server configuration.
  - Tags: log, schemas.py, server, message, autocoder

- **NextRunResponse** (my-games)
  - File: `autocoder/server/schemas.py:561`
  - Response schema for a schedule.
  - Tags: response, schemas.py, next, autocoder, schema

- **TimeControlType** (my-games)
  - File: `apps/api/src/game-engines/chess/types.ts:85`
  - Moves since last pawn move or capture (for 50-move rule)
  - Tags: api, chess, control, time, schema

- **SessionInfo** (my-games)
  - File: `autocoder/server/routers/assistant_chat.py:87`
  - A message within a conversation.
  - Tags: session, info, autocoder, schema, server

- **ConversationMessageModel** (my-games)
  - File: `autocoder/server/routers/assistant_chat.py:69`
  - return bool(re.match(r'^[a-zA-Z0-9_-]{1,50}$', name))


# ==========================================

  - Tags: conversation, message, autocoder, schema, model

- **CreateTerminalRequest** (my-games)
  - File: `autocoder/server/routers/terminal.py:86`
  - Validate terminal ID format.

    Args:
        terminal_id: The terminal ID to validate

    Return

  - Tags: terminal.py, request, create, autocoder, schema

- **PathValidationResponse** (my-games)
  - File: `autocoder/server/schemas.py:351`
  - An entry in a directory listing.
  - Tags: response, schemas.py, path, validation, autocoder

- **ProjectPromptsUpdate** (my-games)
  - File: `autocoder/server/schemas.py:66`
  - Summary of a project for list view.
  - Tags: update, schemas.py, autocoder, project, schema

- **ProjectCreate** (my-games)
  - File: `autocoder/server/schemas.py:27`
  - Import model constants from registry (single source of truth)
  - Tags: schemas.py, create, autocoder, project, schema

- **subscribeNotificationsSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:213`
  - ============================================
  - Tags: api, subscribe, validators.ts, notifications, schema

- **DirectoryListResponse** (my-games)
  - File: `autocoder/server/schemas.py:343`
  - Information about a drive (Windows only).
  - Tags: response, schemas.py, list, autocoder, schema

- **MarkPassingInput** (my-games)
  - File: `autocoder/mcp_server/feature_mcp.py:57`
  - Configuration from environment
  - Tags: mcp_server, feature_mcp.py, passing, mark, autocoder

- **AgentActionResponse** (my-games)
  - File: `autocoder/server/schemas.py:213`
  - Current agent status.
  - Tags: response, schemas.py, autocoder, agent, schema

- **DevServerActionResponse** (my-games)
  - File: `autocoder/server/schemas.py:434`
  - Request schema for starting the dev server.
  - Tags: response, dev, schemas.py, autocoder, schema

- **PieceType** (my-games)
  - File: `games/checkers/server/index.ts:10`
  - Checkers Server-Side Game Engine
  - Tags: server, games, piece, schema, type

- **Schedule** (my-games)
  - File: `autocoder/api/database.py:86`
  - Safely extract dependencies, handling NULL and malformed data.
  - Tags: api, database.py, schedule, autocoder, schema

- **DevServerStartRequest** (my-games)
  - File: `autocoder/server/schemas.py:420`
  - ============================================================================
  - Tags: dev, schemas.py, request, autocoder, schema

- **SettingsResponse** (my-games)
  - File: `autocoder/server/schemas.py:380`
  - Request to create a new directory.
  - Tags: response, schemas.py, autocoder, schema, settings

- **BulkCreateInput** (my-games)
  - File: `autocoder/mcp_server/feature_mcp.py:90`
  - Schema for creating a single feature.
  - Tags: mcp_server, bulk, create, feature_mcp.py, autocoder

- **ModelsResponse** (my-games)
  - File: `autocoder/server/schemas.py:388`
  - Information about an available model.
  - Tags: response, schemas.py, models, autocoder, schema

- **DependencyGraphEdge** (my-games)
  - File: `autocoder/server/schemas.py:147`
  - Minimal node for graph visualization (no description exposed for security).
  - Tags: graph, edge, schemas.py, autocoder, schema

- **WSProgressMessage** (my-games)
  - File: `autocoder/server/schemas.py:236`
  - System setup status.
  - Tags: schemas.py, progress, message, autocoder, schema

- **DirectoryEntry** (my-games)
  - File: `autocoder/server/schemas.py:333`
  - Information about a drive (Windows only).
  - Tags: schemas.py, entry, autocoder, schema, directory

- **updateSettingsSchema** (my-games)
  - File: `apps/api/src/lib/validators.ts:227`
  - ============================================
  - Tags: api, update, validators.ts, schema, settings

- **verifyEmailSchema** (my-games)
  - File: `apps/api/src/routes/auth.ts:957`
  - Email verification token expiry time (24 hours)
  - Tags: api, verify, email, schema, auth.ts

- **PieceType** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:181`
  - ===========================================
  - Tags: pages, gameplaypage.tsx, piece, schema, type

- **FeatureBase** (my-games)
  - File: `autocoder/server/schemas.py:77`
  - Request schema for updating project prompts.
  - Tags: feature, schemas.py, autocoder, schema, server

- **RewardType** (my-games)
  - File: `packages/shared/src/types/index.ts:284`
  - ===========================================
  - Tags: types, packages, reward, shared, schema

- **AgentType** (my-games)
  - File: `autocoder/ui/src/lib/types.ts:187`
  - Original 5
  - Tags: ui, autocoder, agent, schema, type

- **TransactionType** (my-games)
  - File: `packages/shared/src/types/index.ts:61`
  - ===========================================
  - Tags: types, packages, shared, schema, transaction

- **DependencyGraphResponse** (my-games)
  - File: `autocoder/server/schemas.py:153`
  - Minimal node for graph visualization (no description exposed for security).
  - Tags: response, graph, schemas.py, autocoder, schema

- **PieceType** (my-games)
  - File: `apps/web/src/pages/CheckersBoardTestPage.tsx:12`
  - Checkers Board Test Page
  - Tags: checkersboardtestpage.tsx, pages, piece, schema, type

- **PieceType** (my-games)
  - File: `apps/web/src/pages/ChessMoveTestPage.tsx:9`
  - ===========================================
  - Tags: pages, chessmovetestpage.tsx, piece, schema, type

- **SpecSessionStatus** (my-games)
  - File: `autocoder/server/routers/spec_creation.py:54`
  - Validate project name to prevent path traversal.
  - Tags: session, spec_creation.py, spec, autocoder, schema

- **PieceType** (my-games)
  - File: `apps/api/src/game-engines/checkers/types.ts:10`
  - Checkers Engine Types
  - Tags: api, piece, schema, game-engines, type

- **joinWithPasswordSchema** (my-games)
  - File: `apps/api/src/routes/invites.ts:33`
  - Validation schemas
  - Tags: api, with, password, invites.ts, schema

- **SoundType** (my-games)
  - File: `autocoder/ui/src/hooks/useFeatureSound.ts:17`
  - Sound frequencies for different transitions (in Hz)
  - Tags: usefeaturesound.ts, ui, autocoder, hooks, schema

- **ClearInProgressInput** (my-games)
  - File: `autocoder/mcp_server/feature_mcp.py:72`
  - Input for marking a feature as passing.
  - Tags: mcp_server, clear, feature_mcp.py, progress, autocoder

- **ScheduleCreate** (my-games)
  - File: `autocoder/server/schemas.py:478`
  - WebSocket message for dev server status changes.
  - Tags: schemas.py, schedule, create, autocoder, schema

- **DevServerStatus** (my-games)
  - File: `autocoder/server/schemas.py:425`
  - Request schema for starting the dev server.
  - Tags: dev, schemas.py, autocoder, schema, status

- **WSAgentUpdateMessage** (my-games)
  - File: `autocoder/server/schemas.py:277`
  - WebSocket message for agent status changes.
  - Tags: update, schemas.py, message, autocoder, agent

- **PieceType** (my-games)
  - File: `apps/web/src/pages/ChessEnPassantTestPage.tsx:7`
  - ===========================================
  - Tags: pages, chessenpassanttestpage.tsx, piece, schema, type

- **ToastContextType** (my-games)
  - File: `apps/web/src/context/ToastContext.tsx:10`
  - Tags: context, toastcontext.tsx, toast, schema, type

- **AuthContextType** (my-games)
  - File: `apps/web/src/context/AuthContext.tsx:6`
  - AuthContext - Simple authentication context for the application
  - Tags: context, auth, schema, authcontext.tsx, type

### Service

- **YouTubeAutomationService** (ai-dashboard)
  - File: `backend/services/youtube_automation.py:16`
  - AI Dashboard - YouTube Automation Service
  - Tags: service, services, youtube_automation.py, backend, automation

- **SchedulerService** (ai-dashboard)
  - File: `backend/services/scheduler_service.py:15`
  - AI Dashboard - Scheduler Service
  - Tags: service, services, backend, scheduler_service.py, scheduler

- **DeckManager** (my-games)
  - File: `apps/api/src/game-engines/cards/deck.ts:9`
  - Card Games Engine - Deck Management
  - Tags: api, service, manager, deck.ts, cards

- **SchedulerService** (my-games)
  - File: `autocoder/server/services/scheduler_service.py:29`
  - Add parent directory for imports
  - Tags: service, services, scheduler_service.py, autocoder, server

- **CardGameStateManager** (my-games)
  - File: `apps/api/src/game-engines/cards/game-state.ts:10`
  - Card Games Engine - Game State Management
  - Tags: api, game, service, manager, state

- **ConnectionManager** (my-games)
  - File: `autocoder/server/websocket.py:514`
  - Lazy import of count_passing_tests.
  - Tags: service, manager, websocket.py, autocoder, connection

- **DevServerProcessManager** (my-games)
  - File: `autocoder/server/services/dev_server_manager.py:81`
  - for pattern in SENSITIVE_PATTERNS:

        line = re.sub(pattern, '[REDACTED]', line, flags=re.IGNOR

  - Tags: service, dev, process, manager, services

- **AgentProcessManager** (my-games)
  - File: `autocoder/server/services/process_manager.py:54`
  - Remove sensitive information from output lines.
  - Tags: service, services, process, manager, process_manager.py

### Utility

- **getTrendingProjects** (ai-dashboard)
  - File: `frontend/lib/api.ts:103`
  - Tags: frontend, projects, trending, get, api.ts

- **get_videos** (ai-dashboard)
  - File: `backend/main.py:174`
  - API root endpoint
  - Tags: backend, get, main.py, videos, utility

- **get_trending_projects** (ai-dashboard)
  - File: `backend/main.py:247`
  - Get top AI GitHub projects
  - Tags: projects, trending, backend, get, main.py

- **getStats** (ai-dashboard)
  - File: `frontend/lib/api.ts:137`
  - Tags: frontend, get, api.ts, stats, utility

- **get_trending_projects** (ai-dashboard)
  - File: `backend/scrapers/github_trending.py:262`
  - Get top AI projects by stars
  - Tags: projects, scrapers, trending, backend, get

- **getSourceColor** (ai-dashboard)
  - File: `frontend/app/news/page.tsx:54`
  - Tags: frontend, color, get, news, page.tsx

- **updateAutomation** (ai-dashboard)
  - File: `frontend/lib/api.ts:127`
  - Tags: frontend, update, automation, api.ts, utility

- **getAutomations** (ai-dashboard)
  - File: `frontend/lib/api.ts:108`
  - Tags: automations, frontend, get, api.ts, utility

- **get_automation** (ai-dashboard)
  - File: `backend/main.py:282`
  - Get all video automations
  - Tags: backend, automation, get, main.py, utility

- **create_video_draft** (ai-dashboard)
  - File: `backend/services/youtube_automation.py:39`
  - Tags: services, youtube_automation.py, backend, create, draft

- **get_trending_news** (ai-dashboard)
  - File: `backend/main.py:211`
  - Get latest AI news
  - Tags: trending, backend, get, main.py, news

- **get_trending_news** (ai-dashboard)
  - File: `backend/scrapers/news_aggregator.py:294`
  - Get latest AI news from database
  - Tags: scrapers, trending, backend, get, news_aggregator.py

- **formatNumber** (ai-dashboard)
  - File: `frontend/app/videos/page.tsx:44`
  - Tags: frontend, videos, number, page.tsx, format

- **get_scheduler_status** (ai-dashboard)
  - File: `backend/main.py:376`
  - ---------- Scheduler ----------
  - Tags: backend, get, main.py, status, utility

- **get_recently_updated** (ai-dashboard)
  - File: `backend/scrapers/github_trending.py:272`
  - return db.query(GitHubProject).filter(

            GitHubProject.stars >= min_stars
        ).order_

  - Tags: scrapers, backend, get, github_trending.py, updated

- **update_draft** (ai-dashboard)
  - File: `backend/services/youtube_automation.py:207`
  - Tags: services, youtube_automation.py, update, backend, draft

- **get_latest_news** (ai-dashboard)
  - File: `backend/scrapers/news_aggregator.py:277`
  - Tags: scrapers, news_aggregator.py, backend, get, news

- **get_draft** (ai-dashboard)
  - File: `backend/services/youtube_automation.py:304`
  - TODO: Implement actual YouTube upload
  - Tags: services, youtube_automation.py, backend, get, draft

- **update_automation** (ai-dashboard)
  - File: `backend/main.py:312`
  - Create a new video automation from prompt
  - Tags: update, backend, automation, main.py, utility

- **getStatusBadge** (ai-dashboard)
  - File: `frontend/app/youtube-bot/page.tsx:56`
  - Tags: frontend, badge, get, youtube-bot, page.tsx

- **getProjects** (ai-dashboard)
  - File: `frontend/lib/api.ts:98`
  - API Functions
  - Tags: frontend, projects, get, api.ts, utility

- **getSchedulerStatus** (ai-dashboard)
  - File: `frontend/lib/api.ts:147`
  - Tags: frontend, get, api.ts, status, utility

- **formatDate** (ai-dashboard)
  - File: `frontend/app/news/page.tsx:45`
  - Tags: frontend, date, news, page.tsx, format

- **create_automation** (ai-dashboard)
  - File: `backend/main.py:294`
  - Get a specific automation
  - Tags: backend, automation, main.py, create, utility

- **getNews** (ai-dashboard)
  - File: `frontend/lib/api.ts:88`
  - API Functions
  - Tags: frontend, get, api.ts, news, utility

- **get_news** (ai-dashboard)
  - File: `backend/main.py:199`
  - Manually trigger YouTube scraper
  - Tags: backend, get, main.py, news, utility

- **generate_video_content** (ai-dashboard)
  - File: `backend/services/prompt_optimizer.py:58`
  - Create modules
  - Tags: services, backend, content, generate, prompt_optimizer.py

- **get_job_status** (ai-dashboard)
  - File: `backend/services/scheduler_service.py:94`
  - Run GitHub scraper job
  - Tags: job, services, backend, get, scheduler_service.py

- **get_stats** (ai-dashboard)
  - File: `backend/main.py:396`
  - Manually trigger a scheduled job
  - Tags: backend, get, main.py, stats, utility

- **getLanguageColor** (ai-dashboard)
  - File: `frontend/app/projects/page.tsx:51`
  - Tags: frontend, color, projects, get, language

- **get_async_db** (ai-dashboard)
  - File: `backend/database/db.py:60`
  - Dependency for sync database sessions
  - Tags: backend, get, async, db.py, database

- **get_projects** (ai-dashboard)
  - File: `backend/main.py:235`
  - Manually trigger news aggregator
  - Tags: projects, backend, get, main.py, utility

- **updated** (ai-dashboard)
  - File: `frontend/app/youtube-bot/[id]/page.tsx:75`
  - Tags: frontend, [id], youtube-bot, page.tsx, updated

- **calculate_quality_score** (ai-dashboard)
  - File: `backend/database/models.py:31`
  - Tags: backend, quality, calculate, score, models.py

- **getTrendingNews** (ai-dashboard)
  - File: `frontend/lib/api.ts:93`
  - API Functions
  - Tags: frontend, trending, get, api.ts, news

- **get_all_drafts** (ai-dashboard)
  - File: `backend/services/youtube_automation.py:310`
  - Get a video draft by ID
  - Tags: services, youtube_automation.py, backend, get, all

- **createAutomation** (ai-dashboard)
  - File: `frontend/lib/api.ts:118`
  - Tags: frontend, automation, api.ts, create, utility

- **get_db_session** (ai-dashboard)
  - File: `backend/database/db.py:47`
  - Initialize database and create all tables
  - Tags: session, backend, get, db.py, database

- **generate_heygen_video** (ai-dashboard)
  - File: `backend/services/youtube_automation.py:87`
  - Tags: services, youtube_automation.py, backend, generate, heygen

- **get_top_videos** (ai-dashboard)
  - File: `backend/scrapers/youtube_scraper.py:306`
  - Tags: scrapers, backend, get, videos, youtube_scraper.py

- **calculate_trending_score** (ai-dashboard)
  - File: `backend/database/models.py:98`
  - List of topics
  - Tags: trending, backend, calculate, score, models.py

- **getAutomation** (ai-dashboard)
  - File: `frontend/lib/api.ts:113`
  - Tags: frontend, automation, get, api.ts, utility

- **generate_video** (ai-dashboard)
  - File: `backend/main.py:329`
  - Update a video automation draft
  - Tags: backend, generate, main.py, video, utility

- **formatNumber** (ai-dashboard)
  - File: `frontend/app/projects/page.tsx:45`
  - Tags: frontend, projects, number, page.tsx, format

- **getVideos** (ai-dashboard)
  - File: `frontend/lib/api.ts:83`
  - API Functions
  - Tags: frontend, get, api.ts, videos, utility

- **getStatusInfo** (ai-dashboard)
  - File: `frontend/app/youtube-bot/[id]/page.tsx:102`
  - Tags: frontend, get, [id], youtube-bot, info

- **get_db** (ai-dashboard)
  - File: `backend/database/db.py:37`
  - Initialize database and create all tables
  - Tags: backend, get, utility, database, db.py

- **get_automations** (ai-dashboard)
  - File: `backend/main.py:271`
  - Manually trigger GitHub scraper
  - Tags: automations, backend, get, main.py, utility

- **get_top_projects** (ai-dashboard)
  - File: `backend/scrapers/github_trending.py:249`
  - Tags: projects, scrapers, backend, get, github_trending.py

- **parseCastlingRights** (my-games)
  - File: `apps/api/src/game-engines/chess/game-state.ts:121`
  - Check if piece can have moved (for castling rights)
  - Tags: api, chess, game-state.ts, rights, castling

- **updatedReport** (my-games)
  - File: `apps/api/src/routes/moderation.ts:223`
  - Determine new status
  - Tags: api, routes, moderation.ts, report, updated

- **getChessRawMoves** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:465`
  - Tags: chess, get, pages, web, gameplaypage.tsx

- **settlement** (my-games)
  - File: `apps/api/src/routes/wallet.ts:912`
  - Determine the winner's userId
  - Tags: api, settlement, wallet.ts, apps, utility

- **validateFieldSelection** (my-games)
  - File: `apps/api/src/lib/fields.ts:309`
  - Validate that only requested fields are returned
  - Tags: validate, api, selection, fields.ts, field

- **getDayStart** (my-games)
  - File: `apps/api/src/routes/leaderboards.ts:44`
  - Last day of current month
  - Tags: api, routes, get, leaderboards.ts, start

- **get_db_session** (my-games)
  - File: `autocoder/server/routers/features.py:64`
  - Tags: session, get, features.py, autocoder, server

- **createInitialBoard** (my-games)
  - File: `apps/api/src/game-engines/chess/board-utils.ts:12`
  - Chess Board Utilities
  - Tags: api, board-utils.ts, chess, create, board

- **getPseudoLegalMoves** (my-games)
  - File: `apps/api/src/game-engines/chess/move-validation.ts:158`
  - Get all possible squares a piece can move to (excluding check constraints)
  - Tags: api, chess, move-validation.ts, get, game-engines

- **get_passing_count** (my-games)
  - File: `autocoder/parallel_orchestrator.py:371`
  - Permanently failed, count as "done"
  - Tags: get, count, passing, autocoder, parallel_orchestrator.py

- **getRedisClient** (my-games)
  - File: `apps/api/src/services/cacheService.ts:10`
  - Get or create Redis client
  - Tags: api, services, get, cacheservice.ts, client

- **createInitialBoard** (my-games)
  - File: `apps/web/src/pages/ChessMoveTestPage.tsx:52`
  - ===========================================
  - Tags: pages, web, create, board, chessmovetestpage.tsx

- **get_dev_command** (my-games)
  - File: `autocoder/server/services/project_config.py:325`
  - Tags: services, get, server, command, autocoder

- **deleteGames** (my-games)
  - File: `apps/api/src/test/setup.ts:23`
  - Setup database connection for tests
  - Tags: api, delete, setup.ts, games, apps

- **validatePassword** (my-games)
  - File: `apps/web/src/pages/ResetPasswordPage.tsx:30`
  - Check if token is present
  - Tags: validate, resetpasswordpage.tsx, password, pages, apps

- **getCaptureMoves** (my-games)
  - File: `games/checkers/server/index.ts:146`
  - Kings can move in all 4 diagonal directions
  - Tags: capture, get, server, games, checkers

- **getAvatarColor** (my-games)
  - File: `apps/web/src/components/OptimizedImage.tsx:185`
  - Get initials from username
  - Tags: color, avatar, get, components, apps

- **extract_url** (my-games)
  - File: `autocoder/server/services/dev_server_manager.py:68`
  - Remove sensitive information from output lines.
  - Tags: services, url, extract, autocoder, server

- **getStateAnimation** (my-games)
  - File: `autocoder/ui/src/components/OrchestratorAvatar.tsx:94`
  - Animation classes based on orchestrator state
  - Tags: animation, get, components, state, orchestratoravatar.tsx

- **formatDate** (my-games)
  - File: `apps/web/src/pages/StorePage.tsx:226`
  - Update credits balance
  - Tags: storepage.tsx, date, pages, web, apps

- **createSchedule** (my-games)
  - File: `autocoder/ui/src/components/ScheduleModal.tsx:39`
  - Queries and mutations
  - Tags: components, schedule, create, schedulemodal.tsx, autocoder

- **get_db_path** (my-games)
  - File: `autocoder/server/services/assistant_database.py:57`
  - A single message within a conversation.
  - Tags: services, get, path, assistant_database.py, autocoder

- **formattedAmount** (my-games)
  - File: `apps/api/src/services/emailService.ts:246`
  - Send subscription confirmation email
  - Tags: api, services, amount, emailservice.ts, formatted

- **updateFeature** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:134`
  - Tags: feature, update, api.ts, autocoder, ui

- **getStateGlow** (my-games)
  - File: `autocoder/ui/src/components/OrchestratorAvatar.tsx:114`
  - Glow effect based on state
  - Tags: get, components, state, orchestratoravatar.tsx, glow

- **parseIncludes** (my-games)
  - File: `apps/api/src/lib/fields.ts:92`
  - Parse include parameter for eager loading relations
  - Tags: api, fields.ts, parse, apps, utility

- **getPositionBonus** (my-games)
  - File: `games/chess/ai/index.ts:133`
  - ===========================================
  - Tags: chess, get, games, position, ai

- **getDevServerConfig** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:411`
  - Tags: config, dev, get, api.ts, autocoder

- **getRawMoves** (my-games)
  - File: `apps/web/src/pages/ChessCheckmateTestPage.tsx:76`
  - Get raw moves for a piece (without checking for leaving king in check)
  - Tags: get, pages, web, raw, apps

- **createResponse** (my-games)
  - File: `apps/api/src/routes/rooms.test.ts:268`
  - Create a room with first user
  - Tags: response, api, rooms.test.ts, routes, create

- **getPendingCommissions** (my-games)
  - File: `apps/api/src/services/referralXpCommissionService.ts:340`
  - Get pending commissions for a user (commissions they can unlock)
  - Tags: api, services, referralxpcommissionservice.ts, pending, get

- **createCapturePromotionScenario** (my-games)
  - File: `apps/web/src/pages/CheckersKingPromotionTestPage.tsx:77`
  - Scenario: King piece demonstrating backward movement
  - Tags: scenario, checkerskingpromotiontestpage.tsx, capture, pages, create

- **getAgentLogs** (my-games)
  - File: `autocoder/ui/src/hooks/useWebSocket.ts:455`
  - Check every minute
  - Tags: usewebsocket.ts, get, autocoder, agent, hooks

- **getCategoryConfig** (my-games)
  - File: `apps/web/src/pages/FeedbackPage.tsx:280`
  - Update feedback count in list
  - Tags: config, get, pages, feedbackpage.tsx, category

- **formatDate** (my-games)
  - File: `apps/web/src/pages/WalletPage.tsx:537`
  - Tags: date, pages, web, walletpage.tsx, apps

- **validate_project_name** (my-games)
  - File: `autocoder/server/utils/validation.py:10`
  - Shared validation utilities for the server.
  - Tags: validate, name, utils, validation.py, autocoder

- **getStatusBadge** (my-games)
  - File: `apps/web/src/pages/ReferralsPage.tsx:368`
  - Tags: badge, get, pages, referralspage.tsx, status

- **createCreditRoom** (my-games)
  - File: `apps/web/src/pages/CreditDeductionTestPage.tsx:223`
  - Step 3: Create credit game room
  - Tags: pages, credit, create, creditdeductiontestpage.tsx, room

- **getUserIdFromToken** (my-games)
  - File: `apps/api/src/routes/games.ts:9`
  - Helper to extract user ID from token
  - Tags: api, games.ts, routes, get, token

- **create_directory** (my-games)
  - File: `autocoder/server/routers/filesystem.py:433`
  - Tags: filesystem.py, create, autocoder, directory, server

- **getReferralInfo** (my-games)
  - File: `apps/web/src/pages/Level3ReferralTestPage.tsx:96`
  - Wallet API returns creditsBalance directly (not nested in data)
  - Tags: level3referraltestpage.tsx, get, pages, info, apps

- **formatDate** (my-games)
  - File: `apps/web/src/pages/TournamentsPage.tsx:311`
  - Tags: tournamentspage.tsx, date, pages, web, apps

- **getLegalMoves** (my-games)
  - File: `apps/web/src/pages/ChessCheckmateTestPage.tsx:242`
  - Check if a color's king is in check
  - Tags: get, pages, web, legal, apps

- **getPlayerPieces** (my-games)
  - File: `apps/api/src/game-engines/checkers/board.ts:132`
  - Check if square contains opponent piece
  - Tags: api, get, pieces, player, game-engines

- **formatCredits** (my-games)
  - File: `apps/web/src/pages/SubscriptionsPage.tsx:234`
  - Tags: subscriptionspage.tsx, pages, web, apps, format

- **generateToken** (my-games)
  - File: `apps/api/src/middleware/auth.ts:66`
  - Generate refresh token (long-lived)
  - Tags: api, token, generate, auth.ts, apps

- **deleteUsers** (my-games)
  - File: `apps/api/src/test/setup.ts:20`
  - Setup database connection for tests
  - Tags: api, delete, setup.ts, users, apps

- **sanitizedMessage** (my-games)
  - File: `apps/api/src/socket/tournamentChatHandler.ts:177`
  - Sanitize and limit message length
  - Tags: api, sanitized, socket, message, apps

- **validateCastling** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:5218`
  - Tags: validate, api, socket, castling, matchhandler.ts

- **getStoredConversationId** (my-games)
  - File: `autocoder/ui/src/components/AssistantPanel.tsx:23`
  - Tags: get, components, conversation, assistantpanel.tsx, autocoder

- **calculatePeriodFilter** (my-games)
  - File: `apps/api/src/routes/leaderboards.ts:63`
  - Tags: api, routes, calculate, leaderboards.ts, filter

- **updateTournamentWinMilestone** (my-games)
  - File: `apps/api/src/services/milestoneService.ts:330`
  - Update milestone progress when a user wins a tournament
  - Tags: api, services, milestone, update, win

- **create_schedule** (my-games)
  - File: `autocoder/server/routers/schedules.py:121`
  - Tags: schedule, create, autocoder, schedules.py, server

- **getSetupStatus** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:265`
  - ============================================================================
  - Tags: ui, get, api.ts, setup, autocoder

- **deleteButton** (my-games)
  - File: `autocoder/ui/e2e/conversation-history.spec.ts:481`
  - Open history and get count
  - Tags: delete, button, conversation-history.spec.ts, autocoder, e2e

- **validateFileUpload** (my-games)
  - File: `apps/api/src/lib/validators.ts:246`
  - ============================================
  - Tags: validate, api, file, validators.ts, upload

- **createInitialState** (my-games)
  - File: `apps/api/src/game-engines/chess/game-state.ts:21`
  - Chess Game State Management
  - Tags: api, chess, state, game-state.ts, create

- **updateCheck** (my-games)
  - File: `apps/web/src/pages/CreditDeductionTestPage.tsx:60`
  - Tags: update, pages, creditdeductiontestpage.tsx, check, apps

- **get_blocking_dependencies** (my-games)
  - File: `autocoder/api/dependency_resolver.py:121`
  - Tags: api, blocking, get, dependency_resolver.py, autocoder

- **getDayEnd** (my-games)
  - File: `apps/api/src/routes/games.ts:150`
  - Tags: api, games.ts, routes, get, end

- **get_conversation** (my-games)
  - File: `autocoder/server/services/assistant_database.py:156`
  - Tags: services, get, conversation, assistant_database.py, autocoder

- **getCategoryColor** (my-games)
  - File: `autocoder/ui/src/components/FeatureModal.tsx:8`
  - Generate consistent color for category (matches FeatureCard pattern)
  - Tags: color, get, components, featuremodal.tsx, autocoder

- **createChessAI** (my-games)
  - File: `apps/ai-engine/src/games/chess.ts:469`
  - Fewer moves = higher confidence
  - Tags: chess, chess.ts, ai-engine, create, games

- **getWinStreak** (my-games)
  - File: `apps/api/src/services/walletService.ts:476`
  - Get a user's current win streak
  - Tags: api, services, get, win, streak

- **getCategoryMetric** (my-games)
  - File: `apps/web/src/pages/LeaderboardPage.tsx:256`
  - Tags: leaderboardpage.tsx, get, pages, category, metric

- **getOptimalLimit** (my-games)
  - File: `apps/api/src/lib/pagination.ts:112`
  - Calculate optimal page size based on data complexity
  - Tags: api, get, optimal, limit, pagination.ts

- **getStateAnimation** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:520`
  - Original 5
  - Tags: animation, get, components, state, autocoder

- **update_project_path** (my-games)
  - File: `autocoder/registry.py:342`
  - Tags: update, path, autocoder, project, registry.py

- **formatUptime** (my-games)
  - File: `apps/admin/src/pages/Health.tsx:30`
  - Tags: health.tsx, pages, uptime, admin, apps

- **getPotentialSquares** (my-games)
  - File: `apps/api/src/game-engines/checkers/board.ts:287`
  - Check if two squares are equal
  - Tags: api, potential, get, squares, game-engines

- **createInitialBoard** (my-games)
  - File: `games/checkers/server/index.ts:62`
  - For draw by no captures (40-move rule)
  - Tags: server, create, board, games, checkers

- **getSortIcon** (my-games)
  - File: `apps/web/src/pages/LeaderboardPage.tsx:283`
  - Handle column sort click
  - Tags: leaderboardpage.tsx, icon, get, pages, sort

- **create_feature** (my-games)
  - File: `autocoder/server/routers/features.py:173`
  - Tags: feature, features.py, create, autocoder, server

- **get_session_status** (my-games)
  - File: `autocoder/server/routers/spec_creation.py:69`
  - Status of a spec creation session.
  - Tags: session, spec_creation.py, get, autocoder, status

- **getTransporter** (my-games)
  - File: `apps/api/src/services/emailService.ts:15`
  - Email configuration from environment variables
  - Tags: api, services, transporter, get, emailservice.ts

- **get_setting** (my-games)
  - File: `autocoder/registry.py:453`
  - =============================================================================
  - Tags: get, utility, autocoder, registry.py, setting

- **generatePositionKey** (my-games)
  - File: `games/chess/server/index.ts:383`
  - Generate a unique key for position tracking (for threefold repetition)
  - Tags: key, chess, generate, games, position

- **get_ready_features** (my-games)
  - File: `autocoder/api/dependency_resolver.py:348`
  - Depth score: 0-1, higher = closer to root (no deps)
  - Tags: api, get, features, dependency_resolver.py, autocoder

- **getDependencyGraph** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:159`
  - ============================================================================
  - Tags: graph, get, api.ts, autocoder, ui

- **getRateLimitConfig** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:59`
  - Trivia can have rapid answers
  - Tags: api, config, get, socket, limit

- **getCapturedPosition** (my-games)
  - File: `games/checkers/server/index.ts:235`
  - Check if move is a capture
  - Tags: get, server, captured, games, position

- **getLatestThought** (my-games)
  - File: `autocoder/ui/src/components/AgentThought.tsx:41`
  - Extracts the latest agent thought from logs
  - Tags: agentthought.tsx, get, components, autocoder, thought

- **formatDaysDescription** (my-games)
  - File: `autocoder/ui/src/lib/timeUtils.ts:245`
  - Toggle a day in a bitfield.
  - Tags: description, ui, autocoder, days, format

- **getStateText** (my-games)
  - File: `autocoder/ui/src/components/OrchestratorStatusCard.tsx:11`
  - Get a friendly state description
  - Tags: get, components, state, autocoder, orchestratorstatuscard.tsx

- **getSocketUser** (my-games)
  - File: `apps/api/src/middleware/socketAuth.ts:42`
  - Get user or guest from socket
  - Tags: api, socketauth.ts, get, socket, user

- **settings** (my-games)
  - File: `apps/api/src/services/pushNotificationService.ts:320`
  - Send push notification when a spectator joins the match
  - Tags: api, pushnotificationservice.ts, services, settings, apps

- **getPiece** (my-games)
  - File: `apps/web/src/pages/ChessCastlingTestPage.tsx:58`
  - ===========================================
  - Tags: get, pages, piece, chesscastlingtestpage.tsx, apps

- **calculateWinner** (my-games)
  - File: `apps/web/src/pages/TriviaScoringTestPage.tsx:134`
  - ===========================================
  - Tags: winner, triviascoringtestpage.tsx, pages, calculate, apps

- **updatedHostWallet** (my-games)
  - File: `apps/api/src/services/walletService.ts:814`
  - 2. Award host bonus (if applicable)
  - Tags: api, services, host, wallet, walletservice.ts

- **updatedState** (my-games)
  - File: `apps/api/src/socket/handlers/gameHandler.ts:408`
  - Validate card play
  - Tags: api, socket, state, gamehandler.ts, handlers

- **generateId** (my-games)
  - File: `autocoder/ui/src/hooks/useExpandChat.ts:34`
  - Tags: generate, autocoder, hooks, useexpandchat.ts, ui

- **get_session** (my-games)
  - File: `autocoder/server/services/spec_chat_session.py:459`
  - Check if spec creation is complete.
  - Tags: services, session, get, autocoder, spec_chat_session.py

- **updated** (my-games)
  - File: `apps/api/src/routes/wallet.ts:1239`
  - Get or create wallet
  - Tags: api, wallet.ts, updated, apps, utility

- **getPiece** (my-games)
  - File: `games/chess/server/index.ts:114`
  - ===========================================
  - Tags: chess, get, games, piece, server

- **get_settings** (my-games)
  - File: `autocoder/server/routers/settings.py:77`
  - Parse integer setting with default fallback.
  - Tags: get, autocoder, settings, server, settings.py

- **updateCastlingRightsAfterMove** (my-games)
  - File: `apps/api/src/game-engines/chess/game-state.ts:308`
  - Update castling rights after move
  - Tags: api, update, chess, game-state.ts, rights

- **createUser** (my-games)
  - File: `apps/web/src/pages/Level3ReferralTestPage.tsx:64`
  - Tags: level3referraltestpage.tsx, pages, create, user, apps

- **deleteSchedule** (my-games)
  - File: `autocoder/ui/src/components/ScheduleModal.tsx:40`
  - Queries and mutations
  - Tags: delete, components, schedule, schedulemodal.tsx, autocoder

- **getSettings** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:374`
  - ============================================================================
  - Tags: get, api.ts, autocoder, settings, ui

- **getLogColor** (my-games)
  - File: `autocoder/ui/src/components/AgentCard.tsx:170`
  - Tags: log, color, get, components, agentcard.tsx

- **getTransactionColor** (my-games)
  - File: `apps/web/src/pages/WalletPage.tsx:554`
  - Tags: color, get, pages, walletpage.tsx, transaction

- **updateRookRights** (my-games)
  - File: `apps/api/src/game-engines/chess/special-moves.ts:266`
  - If king moves, lose all castling rights for that color
  - Tags: api, update, chess, rook, special-moves.ts

- **getStartOfDay** (my-games)
  - File: `apps/api/src/routes/feedback.ts:14`
  - XP reward for daily feedback
  - Tags: api, routes, get, feedback.ts, start

- **get_session** (my-games)
  - File: `autocoder/parallel_orchestrator.py:195`
  - immediately instead of waiting for the full POLL_INTERVAL timeout.
  - Tags: session, get, autocoder, parallel_orchestrator.py, utility

- **createTimeControl** (my-games)
  - File: `apps/api/src/game-engines/chess/time-controls.ts:14`
  - Chess Time Controls
  - Tags: api, chess, control, create, time-controls.ts

- **get_status_dict** (my-games)
  - File: `autocoder/server/services/dev_server_manager.py:419`
  - Process has terminated
  - Tags: services, get, server, autocoder, status

- **get_project_devserver_manager** (my-games)
  - File: `autocoder/server/routers/devserver.py:92`
  - Tags: manager, get, server, autocoder, project

- **createTestUser** (my-games)
  - File: `apps/api/src/test/setup.ts:45`
  - Additional cleanup if needed
  - Tags: api, setup.ts, create, user, apps

- **get_org_config_path** (my-games)
  - File: `autocoder/security.py:399`
  - Also reject if prefix is empty (would be bare "*")
  - Tags: config, get, path, org, autocoder

- **getWeekStart** (my-games)
  - File: `apps/api/src/routes/games.ts:114`
  - Filter out inactive games and format response
  - Tags: api, week, games.ts, routes, get

- **validateSingleMove** (my-games)
  - File: `apps/api/src/game-engines/checkers/move-validation.ts:29`
  - Checkers Move Validation
  - Tags: validate, api, single, move-validation.ts, move

- **getGameResult** (my-games)
  - File: `apps/api/src/game-engines/chess/rules.ts:359`
  - Check if game is over
  - Tags: api, game, rules.ts, chess, get

- **getStateColor** (my-games)
  - File: `autocoder/ui/src/components/OrchestratorStatusCard.tsx:31`
  - Get state color
  - Tags: color, get, components, state, autocoder

- **setupLobbyHandler** (my-games)
  - File: `apps/api/src/socket/lobbyHandler.ts:33`
  - Track active lobbies
  - Tags: api, lobbyhandler.ts, handler, socket, setup

- **formatNextRun** (my-games)
  - File: `autocoder/ui/src/lib/timeUtils.ts:158`
  - Format an ISO datetime string to a human-readable next run format.
  - Tags: timeutils.ts, next, autocoder, ui, format

- **createDirectory** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:282`
  - ============================================================================
  - Tags: api.ts, create, autocoder, directory, ui

- **formatDate** (my-games)
  - File: `apps/web/src/pages/SubscriptionsPage.tsx:192`
  - Tags: subscriptionspage.tsx, date, pages, web, apps

- **get_windows_drives** (my-games)
  - File: `autocoder/server/routers/filesystem.py:316`
  - List available drives (Windows only).

    Returns null on non-Windows platforms.

  - Tags: get, windows, drives, autocoder, filesystem.py

- **calculateEnPassantTargetAfterMove** (my-games)
  - File: `apps/api/src/game-engines/chess/game-state.ts:344`
  - Calculate en passant target after move
  - Tags: api, chess, passant, calculate, game-state.ts

- **getPlanPrice** (my-games)
  - File: `apps/web/src/pages/SubscriptionsPage.tsx:210`
  - Tags: subscriptionspage.tsx, price, get, pages, plan

- **getAllowedOrigins** (my-games)
  - File: `apps/api/src/config/cors.ts:11`
  - CORS Configuration
  - Tags: api, config, cors.ts, get, allowed

- **calculateChessAiMove** (my-games)
  - File: `games/chess/ai/index.ts:649`
  - No legal moves - this shouldn't happen if game isn't over
  - Tags: chess, calculate, games, ai, utility

- **createInitialState** (my-games)
  - File: `apps/web/src/pages/TicTacToeBoardTestPage.tsx:70`
  - ===========================================
  - Tags: tictactoeboardtestpage.tsx, pages, state, web, create

- **parsedRegistrationCloses** (my-games)
  - File: `apps/api/src/routes/admin.ts:934`
  - Validate game exists
  - Tags: api, routes, admin.ts, registration, closes

- **getWinningLine** (my-games)
  - File: `apps/web/src/pages/MatchReplayPage.tsx:235`
  - Get winning line for highlighting
  - Tags: get, line, pages, web, apps

- **setSoundEnabled** (my-games)
  - File: `apps/web/src/hooks/useSound.ts:246`
  - Play a sound effect
  - Tags: web, usesound.ts, enabled, hooks, set

- **getPlayerScores** (my-games)
  - File: `apps/api/src/game-engines/trivia/game-flow.ts:229`
  - Get player scores for a session
  - Tags: api, get, player, trivia, game-engines

- **updatedPlayer** (my-games)
  - File: `apps/api/src/routes/rooms.ts:672`
  - Find the player
  - Tags: api, routes, player, updated, apps

- **deleteSchedule** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:489`
  - Tags: delete, api.ts, schedule, autocoder, ui

- **get_agent_info** (my-games)
  - File: `autocoder/server/websocket.py:192`
  - Tags: get, info, autocoder, agent, websocket.py

- **getCancellationRules** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:189`
  - Chess needs more moves to be meaningful
  - Tags: api, rules, cancellation, get, socket

- **updateRookRights** (my-games)
  - File: `apps/api/src/game-engines/chess/game-state.ts:323`
  - If king moves, lose all castling rights for that color
  - Tags: api, update, chess, rook, game-state.ts

- **updateProjectPrompts** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:93`
  - Tags: update, api.ts, autocoder, project, ui

- **get_spec_file_status** (my-games)
  - File: `autocoder/server/routers/spec_creation.py:110`
  - Status of spec files on disk (from .spec_status.json).
  - Tags: file, spec_creation.py, get, spec, autocoder

- **parseEnPassantTarget** (my-games)
  - File: `apps/api/src/game-engines/chess/game-state.ts:133`
  - Parse castling rights from FEN
  - Tags: api, chess, passant, game-state.ts, target

- **get_status_dict** (my-games)
  - File: `autocoder/server/services/process_manager.py:498`
  - Process has terminated
  - Tags: services, get, server, process_manager.py, autocoder

- **getAllPossibleMoves** (my-games)
  - File: `apps/api/src/game-engines/checkers/rules.ts:318`
  - Get all possible moves for current player
  - Tags: api, possible, rules.ts, get, all

- **get_terminal_info** (my-games)
  - File: `autocoder/server/services/terminal_manager.py:695`
  - Remove a terminal session from the registry.

    Args:
        project_name: Name of the project
  
  - Tags: services, get, info, autocoder, terminal

- **formatDate** (my-games)
  - File: `apps/web/src/pages/TournamentDetailPage.tsx:175`
  - Default to participants/standings tab for completed tournaments
  - Tags: date, pages, web, apps, format

- **updateCheck** (my-games)
  - File: `apps/web/src/pages/HostBonusTestPage.tsx:87`
  - Tags: hostbonustestpage.tsx, update, pages, check, apps

- **validate_path** (my-games)
  - File: `autocoder/server/routers/filesystem.py:359`
  - Check if drive is accessible
  - Tags: validate, path, autocoder, filesystem.py, server

- **getKingAttacks** (my-games)
  - File: `apps/api/src/game-engines/chess/move-validation.ts:283`
  - Get king attack squares
  - Tags: api, chess, move-validation.ts, attacks, get

- **getCaptureMoves** (my-games)
  - File: `apps/web/src/pages/CheckersKingPromotionTestPage.tsx:128`
  - Tags: checkerskingpromotiontestpage.tsx, capture, get, pages, web

- **getMultiJumpSequences** (my-games)
  - File: `apps/api/src/game-engines/checkers/move-validation.ts:223`
  - Get all multi-jump sequences for a piece
  - Tags: api, move-validation.ts, get, jump, multi

- **getCommissionStats** (my-games)
  - File: `apps/api/src/services/referralXpCommissionService.ts:423`
  - Get commission statistics for a user
  - Tags: api, services, referralxpcommissionservice.ts, get, stats

- **get_app_spec** (my-games)
  - File: `autocoder/prompts.py:141`
  - base_prompt = get_coding_prompt(project_dir)

    # Minimal header - the base prompt already contain

  - Tags: prompts.py, get, app, spec, autocoder

- **formatDate** (my-games)
  - File: `apps/web/src/pages/AdminDashboardPage.tsx:1009`
  - Tags: admindashboardpage.tsx, date, pages, web, apps

- **validateMoveFromAlgebraic** (my-games)
  - File: `apps/api/src/game-engines/chess/chess-engine.ts:456`
  - Get half move clock
  - Tags: validate, api, algebraic, chess-engine.ts, chess

- **getStateDescription** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:558`
  - Get human-readable state description for accessibility
  - Tags: description, get, components, state, autocoder

- **getExpectedMultiplier** (my-games)
  - File: `apps/web/src/pages/StreakMultiplierTestPage.tsx:53`
  - Helper function for calculating expected multiplier
  - Tags: streakmultipliertestpage.tsx, get, pages, multiplier, apps

- **generatedFen** (my-games)
  - File: `apps/api/src/game-engines/chess/quick-test.ts:46`
  - Test 4: FEN parsing
  - Tags: api, generated, chess, game-engines, apps

- **getPiece** (my-games)
  - File: `games/checkers/server/index.ts:98`
  - Pieces only on dark squares (where (row + col) is odd)
  - Tags: get, server, games, piece, checkers

- **getPiece** (my-games)
  - File: `apps/web/src/pages/CheckersMultiJumpTestPage.tsx:66`
  - ===========================================
  - Tags: get, pages, piece, checkersmultijumptestpage.tsx, apps

- **generatedFen** (my-games)
  - File: `apps/api/src/game-engines/chess/test.ts:272`
  - Test 12: FEN parsing
  - Tags: api, generated, chess, game-engines, test.ts

- **validateCorsConfig** (my-games)
  - File: `apps/api/src/config/cors.ts:95`
  - Validate CORS configuration on startup
  - Tags: validate, cors, config, api, cors.ts

- **get_conversation_id** (my-games)
  - File: `autocoder/server/services/assistant_chat_session.py:416`
  - Store the complete response in the database
  - Tags: services, assistant_chat_session.py, get, conversation, autocoder

- **get_devserver_status** (my-games)
  - File: `autocoder/server/routers/devserver.py:115`
  - ============================================================================
  - Tags: get, server, autocoder, status, devserver

- **getSettingLabel** (my-games)
  - File: `apps/web/src/pages/SettingsPage.tsx:116`
  - Tags: label, get, pages, web, settingspage.tsx

- **get_project_path** (my-games)
  - File: `autocoder/registry.py:275`
  - Tags: get, path, autocoder, project, registry.py

- **get_new_project_info** (my-games)
  - File: `autocoder/start.py:131`
  - Tags: get, info, new, project, autocoder

- **parsedEvents** (my-games)
  - File: `apps/api/src/routes/matches.ts:1375`
  - Parse JSON fields
  - Tags: api, routes, matches.ts, events, parsed

- **parseTimeControlString** (my-games)
  - File: `apps/api/src/game-engines/chess/time-controls.ts:169`
  - Parse time control string (e.g., "10+5" for 10 minutes with 5 second increment)
  - Tags: api, chess, control, string, time-controls.ts

- **getCategoryColor** (my-games)
  - File: `autocoder/ui/src/components/FeatureCard.tsx:16`
  - Agent working on this feature
  - Tags: color, get, components, autocoder, category

- **getLegalMoves** (my-games)
  - File: `apps/web/src/pages/ChessCheckTestPage.tsx:242`
  - Check if a color's king is in check
  - Tags: get, pages, web, chesschecktestpage.tsx, legal

- **getCacheStats** (my-games)
  - File: `apps/ai-engine/src/cache.ts:101`
  - Global cache instance
  - Tags: cache, get, ai-engine, stats, cache.ts

- **get_single_feature_prompt** (my-games)
  - File: `autocoder/prompts.py:110`
  - ## ASSIGNED FEATURE

**You are assigned to regression test Feature #{testing_feature_id}.**

### You

  - Tags: feature, single, prompts.py, get, autocoder

- **deleteConversation** (my-games)
  - File: `autocoder/ui/src/components/ConversationHistory.tsx:56`
  - Tags: conversationhistory.tsx, delete, components, conversation, autocoder

- **updateHostMilestone** (my-games)
  - File: `apps/api/src/services/milestoneService.ts:97`
  - Update milestone progress for hosting a game
  - Tags: api, services, host, milestone, update

- **updateResult** (my-games)
  - File: `apps/web/src/pages/StreakResetTestPage.tsx:51`
  - Tags: update, pages, streakresettestpage.tsx, result, apps

- **get_project_dir** (my-games)
  - File: `autocoder/server/routers/devserver.py:61`
  - Validate and sanitize project name to prevent path traversal.
  - Tags: get, dir, autocoder, project, server

- **parsedRegistrationOpens** (my-games)
  - File: `apps/api/src/routes/admin.ts:933`
  - Validate required fields
  - Tags: api, routes, admin.ts, registration, opens

- **get_project_prompts_dir** (my-games)
  - File: `autocoder/prompts.py:19`
  - Prompt Loading Utilities

========================

Functions for loading prompt templates with proje

  - Tags: prompts.py, get, dir, autocoder, project

- **getStateDescription** (my-games)
  - File: `autocoder/ui/src/components/OrchestratorAvatar.tsx:132`
  - Get human-readable state description for accessibility
  - Tags: description, get, components, state, orchestratoravatar.tsx

- **sanitizeHtml** (my-games)
  - File: `apps/api/src/lib/validators.ts:281`
  - Sanitize HTML content to prevent XSS
  - Tags: api, html, validators.ts, apps, sanitize

- **setPiece** (my-games)
  - File: `games/chess/server/index.ts:121`
  - ===========================================
  - Tags: chess, games, piece, set, server

- **createInitialChessBoard** (my-games)
  - File: `apps/web/src/pages/ChessPreviewPage.tsx:48`
  - Chess piece Unicode symbols
  - Tags: chess, pages, web, create, board

- **getScoreBreakdown** (my-games)
  - File: `apps/api/src/game-engines/trivia/scoring.ts:123`
  - Get score breakdown
  - Tags: api, get, score, trivia, scoring.ts

- **get_engine** (my-games)
  - File: `autocoder/server/services/assistant_database.py:62`
  - Get the path to the assistant database for a project.
  - Tags: services, get, engine, assistant_database.py, autocoder

- **set** (my-games)
  - File: `apps/api/src/services/cacheService.ts:58`
  - Get value from cache
  - Tags: api, services, cacheservice.ts, set, apps

- **getMonthEnd** (my-games)
  - File: `apps/api/src/routes/games.ts:137`
  - 0 = Sunday
  - Tags: api, games.ts, routes, get, month

- **validateAndSanitizeEmail** (my-games)
  - File: `apps/api/src/lib/validators.ts:302`
  - Sanitize user input for display
  - Tags: validate, api, email, validators.ts, and

- **createTriviaAI** (my-games)
  - File: `apps/ai-engine/src/games/trivia.d.ts:31`
  - Tags: trivia.d.ts, ai-engine, create, games, trivia

- **getCardDisplay** (my-games)
  - File: `apps/api/src/game-engines/cards/utils.ts:24`
  - Get numeric value for a rank
  - Tags: api, get, utils.ts, display, cards

- **getStatusColor** (my-games)
  - File: `apps/web/src/pages/SubscriptionsPage.tsx:215`
  - Tags: color, subscriptionspage.tsx, get, pages, status

- **updated** (my-games)
  - File: `apps/api/src/routes/notifications.ts:65`
  - PATCH /api/notifications/:id/read - Mark notification as read
  - Tags: api, updated, apps, utility, notifications.ts

- **createFeature** (my-games)
  - File: `autocoder/ui/src/components/AddFeatureForm.tsx:25`
  - Tags: feature, components, create, autocoder, ui

- **getOpponent** (my-games)
  - File: `apps/api/src/game-engines/checkers/rules.ts:134`
  - Get opponent color
  - Tags: api, rules.ts, get, opponent, game-engines

- **get_project** (my-games)
  - File: `autocoder/server/routers/projects.py:210`
  - Register in registry
  - Tags: projects.py, get, autocoder, project, server

- **formatTime** (my-games)
  - File: `apps/api/src/game-engines/chess/time-controls.ts:144`
  - Get remaining time for a color
  - Tags: api, chess, time-controls.ts, game-engines, apps

- **setPiece** (my-games)
  - File: `games/chess/client/ChessBoard.tsx:111`
  - Clone the board for move simulation
  - Tags: chess, games, client, piece, chessboard.tsx

- **formatDuration** (my-games)
  - File: `apps/web/src/pages/MatchPage.tsx:166`
  - Tags: matchpage.tsx, pages, duration, web, apps

- **getSimpleMoves** (my-games)
  - File: `apps/web/src/pages/CheckersMultiJumpTestPage.tsx:130`
  - Check if any piece of the given color has a capture available
  - Tags: get, pages, web, simple, checkersmultijumptestpage.tsx

- **validate_concurrency** (my-games)
  - File: `autocoder/server/schemas.py:186`
  - Validate model is in the allowed list.
  - Tags: validate, concurrency, schemas.py, autocoder, server

- **getPiece** (my-games)
  - File: `apps/web/src/pages/ChessEnPassantTestPage.tsx:58`
  - ===========================================
  - Tags: get, pages, chessenpassanttestpage.tsx, piece, apps

- **validate_chmod_command** (my-games)
  - File: `autocoder/security.py:270`
  - The target is typically the last non-flag argument
  - Tags: validate, command, autocoder, security.py, chmod

- **deleteRooms** (my-games)
  - File: `apps/api/src/test/setup.ts:21`
  - Setup database connection for tests
  - Tags: api, delete, setup.ts, rooms, apps

- **formatRelativeTime** (my-games)
  - File: `autocoder/ui/src/components/OrchestratorStatusCard.tsx:48`
  - Get state color
  - Tags: components, utility, autocoder, orchestratorstatuscard.tsx, ui

- **validateFEN** (my-games)
  - File: `apps/api/src/game-engines/chess/game-state.ts:378`
  - Clone game state
  - Tags: validate, api, chess, game-state.ts, game-engines

- **validateEmail** (my-games)
  - File: `apps/web/src/pages/RegisterPage.tsx:74`
  - Unsaved changes protection
  - Tags: validate, registerpage.tsx, pages, email, apps

- **getPlayerName** (my-games)
  - File: `apps/web/src/pages/MatchHistoryPage.tsx:100`
  - Tags: name, get, pages, player, matchhistorypage.tsx

- **getLegalMoves** (my-games)
  - File: `apps/web/src/pages/ChessCastlingTestPage.tsx:200`
  - Get legal moves including castling
  - Tags: get, pages, web, chesscastlingtestpage.tsx, legal

- **create_conversation** (my-games)
  - File: `autocoder/server/services/assistant_database.py:93`
  - Get a new database session for a project.
  - Tags: services, create, conversation, assistant_database.py, autocoder

- **create_client** (my-games)
  - File: `autocoder/client.py:124`
  - Browser management
  - Tags: create, client, autocoder, client.py, utility

- **getStreakCount** (my-games)
  - File: `apps/api/src/game-engines/trivia/validation.ts:120`
  - Get user's current streak count in a session
  - Tags: api, get, count, trivia, streak

- **createPaginationLinks** (my-games)
  - File: `apps/api/src/lib/pagination.ts:73`
  - Create pagination links for API response headers
  - Tags: api, links, pagination, create, pagination.ts

- **parsePagination** (my-games)
  - File: `apps/api/src/lib/pagination.ts:21`
  - Parse pagination parameters from request query
  - Tags: api, pagination, pagination.ts, parse, apps

- **getGameState** (my-games)
  - File: `apps/api/src/game-engines/trivia/game-flow.ts:359`
  - Cleanup game state (call when session is complete)
  - Tags: api, game, get, state, trivia

- **getMoveHint** (my-games)
  - File: `apps/api/src/game-engines/checkers/rules.ts:438`
  - Get move hint for current player
  - Tags: hint, api, rules.ts, get, checkers

- **getSimpleMoves** (my-games)
  - File: `games/checkers/server/index.ts:114`
  - Get all possible simple moves (non-captures) for a piece
  - Tags: get, server, games, checkers, simple

- **getSpecStatus** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:257`
  - ============================================================================
  - Tags: ui, get, api.ts, spec, autocoder

- **getNextQuestion** (my-games)
  - File: `apps/api/src/game-engines/trivia/game-flow.ts:189`
  - Get the next question
  - Tags: api, get, question, next, trivia

- **get_existing_projects** (my-games)
  - File: `autocoder/start.py:65`
  - Check legacy location in project root
  - Tags: projects, get, autocoder, start.py, existing

- **setPiece** (my-games)
  - File: `apps/web/src/pages/ChessCastlingTestPage.tsx:65`
  - Helper functions (matching server logic)
  - Tags: pages, piece, chesscastlingtestpage.tsx, set, apps

- **get_expand_session_status** (my-games)
  - File: `autocoder/server/routers/expand_project.py:68`
  - Status of an expansion session.
  - Tags: expand_project.py, session, get, expand, autocoder

- **formatDate** (my-games)
  - File: `apps/admin/src/pages/Tournaments.tsx:70`
  - Tags: date, pages, tournaments.tsx, admin, apps

- **createBackRankMate** (my-games)
  - File: `apps/web/src/pages/ChessCheckmateTestPage.tsx:345`
  - e4
  - Tags: pages, back, create, mate, apps

- **validate_project_name** (my-games)
  - File: `autocoder/server/routers/devserver.py:51`
  - Get project path from registry.
  - Tags: validate, name, autocoder, project, server

- **get_devserver_manager** (my-games)
  - File: `autocoder/server/services/dev_server_manager.py:435`
  - Get current status as a dictionary.
  - Tags: services, manager, get, server, autocoder

- **getPerformanceReport** (my-games)
  - File: `apps/api/src/lib/performance.ts:289`
  - Memory usage tracker
  - Tags: api, get, report, apps, performance

- **setPieceAt** (my-games)
  - File: `apps/api/src/game-engines/chess/board-utils.ts:67`
  - Convert array indices to square
  - Tags: api, board-utils.ts, chess, piece, set

- **getLegalMoves** (my-games)
  - File: `apps/api/src/game-engines/chess/rules.ts:68`
  - Get all legal moves for a color (excluding moves that would leave king in check)
  - Tags: api, rules.ts, chess, get, game-engines

- **getUserLevelInfo** (my-games)
  - File: `apps/api/src/services/levelService.ts:176`
  - Get level information for display
  - Tags: api, services, levelservice.ts, get, level

- **parseSort** (my-games)
  - File: `apps/api/src/lib/fields.ts:120`
  - Parse sort parameter
  - Tags: api, fields.ts, sort, parse, apps

- **getSessionDetails** (my-games)
  - File: `apps/api/src/game-engines/trivia/game-flow.ts:320`
  - Get session details
  - Tags: api, session, get, trivia, details

- **validateDateRanges** (my-games)
  - File: `apps/web/src/pages/AdminDashboardPage.tsx:366`
  - Helper function to get current datetime in format suitable for datetime-local input
  - Tags: validate, admindashboardpage.tsx, date, pages, apps

- **formatCredits** (my-games)
  - File: `apps/web/src/pages/TournamentsPage.tsx:268`
  - Refresh tournaments list
  - Tags: tournamentspage.tsx, pages, web, apps, format

- **deleteInProgressRef** (my-games)
  - File: `apps/web/src/pages/AdminDashboardPage.tsx:285`
  - Delete tournament state
  - Tags: delete, admindashboardpage.tsx, pages, progress, ref

- **calculateWinner** (my-games)
  - File: `games/card-games/server/index.ts:155`
  - ===========================================
  - Tags: winner, card-games, calculate, games, server

- **getReferralTree** (my-games)
  - File: `apps/web/src/pages/Level3ReferralTestPage.tsx:103`
  - Wallet API returns creditsBalance directly (not nested in data)
  - Tags: level3referraltestpage.tsx, get, tree, pages, apps

- **formatTimestamp** (my-games)
  - File: `autocoder/ui/src/components/ActivityFeed.tsx:18`
  - Tags: activityfeed.tsx, components, timestamp, autocoder, ui

- **get_conversations** (my-games)
  - File: `autocoder/server/services/assistant_database.py:110`
  - Create a new conversation for a project.
  - Tags: services, get, assistant_database.py, autocoder, server

- **getTimeRemaining** (my-games)
  - File: `apps/web/src/pages/StorePage.tsx:237`
  - Refresh history
  - Tags: storepage.tsx, get, time, pages, apps

- **getWeekEnd** (my-games)
  - File: `apps/api/src/routes/games.ts:122`
  - Helper functions for calendar-based date calculations
  - Tags: api, week, games.ts, routes, get

- **formatDate** (my-games)
  - File: `apps/admin/src/components/AuditLog.tsx:71`
  - For now, show empty state since audit logs might not be fully implemented
  - Tags: date, components, auditlog.tsx, admin, apps

- **getRawMoves** (my-games)
  - File: `apps/web/src/pages/ChessEnPassantTestPage.tsx:82`
  - Get raw moves (for attack checking)
  - Tags: get, pages, chessenpassanttestpage.tsx, web, raw

- **calculateTTTAiMove** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:623`
  - Tags: api, socket, calculate, matchhandler.ts, apps

- **getRawMoves** (my-games)
  - File: `apps/web/src/pages/ChessPawnPromotionTestPage.tsx:82`
  - Get raw moves (for attack checking)
  - Tags: chesspawnpromotiontestpage.tsx, get, pages, web, raw

- **getStatusBadge** (my-games)
  - File: `apps/web/src/pages/FeedbackPage.tsx:284`
  - Update feedback count in list
  - Tags: badge, get, pages, feedbackpage.tsx, status

- **get_session_info** (my-games)
  - File: `autocoder/server/routers/assistant_chat.py:185`
  - List all active assistant sessions.
  - Tags: session, get, info, autocoder, server

- **getEmptyCells** (my-games)
  - File: `games/tic-tac-toe/ai/index.ts:35`
  - Columns
  - Tags: get, tic-tac-toe, games, cells, empty

- **createPrismaQueryTracker** (my-games)
  - File: `apps/api/src/lib/performance.ts:220`
  - Prisma middleware for query tracking
  - Tags: api, prisma, create, query, tracker

- **validate_project_name** (my-games)
  - File: `autocoder/server/routers/terminal.py:56`
  - WebSocket close codes for terminal endpoint.
  - Tags: validate, name, terminal.py, autocoder, project

- **calculateChessLegalMoves** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:619`
  - Tags: chess, pages, calculate, web, gameplaypage.tsx

- **get_project_info** (my-games)
  - File: `autocoder/registry.py:318`
  - Get all registered projects.

    Returns:
        Dictionary mapping project names to their info di

  - Tags: get, info, autocoder, project, registry.py

- **updatedWallet** (my-games)
  - File: `apps/api/src/routes/admin.ts:1143`
  - Refund participants
  - Tags: api, routes, admin.ts, wallet, updated

- **validateEnPassant** (my-games)
  - File: `apps/api/src/game-engines/chess/special-moves.ts:129`
  - Validate en passant capture
  - Tags: validate, api, chess, passant, special-moves.ts

- **settingKeys** (my-games)
  - File: `apps/web/src/pages/SettingsPage.tsx:140`
  - Get the setting name for specific feedback
  - Tags: pages, keys, utility, settingspage.tsx, apps

- **setupTestUser** (my-games)
  - File: `apps/web/src/pages/CreditDeductionTestPage.tsx:92`
  - Initialize: record initial balance
  - Tags: pages, setup, creditdeductiontestpage.tsx, user, apps

- **getPawnAttacks** (my-games)
  - File: `apps/api/src/game-engines/chess/move-validation.ts:310`
  - Get pawn attack squares (excluding en passant)
  - Tags: api, chess, move-validation.ts, attacks, get

- **updateCastlingRights** (my-games)
  - File: `apps/api/src/game-engines/chess/special-moves.ts:248`
  - Update castling rights after a move
  - Tags: api, update, chess, special-moves.ts, rights

- **get_messages** (my-games)
  - File: `autocoder/server/services/expand_chat_session.py:442`
  - Get the total number of features created in this session.
  - Tags: messages, services, get, expand_chat_session.py, autocoder

- **getEnPassantMove** (my-games)
  - File: `apps/api/src/game-engines/chess/special-moves.ts:345`
  - Get en passant move
  - Tags: api, chess, passant, get, special-moves.ts

- **updatedUser** (my-games)
  - File: `apps/web/src/pages/ProfilePage.tsx:455`
  - Update local state and localStorage
  - Tags: pages, profilepage.tsx, user, updated, apps

- **get_session** (my-games)
  - File: `autocoder/server/services/assistant_chat_session.py:426`
  - Get the current conversation ID.
  - Tags: services, session, assistant_chat_session.py, get, autocoder

- **getAgentTypeBadge** (my-games)
  - File: `autocoder/ui/src/components/AgentCard.tsx:54`
  - Yellow - just pivoting, not a real error
  - Tags: badge, ui, get, components, agentcard.tsx

- **updateSettings** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:378`
  - ============================================================================
  - Tags: update, api.ts, autocoder, settings, ui

- **createCheckPosition1** (my-games)
  - File: `apps/web/src/pages/ChessCheckTestPage.tsx:279`
  - Check if any legal moves exist for a color
  - Tags: pages, create, chesschecktestpage.tsx, check, position

- **formatDate** (my-games)
  - File: `apps/web/src/pages/MatchHistoryPage.tsx:89`
  - Tags: date, pages, web, matchhistorypage.tsx, apps

- **getInitials** (my-games)
  - File: `apps/web/src/components/OptimizedImage.tsx:175`
  - Get initials from username
  - Tags: get, components, initials, apps, web

- **createCheckPosition3** (my-games)
  - File: `apps/web/src/pages/ChessCheckTestPage.tsx:297`
  - Queen on same file as black king - CHECK!
  - Tags: pages, create, chesschecktestpage.tsx, check, position

- **updatedMatch** (my-games)
  - File: `apps/api/src/routes/matches.ts:541`
  - Get the current game state
  - Tags: api, routes, match, matches.ts, updated

- **createMove** (my-games)
  - File: `apps/api/src/game-engines/chess/board-utils.ts:190`
  - Get opponent color
  - Tags: api, board-utils.ts, chess, create, game-engines

- **createInitialChessBoard** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:683`
  - Create initial chess board for display
  - Tags: chess, pages, web, gameplaypage.tsx, create

- **getPositionLabel** (my-games)
  - File: `apps/web/src/pages/TournamentPrizeTestPage.tsx:187`
  - Filter to tournament_complete notifications
  - Tags: label, tournamentprizetestpage.tsx, get, position, pages

- **validateCardPlay** (my-games)
  - File: `apps/api/src/socket/handlers/gameHandler.ts:708`
  - Base score of 1000, reduced by response time
  - Tags: validate, api, socket, play, handlers

- **calculateTriviaScore** (my-games)
  - File: `apps/api/src/socket/handlers/gameHandler.ts:701`
  - Tags: api, socket, calculate, score, trivia

- **getPawnStartRank** (my-games)
  - File: `apps/api/src/game-engines/chess/board-utils.ts:215`
  - Check if move is a capture
  - Tags: api, board-utils.ts, chess, get, game-engines

- **createEmptyChessBoard** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:715`
  - Tags: chess, pages, gameplaypage.tsx, create, board

- **getPlayerName** (my-games)
  - File: `apps/web/src/pages/MatchReplayPage.tsx:180`
  - Tags: name, get, pages, player, apps

- **deleteAccountLockouts** (my-games)
  - File: `apps/api/src/test/setup.ts:25`
  - Cleanup database connection
  - Tags: api, delete, account, setup.ts, lockouts

- **getTestAuthToken** (my-games)
  - File: `apps/api/src/test/setup.ts:70`
  - Helper to get auth token for tests
  - Tags: api, setup.ts, get, token, auth

- **getWinningLine** (my-games)
  - File: `apps/web/src/pages/TicTacToeBoardTestPage.tsx:56`
  - Bottom row
  - Tags: tictactoeboardtestpage.tsx, get, line, pages, web

- **getLevelTitle** (my-games)
  - File: `apps/api/src/services/levelService.ts:216`
  - Level titles/names based on level ranges (optional cosmetic feature)
  - Tags: api, services, levelservice.ts, get, level

- **get_command_for_validation** (my-games)
  - File: `autocoder/security.py:340`
  - The command should be exactly ./init.sh (possibly with arguments)
  - Tags: get, validation, for, command, autocoder

- **getMovementDirections** (my-games)
  - File: `games/checkers/server/index.ts:129`
  - Get all possible simple moves (non-captures) for a piece
  - Tags: directions, movement, get, server, games

- **parsedAnswers** (my-games)
  - File: `apps/api/src/routes/trivia.ts:322`
  - Parse options for each question
  - Tags: answers, api, routes, trivia.ts, parsed

- **get_coding_prompt** (my-games)
  - File: `autocoder/prompts.py:72`
  - Load the initializer prompt (project-specific if available).
  - Tags: prompts.py, get, autocoder, coding, utility

- **validate_pkill_command** (my-games)
  - File: `autocoder/security.py:222`
  - Skip flags/options
  - Tags: validate, pkill, command, autocoder, security.py

- **get_terminal_session** (my-games)
  - File: `autocoder/server/services/terminal_manager.py:644`
  - Remove session if exists (will be stopped async by caller)
  - Tags: services, session, get, autocoder, terminal

- **get_dependency_graph** (my-games)
  - File: `autocoder/server/routers/features.py:314`
  - Tags: graph, get, features.py, autocoder, server

- **createInitialChessState** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:4143`
  - Count position occurrences in history
  - Tags: api, chess, socket, state, create

- **getYearStart** (my-games)
  - File: `apps/api/src/routes/leaderboards.ts:37`
  - Last day of current month
  - Tags: api, routes, get, leaderboards.ts, start

- **updatedWallet** (my-games)
  - File: `apps/api/src/routes/auth.ts:558`
  - Get or create wallet
  - Tags: api, routes, wallet, auth.ts, updated

- **createInitialBoard** (my-games)
  - File: `games/chess/server/index.ts:72`
  - For pawn promotion
  - Tags: chess, server, create, board, games

- **get_all_settings** (my-games)
  - File: `autocoder/registry.py:501`
  - Tags: get, all, autocoder, settings, registry.py

- **getLegalMoves** (my-games)
  - File: `apps/web/src/pages/ChessEnPassantTestPage.tsx:200`
  - Get legal moves including en passant
  - Tags: get, pages, chessenpassanttestpage.tsx, web, legal

- **getCardValue** (my-games)
  - File: `games/card-games/server/index.ts:74`
  - For blackjack variant
  - Tags: get, card-games, server, value, games

- **createInitialCheckersState** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:5417`
  - 0 for red, 1 for black
  - Tags: api, socket, state, create, checkers

- **getPiece** (my-games)
  - File: `apps/web/src/pages/ChessCheckmateTestPage.tsx:56`
  - File and rank labels
  - Tags: get, pages, piece, apps, web

- **createSeededRandom** (my-games)
  - File: `apps/web/src/pages/TriviaGameTestPage.tsx:170`
  - Geography - Easy
  - Tags: triviagametestpage.tsx, pages, seeded, create, random

- **delete_schedule** (my-games)
  - File: `autocoder/server/routers/schedules.py:349`
  - Tags: delete, schedule, autocoder, schedules.py, server

- **setPiece** (my-games)
  - File: `apps/web/src/pages/ChessEnPassantTestPage.tsx:65`
  - Helper functions (matching server logic)
  - Tags: pages, chessenpassanttestpage.tsx, piece, set, apps

- **calculateTotalCredits** (my-games)
  - File: `apps/api/src/routes/topups.ts:72`
  - $34.99
  - Tags: api, routes, calculate, total, topups.ts

- **updatedGame** (my-games)
  - File: `apps/api/src/routes/admin.ts:790`
  - Tags: api, game, routes, admin.ts, updated

- **getPiece** (my-games)
  - File: `apps/web/src/pages/ChessCheckTestPage.tsx:56`
  - File and rank labels
  - Tags: get, pages, chesschecktestpage.tsx, piece, apps

- **updateFeature** (my-games)
  - File: `autocoder/ui/src/components/EditFeatureForm.tsx:32`
  - Tags: feature, update, components, editfeatureform.tsx, autocoder

- **createResponse** (my-games)
  - File: `apps/web/src/pages/XpWinTestPage.tsx:93`
  - Step 2: Create and win an AI match
  - Tags: response, pages, create, apps, web

- **setCsrfCookie** (my-games)
  - File: `apps/api/src/middleware/csrf.ts:65`
  - Set CSRF token cookie
  - Tags: api, csrf.ts, middleware, set, cookie

- **calculateFinalStats** (my-games)
  - File: `apps/api/src/game-engines/trivia/scoring.ts:148`
  - Calculate final game statistics
  - Tags: api, calculate, stats, trivia, scoring.ts

- **formatDuration** (my-games)
  - File: `autocoder/ui/src/lib/timeUtils.ts:143`
  - Format a duration in minutes to a human-readable string.
  - Tags: duration, autocoder, ui, format, timeutils.ts

- **createEmptyBoard** (my-games)
  - File: `apps/web/src/pages/ChessEnPassantTestPage.tsx:415`
  - ===========================================
  - Tags: pages, chessenpassanttestpage.tsx, create, board, empty

- **formatNumber** (my-games)
  - File: `apps/web/src/pages/WalletPage.tsx:533`
  - Tags: pages, web, number, walletpage.tsx, apps

- **parsedStartsAt** (my-games)
  - File: `apps/api/src/routes/admin.ts:937`
  - Parse dates
  - Tags: api, routes, starts, admin.ts, parsed

- **getChessPiece** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:444`
  - ===========================================
  - Tags: chess, get, pages, gameplaypage.tsx, piece

- **createAndShuffleDeck** (my-games)
  - File: `games/card-games/server/index.ts:99`
  - CRITICAL: This function performs server-side deck shuffling
  - Tags: card-games, create, shuffle, games, and

- **deleteTerminal** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:444`
  - Tags: delete, api.ts, autocoder, terminal, ui

- **createUserB** (my-games)
  - File: `apps/web/src/pages/Level2ReferralTestPage.tsx:107`
  - Step 2: Create User B using User A's referral code
  - Tags: pages, create, user, level2referraltestpage.tsx, apps

- **getHitRate** (my-games)
  - File: `apps/api/src/lib/cache/cacheService.ts:158`
  - Get cache statistics
  - Tags: api, cache, get, cacheservice.ts, hit

- **getPromotionSquares** (my-games)
  - File: `apps/api/src/game-engines/checkers/king-promotion.ts:100`
  - Check if a move sequence results in promotion
  - Tags: api, get, squares, game-engines, king-promotion.ts

- **validatePromotion** (my-games)
  - File: `apps/api/src/game-engines/chess/special-moves.ts:203`
  - Check if pawn promotion is valid
  - Tags: validate, api, chess, special-moves.ts, game-engines

- **validate_project_name** (my-games)
  - File: `autocoder/server/routers/schedules.py:47`
  - Get project path from registry.
  - Tags: validate, name, autocoder, project, schedules.py

- **updateCheck** (my-games)
  - File: `apps/web/src/pages/XpWinTestPage.tsx:46`
  - Tags: update, pages, check, apps, web

- **get_scheduler** (my-games)
  - File: `autocoder/server/services/scheduler_service.py:668`
  - Global scheduler instance
  - Tags: services, get, scheduler_service.py, autocoder, server

- **create_features_bulk** (my-games)
  - File: `autocoder/server/routers/features.py:225`
  - ============================================================================
  - Tags: bulk, features.py, create, features, autocoder

- **calculateEnPassantTarget** (my-games)
  - File: `apps/api/src/game-engines/chess/special-moves.ts:287`
  - Calculate en passant target square after a move
  - Tags: api, chess, passant, calculate, special-moves.ts

- **getCachedEvaluation** (my-games)
  - File: `apps/ai-engine/src/cache.ts:93`
  - Global cache instance
  - Tags: get, ai-engine, evaluation, cache.ts, apps

- **getCastlingMove** (my-games)
  - File: `apps/api/src/game-engines/chess/special-moves.ts:314`
  - Get castling move
  - Tags: api, chess, get, special-moves.ts, castling

- **get_session** (my-games)
  - File: `autocoder/mcp_server/feature_mcp.py:128`
  - Create project directory if it doesn't exist
  - Tags: mcp_server, session, get, feature_mcp.py, autocoder

- **get_ready_features** (my-games)
  - File: `autocoder/parallel_orchestrator.py:262`
  - Sort by scheduling score (higher = first), then priority, then id
  - Tags: get, features, autocoder, parallel_orchestrator.py, ready

- **getStatusColor** (my-games)
  - File: `apps/web/src/pages/Level3ReferralTestPage.tsx:225`
  - Tags: color, level3referraltestpage.tsx, get, pages, status

- **getMinDateTime** (my-games)
  - File: `apps/web/src/pages/AdminDashboardPage.tsx:359`
  - Helper function to get current datetime in format suitable for datetime-local input
  - Tags: admindashboardpage.tsx, date, get, min, pages

- **setAuthCookie** (my-games)
  - File: `apps/api/src/middleware/auth.ts:14`
  - Set JWT token as httpOnly cookie
  - Tags: api, auth, set, auth.ts, cookie

- **getDayStart** (my-games)
  - File: `apps/api/src/routes/games.ts:144`
  - Tags: api, games.ts, routes, get, start

- **createSampleCheckersBoard** (my-games)
  - File: `apps/ai-engine/tests/ai.test.ts:28`
  - Helper to create a sample checkers board
  - Tags: ai-engine, create, board, sample, ai.test.ts

- **createCheckersAI** (my-games)
  - File: `apps/ai-engine/src/games/checkers.d.ts:24`
  - Tags: checkers.d.ts, ai-engine, create, games, apps

- **updatedWallet** (my-games)
  - File: `apps/api/src/services/referralXpCommissionService.ts:223`
  - Award the XP to the user's wallet
  - Tags: api, services, referralxpcommissionservice.ts, wallet, updated

- **createTerminal** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:423`
  - ============================================================================
  - Tags: api.ts, create, autocoder, terminal, ui

- **getAiXpEarnedToday** (my-games)
  - File: `apps/api/src/services/walletService.ts:97`
  - Get the amount of XP earned from AI matches today for a user
  - Tags: api, services, get, walletservice.ts, apps

- **createFeaturesBulk** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:145`
  - Tags: bulk, api.ts, create, features, autocoder

- **getAudioContext** (my-games)
  - File: `apps/web/src/hooks/useSound.ts:86`
  - Cache the sound enabled setting
  - Tags: context, get, audio, usesound.ts, hooks

- **getInitialGameState** (my-games)
  - File: `apps/api/src/routes/rooms.ts:1025`
  - Initialize game state for a match
  - Tags: api, game, routes, get, state

- **settleCreditsMatch** (my-games)
  - File: `apps/api/src/services/walletService.ts:699`
  - True if entry fees were refunded instead of settled
  - Tags: api, services, match, settle, walletservice.ts

- **delete_project** (my-games)
  - File: `autocoder/server/routers/projects.py:238`
  - Tags: delete, projects.py, autocoder, project, server

- **parseOptions** (my-games)
  - File: `apps/api/src/game-engines/trivia/question-selection.ts:150`
  - Parse options from JSON string
  - Tags: api, question-selection.ts, trivia, options, game-engines

- **updatedUser** (my-games)
  - File: `apps/api/src/routes/auth.ts:920`
  - Update the user's login streak directly
  - Tags: api, routes, user, auth.ts, updated

- **create_terminal** (my-games)
  - File: `autocoder/server/services/terminal_manager.py:532`
  - Global registry of terminal sessions per project with thread safety
  - Tags: services, create, autocoder, terminal, server

- **calculateWinner** (my-games)
  - File: `games/trivia/server/index.ts:429`
  - Tags: winner, calculate, games, trivia, server

- **getMovementDirections** (my-games)
  - File: `apps/web/src/pages/CheckersMultiJumpTestPage.tsx:82`
  - Get movement directions based on piece type and color
  - Tags: directions, movement, get, pages, checkersmultijumptestpage.tsx

- **createAssistantConversation** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:348`
  - Tags: api.ts, create, conversation, autocoder, ui

- **getLegalMoves** (my-games)
  - File: `apps/api/src/game-engines/checkers/move-validation.ts:418`
  - Get all legal moves for a player
  - Tags: api, move-validation.ts, get, checkers, game-engines

- **updateResult** (my-games)
  - File: `apps/api/src/services/milestoneService.ts:348`
  - Get all tournament win milestones
  - Tags: api, services, update, result, apps

- **sanitizedMessage** (my-games)
  - File: `apps/api/src/routes/tournaments.ts:1338`
  - Check if user is a participant
  - Tags: api, sanitized, routes, message, apps

- **getRemainingTime** (my-games)
  - File: `apps/api/src/game-engines/chess/time-controls.ts:137`
  - Get winner by flag fall
  - Tags: api, chess, get, remaining, time-controls.ts

- **getGameAdapter** (my-games)
  - File: `apps/api/src/game-engines/registry.ts:18`
  - Tags: api, game, adapter, get, registry.ts

- **get_features_created** (my-games)
  - File: `autocoder/server/services/expand_chat_session.py:434`
  - Tags: services, get, expand_chat_session.py, features, created

- **getStatusColor** (my-games)
  - File: `apps/admin/src/pages/Tournaments.tsx:74`
  - Tags: color, get, tournaments.tsx, admin, status

- **createStandardDeck** (my-games)
  - File: `games/card-games/server/index.ts:80`
  - ===========================================
  - Tags: card-games, standard, create, games, deck

- **formatDuration** (my-games)
  - File: `apps/web/src/pages/AdminDashboardPage.tsx:617`
  - Tags: admindashboardpage.tsx, pages, duration, web, apps

- **deleteProject** (my-games)
  - File: `autocoder/ui/src/components/ProjectSelector.tsx:27`
  - Tags: delete, projectselector.tsx, components, autocoder, project

- **createInitialBoard** (my-games)
  - File: `apps/web/src/pages/CheckersBoardTestPage.tsx:32`
  - ===========================================
  - Tags: checkersboardtestpage.tsx, pages, web, create, board

- **getPiece** (my-games)
  - File: `apps/web/src/pages/ChessPawnPromotionTestPage.tsx:58`
  - ===========================================
  - Tags: chesspawnpromotiontestpage.tsx, get, pages, piece, apps

- **get_testing_prompt** (my-games)
  - File: `autocoder/prompts.py:77`
  - Load the initializer prompt (project-specific if available).
  - Tags: testing, prompts.py, get, autocoder, utility

- **calculatePeriodFilter** (my-games)
  - File: `apps/api/src/routes/games.ts:163`
  - Tags: api, games.ts, routes, calculate, filter

- **getTranslation** (my-games)
  - File: `apps/web/src/i18n/translations.ts:292`
  - Tags: get, translations.ts, translation, i18n, apps

- **createChessAI** (my-games)
  - File: `apps/ai-engine/src/games/chess.d.ts:28`
  - Tags: chess.d.ts, chess, ai-engine, create, games

- **validatePagination** (my-games)
  - File: `apps/api/src/lib/pagination.ts:132`
  - Validate pagination parameters
  - Tags: validate, api, pagination, pagination.ts, apps

- **getCardValue** (my-games)
  - File: `apps/api/src/game-engines/cards/utils.ts:12`
  - Card Games Engine - Card Utilities
  - Tags: api, get, utils.ts, value, cards

- **formattedPlayer** (my-games)
  - File: `apps/api/src/routes/rooms.ts:435`
  - Emit socket event for real-time update
  - Tags: api, routes, player, formatted, apps

- **getCacheStats** (my-games)
  - File: `apps/api/src/services/cacheService.ts:389`
  - Cache statistics
  - Tags: api, services, cache, get, cacheservice.ts

- **get_agent_status** (my-games)
  - File: `autocoder/server/routers/agent.py:86`
  - Tags: agent.py, get, autocoder, agent, status

- **createSmotheredMate** (my-games)
  - File: `apps/web/src/pages/ChessCheckmateTestPage.tsx:410`
  - f2 pawn moved to f3
  - Tags: pages, create, mate, smothered, apps

- **getSquaresForColor** (my-games)
  - File: `apps/api/src/game-engines/chess/board-utils.ts:97`
  - Check if square has piece of specific color
  - Tags: api, color, board-utils.ts, chess, get

- **getPromotionRow** (my-games)
  - File: `apps/api/src/game-engines/checkers/king-promotion.ts:174`
  - Get promotion row for a player
  - Tags: api, get, checkers, game-engines, king-promotion.ts

- **validateChessMove** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:5094`
  - Chess move validation
  - Tags: validate, api, chess, socket, matchhandler.ts

- **getStatusIcon** (my-games)
  - File: `apps/web/src/pages/Level3ReferralTestPage.tsx:216`
  - Tags: level3referraltestpage.tsx, icon, get, pages, status

- **get_status** (my-games)
  - File: `autocoder/parallel_orchestrator.py:1116`
  - Use short timeout since we're just waiting for final agents to finish
  - Tags: get, autocoder, parallel_orchestrator.py, status, utility

- **getJumpMoves** (my-games)
  - File: `apps/api/src/game-engines/checkers/move-validation.ts:170`
  - Get all jump moves for a piece
  - Tags: api, move-validation.ts, get, jump, checkers

- **createAndShuffleDeck** (my-games)
  - File: `games/shit-happens/server/index.ts:124`
  - ===========================================
  - Tags: shit-happens, create, shuffle, games, and

- **createInitialState** (my-games)
  - File: `apps/api/src/game-engines/checkers/board.ts:58`
  - Create initial game state
  - Tags: api, state, create, checkers, game-engines

- **generateTwoFactorSecret** (my-games)
  - File: `apps/api/src/lib/twoFactor.ts:15`
  - Two-Factor Authentication Service
  - Tags: api, two, twofactor.ts, generate, secret

- **createTimeControlFromString** (my-games)
  - File: `apps/api/src/game-engines/chess/time-controls.ts:203`
  - Create time control from string
  - Tags: api, chess, control, from, string

- **get_all_passing_features** (my-games)
  - File: `autocoder/progress.py:108`
  - SELECT

                    COUNT(*) as total,
                    SUM(CASE WHEN passes = 1 THEN 1 EL

  - Tags: get, all, features, passing, progress.py

- **formatCredits** (my-games)
  - File: `apps/web/src/pages/TournamentDetailPage.tsx:194`
  - Tags: pages, web, tournamentdetailpage.tsx, apps, format

- **validateCheckersMoveInternally** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:5452`
  - Validate checkers move
  - Tags: validate, api, socket, utility, internally

- **parsed** (my-games)
  - File: `apps/api/src/game-engines/chess/time-controls.ts:204`
  - Create time control from string
  - Tags: api, parsed, chess, time-controls.ts, game-engines

- **get_database_url** (my-games)
  - File: `autocoder/api/database.py:186`
  - Return the path to the SQLite database for a project.
  - Tags: api, url, get, database.py, autocoder

- **getRoundName** (my-games)
  - File: `apps/api/src/routes/tournaments.ts:399`
  - Generate round names
  - Tags: api, name, routes, round, get

- **updatedTournament** (my-games)
  - File: `apps/api/src/routes/tournaments.ts:941`
  - Update tournament status to in_progress
  - Tags: api, routes, tournament, updated, apps

- **formatTime** (my-games)
  - File: `apps/web/src/pages/MatchReplayPage.tsx:189`
  - Tags: pages, web, apps, format, matchreplaypage.tsx

- **getWinStreakBonusPercent** (my-games)
  - File: `apps/api/src/services/walletService.ts:138`
  - Get the win streak bonus percentage based on current streak
  - Tags: api, services, get, win, streak

- **get_db** (my-games)
  - File: `autocoder/api/database.py:385`
  - Set the global session maker.
  - Tags: api, get, database.py, autocoder, utility

- **formatTime** (my-games)
  - File: `apps/web/src/components/NotificationsDropdown.tsx:172`
  - Tags: components, web, notificationsdropdown.tsx, apps, format

- **updated** (my-games)
  - File: `apps/api/src/routes/matches.ts:583`
  - Update the forfeiting player
  - Tags: api, matches.ts, updated, apps, utility

- **getXpForLevel** (my-games)
  - File: `apps/api/src/services/levelService.ts:32`
  - Calculate the total XP required to reach a given level
  - Tags: api, services, levelservice.ts, get, level

- **createChessGame** (my-games)
  - File: `apps/api/src/game-engines/chess/index.ts:166`
  - Export chess engine
  - Tags: api, game, chess, create, game-engines

- **getRankIcon** (my-games)
  - File: `apps/web/src/pages/FeedbackPage.tsx:299`
  - Tags: icon, get, pages, feedbackpage.tsx, apps

- **deleteProject** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:83`
  - Tags: delete, api.ts, autocoder, project, ui

- **get_resumable_features** (my-games)
  - File: `autocoder/parallel_orchestrator.py:224`
  - Multiple testing agents can test the same feature - that's fine
  - Tags: get, features, autocoder, resumable, parallel_orchestrator.py

- **getMovementDirections** (my-games)
  - File: `apps/web/src/pages/CheckersKingPromotionTestPage.tsx:89`
  - Scenario: Red capture leading to promotion
  - Tags: checkerskingpromotiontestpage.tsx, directions, movement, get, pages

- **validateAnswer** (my-games)
  - File: `apps/api/src/game-engines/trivia/validation.ts:21`
  - Trivia Game Engine - Answer Validation
  - Tags: validate, api, answer, trivia, game-engines

- **getFlagFallWinner** (my-games)
  - File: `apps/api/src/game-engines/chess/time-controls.ts:114`
  - Check if a color has run out of time (flag fall)
  - Tags: api, winner, chess, get, flag

- **validateEmail** (my-games)
  - File: `apps/web/src/pages/ForgotPasswordPage.tsx:17`
  - Development mode - show reset link
  - Tags: validate, forgotpasswordpage.tsx, pages, email, apps

- **get_project_prompts** (my-games)
  - File: `autocoder/server/routers/projects.py:280`
  - Unregister from registry
  - Tags: routers, projects.py, get, autocoder, project

- **getInitialGameState** (my-games)
  - File: `apps/api/src/routes/matches.ts:812`
  - Initialize game state for a match
  - Tags: api, game, routes, matches.ts, get

- **getCurrentPlayer** (my-games)
  - File: `apps/web/src/pages/RoomLobbyPage.tsx:442`
  - Find the current player in the room
  - Tags: roomlobbypage.tsx, get, pages, current, player

- **normalizedEmail** (my-games)
  - File: `apps/api/src/lib/lockout.ts:163`
  - Get lockout status for display to user
  - Tags: api, email, lockout.ts, normalized, utility

- **formattedTime** (my-games)
  - File: `apps/api/src/services/emailService.ts:202`
  - Send tournament starting soon notification
  - Tags: api, services, emailservice.ts, formatted, apps

- **get_registry_path** (my-games)
  - File: `autocoder/registry.py:121`
  - Get the config directory: ~/.autocoder/

    Returns:
        Path to ~/.autocoder/ (created if it d

  - Tags: registry, get, path, autocoder, registry.py

- **getCapturedPosition** (my-games)
  - File: `apps/web/src/pages/CheckersKingPromotionTestPage.tsx:187`
  - Tags: checkerskingpromotiontestpage.tsx, get, pages, captured, position

- **getTransactionTypeLabel** (my-games)
  - File: `apps/api/src/routes/wallet.ts:261`
  - Reference Info
  - Tags: api, label, routes, wallet.ts, get

- **updatedWallet** (my-games)
  - File: `apps/api/src/routes/streak-protection.ts:166`
  - Calculate expiration date
  - Tags: api, routes, streak-protection.ts, wallet, updated

- **createFeature** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:111`
  - ============================================================================
  - Tags: feature, api.ts, create, autocoder, ui

- **formatTimestamp** (my-games)
  - File: `autocoder/ui/src/components/DebugLogViewer.tsx:292`
  - Get color class for log level using theme CSS variables
  - Tags: components, debuglogviewer.tsx, timestamp, autocoder, ui

- **calculateHandValue** (my-games)
  - File: `apps/api/src/game-engines/cards/utils.ts:209`
  - Get all cards of a specific suit from hand
  - Tags: api, calculate, utils.ts, value, cards

- **createRes** (my-games)
  - File: `apps/web/src/pages/CreditDeductionTestPage.tsx:242`
  - Get Tic-Tac-Toe game
  - Tags: pages, create, creditdeductiontestpage.tsx, apps, web

- **getCardsOfSuit** (my-games)
  - File: `apps/api/src/game-engines/cards/utils.ts:195`
  - Remove card from hand by ID
  - Tags: api, get, suit, utils.ts, cards

- **get_dependencies_safe** (my-games)
  - File: `autocoder/api/database.py:77`
  - Handle legacy NULL values gracefully - treat as False
  - Tags: api, safe, get, database.py, autocoder

- **getProject** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:79`
  - Projects API
  - Tags: get, api.ts, autocoder, project, ui

- **validate_project_command** (my-games)
  - File: `autocoder/security.py:517`
  - Enforce 100 command limit
  - Tags: validate, command, autocoder, project, security.py

- **get_effective_commands** (my-games)
  - File: `autocoder/security.py:564`
  - Args validation (Phase 1 - just check structure)
  - Tags: commands, get, effective, autocoder, security.py

- **get_messages** (my-games)
  - File: `autocoder/server/services/spec_chat_session.py:449`
  - Check if spec creation is complete.
  - Tags: messages, services, get, autocoder, spec_chat_session.py

- **getDayEnd** (my-games)
  - File: `apps/api/src/routes/leaderboards.ts:50`
  - Last day of current month
  - Tags: api, routes, get, leaderboards.ts, end

- **getRankBadge** (my-games)
  - File: `apps/web/src/pages/LeaderboardPage.tsx:249`
  - Read page from URL on mount
  - Tags: leaderboardpage.tsx, badge, get, pages, apps

- **createCheckNotCheckmate** (my-games)
  - File: `apps/web/src/pages/ChessCheckmateTestPage.tsx:456`
  - Queen and King Mate - Basic endgame mate
  - Tags: pages, checkmate, create, not, check

- **get_initializer_prompt** (my-games)
  - File: `autocoder/prompts.py:67`
  - Tags: prompts.py, get, autocoder, initializer, utility

- **update_schedule** (my-games)
  - File: `autocoder/server/routers/schedules.py:295`
  - Tags: update, schedule, autocoder, schedules.py, server

- **getUser** (my-games)
  - File: `apps/api/src/services/cacheService.ts:335`
  - Invalidate user cache
  - Tags: api, services, get, cacheservice.ts, user

- **set_dependencies** (my-games)
  - File: `autocoder/server/routers/features.py:681`
  - Tags: routers, features.py, autocoder, set, server

- **updateStep** (my-games)
  - File: `apps/web/src/pages/Level3ReferralTestPage.tsx:45`
  - Tags: level3referraltestpage.tsx, update, pages, step, apps

- **setAuthUser** (my-games)
  - File: `apps/api/src/lib/sentry.ts:47`
  - Tags: api, sentry.ts, user, auth, set

- **setPiece** (my-games)
  - File: `games/checkers/server/index.ts:105`
  - ===========================================
  - Tags: server, games, piece, set, checkers

- **setPiece** (my-games)
  - File: `apps/web/src/pages/ChessPawnPromotionTestPage.tsx:65`
  - Helper functions (matching server logic)
  - Tags: chesspawnpromotiontestpage.tsx, pages, piece, set, apps

- **get_blocked_features** (my-games)
  - File: `autocoder/api/dependency_resolver.py:380`
  - Sort by scheduling score (higher = first), then priority, then id
  - Tags: api, blocked, get, features, dependency_resolver.py

- **getGameScore** (my-games)
  - File: `apps/api/src/game-engines/checkers/rules.ts:406`
  - Get game score for evaluation
  - Tags: api, game, rules.ts, get, score

- **getDrawReason** (my-games)
  - File: `apps/api/src/game-engines/chess/rules.ts:329`
  - Check if game is a draw
  - Tags: api, rules.ts, chess, get, draw

- **updatedJackpot** (my-games)
  - File: `apps/api/src/routes/jackpot.ts:172`
  - Update tournament jackpot contribution
  - Tags: api, routes, jackpot.ts, jackpot, updated

- **updated** (my-games)
  - File: `apps/web/src/pages/StreakResetTestPage.tsx:53`
  - Tags: pages, streakresettestpage.tsx, updated, apps, web

- **getLeaderboard** (my-games)
  - File: `apps/api/src/services/cacheService.ts:350`
  - Get user from cache with fallback
  - Tags: api, services, get, cacheservice.ts, leaderboard

- **formatEndTime** (my-games)
  - File: `autocoder/ui/src/lib/timeUtils.ts:186`
  - Format an ISO datetime string to show the end time.
  - Tags: end, autocoder, ui, format, timeutils.ts

- **deleted** (my-games)
  - File: `apps/api/src/lib/cache/cacheService.ts:96`
  - Delete a value from cache
  - Tags: api, cache, cacheservice.ts, apps, deleted

- **getRoleBadgeColor** (my-games)
  - File: `apps/web/src/pages/AdminDashboardPage.tsx:1018`
  - Tags: color, admindashboardpage.tsx, badge, get, pages

- **createSeededRandom** (my-games)
  - File: `packages/game-core/src/index.ts:177`
  - Calculate the best move for a given state
  - Tags: game-core, packages, seeded, create, random

- **delete_terminal** (my-games)
  - File: `autocoder/server/services/terminal_manager.py:610`
  - Tags: delete, services, autocoder, terminal, server

- **formatLobbyState** (my-games)
  - File: `apps/api/src/socket/lobbyHandler.ts:366`
  - If no connections left, clean up the lobby
  - Tags: api, lobbyhandler.ts, socket, state, lobby

- **getLegalMoves** (my-games)
  - File: `apps/web/src/pages/ChessPawnPromotionTestPage.tsx:200`
  - Get legal moves for a pawn (including promotion handling)
  - Tags: chesspawnpromotiontestpage.tsx, get, pages, web, legal

- **setupMatchHandler** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:1625`
  - Stop the clock interval for a match
  - Tags: api, match, handler, socket, setup

- **formatMatchTime** (my-games)
  - File: `apps/web/src/pages/ProfilePage.tsx:475`
  - Close edit mode after short delay
  - Tags: match, pages, web, profilepage.tsx, apps

- **validateTimeControl** (my-games)
  - File: `apps/api/src/game-engines/chess/time-controls.ts:255`
  - Create time control from preset name
  - Tags: validate, api, chess, control, time-controls.ts

- **getStateGlow** (my-games)
  - File: `autocoder/ui/src/components/AgentAvatar.tsx:541`
  - Glow effect based on state
  - Tags: get, components, state, glow, autocoder

- **getOpeningMoves** (my-games)
  - File: `apps/ai-engine/src/openings.ts:153`
  - Check if position is in opening book
  - Tags: get, ai-engine, opening, apps, openings.ts

- **validateGameState** (my-games)
  - File: `apps/api/src/game-engines/chess/rules.ts:390`
  - Validate game state integrity
  - Tags: validate, api, game, rules.ts, chess

- **getWeekStart** (my-games)
  - File: `apps/api/src/routes/leaderboards.ts:7`
  - Helper functions for calendar-based date calculations
  - Tags: api, week, routes, get, leaderboards.ts

- **updatedFromWallet** (my-games)
  - File: `apps/api/src/services/walletService.ts:1321`
  - Get sender for notification
  - Tags: api, services, from, wallet, walletservice.ts

- **getLegalMoves** (my-games)
  - File: `games/chess/server/index.ts:307`
  - Tags: chess, get, server, games, legal

- **validate_testing_ratio** (my-games)
  - File: `autocoder/server/schemas.py:409`
  - Request schema for updating global settings.
  - Tags: validate, testing, schemas.py, autocoder, server

- **getFeature** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:118`
  - Tags: feature, get, api.ts, autocoder, ui

- **updatedSubscription** (my-games)
  - File: `apps/api/src/routes/subscriptions.ts:1023`
  - Calculate new period dates
  - Tags: api, routes, subscription, updated, apps

- **validatePath** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:322`
  - Unix root path like "/newfolder"
  - Tags: validate, path, api.ts, autocoder, ui

- **get_schedule** (my-games)
  - File: `autocoder/server/routers/schedules.py:267`
  - Tags: get, schedule, autocoder, schedules.py, server

- **create_database** (my-games)
  - File: `autocoder/api/database.py:335`
  - Add max_concurrency column if missing (for upgrades)
  - Tags: api, database.py, create, autocoder, database

- **validate_dependencies** (my-games)
  - File: `autocoder/api/dependency_resolver.py:198`
  - Assume cycle if too deep (fail-safe)
  - Tags: validate, api, dependency_resolver.py, autocoder, utility

- **get_system_prompt** (my-games)
  - File: `autocoder/server/services/assistant_chat_session.py:75`
  - Feature management tools (create/skip but not mark_passing)
  - Tags: services, assistant_chat_session.py, get, system, autocoder

- **createProject** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:68`
  - Handle 204 No Content responses
  - Tags: api.ts, create, autocoder, project, ui

- **validate_terminal_id** (my-games)
  - File: `autocoder/server/routers/terminal.py:72`
  - Get project path from registry.
  - Tags: validate, terminal.py, autocoder, terminal, server

- **get_project_stats_endpoint** (my-games)
  - File: `autocoder/server/routers/projects.py:343`
  - Tags: projects.py, get, endpoint, stats, autocoder

- **getPiece** (my-games)
  - File: `apps/web/src/pages/ChessMoveTestPage.tsx:88`
  - Tags: get, pages, chessmovetestpage.tsx, piece, apps

- **getAuthHeaders** (my-games)
  - File: `apps/web/src/pages/FeedbackPage.tsx:118`
  - Tags: headers, get, pages, feedbackpage.tsx, auth

- **getCurrentState** (my-games)
  - File: `apps/web/src/pages/MatchReplayPage.tsx:118`
  - Get current state based on event index
  - Tags: get, pages, state, current, apps

- **formatTimeRemaining** (my-games)
  - File: `apps/web/src/pages/ReferralsPage.tsx:352`
  - Tags: time, pages, web, referralspage.tsx, remaining

- **getSquaresBetween** (my-games)
  - File: `apps/api/src/game-engines/checkers/board.ts:254`
  - Calculate all squares between two squares (for jump validation)
  - Tags: api, between, get, squares, game-engines

- **createSampleChessBoard** (my-games)
  - File: `apps/ai-engine/tests/ai.test.ts:14`
  - AI Engine Tests
  - Tags: chess, ai-engine, create, board, sample

- **validate_project_name** (my-games)
  - File: `autocoder/server/routers/spec_creation.py:45`
  - Get project path from registry.
  - Tags: validate, name, autocoder, project, spec_creation.py

- **getPiece** (my-games)
  - File: `games/chess/client/ChessBoard.tsx:103`
  - ===========================================
  - Tags: chess, get, games, client, piece

- **createTestGame** (my-games)
  - File: `apps/api/src/test/setup.ts:80`
  - Helper to get auth token for tests
  - Tags: api, game, setup.ts, create, apps

- **createProject** (my-games)
  - File: `autocoder/ui/src/components/NewProjectModal.tsx:49`
  - Suppress unused variable warning - specMethod may be used in future
  - Tags: components, create, newprojectmodal.tsx, autocoder, project

- **setupReferral** (my-games)
  - File: `apps/web/src/pages/ReferralCommissionTestPage.tsx:97`
  - Tags: pages, referralcommissiontestpage.tsx, setup, apps, web

- **formatDateTime** (my-games)
  - File: `apps/web/src/pages/AdminDashboardPage.tsx:998`
  - Tags: admindashboardpage.tsx, date, pages, web, apps

- **createEmptyBoard** (my-games)
  - File: `apps/web/src/pages/ChessCastlingTestPage.tsx:419`
  - ===========================================
  - Tags: pages, create, board, chesscastlingtestpage.tsx, empty

- **create_project_terminal** (my-games)
  - File: `autocoder/server/routers/terminal.py:140`
  - If no terminals exist, create a default one
  - Tags: terminal.py, create, autocoder, project, terminal

- **delete_project_conversation** (my-games)
  - File: `autocoder/server/routers/assistant_chat.py:158`
  - Tags: delete, conversation, autocoder, project, server

- **get_project_allowed_commands** (my-games)
  - File: `autocoder/security.py:615`
  - Add project-specific commands
  - Tags: commands, get, allowed, autocoder, project

- **calculateLevelFromXp** (my-games)
  - File: `apps/api/src/services/levelService.ts:44`
  - Calculate the level for a given amount of total XP
  - Tags: api, services, levelservice.ts, level, calculate

- **updatedWallet** (my-games)
  - File: `apps/api/src/routes/referrals.ts:441`
  - First, simulate giving the user credits (create a mock transaction)
  - Tags: api, referrals.ts, routes, wallet, updated

- **generateRefreshToken** (my-games)
  - File: `apps/api/src/middleware/auth.ts:46`
  - Clear auth cookie
  - Tags: api, token, generate, refresh, auth.ts

- **validateChessMove** (my-games)
  - File: `apps/api/src/socket/handlers/gameHandler.ts:513`
  - Validate chess move using the chess engine
  - Tags: validate, api, chess, socket, handlers

- **generateChessPositionKey** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:4060`
  - Which player timed out (0 or 1)
  - Tags: api, key, chess, socket, generate

- **validate_project_path** (my-games)
  - File: `autocoder/registry.py:369`
  - =============================================================================
  - Tags: validate, path, autocoder, project, registry.py

- **get_session** (my-games)
  - File: `autocoder/server/services/assistant_database.py:82`
  - Use as_posix() for cross-platform compatibility with SQLite connection strings
  - Tags: services, session, get, assistant_database.py, autocoder

- **formatTimeLong** (my-games)
  - File: `apps/api/src/game-engines/chess/time-controls.ts:154`
  - Format time as MM:SS
  - Tags: api, chess, long, time-controls.ts, game-engines

- **getOpponentName** (my-games)
  - File: `apps/web/src/pages/UserProfilePage.tsx:290`
  - Tags: name, userprofilepage.tsx, get, pages, opponent

- **parsed** (my-games)
  - File: `autocoder/ui/src/components/ScheduleModal.tsx:338`
  - Tags: components, schedulemodal.tsx, autocoder, parsed, ui

- **createSchedule** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:461`
  - ============================================================================
  - Tags: api.ts, schedule, create, autocoder, ui

- **create_session** (my-games)
  - File: `autocoder/server/services/spec_chat_session.py:465`
  - return self.complete

    def get_messages(self) -> list[dict]:

  - Tags: services, session, create, autocoder, spec_chat_session.py

- **calculateTriviaWinner** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:4448`
  - Calculate trivia winner based on scores
  - Tags: api, winner, socket, calculate, trivia

- **getDevServerStatus** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:389`
  - ============================================================================
  - Tags: dev, ui, get, api.ts, autocoder

- **getLevelProgress** (my-games)
  - File: `apps/api/src/services/levelService.ts:64`
  - Get detailed level progress information
  - Tags: api, services, levelservice.ts, get, level

- **getNextSequenceNumber** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:5383`
  - Tags: api, get, socket, next, sequence

- **get_playwright_headless** (my-games)
  - File: `autocoder/client.py:41`
  - Custom API endpoint (e.g., https://api.z.ai/api/anthropic)
  - Tags: playwright, get, headless, autocoder, client.py

- **getRawMoves** (my-games)
  - File: `apps/web/src/pages/ChessMoveTestPage.tsx:106`
  - Get raw moves without checking for check
  - Tags: get, pages, web, raw, chessmovetestpage.tsx

- **getKnightAttacks** (my-games)
  - File: `apps/api/src/game-engines/chess/move-validation.ts:255`
  - Get knight attack squares
  - Tags: api, chess, move-validation.ts, attacks, get

- **updatedUsedCodes** (my-games)
  - File: `apps/api/src/lib/twoFactor.ts:142`
  - 2FA not enabled for this user
  - Tags: api, codes, twofactor.ts, used, updated

- **getCardsOfRank** (my-games)
  - File: `apps/api/src/game-engines/cards/utils.ts:202`
  - Add card to hand
  - Tags: api, get, utils.ts, cards, game-engines

- **getSimpleMoves** (my-games)
  - File: `apps/web/src/pages/CheckersKingPromotionTestPage.tsx:114`
  - Regular pieces can only move forward
  - Tags: checkerskingpromotiontestpage.tsx, get, pages, web, simple

- **getLogColor** (my-games)
  - File: `autocoder/ui/src/components/DebugLogViewer.tsx:277`
  - Get color class for log level using theme CSS variables
  - Tags: log, color, get, components, debuglogviewer.tsx

- **getLayoutedElements** (my-games)
  - File: `autocoder/ui/src/components/DependencyGraph.tsx:166`
  - Layout nodes using dagre
  - Tags: layouted, get, components, dependencygraph.tsx, elements

- **createEmptyBoard** (my-games)
  - File: `apps/web/src/pages/CheckersMultiJumpTestPage.tsx:58`
  - ===========================================
  - Tags: pages, create, board, empty, checkersmultijumptestpage.tsx

- **getOpeningMove** (my-games)
  - File: `apps/ai-engine/src/openings.ts:117`
  - Get opening move from the book
  - Tags: get, ai-engine, opening, apps, openings.ts

- **getOrCreateJackpot** (my-games)
  - File: `apps/api/src/routes/jackpot.ts:10`
  - Helper to get or create the jackpot record
  - Tags: api, routes, jackpot.ts, get, jackpot

- **getMatchTopOffset** (my-games)
  - File: `apps/web/src/pages/TournamentDetailPage.tsx:382`
  - Height of each match box (with padding for live badge)
  - Tags: match, get, pages, offset, top

- **update_settings** (my-games)
  - File: `autocoder/server/routers/settings.py:90`
  - Get current global settings.
  - Tags: update, autocoder, settings, server, settings.py

- **updatedTournament** (my-games)
  - File: `apps/api/src/routes/admin.ts:1046`
  - Tags: api, routes, admin.ts, tournament, updated

- **formatDateTime** (my-games)
  - File: `apps/web/src/pages/TournamentsPage.tsx:320`
  - Tags: tournamentspage.tsx, date, pages, web, apps

- **getSessionAnswers** (my-games)
  - File: `apps/api/src/game-engines/trivia/validation.ts:164`
  - Check if a streak count is a milestone (3, 5, 10, 15, etc.)
  - Tags: answers, api, session, get, trivia

- **getPiece** (my-games)
  - File: `apps/api/src/game-engines/checkers/board.ts:71`
  - Create initial game state
  - Tags: api, get, piece, game-engines, board.ts

- **get_project_choice** (my-games)
  - File: `autocoder/start.py:110`
  - Display list of existing projects.
  - Tags: get, autocoder, choice, project, start.py

- **validate_project_name** (my-games)
  - File: `autocoder/server/routers/projects.py:78`
  - Tags: validate, name, projects.py, autocoder, project

- **get** (my-games)
  - File: `apps/api/src/services/cacheService.ts:45`
  - Get value from cache
  - Tags: api, services, get, cacheservice.ts, apps

- **formatRelativeTime** (my-games)
  - File: `apps/web/src/pages/HomePage.tsx:61`
  - Helper function to format relative time
  - Tags: homepage.tsx, pages, utility, web, apps

- **createQueenKingMate** (my-games)
  - File: `apps/web/src/pages/ChessCheckmateTestPage.tsx:442`
  - Black king on edge
  - Tags: pages, queen, create, mate, king

- **get_devserver_config** (my-games)
  - File: `autocoder/server/routers/devserver.py:205`
  - Tags: config, get, server, autocoder, devserver

- **createRedPromotionScenario** (my-games)
  - File: `apps/web/src/pages/CheckersKingPromotionTestPage.tsx:45`
  - ===========================================
  - Tags: scenario, checkerskingpromotiontestpage.tsx, pages, web, create

- **generateConfetti** (my-games)
  - File: `autocoder/ui/src/components/CelebrationOverlay.tsx:13`
  - Generate random confetti particles
  - Tags: confetti, celebrationoverlay.tsx, components, generate, autocoder

- **calculateValidMoves** (my-games)
  - File: `games/chess/client/ChessBoard.tsx:403`
  - Get the last move for highlighting
  - Tags: valid, chess, calculate, games, client

- **get_project_stats** (my-games)
  - File: `autocoder/server/routers/projects.py:88`
  - Validate and sanitize project name to prevent path traversal.
  - Tags: projects.py, get, stats, autocoder, project

- **updatedWallet** (my-games)
  - File: `apps/api/src/routes/tournaments.ts:734`
  - Credit prize to winner's wallet if they won credits
  - Tags: api, routes, wallet, updated, apps

- **setStoredConversationId** (my-games)
  - File: `autocoder/ui/src/components/AssistantPanel.tsx:36`
  - Invalid stored data, ignore
  - Tags: components, conversation, assistantpanel.tsx, autocoder, set

- **getAllLegalMoves** (my-games)
  - File: `games/chess/ai/index.ts:332`
  - Handle en passant capture
  - Tags: chess, get, all, games, legal

- **getPlayerInitial** (my-games)
  - File: `apps/web/src/pages/MatchPage.tsx:161`
  - Match forfeited successfully, refresh match data
  - Tags: matchpage.tsx, get, pages, web, player

- **getRemainingBackupCodes** (my-games)
  - File: `apps/api/src/lib/twoFactor.ts:229`
  - Get remaining backup codes count
  - Tags: api, codes, twofactor.ts, backup, get

- **formatRelativeTime** (my-games)
  - File: `autocoder/ui/src/components/ConversationHistory.tsx:25`
  - Format a relative time string from an ISO date
  - Tags: conversationhistory.tsx, components, utility, autocoder, ui

- **getSquaresBetween** (my-games)
  - File: `apps/api/src/game-engines/chess/board-utils.ts:153`
  - Check if squares are on same file
  - Tags: api, board-utils.ts, chess, between, get

- **getQuestionCount** (my-games)
  - File: `apps/api/src/game-engines/trivia/question-selection.ts:188`
  - Get question count by category and difficulty
  - Tags: api, get, question-selection.ts, count, question

- **calculateStreakBonus** (my-games)
  - File: `apps/api/src/game-engines/trivia/scoring.ts:80`
  - Calculate streak bonus
  - Tags: api, calculate, trivia, scoring.ts, streak

- **getTransactionIcon** (my-games)
  - File: `apps/web/src/pages/WalletPage.tsx:547`
  - Tags: icon, get, pages, walletpage.tsx, transaction

- **calculateTimeBonus** (my-games)
  - File: `apps/api/src/game-engines/trivia/scoring.ts:65`
  - Calculate time bonus
  - Tags: api, calculate, trivia, scoring.ts, game-engines

- **updatedActivePlayers** (my-games)
  - File: `apps/api/src/routes/rooms.ts:689`
  - Emit socket event for real-time update
  - Tags: api, players, routes, active, updated

- **createTwoRooksMate** (my-games)
  - File: `apps/web/src/pages/ChessCheckmateTestPage.tsx:427`
  - White knight delivers smothered mate
  - Tags: two, pages, create, mate, rooks

- **calculateScore** (my-games)
  - File: `apps/api/src/game-engines/trivia/scoring.ts:39`
  - Maximum time bonus
  - Tags: api, calculate, score, trivia, scoring.ts

- **settings** (my-games)
  - File: `apps/api/src/routes/settings.ts:60`
  - Tags: api, settings, apps, utility, routes

- **getPlayerByIndex** (my-games)
  - File: `apps/web/src/pages/MatchReplayPage.tsx:185`
  - Tags: get, pages, player, index, apps

- **formatDuration** (my-games)
  - File: `apps/web/src/pages/MatchHistoryPage.tsx:82`
  - Tags: pages, duration, web, matchhistorypage.tsx, apps

- **getCsrfToken** (my-games)
  - File: `apps/api/src/middleware/csrf.ts:116`
  - Get CSRF token endpoint (for initial page load)
  - Tags: api, csrf.ts, get, token, middleware

- **getPendingHostingBonuses** (my-games)
  - File: `apps/api/src/services/walletService.ts:1530`
  - Get all pending hosting bonuses for a user
  - Tags: api, services, pending, get, bonuses

- **getCaptureMoves** (my-games)
  - File: `apps/web/src/pages/CheckersMultiJumpTestPage.tsx:94`
  - Get movement directions based on piece type and color
  - Tags: capture, get, pages, web, checkersmultijumptestpage.tsx

- **delete_project_terminal** (my-games)
  - File: `autocoder/server/routers/terminal.py:200`
  - Tags: delete, terminal.py, autocoder, project, terminal

- **setLanguage** (my-games)
  - File: `apps/web/src/hooks/useI18n.ts:30`
  - Listen for storage events to sync across tabs
  - Tags: usei18n.ts, language, hooks, set, apps

- **parseFields** (my-games)
  - File: `apps/api/src/lib/fields.ts:24`
  - Parse fields query parameter
  - Tags: api, fields.ts, parse, apps, fields

- **validate_project_name** (my-games)
  - File: `autocoder/server/routers/assistant_chat.py:50`
  - Get project path from registry.
  - Tags: validate, name, autocoder, project, server

- **getCardColor** (my-games)
  - File: `apps/api/src/game-engines/cards/utils.ts:37`
  - Get human-readable display for a card
  - Tags: api, color, get, utils.ts, cards

- **formatJoinDate** (my-games)
  - File: `apps/web/src/pages/ProfilePage.tsx:503`
  - Format date for display
  - Tags: date, pages, web, profilepage.tsx, join

- **getPlanById** (my-games)
  - File: `apps/api/src/routes/webhooks.ts:22`
  - Subscription plan definitions (shared with subscriptions.ts)
  - Tags: api, routes, get, plan, apps

- **getRawMoves** (my-games)
  - File: `games/chess/client/ChessBoard.tsx:129`
  - Find the king of a given color
  - Tags: chess, get, raw, games, client

- **createNoCheckPosition** (my-games)
  - File: `apps/web/src/pages/ChessCheckTestPage.tsx:306`
  - Knight checking black king
  - Tags: pages, create, chesschecktestpage.tsx, check, position

- **get_next_scheduled_run** (my-games)
  - File: `autocoder/server/routers/schedules.py:205`
  - Tags: get, scheduled, next, autocoder, schedules.py

- **getRegularMoves** (my-games)
  - File: `apps/api/src/game-engines/checkers/move-validation.ts:126`
  - Get all regular moves for a piece
  - Tags: api, move-validation.ts, get, regular, checkers

- **get_manager** (my-games)
  - File: `autocoder/server/services/process_manager.py:517`
  - Global registry of process managers per project with thread safety
  - Tags: services, manager, get, process_manager.py, autocoder

- **getWalletBalance** (my-games)
  - File: `apps/api/src/services/walletService.ts:537`
  - Get wallet balance for a user
  - Tags: api, services, get, wallet, balance

- **get_config_dir** (my-games)
  - File: `autocoder/registry.py:109`
  - =============================================================================
  - Tags: config, get, dir, autocoder, registry.py

- **deleted** (my-games)
  - File: `apps/api/src/services/queueService.ts:190`
  - Tags: api, services, queueservice.ts, apps, deleted

- **getMonthEnd** (my-games)
  - File: `apps/api/src/routes/leaderboards.ts:30`
  - 0 = Sunday
  - Tags: api, routes, get, month, leaderboards.ts

- **getOpeningBookSize** (my-games)
  - File: `apps/ai-engine/src/openings.ts:170`
  - Add a custom opening to the book
  - Tags: get, ai-engine, opening, size, apps

- **getAllPseudoLegalMoves** (my-games)
  - File: `apps/api/src/game-engines/chess/move-validation.ts:192`
  - Get all pseudo-legal moves for all pieces of a color
  - Tags: api, chess, move-validation.ts, get, moves

- **getDatabaseLatency** (my-games)
  - File: `apps/api/src/lib/dbHealth.ts:52`
  - Check database connection latency
  - Tags: api, dbhealth.ts, get, apps, latency

- **extract_commands** (my-games)
  - File: `autocoder/security.py:138`
  - Split on && and || while preserving the ability to handle each segment
  - Tags: commands, extract, autocoder, security.py, utility

- **calculateHandScore** (my-games)
  - File: `games/card-games/server/index.ts:151`
  - ===========================================
  - Tags: card-games, calculate, server, score, games

- **getLegalMoves** (my-games)
  - File: `apps/web/src/pages/ChessMoveTestPage.tsx:267`
  - Tags: get, pages, web, chessmovetestpage.tsx, legal

- **validateMoveSequence** (my-games)
  - File: `apps/api/src/game-engines/checkers/move-validation.ts:372`
  - Validate a complete move sequence
  - Tags: validate, api, move-validation.ts, sequence, checkers

- **createStalematePosition** (my-games)
  - File: `apps/web/src/pages/ChessCheckmateTestPage.tsx:472`
  - Black king in check but can escape
  - Tags: position, pages, create, stalemate, web

- **calculateChessAiMove** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:1044`
  - Tags: api, chess, socket, calculate, matchhandler.ts

- **getSubscriptionStatus** (my-games)
  - File: `apps/api/src/services/subscriptionService.ts:43`
  - Get the current subscription status for a user, including grace period logic
  - Tags: api, services, subscription, get, subscriptionservice.ts

- **createCheckersAI** (my-games)
  - File: `apps/ai-engine/src/games/checkers.ts:346`
  - Tags: ai-engine, create, games, apps, checkers.ts

- **formatJoinDate** (my-games)
  - File: `apps/web/src/pages/UserProfilePage.tsx:262`
  - Update follow stats
  - Tags: date, userprofilepage.tsx, pages, web, join

- **create_new_project_flow** (my-games)
  - File: `autocoder/start.py:330`
  - Tags: flow, create, new, project, autocoder

- **getStatusBadgeColor** (my-games)
  - File: `apps/web/src/pages/AdminDashboardPage.tsx:987`
  - Tags: color, admindashboardpage.tsx, badge, get, pages

- **formatReward** (my-games)
  - File: `apps/web/src/pages/MilestonesPage.tsx:200`
  - Tags: milestonespage.tsx, reward, pages, web, apps

- **getLegalMoves** (my-games)
  - File: `apps/web/src/pages/CheckersMultiJumpTestPage.tsx:145`
  - Get simple moves (non-captures)
  - Tags: get, pages, web, checkersmultijumptestpage.tsx, legal

- **create_session** (my-games)
  - File: `autocoder/server/services/assistant_chat_session.py:432`
  - Get the current conversation ID.
  - Tags: services, session, assistant_chat_session.py, create, autocoder

- **deleteFeature** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:122`
  - Tags: delete, feature, api.ts, autocoder, ui

- **get_venv_python** (my-games)
  - File: `autocoder/start_ui.py:59`
  - Find an available port starting from the given port.
  - Tags: get, venv, autocoder, python, start_ui.py

- **getWarmingStats** (my-games)
  - File: `apps/api/src/lib/cache/warming.ts:326`
  - Get cache warming statistics
  - Tags: api, cache, get, warming, stats

- **formatDateTime** (my-games)
  - File: `apps/web/src/pages/TournamentDetailPage.tsx:184`
  - Tags: date, pages, web, apps, format

- **get_default_dev_command** (my-games)
  - File: `autocoder/server/services/project_config.py:303`
  - Check for Go project
  - Tags: services, dev, get, server, command

- **updated** (my-games)
  - File: `autocoder/ui/src/components/DebugLogViewer.tsx:121`
  - Handle renaming a terminal
  - Tags: components, debuglogviewer.tsx, autocoder, updated, ui

- **setup_status** (my-games)
  - File: `autocoder/server/main.py:160`
  - WebSocket endpoint for real-time project updates.
  - Tags: setup, main.py, autocoder, status, server

- **createLimiter** (my-games)
  - File: `apps/api/src/middleware/rateLimiter.ts:7`
  - Mock rate limiter for tests
  - Tags: api, ratelimiter.ts, create, limiter, apps

- **getCapturedPosition** (my-games)
  - File: `apps/web/src/pages/CheckersMultiJumpTestPage.tsx:177`
  - Check if any piece has a capture - if so, captures are mandatory
  - Tags: get, pages, captured, checkersmultijumptestpage.tsx, position

- **get_all_complete** (my-games)
  - File: `autocoder/parallel_orchestrator.py:331`
  - Log to debug file (but not every call to avoid spam)
  - Tags: get, complete, all, autocoder, parallel_orchestrator.py

- **updateLoginStreakMilestone** (my-games)
  - File: `apps/api/src/services/milestoneService.ts:130`
  - Update login streak milestone
  - Tags: api, login, services, milestone, update

- **createKingMovementScenario** (my-games)
  - File: `apps/web/src/pages/CheckersKingPromotionTestPage.tsx:67`
  - Scenario: Black piece about to promote (one move away from row 7)
  - Tags: scenario, checkerskingpromotiontestpage.tsx, movement, pages, create

- **sanitizeUserInput** (my-games)
  - File: `apps/api/src/lib/validators.ts:295`
  - Sanitize HTML content to prevent XSS
  - Tags: api, validators.ts, user, input, apps

- **validate_init_script** (my-games)
  - File: `autocoder/security.py:315`
  - Only allow +x variants (making files executable)
  - Tags: validate, security.py, autocoder, init, script

- **updatedWallet** (my-games)
  - File: `apps/api/src/routes/topups.ts:180`
  - Add credits to wallet in a transaction
  - Tags: api, routes, wallet, topups.ts, updated

- **getLegalMoves** (my-games)
  - File: `games/chess/client/ChessBoard.tsx:301`
  - Check if a color's king is in check
  - Tags: chess, get, games, client, chessboard.tsx

- **generateAccessToken** (my-games)
  - File: `apps/api/src/middleware/auth.ts:39`
  - Clear auth cookie
  - Tags: api, middleware, token, generate, auth.ts

- **getChessPositionBonus** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:690`
  - Tags: api, chess, get, socket, matchhandler.ts

- **getActionColor** (my-games)
  - File: `apps/admin/src/components/AuditLog.tsx:75`
  - For now, show empty state since audit logs might not be fully implemented
  - Tags: color, get, components, auditlog.tsx, admin

- **validateEmail** (my-games)
  - File: `apps/web/src/pages/LoginPage.tsx:142`
  - If in dev mode with mock URL, process directly
  - Tags: validate, pages, email, loginpage.tsx, apps

- **getOpponentName** (my-games)
  - File: `apps/web/src/pages/ProfilePage.tsx:492`
  - Get opponent name for a match
  - Tags: name, get, pages, opponent, profilepage.tsx

- **validate_project_name** (my-games)
  - File: `autocoder/server/websocket.py:571`
  - Get number of active connections for a project.
  - Tags: validate, name, autocoder, project, websocket.py

- **getAllChessLegalMoves** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:838`
  - Tags: api, chess, get, socket, all

- **formatPrice** (my-games)
  - File: `apps/web/src/pages/SubscriptionsPage.tsx:230`
  - Tags: subscriptionspage.tsx, price, pages, web, apps

- **createAI** (my-games)
  - File: `apps/api/src/routes/ai.ts:294`
  - Helper functions
  - Tags: api, create, apps, utility, ai.ts

- **updatedWallet** (my-games)
  - File: `apps/api/src/services/walletService.ts:1744`
  - Get game name for the transaction description
  - Tags: api, services, wallet, walletservice.ts, updated

- **createUserC** (my-games)
  - File: `apps/web/src/pages/Level2ReferralTestPage.tsx:144`
  - Step 3: Create User C using User B's referral code
  - Tags: pages, create, user, level2referraltestpage.tsx, apps

- **getBreadcrumbs** (my-games)
  - File: `autocoder/ui/src/components/FolderBrowser.tsx:110`
  - Refresh the directory listing
  - Tags: get, components, breadcrumbs, autocoder, folderbrowser.tsx

- **getUserSocketId** (my-games)
  - File: `apps/api/src/socket/presenceHandler.ts:86`
  - Broadcast offline status to friends who are online
  - Tags: api, get, socket, presencehandler.ts, user

- **get_expand_session** (my-games)
  - File: `autocoder/server/services/expand_chat_session.py:452`
  - Get the total number of features created in this session.
  - Tags: services, session, get, expand_chat_session.py, expand

- **getRawMoves** (my-games)
  - File: `apps/web/src/pages/ChessCastlingTestPage.tsx:82`
  - Get raw moves (for attack checking)
  - Tags: get, pages, web, raw, chesscastlingtestpage.tsx

- **set_dev_command** (my-games)
  - File: `autocoder/server/services/project_config.py:354`
  - Check for custom command first
  - Tags: services, server, command, autocoder, set

- **parse_args** (my-games)
  - File: `autocoder/autonomous_agent_demo.py:51`
  - Load environment variables from .env file (if it exists)
  - Tags: args, autonomous_agent_demo.py, autocoder, parse, utility

- **create_project_conversation** (my-games)
  - File: `autocoder/server/routers/assistant_chat.py:137`
  - Tags: create, conversation, autocoder, project, server

- **format** (my-games)
  - File: `apps/api/src/routes/wallet.ts:1138`
  - GET /api/wallet/transactions/export - Export transaction history as CSV
  - Tags: api, wallet.ts, utility, apps, format

- **getMonthStart** (my-games)
  - File: `apps/api/src/routes/leaderboards.ts:23`
  - Helper functions for calendar-based date calculations
  - Tags: api, routes, get, month, leaderboards.ts

- **set_setting** (my-games)
  - File: `autocoder/registry.py:477`
  - Tags: setting, autocoder, set, registry.py, utility

- **getMonthStart** (my-games)
  - File: `apps/api/src/routes/games.ts:130`
  - Helper functions for calendar-based date calculations
  - Tags: api, games.ts, routes, get, month

- **parseFEN** (my-games)
  - File: `apps/api/src/game-engines/chess/game-state.ts:44`
  - Parse FEN string to game state
  - Tags: api, chess, game-state.ts, game-engines, parse

- **set** (my-games)
  - File: `apps/api/src/lib/cache/cacheService.ts:80`
  - Set a value in cache with optional TTL
  - Tags: api, cache, cacheservice.ts, set, apps

- **getWalletBalance** (my-games)
  - File: `apps/web/src/pages/Level3ReferralTestPage.tsx:88`
  - Tags: level3referraltestpage.tsx, get, pages, wallet, balance

- **formatCredits** (my-games)
  - File: `apps/web/src/pages/TournamentPrizeTestPage.tsx:183`
  - Filter to tournament_complete notifications
  - Tags: tournamentprizetestpage.tsx, pages, web, apps, format

- **get_home_directory** (my-games)
  - File: `autocoder/server/routers/filesystem.py:506`
  - Tags: get, server, filesystem.py, autocoder, directory

- **validateCastling** (my-games)
  - File: `apps/api/src/game-engines/chess/special-moves.ts:23`
  - Chess Special Moves
  - Tags: validate, api, chess, special-moves.ts, castling

- **getStateColor** (my-games)
  - File: `autocoder/ui/src/components/AgentCard.tsx:35`
  - Get state color
  - Tags: color, get, components, state, agentcard.tsx

- **getPieceAt** (my-games)
  - File: `apps/api/src/game-engines/chess/board-utils.ts:61`
  - Convert array indices to square
  - Tags: api, board-utils.ts, chess, get, piece

- **setActiveTab** (my-games)
  - File: `autocoder/ui/src/components/DebugLogViewer.tsx:74`
  - Terminal management state
  - Tags: tab, components, active, debuglogviewer.tsx, autocoder

- **updateReferralMilestone** (my-games)
  - File: `apps/api/src/services/milestoneService.ts:294`
  - Update milestone progress when a user refers someone
  - Tags: api, services, milestone, update, apps

- **getSchedule** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:471`
  - Tags: get, api.ts, schedule, autocoder, ui

- **getUserData** (my-games)
  - File: `apps/web/src/pages/RoomLobbyPage.tsx:101`
  - Get current user from localStorage
  - Tags: data, roomlobbypage.tsx, get, pages, user

- **updateSettings** (my-games)
  - File: `autocoder/ui/src/components/SettingsModal.tsx:12`
  - Tags: update, components, autocoder, settings, ui

- **formatDate** (my-games)
  - File: `apps/admin/src/pages/Users.tsx:100`
  - Tags: date, pages, admin, apps, format

- **getRawMoves** (my-games)
  - File: `apps/web/src/pages/ChessCheckTestPage.tsx:76`
  - Get raw moves for a piece (without checking for leaving king in check)
  - Tags: get, pages, web, chesschecktestpage.tsx, raw

- **transformedUsers** (my-games)
  - File: `apps/api/src/routes/admin.ts:106`
  - Transform to include additional info
  - Tags: api, transformed, routes, admin.ts, users

- **updateScore** (my-games)
  - File: `apps/api/src/game-engines/trivia/scoring.ts:104`
  - Update score after answer validation
  - Tags: api, update, score, trivia, scoring.ts

- **getFilteredMilestones** (my-games)
  - File: `apps/web/src/pages/MilestonesPage.tsx:186`
  - Refresh milestones data
  - Tags: milestonespage.tsx, get, pages, milestones, apps

- **getTimeUntil** (my-games)
  - File: `apps/web/src/pages/TournamentsPage.tsx:330`
  - Tags: tournamentspage.tsx, get, pages, until, apps

- **formatSourceName** (my-games)
  - File: `apps/web/src/pages/ReferralsPage.tsx:432`
  - Track share (likely WhatsApp or other)
  - Tags: name, pages, web, referralspage.tsx, source

- **getPromotionRank** (my-games)
  - File: `apps/api/src/game-engines/chess/board-utils.ts:210`
  - Check if move is a capture
  - Tags: api, board-utils.ts, chess, get, game-engines

- **updatedUser** (my-games)
  - File: `apps/api/src/routes/users.ts:188`
  - Check if username is taken
  - Tags: api, routes, user, updated, apps

- **getOpponentColor** (my-games)
  - File: `apps/api/src/game-engines/chess/board-utils.ts:180`
  - Check if path is clear (no pieces between)
  - Tags: api, color, board-utils.ts, chess, get

- **get_database_path** (my-games)
  - File: `autocoder/api/database.py:181`
  - Convert override to dictionary for JSON serialization.
  - Tags: api, get, path, database.py, autocoder

- **delete_feature** (my-games)
  - File: `autocoder/server/routers/features.py:478`
  - Compute passing IDs for response
  - Tags: delete, feature, features.py, autocoder, server

- **createTriviaAI** (my-games)
  - File: `apps/ai-engine/src/games/trivia.ts:175`
  - Utility methods for external use
  - Tags: trivia.ts, ai-engine, create, games, trivia

- **get_blocked_paths** (my-games)
  - File: `autocoder/server/routers/filesystem.py:102`
  - Universal blocked paths (relative to home directory)
  - Tags: blocked, get, paths, autocoder, filesystem.py

- **createMove** (my-games)
  - File: `apps/api/src/game-engines/chess/test.ts:11`
  - Chess Engine Test Suite
  - Tags: api, chess, create, game-engines, test.ts

- **getMemoryUsage** (my-games)
  - File: `apps/api/src/lib/performance.ts:273`
  - Memory usage tracker
  - Tags: api, get, performance.ts, apps, memory

- **update_project_prompts** (my-games)
  - File: `autocoder/server/routers/projects.py:313`
  - Tags: routers, projects.py, update, autocoder, project

- **validate_project_name** (my-games)
  - File: `autocoder/server/routers/agent.py:61`
  - Parse testing agent settings with defaults
  - Tags: validate, name, agent.py, autocoder, project

- **getQueueStats** (my-games)
  - File: `apps/api/src/services/queueService.ts:365`
  - Get queue statistics
  - Tags: api, services, queueservice.ts, get, stats

- **createTimeControlFromPreset** (my-games)
  - File: `apps/api/src/game-engines/chess/time-controls.ts:241`
  - Create time control from preset name
  - Tags: api, preset, chess, control, from

- **updateSchedule** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:478`
  - Tags: update, api.ts, schedule, autocoder, ui

- **get_feature** (my-games)
  - File: `autocoder/server/routers/features.py:382`
  - ============================================================================
  - Tags: feature, get, features.py, autocoder, server

- **create_expand_session** (my-games)
  - File: `autocoder/server/services/expand_chat_session.py:458`
  - Get all messages in the conversation.
  - Tags: services, session, expand_chat_session.py, create, expand

- **update_devserver_config** (my-games)
  - File: `autocoder/server/routers/devserver.py:233`
  - Tags: config, update, server, autocoder, devserver

- **get_project_conversation** (my-games)
  - File: `autocoder/server/routers/assistant_chat.py:113`
  - Tags: get, conversation, autocoder, project, server

- **createCheckersGame** (my-games)
  - File: `apps/api/src/game-engines/checkers/index.ts:311`
  - This is a simplified version - full implementation would
  - Tags: api, game, create, game-engines, apps

- **getUserAnswers** (my-games)
  - File: `apps/api/src/game-engines/trivia/validation.ts:192`
  - Get user's answers in a session
  - Tags: answers, api, get, user, trivia

- **formatMatchTime** (my-games)
  - File: `apps/web/src/pages/UserProfilePage.tsx:274`
  - Tags: match, userprofilepage.tsx, pages, web, apps

- **get_project_config** (my-games)
  - File: `autocoder/server/services/project_config.py:424`
  - Tags: config, services, get, autocoder, project

- **getWeekEnd** (my-games)
  - File: `apps/api/src/routes/leaderboards.ts:15`
  - Helper functions for calendar-based date calculations
  - Tags: api, week, routes, get, leaderboards.ts

- **validate_base64_and_size** (my-games)
  - File: `autocoder/server/schemas.py:306`
  - Image attachment from client for spec creation chat.
  - Tags: validate, schemas.py, and, autocoder, size

- **createBlackPromotionScenario** (my-games)
  - File: `apps/web/src/pages/CheckersKingPromotionTestPage.tsx:56`
  - Red piece on row 1, ready to move to row 0 and become king
  - Tags: scenario, checkerskingpromotiontestpage.tsx, pages, web, create

- **getNotificationIcon** (my-games)
  - File: `apps/web/src/components/NotificationsDropdown.tsx:157`
  - Tags: icon, get, components, notificationsdropdown.tsx, notification

- **calculateWinner** (my-games)
  - File: `games/shit-happens/server/index.ts:177`
  - Insert a card into the ranking line at the correct position
  - Tags: winner, shit-happens, calculate, games, server

- **deleteFeature** (my-games)
  - File: `autocoder/ui/src/components/FeatureModal.tsx:39`
  - Tags: delete, feature, components, featuremodal.tsx, autocoder

- **validate_model** (my-games)
  - File: `autocoder/server/schemas.py:531`
  - Tags: validate, schemas.py, autocoder, model, server

- **createFoolsMate** (my-games)
  - File: `apps/web/src/pages/ChessCheckmateTestPage.tsx:364`
  - Pawns blocking escape
  - Tags: fools, pages, create, mate, apps

- **createCheckPosition2** (my-games)
  - File: `apps/web/src/pages/ChessCheckTestPage.tsx:288`
  - Create different test positions
  - Tags: pages, create, chesschecktestpage.tsx, check, position

- **getJackpotStatus** (my-games)
  - File: `apps/api/src/services/jackpotService.ts:113`
  - Get current jackpot status with breakdown of sources
  - Tags: api, jackpotservice.ts, services, get, jackpot

- **setupPresenceHandler** (my-games)
  - File: `apps/api/src/socket/presenceHandler.ts:24`
  - Presence events constants (defined locally to avoid module resolution issues)
  - Tags: api, presence, handler, socket, setup

- **get_messages** (my-games)
  - File: `autocoder/server/services/assistant_database.py:239`
  - Tags: messages, services, get, assistant_database.py, autocoder

- **createUserA** (my-games)
  - File: `apps/web/src/pages/Level2ReferralTestPage.tsx:65`
  - Steps tracking
  - Tags: pages, create, user, level2referraltestpage.tsx, apps

- **get_connection_count** (my-games)
  - File: `autocoder/server/websocket.py:559`
  - Clean up dead connections
  - Tags: websocket.py, get, count, autocoder, connection

- **getPlayerName** (my-games)
  - File: `apps/web/src/pages/MatchPage.tsx:157`
  - Match forfeited successfully, refresh match data
  - Tags: name, matchpage.tsx, get, pages, player

- **getFeatureState** (my-games)
  - File: `autocoder/ui/src/hooks/useFeatureSound.ts:61`
  - Clean up audio context after sounds finish
  - Tags: feature, usefeaturesound.ts, get, state, autocoder

- **settingLabel** (my-games)
  - File: `apps/web/src/pages/SettingsPage.tsx:141`
  - Get the setting name for specific feedback
  - Tags: label, pages, utility, settingspage.tsx, apps

- **getAssistantConversation** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:339`
  - ============================================================================
  - Tags: get, api.ts, conversation, autocoder, ui

- **sanitize_output** (my-games)
  - File: `autocoder/server/services/dev_server_manager.py:61`
  - AWS keys
  - Tags: services, autocoder, output, server, sanitize

- **get_project_manager** (my-games)
  - File: `autocoder/server/routers/agent.py:71`
  - Validate and sanitize project name to prevent path traversal.
  - Tags: agent.py, manager, get, autocoder, project

- **update_feature** (my-games)
  - File: `autocoder/server/routers/features.py:415`
  - Tags: feature, update, features.py, autocoder, server

- **updatedSubscription** (my-games)
  - File: `apps/api/src/services/subscriptionService.ts:301`
  - Set the period to be in the past
  - Tags: api, services, subscription, subscriptionservice.ts, updated

- **getLogLevel** (my-games)
  - File: `autocoder/ui/src/components/DebugLogViewer.tsx:262`
  - Get the current log count based on active tab
  - Tags: log, get, level, components, debuglogviewer.tsx

- **deleteMatches** (my-games)
  - File: `apps/api/src/test/setup.ts:22`
  - Setup database connection for tests
  - Tags: api, delete, matches, setup.ts, apps

- **generateCsrfToken** (my-games)
  - File: `apps/api/src/middleware/csrf.ts:21`
  - Generate a secure CSRF token
  - Tags: api, csrf.ts, middleware, token, generate

- **deleteFailedLogins** (my-games)
  - File: `apps/api/src/test/setup.ts:24`
  - Cleanup database connection
  - Tags: api, delete, failed, setup.ts, apps

- **parseFilters** (my-games)
  - File: `apps/api/src/lib/fields.ts:143`
  - Parse filter parameters
  - Tags: api, fields.ts, filters, parse, apps

- **validateCheckersMove** (my-games)
  - File: `apps/api/src/socket/handlers/gameHandler.ts:626`
  - Validate checkers move using the checkers engine
  - Tags: validate, api, socket, utility, handlers

- **getPieceCount** (my-games)
  - File: `apps/api/src/game-engines/checkers/board.ts:153`
  - Get all pieces for a player
  - Tags: api, get, count, piece, game-engines

- **setupTournamentChatHandler** (my-games)
  - File: `apps/api/src/socket/tournamentChatHandler.ts:23`
  - socketId -> user info
  - Tags: api, handler, socket, setup, tournament

- **createEmptyBoard** (my-games)
  - File: `apps/web/src/pages/CheckersKingPromotionTestPage.tsx:40`
  - ===========================================
  - Tags: checkerskingpromotiontestpage.tsx, pages, create, board, empty

- **getTTTEmptyCells** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:515`
  - Rows
  - Tags: api, get, socket, matchhandler.ts, cells

- **getLegalMoves** (my-games)
  - File: `apps/web/src/pages/CheckersKingPromotionTestPage.tsx:162`
  - Tags: checkerskingpromotiontestpage.tsx, get, pages, web, legal

- **setPiece** (my-games)
  - File: `apps/web/src/pages/CheckersMultiJumpTestPage.tsx:73`
  - ===========================================
  - Tags: pages, piece, set, checkersmultijumptestpage.tsx, apps

- **createEmptyBoard** (my-games)
  - File: `apps/web/src/pages/ChessPawnPromotionTestPage.tsx:394`
  - ===========================================
  - Tags: chesspawnpromotiontestpage.tsx, pages, create, board, empty

- **getAvailableModels** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:370`
  - ============================================================================
  - Tags: get, api.ts, models, autocoder, available

- **getNextScheduledRun** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:498`
  - Tags: get, scheduled, api.ts, next, autocoder

- **get_available_models** (my-games)
  - File: `autocoder/server/routers/settings.py:47`
  - Parse YOLO mode string to boolean.
  - Tags: get, models, autocoder, available, server

- **generateBackupCode** (my-games)
  - File: `apps/api/src/lib/twoFactor.ts:210`
  - Generate a random backup code
  - Tags: api, twofactor.ts, backup, code, generate

- **setup_python_venv** (my-games)
  - File: `autocoder/start_ui.py:77`
  - Run a command and return success status.
  - Tags: setup, venv, autocoder, python, start_ui.py

- **sanitizedMessage** (my-games)
  - File: `apps/api/src/socket/matchHandler.ts:3087`
  - Check if chat is enabled (both players consented)
  - Tags: api, sanitized, socket, message, matchhandler.ts

- **normalizedPath** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:287`
  - Backend expects { parent_path, name }, not { path }
  - Tags: ui, path, api.ts, autocoder, normalized

- **getDatabaseStats** (my-games)
  - File: `apps/api/src/lib/dbHealth.ts:28`
  - Check if database connection is healthy
  - Tags: api, dbhealth.ts, get, stats, apps

- **generateId** (my-games)
  - File: `autocoder/ui/src/hooks/useSpecChat.ts:30`
  - Tags: usespecchat.ts, generate, autocoder, hooks, ui

- **updatedToWallet** (my-games)
  - File: `apps/api/src/services/walletService.ts:1358`
  - 2. Get or create recipient's wallet
  - Tags: api, services, wallet, walletservice.ts, updated

- **generateId** (my-games)
  - File: `autocoder/ui/src/hooks/useAssistantChat.ts:26`
  - Tags: generate, autocoder, hooks, ui, useassistantchat.ts

- **generateTestEmail** (my-games)
  - File: `apps/web/src/pages/StreakResetTestPage.tsx:59`
  - Tags: pages, generate, email, streakresettestpage.tsx, apps

- **getPlanIcon** (my-games)
  - File: `apps/web/src/pages/SubscriptionsPage.tsx:238`
  - Tags: subscriptionspage.tsx, icon, get, pages, plan

- **formatChessClockTime** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:720`
  - Format time for chess clock display (mm:ss)
  - Tags: chess, clock, pages, web, gameplaypage.tsx

- **sanitize_output** (my-games)
  - File: `autocoder/server/services/process_manager.py:47`
  - Anthropic API keys
  - Tags: services, process_manager.py, autocoder, output, server

- **getAgentStatus** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:203`
  - ============================================================================
  - Tags: ui, get, api.ts, autocoder, agent

- **getCurrentLogCount** (my-games)
  - File: `autocoder/ui/src/components/DebugLogViewer.tsx:248`
  - Handle clear button based on active tab
  - Tags: log, get, components, count, debuglogviewer.tsx

- **getProjectPrompts** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:89`
  - Tags: get, api.ts, autocoder, project, ui

- **createScholarsMate** (my-games)
  - File: `apps/web/src/pages/ChessCheckmateTestPage.tsx:298`
  - ============================================
  - Tags: scholars, pages, create, mate, apps

- **getLegalMoves** (my-games)
  - File: `games/checkers/server/index.ts:183`
  - Get all legal moves for a piece (considering forced captures)
  - Tags: get, server, games, checkers, legal

- **formatTime** (my-games)
  - File: `apps/web/src/components/TournamentChat.tsx:60`
  - Clear new message indicator when opening chat
  - Tags: components, web, tournamentchat.tsx, apps, format

- **setChessPiece** (my-games)
  - File: `apps/web/src/pages/GamePlayPage.tsx:449`
  - Chess Legal Move Calculation
  - Tags: chess, pages, gameplaypage.tsx, piece, set

- **delete_conversation** (my-games)
  - File: `autocoder/server/services/assistant_database.py:183`
  - Tags: delete, services, conversation, assistant_database.py, autocoder

- **formatDateTime** (my-games)
  - File: `apps/web/src/pages/SubscriptionsPage.tsx:200`
  - Tags: subscriptionspage.tsx, date, pages, web, apps

- **getGoogleConfig** (my-games)
  - File: `apps/api/src/routes/auth.ts:15`
  - Google OAuth configuration - read at runtime, not module load time
  - Tags: google, config, api, routes, get

- **setDependencies** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:185`
  - Tags: api.ts, autocoder, set, ui, utility

- **parseCursorPagination** (my-games)
  - File: `apps/api/src/lib/pagination.ts:160`
  - Cursor-based pagination (for future use with large datasets)
  - Tags: api, pagination, cursor, pagination.ts, parse

- **getStats** (my-games)
  - File: `apps/api/src/lib/cache/cacheService.ts:137`
  - Clear all cache entries
  - Tags: api, cache, get, cacheservice.ts, stats

- **settings** (my-games)
  - File: `apps/api/src/socket/presenceHandler.ts:123`
  - For each friend who has notifications enabled and is online
  - Tags: api, socket, presencehandler.ts, settings, apps

- **set_session_maker** (my-games)
  - File: `autocoder/api/database.py:379`
  - Migrate to add schedules tables
  - Tags: api, session, database.py, maker, autocoder

- **getPlanById** (my-games)
  - File: `apps/api/src/routes/subscriptions.ts:193`
  - Helper function to get plan by id
  - Tags: api, routes, get, plan, apps

- **getAvailableCategories** (my-games)
  - File: `apps/api/src/game-engines/trivia/question-selection.ts:167`
  - Get available categories
  - Tags: api, get, question-selection.ts, categories, trivia

- **createCheckMustEscapePosition** (my-games)
  - File: `apps/web/src/pages/ChessCheckTestPage.tsx:325`
  - White pieces
  - Tags: pages, create, escape, chesschecktestpage.tsx, check

- **getPiece** (my-games)
  - File: `apps/web/src/pages/CheckersKingPromotionTestPage.tsx:109`
  - Kings can move in all 4 diagonal directions
  - Tags: checkerskingpromotiontestpage.tsx, get, pages, piece, apps

- **getMascotColor** (my-games)
  - File: `autocoder/ui/src/components/ActivityFeed.tsx:84`
  - Tags: color, activityfeed.tsx, get, components, autocoder

- **getPieceChar** (my-games)
  - File: `apps/api/src/game-engines/chess/game-state.ts:210`
  - Get piece character for FEN
  - Tags: api, char, chess, get, game-state.ts

- **updatedWinnerWallet** (my-games)
  - File: `apps/api/src/services/walletService.ts:765`
  - 1. Award credits to winner
  - Tags: api, winner, services, wallet, walletservice.ts

- **getBadgeStyle** (my-games)
  - File: `apps/web/src/pages/ProfilePage.tsx:907`
  - Determine badge background color based on badgeColor
  - Tags: badge, get, pages, profilepage.tsx, apps

- **getStateText** (my-games)
  - File: `autocoder/ui/src/components/AgentCard.tsx:13`
  - Get a friendly state description
  - Tags: get, components, state, agentcard.tsx, autocoder

- **settings** (my-games)
  - File: `apps/api/src/services/emailService.ts:137`
  - Send marketing email to user (if opted in)
  - Tags: api, services, emailservice.ts, settings, apps

- **getLockoutStatus** (my-games)
  - File: `apps/api/src/lib/lockout.ts:157`
  - Get lockout status for display to user
  - Tags: api, get, lockout, lockout.ts, status

- **getSlidingAttacks** (my-games)
  - File: `apps/api/src/game-engines/chess/move-validation.ts:217`
  - Get sliding piece attacks (for check detection)
  - Tags: api, chess, sliding, attacks, get

- **getRawMoves** (my-games)
  - File: `games/chess/server/index.ts:160`
  - Get raw moves without checking for leaving king in check
  - Tags: chess, get, server, raw, games

- **create_project** (my-games)
  - File: `autocoder/server/routers/projects.py:132`
  - Skip if path no longer exists
  - Tags: projects.py, create, autocoder, project, server

- **formatDate** (my-games)
  - File: `apps/web/src/pages/ReferralsPage.tsx:343`
  - Tags: date, pages, web, referralspage.tsx, apps

- **updateGamePlayedMilestone** (my-games)
  - File: `apps/api/src/services/milestoneService.ts:16`
  - Milestone Service
  - Tags: api, game, services, milestone, update

- **deleteAssistantConversation** (my-games)
  - File: `autocoder/ui/src/lib/api.ts:356`
  - Tags: delete, api.ts, conversation, autocoder, ui

- **updatedWallet** (my-games)
  - File: `apps/api/src/routes/wallet.ts:1240`
  - Get or create wallet
  - Tags: api, routes, wallet.ts, wallet, updated
