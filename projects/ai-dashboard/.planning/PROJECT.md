# AI Dashboard - Project Definition

> Personal AI command center for tracking top AI content and automating YouTube video creation

---

## Vision

A comprehensive dashboard that:
1. Automatically aggregates the best AI content from YouTube, news sources, and GitHub
2. Provides a YouTube automation pipeline for creating and publishing AI-focused videos
3. Runs on scheduled intervals with minimal maintenance

---

## Problem Statement

Keeping up with AI developments is time-consuming:
- Too many YouTube videos to watch
- News scattered across multiple sources
- Hard to track trending open-source projects
- Creating YouTube content requires manual effort

---

## Solution

An automated dashboard that:
- Scrapes top AI videos every 8 hours (quality-ranked)
- Aggregates AI news every 4 hours from trusted sources
- Tracks GitHub trending AI projects every 12 hours
- Provides a prompt-to-YouTube pipeline with approval workflow

---

## Target Users

- **Primary:** You (personal tool)
- **Secondary:** AI enthusiasts who want curated content

---

## Core Features

### 1. YouTube AI Video Scraper
- Fetch top AI/ML videos using Apify
- Quality scoring: views, likes, engagement rate
- Filter: >10K views, >2% engagement, last 8 days
- Schedule: Every 8 hours

### 2. AI News Aggregator
- Sources: TechCrunch, Verge, Hacker News, Reddit
- Ranking by engagement signals
- Schedule: Every 4 hours

### 3. GitHub Trending Projects
- Top 20 AI/ML repositories
- Track weekly star growth
- Categories: ML, NLP, Computer Vision, Agents
- Schedule: Every 12 hours

### 4. YouTube Automation Pipeline
- User prompt input
- DSPy/LangChain optimization
- Claude script generation
- HeyGen video creation
- Preview & edit workflow
- Approval gate
- YouTube upload

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, SQLAlchemy, SQLite |
| Scheduler | APScheduler |
| Frontend | Next.js 14, TypeScript, Tailwind |
| Scrapers | Apify, yt-dlp, GitHub API |
| AI | Claude API, DSPy |
| Video | HeyGen |

---

## Success Criteria

1. Dashboard loads with fresh data within 24 hours
2. All three scrapers run on schedule without failure
3. YouTube automation creates publishable video from prompt
4. Frontend displays all data with proper filtering/sorting

---

## Out of Scope (v1)

- Multi-user authentication
- Public deployment
- Mobile app
- Real-time notifications
- Video editing within the app

---

## Dependencies

| Service | Purpose | Required |
|---------|---------|----------|
| Apify | YouTube scraping | Yes |
| Anthropic | Claude for scripts | Yes |
| HeyGen | Video generation | For YouTube Bot |
| GitHub Token | Higher rate limits | Recommended |

---

## Timeline

- **Phase 1:** Core scrapers and data display
- **Phase 2:** YouTube automation pipeline
- **Phase 3:** Polish and deployment

---

*Created: 2026-01-25*
*Framework: MyWork GSD*
