# AI Dashboard - Pitfalls and Common Mistakes

**Last Updated**: 2026-01-29
**Project Status**: MVP Complete, Phase 7 (Production-Ready)

---

## Critical Pitfalls (Must Avoid)

### 1. Breaking YouTube OAuth Flow ⚠️ **CRITICAL**

**The Mistake**:
Modifying the OAuth flow without understanding the complete flow.

**What Happens**:
- OAuth tokens become invalid
- Users can't authenticate
- Uploads fail completely
- **System becomes unusable**

**How to Avoid**:
1. **Read the complete OAuth flow first**:
   - `backend/services/youtube_automation.py` - Complete OAuth logic
   - Test OAuth flow in development first
   - Never modify OAuth in production without testing

2. **Understand token storage**:
   - Tokens stored in database
   - Refresh tokens must be handled carefully
   - Never log tokens or expose them in API responses

3. **Test OAuth completely**:
   - Test authorization flow end-to-end
   - Test token refresh logic
   - Test error handling (user denies access)
   - Test with real YouTube account

**Recovery**:
If OAuth is broken:
1. Revert changes immediately
2. Clear all tokens from database
3. Test OAuth flow from scratch
4. Re-deploy only when verified

---

### 2. Corrupting the Database ⚠️ **CRITICAL**

**The Mistake**:
Modifying database schema without proper migration.

**What Happens**:
- Existing data becomes inaccessible
- Application crashes on startup
- **Data loss possible**

**How to Avoid**:
1. **Always backup before schema changes**:
   ```bash
   cp ai_dashboard.db ai_dashboard.db.backup
   ```

2. **Use Alembic for migrations** (future):
   ```bash
   alembic revision --autogenerate -m "description"
   alembic upgrade head
   ```

3. **Test migrations on copy**:
   - Copy database to test environment
   - Run migration on test database
   - Verify data integrity
   - Only then run on production

4. **Never modify models.py directly in production**:
   - Create migration first
   - Test migration
   - Apply migration
   - Verify application works

**Recovery**:
If database is corrupted:
1. Restore from backup: `cp ai_dashboard.db.backup ai_dashboard.db`
2. If no backup, attempt manual data recovery
3. Consider this a **critical lesson** - always backup!

---

### 3. Breaking Scraper Scheduled Jobs ⚠️ **HIGH**

**The Mistake**:
Modifying scraper logic without considering scheduler impact.

**What Happens**:
- Scrapers stop running automatically
- Data becomes stale
- **User sees no new content**

**How to Avoid**:
1. **Understand APScheduler**:
   - Jobs are scheduled with cron-like syntax
   - Jobs must not overlap
   - Jobs must handle errors gracefully

2. **Test scraper changes locally**:
   ```python
   # Test scraper manually
   from scrapers.news import NewsAggregator
   scraper = NewsAggregator()
   items = scraper.scrape()
   print(f"Scraped {len(items)} items")
   ```

3. **Add error handling**:
   ```python
   try:
       items = scraper.scrape()
   except Exception as e:
       logger.error(f"Scraper failed: {e}")
       # Don't crash the scheduler!
   ```

4. **Monitor scraper logs**:
   - Check logs regularly
   - Look for scraper failures
   - Fix issues promptly

**Recovery**:
If scrapers stop working:
1. Check scheduler logs: `grep "scrap" logs/`
2. Manually run scraper to test
3. Restart scheduler if needed
4. Fix the bug and redeploy

---

### 4. Exposing Sensitive Data ⚠️ **SECURITY**

**The Mistake**:
Committing sensitive data to Git or exposing in API responses.

**What Happens**:
- **Security breach** - OAuth tokens exposed
- **Privacy violation** - User data exposed
- **Account takeover** - YouTube account compromised

**How to Avoid**:
1. **Never commit .env files**:
   ```gitignore
   .env
   *.db
   __pycache__
   ```

2. **Use .env.example for documentation**:
   ```bash
   # .env.example (safe to commit)
   YOUTUBE_CLIENT_ID=your_client_id_here
   YOUTUBE_CLIENT_SECRET=your_client_secret_here
   ```

3. **Never log sensitive data**:
   ```python
   # BAD - Don't do this!
   logger.info(f"Token: {access_token}")

   # GOOD - Log without sensitive data
   logger.info("OAuth token received")
   ```

4. **Never expose tokens in API responses**:
   ```python
   # BAD - Don't do this!
   @app.get("/api/youtube/status")
   def get_status():
       return {"token": access_token}  # ❌ Exposed!

   # GOOD - Return status only
   @app.get("/api/youtube/status")
   def get_status():
       return {"connected": bool(access_token)}  # ✅ Safe
   ```

**Recovery**:
If sensitive data is exposed:
1. **Immediately rotate secrets**:
   - Revoke OAuth tokens in YouTube Console
   - Generate new client credentials
   - Update .env file
2. **Remove exposed data from Git history**:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" HEAD
   ```
3. **Force push** (if necessary, but be careful!)

---

### 5. Blocking the Event Loop ⚠️ **PERFORMANCE**

**The Mistake**:
Using synchronous operations in async functions.

**What Happens**:
- Application becomes unresponsive
- Scrapers run slowly
- **Poor user experience**

**How to Avoid**:
1. **Use async/await correctly**:
   ```python
   # GOOD - Async scraper
   async def scrape_news():
       async with aiohttp.ClientSession() as session:
           async with session.get(url) as response:
               return await response.text()

   # BAD - Synchronous scraper in async function
   async def scrape_news():
       response = requests.get(url)  # ❌ Blocks!
       return response.text
   ```

2. **Use async database operations**:
   ```python
   # GOOD - Async database query
   async def get_news():
       async with AsyncSession(database.engine) as session:
           result = await session.execute(select(NewsItem))
           return result.scalars().all()
   ```

3. **Run scrapers in background**:
   ```python
   # Use APScheduler for background jobs
   scheduler.add_job(scrape_news, 'interval', minutes=30)
   ```

**Recovery**:
If application is unresponsive:
1. Check for blocking operations
2. Convert to async where needed
3. Use background tasks for long-running operations

---

## Common Mistakes (Frequently Encountered)

### 6. Forgetting to Handle Scraping Errors

**The Mistake**:
Scrapers fail when website structure changes.

**What Happens**:
- Scrapers return empty results
- Database fills with errors
- **User sees no content**

**How to Avoid**:
1. **Add error handling to all scrapers**:
   ```python
   try:
       items = scraper.scrape()
   except Exception as e:
       logger.error(f"Scraper failed: {e}")
       items = []  # Return empty list, don't crash
   ```

2. **Validate scraped data**:
   ```python
   if not items or len(items) == 0:
       logger.warning("Scraper returned no items")
       return []
   ```

3. **Set scraping timeouts**:
   ```python
   response = requests.get(url, timeout=10)  # 10 second timeout
   ```

**Recovery**:
If scraper is failing:
1. Check logs for error messages
2. Test scraper manually
3. Fix the scraper code
4. Clear database of bad data

---

### 7. Hardcoding URLs and Configuration

**The Mistake**:
Hardcoding URLs, credentials, or configuration.

**What Happens**:
- Can't change configuration without code changes
- Deployment becomes difficult
- **Maintenance nightmare**

**How to Avoid**:
1. **Use environment variables**:
   ```python
   import os
   NEWS_SOURCES = os.getenv("NEWS_SOURCES", "").split(",")
   ```

2. **Use configuration files**:
   ```python
   import json
   with open("config.json") as f:
       config = json.load(f)
   ```

3. **Document configuration**:
   - Update .env.example with new variables
   - Document in README.md

**Recovery**:
If hardcoded values need to change:
1. Refactor to use environment variables
2. Update .env.example
3. Test with different configurations

---

### 8. Ignoring Frontend Performance

**The Mistake**:
Loading all data at once or not optimizing images.

**What Happens**:
- Slow page loads
- High memory usage
- **Poor user experience**

**How to Avoid**:
1. **Implement pagination**:
   ```typescript
   // Load items in batches
   const [page, setPage] = useState(1)
   const items = await fetchNews(page)
   ```

2. **Use Next.js Image optimization**:
   ```typescript
   import Image from 'next/image'
   <Image src={thumbnail} width={320} height={180} />
   ```

3. **Lazy load components**:
   ```typescript
   import dynamic from 'next/dynamic'
   const HeavyComponent = dynamic(() => import('./HeavyComponent'))
   ```

**Recovery**:
If frontend is slow:
1. Add pagination to large lists
2. Optimize images (use Next.js Image)
3. Lazy load components
4. Use React.memo() for expensive components

---

### 9. Not Testing API Changes

**The Mistake**:
Modifying API without testing frontend integration.

**What Happens**:
- Frontend breaks after API changes
- **Application becomes unusable**
- Users see errors

**How to Avoid**:
1. **Test API changes manually**:
   ```bash
   curl http://localhost:8000/api/news
   ```

2. **Test with frontend**:
   - Start frontend: `npm run dev`
   - Navigate to affected pages
   - Verify data loads correctly

3. **Version your API** (future):
   ```python
   @app.get("/api/v2/news")  # Versioned endpoint
   ```

**Recovery**:
If API breaks frontend:
1. Revert API changes
2. Test API and frontend together
3. Fix the issue
4. Re-deploy both together

---

### 10. Forgetting to Restart Services

**The Mistake**:
Modifying code but not restarting services.

**What Happens**:
- Changes don't take effect
- **Confusion - "Why isn't it working?"**
- Wasted debugging time

**How to Avoid**:
1. **Backend changes require restart**:
   ```bash
   # After modifying backend code
   pkill -f "python main.py"
   python main.py
   ```

2. **Frontend changes hot-reload**:
   - Next.js hot-reloads automatically
   - But sometimes need to restart dev server

3. **Scheduler changes require restart**:
   ```bash
   # After modifying scheduler jobs
   pkill -f "python main.py"
   python main.py
   ```

**Recovery**:
If changes aren't taking effect:
1. Check if services are running
2. Restart backend services
3. Restart frontend dev server
4. Clear browser cache

---

## Development Workflow Pitfalls

### 11. Working on Wrong Branch

**The Mistake**:
Making changes on wrong Git branch.

**What Happens**:
- Changes go to wrong place
- **Merge conflicts**
- Confusion about what's deployed

**How to Avoid**:
1. **Always check current branch**:
   ```bash
   git branch
   ```

2. **Create feature branches**:
   ```bash
   git checkout -b feature/new-feature
   ```

3. **Merge to main when done**:
   ```bash
   git checkout main
   git merge feature/new-feature
   ```

**Recovery**:
If on wrong branch:
1. Stash changes: `git stash`
2. Checkout correct branch: `git checkout main`
3. Apply changes: `git stash pop`

---

### 12. Not Reading Documentation First

**The Mistake**:
Starting work without reading project documentation.

**What Happens**:
- Duplicate work
- Wrong approach
- **Wasted time**

**How to Avoid**:
1. **Always read CLAUDE.md first**:
   ```bash
   cat projects/ai-dashboard/CLAUDE.md
   ```

2. **Check planning docs**:
   - `.planning/STATE.md` - Current status
   - `.planning/PROJECT.md` - Project vision
   - `.planning/ROADMAP.md` - What's been done

3. **Check research docs**:
   - `.planning/research/ARCHITECTURE.md` - System design
   - `.planning/research/FEATURES.md` - Feature list
   - `.planning/research/PITFALLS.md` - This file!

**Recovery**:
If you realize you didn't read docs:
1. Stop what you're doing
2. Read the relevant documentation
3. Adjust your approach if needed

---

## YouTube-Specific Pitfalls

### 13. Exceeding YouTube API Quota

**The Mistake**:
Uploading too many videos too quickly.

**What Happens**:
- API quota exceeded
- Uploads fail
- **Can't upload for 24 hours**

**How to Avoid**:
1. **Check quota limits**:
   - YouTube has daily quota limits
   - Check YouTube Console for current quota

2. **Implement rate limiting**:
   ```python
   time.sleep(60)  # Wait between uploads
   ```

3. **Monitor quota usage**:
   ```python
   quota_used = len(uploads_today)
   if quota_used >= QUOTA_LIMIT:
       logger.warning("Quota limit reached")
       return
   ```

**Recovery**:
If quota exceeded:
1. Wait for quota to reset (usually 24 hours)
2. Reduce upload frequency
3. Consider implementing quota management

---

### 14. Ignoring YouTube Video Requirements

**The Mistake**:
Uploading videos that don't meet YouTube requirements.

**What Happens**:
- Uploads fail
- Videos rejected
- **Wasted time**

**How to Avoid**:
1. **Check video requirements**:
   - Format: MP4, MOV, AVI
   - Duration: < 12 hours (recommended < 15 minutes)
   - Size: < 256 GB (recommended < 500 MB)
   - Resolution: 720p to 4K

2. **Validate before upload**:
   ```python
   def validate_video(video_path):
       # Check file exists
       # Check file size
       # Check video duration
       # Check video format
   ```

**Recovery**:
If video rejected:
1. Check rejection reason in YouTube Console
2. Fix the issue (convert, compress, etc.)
3. Re-upload

---

## Summary

**Most Critical Pitfalls**:
1. ⚠️ Breaking YouTube OAuth flow
2. ⚠️ Corrupting the database
3. ⚠️ Breaking scraper scheduled jobs
4. ⚠️ Exposing sensitive data
5. ⚠️ Blocking the event loop

**Common Mistakes**:
6. Scraping error handling
7. Hardcoding configuration
8. Frontend performance
9. API testing
10. Service restart

**Development Workflow**:
11. Wrong Git branch
12. Not reading documentation

**YouTube-Specific**:
13. API quota limits
14. Video requirements

**How to Avoid Pitfalls**:
1. ✅ **Read documentation first** - CLAUDE.md, PITFALLS.md
2. ✅ **Test changes locally** - Never deploy without testing
3. ✅ **Backup before changes** - Database, configuration
4. ✅ **Use version control** - Git branches, commits
5. ✅ **Monitor logs** - Check for errors regularly
6. ✅ **Ask questions** - If unsure, ask before proceeding

**When in Doubt**:
1. Stop what you're doing
2. Read the relevant documentation
3. Test your changes
4. Ask for help if needed
5. Only proceed when confident

**Remember**: It's better to be cautious than to break production!
