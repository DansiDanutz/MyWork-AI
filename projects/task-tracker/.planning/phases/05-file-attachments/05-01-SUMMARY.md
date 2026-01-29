---
phase: 05-file-attachments
plan: 01
subsystem: file-management
tags: [prisma, database, file-validation, security, nextjs]
requires: [04-05]
provides: [file-attachment-schema, file-validation-utilities]
affects: [05-02, 05-03, 05-04, 05-05, 05-06]
tech-stack:
  added: [react-dropzone, file-type, sharp, tus-js-client, @tus/server,
  @tus/file-store]
  patterns: [content-based-mime-validation, magic-byte-detection,
  file-size-validation]
key-files:
  created:

```markdown

- src/shared/lib/file-validation.ts

```yaml

  modified:

```markdown

- prisma/schema.prisma
- next.config.ts
- package.json

```yaml

decisions:

  - id: FILE-001

```yaml
title: Content-based MIME validation over client-provided types
rationale: Security-critical to validate actual file content using magic
bytes, not trust client-provided MIME types or extensions

```yaml

  - id: FILE-002

```yaml
title: 25MB file size limit with 5MB Server Actions threshold
rationale: 25MB generous enough for documents/media, 5MB threshold
determines Server Actions vs TUS protocol for resumable uploads

```

  - id: FILE-003

```yaml
title: FileAttachment with denormalized userId
rationale: Enables direct ownership checks without joining through Task,
improves query performance

```yaml

  - id: FILE-004

```yaml
title: Cascade delete file attachments when task deleted
rationale: Clean orphan file prevention, no abandoned attachments in
database or filesystem

```yaml

metrics:
  duration: 4 minutes
  completed: 2026-01-26
---

# Phase 05 Plan 01: File Attachment Schema & Validation Summary

**One-liner:** Established secure file attachment foundation with magic byte
validation, FileAttachment Prisma model, and resumable upload infrastructure

## What Was Built

### Database Schema

- **FileAttachment model** with comprehensive metadata tracking
  - Task relation with cascade delete (clean orphan prevention)
  - Denormalized userId for direct ownership checks
  - File metadata: filename (display), storedFilename (UUID), mimeType, size
  - Optional thumbnailPath for image previews
  - Indexes on taskId and userId for performance
- **Task model extension** with attachments relation

### File Validation Utilities

- **Content-based MIME validation** using file-type library
  - Magic byte detection for binary files
  - UTF-8 validation for text files without magic bytes
  - Whitelist approach: images, documents, text files, archives
  - Security-critical: validates actual file content, not client metadata
- **Size validation** with 25MB limit and empty file detection
- **Helper functions**:
  - `formatFileSize`: Human-readable size display
  - `shouldUseTusProtocol`: Upload method selection (5MB threshold)
  - `getExtensionFromMime`: File extension mapping
  - `isImageMime`: Thumbnail generation decision

### Infrastructure Configuration

- **Next.js Server Actions** body size limit increased to 5MB
  - Supports small file uploads via Server Actions
  - Large files (>5MB) will use TUS protocol
- **Dependencies installed**:
  - react-dropzone (drag & drop UI)
  - file-type (magic byte detection)
  - sharp (thumbnail generation)
  - tus-js-client, @tus/server, @tus/file-store (resumable uploads)

## Technical Decisions

### FILE-001: Content-Based MIME Validation

**Decision:** Validate file types by reading magic bytes (binary signature),
never trust client-provided MIME types or extensions.

**Context:** Client-provided file information (MIME type, extension) can be
trivially spoofed. Malicious users could upload executable files disguised as
images.

**Implementation:**

- Use file-type library to read binary signatures
- Fallback to UTF-8 validation for text files
- Whitelist approach with ALLOWED_MIME_TYPES constant
- Reject files with unrecognized or disallowed signatures

**Security benefit:** Prevents malicious file uploads by validating actual
content

---

### FILE-002: 25MB Limit with 5MB Server Actions Threshold

**Decision:** Set MAX_FILE_SIZE to 25MB, use Server Actions for ≤5MB, TUS
protocol for >5MB.

**Context:** Server Actions have practical size limits. Large file uploads need
resumable protocol for reliability.

**Implementation:**

- MAX_FILE_SIZE = 25MB (generous for documents, presentations, media)
- SERVER_ACTION_SIZE_LIMIT = 5MB (Next.js body size limit)
- shouldUseTusProtocol helper determines upload method
- next.config.ts configured with bodySizeLimit: '5mb'

**Trade-offs:**

- ✅ Small files: Fast, simple Server Actions
- ✅ Large files: Resumable, network-interrupt recovery
- ⚠️ Two upload code paths to maintain

---

### FILE-003: Denormalized userId in FileAttachment

**Decision:** Store userId directly on FileAttachment, not just via Task
relation.

**Context:** Frequent ownership checks would require joining through Task table.

**Implementation:**

```prisma

model FileAttachment {
  userId  String  // Denormalized
  taskId  String
  task    Task @relation(...)
}

```yaml

**Benefits:**

- Direct ownership queries: `WHERE userId = ?`
- No join required for access control checks
- Faster user file quota calculations

**Trade-off:** Data duplication (userId in both Task and FileAttachment), but
performance gain worth it

---

### FILE-004: Cascade Delete on Task Deletion

**Decision:** Configure FileAttachment with `onDelete: Cascade` when task
deleted.

**Context:** Need automatic cleanup to prevent orphaned attachments.

**Implementation:**

```prisma

task Task @relation(fields: [taskId], references: [id], onDelete: Cascade)

```yaml

**Cleanup flow:**

1. User deletes task
2. Database cascade deletes FileAttachment records
3. Background job (05-03) will delete physical files from filesystem

**Benefit:** Guaranteed no orphaned database records, clean data model

## Implementation Notes

### File Type Detection Strategy

1. **Binary files**: Read magic bytes using file-type library
2. **Text files**: Validate UTF-8 encoding (no magic bytes)
3. **Unknown/corrupted**: Reject with clear error message
4. **Disallowed types**: Reject against ALLOWED_MIME_TYPES whitelist

### Validation Flow

```typescript

// Security-critical validation order

1. validateFileSize(size) → Reject if >25MB or empty
2. validateFileType(buffer) → Read magic bytes, check whitelist
3. If both pass → Proceed with upload
4. If either fails → Return clear error to user

```markdown

### Upload Strategy Decision Tree

```python
File size ≤ 5MB → Server Actions (simple, fast)
File size > 5MB → TUS protocol (resumable, network-safe)
File size > 25MB → Reject with error

```python

## Deviations from Plan

None - plan executed exactly as written.

## Next Phase Readiness

### Blockers for 05-02 (File Storage & TUS Upload)

None - all dependencies installed, schema in place

### Required for 05-02

- ✅ FileAttachment model exists
- ✅ File validation utilities available
- ✅ TUS dependencies installed
- ✅ Size threshold helpers (shouldUseTusProtocol)

### Integration Points for Future Plans

- **05-02**: Will use FileAttachment model to store metadata
- **05-03**: Will use validateFileType, validateFileSize for uploads
- **05-04**: Will use isImageMime for thumbnail generation
- **05-05**: Will query FileAttachment via Task.attachments relation
- **05-06**: Will use formatFileSize for file size display

## Reusable Patterns for Brain

### Pattern: Content-Based File Validation

**Module:** `src/shared/lib/file-validation.ts`

**When to use:** Any file upload feature requiring security

**Key exports:**

```typescript

validateFileType(buffer: Buffer) → Promise<FileValidationResult>
validateFileSize(size: number) → FileValidationResult
ALLOWED_MIME_TYPES: readonly string[]
MAX_FILE_SIZE: number

```yaml

**Security guarantee:** Validates actual file content, not client metadata

**Learning:** Never trust client-provided MIME types or extensions. Always read
magic bytes.

---

### Pattern: Denormalized Foreign Keys for Performance

**Location:** FileAttachment.userId

**When to use:** Frequent ownership checks, user quota calculations

**Trade-off:** Data duplication vs query performance

**Learning:** Denormalization worth it when avoiding joins in hot paths

---

### Pattern: Cascade Delete for Related Data

**Location:** FileAttachment → Task relation

**When to use:** Child records should never exist without parent

**Benefits:** Clean data model, automatic orphan prevention

**Combine with:** Background jobs for physical file cleanup

## Testing Notes

### Manual Verification Performed

- ✅ Prisma migration applied successfully
- ✅ TypeScript compiles without errors (npx tsc --noEmit)
- ✅ All dependencies installed (verified with npm ls)
- ✅ Constants set correctly (25MB, 5MB thresholds)
- ✅ FileAttachment model visible in Prisma schema

### Known Issues

- ⚠️ Next.js 15.0.3 production build fails (documented in STATE.md)
  - Error: Pages Router components incorrectly bundled in App Router
  - Workaround: Development server works correctly
  - Impact: Cannot deploy to production until Next.js fix or workaround
  - Not blocking current development

## Files Changed

### Created

- `src/shared/lib/file-validation.ts` (192 lines)
  - Content-based MIME validation
  - File size validation
  - Helper utilities for upload strategy

### Modified

- `prisma/schema.prisma`
  - Added FileAttachment model (20 lines)
  - Added Task.attachments relation (1 line)
- `next.config.ts`
  - Added experimental.serverActions.bodySizeLimit: '5mb'
  - Added images.remotePatterns for thumbnails
- `package.json`
  - Added react-dropzone, file-type, sharp, tus-* dependencies

## Commits

| Commit | Message | Files |
| -------- | --------- | ------- |
| f29ba01 | feat(05-01): insta... | package.json, next... |
| fd755a7 | feat(05-01): add F... | prisma/schema.prisma |
| 5a11a7d | feat(05-01): creat... | src/shared/lib/fil... |

## Success Criteria

All criteria met:

- [x] FileAttachment model exists in database schema
- [x] File validation utility can detect MIME types by content (magic bytes)
- [x] Server Actions body size limit is configured for 5MB
- [x] All dependencies installed (react-dropzone, file-type, sharp, tus-*)
- [x] TypeScript compiles without errors
- [x] Cascade delete configured (files deleted when task deleted)

---

**Status:** ✅ Complete
**Duration:** 4 minutes
**Next:** 05-02 - File storage utilities and TUS upload endpoint
