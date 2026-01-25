# Task Tracker

A focused task management app with status tracking, optimistic UI updates, and user-owned task workflows.

## Quick Start

```bash
# From the project root
cd projects/task-tracker

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Prisma setup
npx prisma generate
npx prisma migrate dev --name init

# Run dev server
npm run dev
```

App runs on `http://localhost:3000` by default.

## Environment

See `.env.example` for required values. Key items:

- `DATABASE_URL`
- `NEXT_PUBLIC_APP_URL`
- `AUTH_GITHUB_ID`
- `AUTH_GITHUB_SECRET`
- `AUTH_SECRET` (generate via `npx auth secret`)

## Scripts

- `npm run dev` - local development
- `npm run build` - production build
- `npm run start` - start production server
- `npm run lint` - lint

## Tech Stack

- Next.js 15
- Auth.js (NextAuth)
- Prisma + PostgreSQL
- Tailwind CSS

## Project Structure

- `src/app` - routes and pages
- `src/shared` - shared UI + utilities
- `prisma/` - schema and migrations
- `.planning/` - GSD planning artifacts

## Notes

- GitHub OAuth is required for authentication.
- Use the repository root `CONTRIBUTING.md` for workflow standards.
- Live status: https://mywork-task-tracker.vercel.app/status
