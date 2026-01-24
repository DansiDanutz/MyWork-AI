# Testing Patterns

**Analysis Date:** 2026-01-24

## Test Framework

**Runner:**
- Not detected - No Jest, Vitest, or Pytest configuration found in codebase
- Frontend has no test runner configured despite having TypeScript
- Backend has no test framework in requirements.txt

**Assertion Library:**
- Not detected - No testing library present

**Run Commands:**
- Frontend: `npm run lint` - Only linting, no test command exists
- Backend: No test command available

**Status:** This codebase has NO automated testing infrastructure configured.

## Test File Organization

**Location:**
- No test files exist in the codebase
- No `tests/`, `__tests__/`, or `.test.ts/.spec.ts` files found (outside node_modules)

**Naming:**
- Not applicable - no testing convention established

**Structure:**
- Not applicable - no tests present

## Manual Testing Approach

Since automated tests are not configured, the project appears to rely on manual testing:

**Frontend Manual Testing:**
- Navigate through pages and verify UI renders correctly
- Test data loading: visit `/` (dashboard), `/videos`, `/news`, `/projects`, `/youtube-bot`
- Verify buttons trigger correct API calls
- Check error states display properly when API fails

**Backend Manual Testing:**
- Use FastAPI's built-in `/docs` endpoint for testing (accessible at `http://localhost:8000/docs`)
- Manually trigger scrapers via endpoint: `POST /api/videos/scrape`, `POST /api/news/scrape`, `POST /api/projects/scrape`
- Monitor database directly to verify data is persisted
- Check scheduler status via `GET /api/scheduler/status`

## Mocking

**Framework:** Not applicable - no test framework

**Patterns:**
- No mocking library present in dependencies
- Manual mocking would be needed if tests were added

**What to Mock (if tests were to be added):**
- Apify API responses in YouTube scraper tests
- YouTube Data API responses
- HeyGen API for video generation
- Anthropic/Claude API for prompt optimization
- Database queries using SQLAlchemy test fixtures

**What NOT to Mock:**
- Core business logic calculations (quality_score, trending_score)
- Data transformation and parsing logic
- Database ORM operations (if using in-memory SQLite for tests)

## Fixtures and Factories

**Test Data:**
- Not implemented - no test fixtures exist
- Backend has hardcoded search queries in `youtube_scraper.py`:
```python
AI_SEARCH_QUERIES = [
    "AI tutorial 2025",
    "machine learning tutorial",
    "ChatGPT tutorial",
    # ... more queries
]
```

**Location:**
- Would be in `tests/fixtures/` or `tests/factories.py` if implemented
- Currently would need to use real API data or create mock responses

## Coverage

**Requirements:** Not enforced - no coverage tool configured

**View Coverage:**
- Not available - would typically use `pytest --cov` for Python or `jest --coverage` for TS

## Test Types

**Unit Tests:**
- Should test: Individual functions like `formatNumber()`, scoring algorithms (`calculate_quality_score()`, `calculate_trending_score()`)
- Not currently implemented

**Integration Tests:**
- Should test: API endpoints with database (scrapers saving to DB, retrieving data)
- Should test: End-to-end automation flow (create automation → generate video → upload)
- Not currently implemented

**E2E Tests:**
- Framework: Not used - would benefit from Playwright or Cypress
- Should test: Full user workflows in browser
  - Create a new YouTube automation from scratch
  - Scrape videos and verify they appear on dashboard
  - Navigate between pages

**Manual Testing Procedures:**

**Dashboard Page (`/`):**
1. Verify stats cards load (Videos, AI News, GitHub Projects, Automations)
2. Test "Refresh" button - should reload stats without page refresh
3. Verify "Recent Scrapes" section shows latest scraper activity
4. Click on stat cards to navigate to respective pages
5. Test error state by stopping backend and refreshing

**Videos Page (`/videos`):**
1. Verify videos load in grid
2. Test "Refresh" button
3. Test "Scrape Now" button - should trigger scraper and update list
4. Verify video cards display thumbnail, title, view count, like count
5. Test "Watch on YouTube" links open YouTube in new tab
6. Test error handling when API is unavailable

**YouTube Bot Page (`/youtube-bot`):**
1. Verify existing automations load
2. Click "Create Video" to open modal
3. Fill in prompt, target audience, video length
4. Submit form - should create automation and show in list
5. Verify status badges display correctly for different automation states
6. Verify actions appear for each status (Edit for draft, Generate for pending, etc.)

**API Endpoint Testing (via Swagger UI at localhost:8000/docs):**
1. Test `GET /api/videos` with different limit values
2. Test `GET /api/news` and `GET /api/news/trending`
3. Test `GET /api/projects` and `GET /api/projects/trending`
4. Test `POST /api/videos/scrape` - should update database
5. Test `POST /api/automation` with sample prompt
6. Test `PATCH /api/automation/{id}` to update fields
7. Test `POST /api/automation/{id}/approve` to upload video
8. Verify error responses with invalid inputs

## Error Scenarios to Test

**Frontend:**
- Network failure during data fetch - verify error message displays
- Empty data states - verify "No data" messages display
- Long loading times - verify loading spinner shows
- Invalid API responses - should gracefully handle missing fields
- Button disabled states during async operations

**Backend:**
- Missing API keys (APIFY_API_KEY, YOUTUBE_API_KEY, ANTHROPIC_API_KEY)
- API rate limiting from external services
- Database connection failures
- Invalid input data (null values, missing required fields)
- Duplicate data insertion (unique constraints)

## Current Testing Gaps

**Critical Areas Lacking Tests:**
1. Video quality score calculation logic (`YouTubeVideo.calculate_quality_score()`)
2. Project trending score calculation (`GitHubProject.calculate_trending_score()`)
3. YouTube data parsing logic (`_parse_apify_video()`, `_parse_youtube_api_video()`)
4. Prompt optimization and content generation (`PromptOptimizer` class)
5. Video automation pipeline (`YouTubeAutomationService`)
6. API request/response handling
7. Database persistence and retrieval
8. Scraper error handling and retries

**Recommended Test Implementation Order:**
1. Set up Jest for frontend or Vitest (fastest setup)
2. Set up Pytest for backend
3. Add unit tests for calculation/parsing functions
4. Add integration tests for API endpoints
5. Add E2E tests for user workflows

## Recommended Testing Setup

**Frontend:**
```bash
npm install --save-dev vitest @vitest/ui jsdom @testing-library/react @testing-library/jest-dom
```

**Backend:**
```bash
pip install pytest pytest-asyncio pytest-cov httpx[http2]
```

**Example Frontend Test Structure (would go in `__tests__/`):**
```typescript
// app/__tests__/page.test.tsx
import { render, screen } from '@testing-library/react';
import Dashboard from '@/app/page';

describe('Dashboard', () => {
  it('displays loading state initially', () => {
    render(<Dashboard />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });
});
```

**Example Backend Test Structure (would go in `tests/`):**
```python
# tests/test_youtube_scraper.py
import pytest
from database.models import YouTubeVideo

@pytest.mark.asyncio
async def test_parse_apify_video():
    scraper = YouTubeScraper()
    item = {
        "id": "video123",
        "title": "Test Video",
        "channelName": "Test Channel"
    }
    result = scraper._parse_apify_video(item, "test query")
    assert result["video_id"] == "video123"
```

---

*Testing analysis: 2026-01-24*
