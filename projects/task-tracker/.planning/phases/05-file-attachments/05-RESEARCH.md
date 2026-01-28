# Phase 5: File Attachments - Research

**Researched:** 2026-01-25
**Domain:** File upload and management in Next.js 15 with Server Actions
**Confidence:** HIGH

## Summary

File upload in Next.js 15 has evolved significantly with Server Actions, which
now handle FormData natively without additional API routes. However, the context
requirements (25MB files, chunked uploads, resume capability) exceed the
standard Server Actions body size limit (1MB default, configurable to ~5MB max).

**Key findings:**

- Server Actions work great for small-to-medium files (< 5MB) with simple
  implementation
- Chunked uploads with resume capability require dedicated API routes or
  third-party protocols (TUS)
- react-dropzone is the de facto standard for drag & drop UI
- file-type (npm) provides content-based MIME validation (critical for security)
- Sharp is the fastest library for thumbnail generation
- ClamAV integration or pompelmi library recommended for malware scanning

**Primary recommendation:** Use Server Actions for initial upload UI, but
implement dedicated chunked upload API routes using TUS protocol or custom
chunking for files > 5MB. This hybrid approach balances simplicity for small
files with robustness for large files.

## Standard Stack

The established libraries/tools for file upload in Next.js 15:

### Core

| Library | Version | Purpose | Why Standard |
| --------- | --------- | --------- | -------------- |
| react-dropzone | 14.x | Drag & drop UI | Most popula... |
| file-type | 19.x | Content-bas... | Security-cr... |
  | sharp | 0.33.x | Image proce... | Fastest Nod... |  
  | @prisma/client | 7.x | File metada... | Already in ... |  

### Supporting

| Library | Version | Purpose | When to Use |
| --------- | --------- | --------- | ------------- |
| tus-js-client | 4.x | Resumable u... | Files > 5MB... |
| tus-node-se... | 1.x | Resumable u... | Files > 5MB... |
| pompelmi | Latest | In-process ... | Privacy-com... |
  | clamscan | 2.x | ClamAV Node... | If ClamAV a... |  
| image-thumb... | 1.x | Quick thumb... | Alternative... |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
| ------------ | ----------- | ---------- |
| react-dropzone | Native drag & drop... | Less code, but mis... |
| file-type | mime-types | Faster but only checks extensions (security risk) |
| sharp | jimp | Pure JS (no native deps) but 30x slower |
  | TUS protocol | Custom chunking | More control but m... |  

**Installation:**

```bash

# Core dependencies

npm install react-dropzone file-type sharp

# For chunked/resumable uploads (25MB requirement)

npm install tus-js-client @tus/server

# For security scanning (choose one)

npm install pompelmi          # In-process scanning
npm install clamscan          # Requires ClamAV daemon

```markdown

## Architecture Patterns

### Recommended Project Structure

```
src/
├── app/
│   ├── api/
│   │   ├── files/
│   │   │   ├── upload/route.ts       # TUS upload endpoint
│   │   │   ├── download/[id]/route.ts # Secure file serving
│   │   │   └── thumbnail/[id]/route.ts # Thumbnail generation
│   └── actions/
│       └── files.ts                   # Server Actions for small files
├── components/
│   ├── FileDropzone.tsx               # Drag & drop component
│   ├── FileUploadProgress.tsx         # Progress bar with cancellation
│   └── FileThumbnail.tsx              # Preview component
├── lib/
│   ├── file-upload.ts                 # Upload utilities
│   ├── file-validation.ts             # MIME validation & security
│   ├── file-storage.ts                # Filesystem operations
│   └── thumbnail-generator.ts         # Sharp integration
└── uploads/                            # File storage (gitignored)

```
└── [userId]/
    └── [taskId]/
        ├── [fileId].ext
        └── thumbs/
            └── [fileId].webp

```
```markdown

### Pattern 1: Server Actions for Small Files (< 5MB)

**What:** Use Next.js Server Actions directly for simple file uploads without
separate API routes

**When to use:** Files under 5MB, no chunking/resume required, standard form
submission

**Example:**

```typescript

// src/app/actions/files.ts
'use server'

import { auth } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { validateFileType } from '@/lib/file-validation'
import fs from 'fs/promises'
import path from 'path'

export async function uploadFileSimple(formData: FormData) {
  const session = await auth()
  if (!session?.user?.id) throw new Error('Unauthorized')

  const file = formData.get('file') as File
  const taskId = formData.get('taskId') as string

  // Validate file type by content, not extension
  const buffer = Buffer.from(await file.arrayBuffer())
  const fileType = await validateFileType(buffer)

  if (!fileType.isValid) {

```
return { error: 'Invalid file type' }

```
  }

  // Store file
  const uploadDir = path.join(process.cwd(), 'uploads', session.user.id, taskId)
  await fs.mkdir(uploadDir, { recursive: true })

  const filename = `${crypto.randomUUID()}.${fileType.ext}`
  await fs.writeFile(path.join(uploadDir, filename), buffer)

  // Save metadata
  const attachment = await prisma.fileAttachment.create({

```
data: {
  taskId,
  filename: file.name,
  storedFilename: filename,
  mimeType: fileType.mime,
  size: file.size,
  userId: session.user.id,
},

```
  })

  return { success: true, id: attachment.id }
}

```

**Configure body size limit in next.config.ts:**

```typescript

const nextConfig: NextConfig = {
  experimental: {

```
serverActions: {
  bodySizeLimit: '5mb', // Increase from default 1mb
},

```
  },
}

```markdown

### Pattern 2: TUS Protocol for Large Files (> 5MB)

**What:** Implement TUS resumable upload protocol for chunked uploads with
resume capability

**When to use:** Files > 5MB, need resume after network interruption, progress
tracking

**Example Server:**

```typescript

// src/app/api/files/upload/route.ts
import { Server } from '@tus/server'
import { FileStore } from '@tus/file-store'
import { NextRequest } from 'next/server'
import path from 'path'

const uploadDir = path.join(process.cwd(), 'uploads', 'temp')

const tusServer = new Server({
  path: '/api/files/upload',
  datastore: new FileStore({ directory: uploadDir }),

  // Security: validate on upload complete
  async onUploadFinish(req, upload) {

```
const userId = req.headers['user-id'] // From auth middleware
const taskId = upload.metadata?.taskId

// Move from temp to final location
// Validate file type
// Create DB record

```
  },
})

export async function POST(request: NextRequest) {
  return tusServer.handle(request)
}

export async function HEAD(request: NextRequest) {
  return tusServer.handle(request)
}

export async function PATCH(request: NextRequest) {
  return tusServer.handle(request)
}

export async function OPTIONS(request: NextRequest) {
  return tusServer.handle(request)
}

```

**Example Client:**

```typescript

// src/components/FileDropzone.tsx
import { useDropzone } from 'react-dropzone'
import * as tus from 'tus-js-client'
import { useState } from 'react'

export function FileDropzone({ taskId }: { taskId: string }) {
  const [progress, setProgress] = useState<Record<string, number>>({})
  const [uploads, setUploads] = useState<Record<string, tus.Upload>>({})

  const onDrop = (acceptedFiles: File[]) => {

```
acceptedFiles.forEach((file) => {
  const upload = new tus.Upload(file, {
    endpoint: '/api/files/upload',
    retryDelays: [0, 3000, 5000, 10000, 20000],
    metadata: {
      filename: file.name,
      filetype: file.type,
      taskId,
    },
    onProgress: (bytesUploaded, bytesTotal) => {
      const percentage = ((bytesUploaded / bytesTotal) * 100).toFixed(2)
      setProgress((prev) => ({ ...prev, [file.name]: Number(percentage) }))
    },
    onSuccess: () => {
      console.log('Upload complete:', file.name)
      setUploads((prev) => {
        const { [file.name]: _, ...rest } = prev
        return rest
      })
    },
    onError: (error) => {
      console.error('Upload failed:', error)
    },
  })

  setUploads((prev) => ({ ...prev, [file.name]: upload }))
  upload.start()
})

```
  }

  const cancelUpload = (filename: string) => {

```
uploads[filename]?.abort()
setUploads((prev) => {
  const { [filename]: _, ...rest } = prev
  return rest
})

```
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({

```
onDrop,
maxSize: 25 * 1024 * 1024, // 25MB

```
  })

  return (

```
<div {...getRootProps()} className="border-2 border-dashed p-8">
  <input {...getInputProps()} />
  {isDragActive ? (
    <p>Drop files here...</p>
  ) : (
    <p>Drag files here, or click to select</p>
  )}

  {Object.entries(progress).map(([filename, pct]) => (
    <div key={filename} className="mt-2">
      <div className="flex justify-between">
        <span>{filename}</span>
        <button onClick={() => cancelUpload(filename)}>Cancel</button>
      </div>
      <progress value={pct} max="100" className="w-full" />
    </div>
  ))}
</div>

```
  )
}

```markdown

### Pattern 3: Content-Based File Validation

**What:** Validate files by reading magic numbers (binary signatures), not
extensions

**When to use:** Every file upload (security-critical)

**Example:**

```typescript

// src/lib/file-validation.ts
import { fileTypeFromBuffer } from 'file-type'

const ALLOWED_MIME_TYPES = [
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  // Add more as needed
]

const MAX_FILE_SIZE = 25 * 1024 * 1024 // 25MB

export async function validateFileType(buffer: Buffer) {
  // Check magic number (first few bytes)
  const type = await fileTypeFromBuffer(buffer)

  if (!type) {

```
return { isValid: false, error: 'Unable to detect file type' }

```
  }

  if (!ALLOWED_MIME_TYPES.includes(type.mime)) {

```
return {
  isValid: false,
  error: `File type ${type.mime} not allowed`,
  detected: type.mime,
}

```
  }

  return {

```
isValid: true,
mime: type.mime,
ext: type.ext,

```
  }
}

export function validateFileSize(size: number) {
  if (size > MAX_FILE_SIZE) {

```
return {
  isValid: false,
  error: `File size ${(size / 1024 / 1024).toFixed(2)}MB exceeds limit of ${MAX_FILE_SIZE / 1024 / 1024}MB`,
}

```
  }
  return { isValid: true }
}

```

### Pattern 4: Secure File Serving with Authentication

**What:** Serve files through authenticated route handlers, not direct
filesystem access

**When to use:** All file downloads (enforces task ownership)

**Example:**

```typescript

// src/app/api/files/download/[id]/route.ts
import { auth } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs/promises'
import path from 'path'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const session = await auth()
  if (!session?.user?.id) {

```
return new NextResponse('Unauthorized', { status: 401 })

```
  }

  // Get file metadata
  const file = await prisma.fileAttachment.findUnique({

```
where: { id: params.id },
include: { task: true },

```
  })

  if (!file) {

```
return new NextResponse('File not found', { status: 404 })

```
  }

  // Check ownership (user owns the task)
  if (file.task.userId !== session.user.id) {

```
return new NextResponse('Forbidden', { status: 403 })

```
  }

  // Read file
  const filePath = path.join(

```
process.cwd(),
'uploads',
file.userId,
file.taskId,
file.storedFilename

```
  )

  try {

```
const buffer = await fs.readFile(filePath)

return new NextResponse(buffer, {
  headers: {
    'Content-Type': file.mimeType,
    'Content-Disposition': `attachment; filename="${file.filename}"`,
    'Content-Length': file.size.toString(),
  },
})

```
  } catch (error) {

```
return new NextResponse('File not found on disk', { status: 404 })

```
  }
}

```markdown

### Pattern 5: Thumbnail Generation with Sharp

**What:** Generate optimized thumbnails on upload for fast preview display

**When to use:** Image files only, after successful upload

**Example:**

```typescript

// src/lib/thumbnail-generator.ts
import sharp from 'sharp'
import path from 'path'
import fs from 'fs/promises'

const THUMBNAIL_SIZE = 200 // pixels
const THUMBNAIL_QUALITY = 80

export async function generateThumbnail(
  sourcePath: string,
  userId: string,
  taskId: string,
  fileId: string
): Promise<string | null> {
  const ext = path.extname(sourcePath).toLowerCase()
  const imageExts = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

  if (!imageExts.includes(ext)) {

```
return null // Not an image

```
  }

  try {

```
const thumbDir = path.join(
  process.cwd(),
  'uploads',
  userId,
  taskId,
  'thumbs'
)
await fs.mkdir(thumbDir, { recursive: true })

const thumbPath = path.join(thumbDir, `${fileId}.webp`)

await sharp(sourcePath)
  .resize(THUMBNAIL_SIZE, THUMBNAIL_SIZE, {
    fit: 'cover',
    position: 'center',
  })
  .webp({ quality: THUMBNAIL_QUALITY })
  .toFile(thumbPath)

return thumbPath

```
  } catch (error) {

```
console.error('Thumbnail generation failed:', error)
return null

```
  }
}

```

### Pattern 6: Cascade Delete with Prisma

**What:** Automatically delete files when parent task is deleted

**When to use:** File cleanup on task deletion

**Example:**

```prisma

// prisma/schema.prisma
model Task {
  id          String   @id @default(cuid())
  title       String
  userId      String
  attachments FileAttachment[]

  @@index([userId])
}

model FileAttachment {
  id              String   @id @default(cuid())
  taskId          String
  task            Task     @relation(fields: [taskId], references: [id], onDelete: Cascade)
  filename        String   // Original filename
  storedFilename  String   // UUID-based stored filename
  mimeType        String
  size            Int
  userId          String
  thumbnailPath   String?
  createdAt       DateTime @default(now())

  @@index([taskId])
  @@index([userId])
}

```yaml

**Cleanup middleware:**

```typescript

// src/lib/file-cleanup.ts
import { prisma } from '@/lib/prisma'
import fs from 'fs/promises'
import path from 'path'

// Call this BEFORE deleting task
export async function cleanupTaskFiles(taskId: string) {
  const files = await prisma.fileAttachment.findMany({

```
where: { taskId },

```
  })

  for (const file of files) {

```
try {
  // Delete main file
  const filePath = path.join(
    process.cwd(),
    'uploads',
    file.userId,
    taskId,
    file.storedFilename
  )
  await fs.unlink(filePath).catch(() => {}) // Ignore if doesn't exist

  // Delete thumbnail if exists
  if (file.thumbnailPath) {
    await fs.unlink(file.thumbnailPath).catch(() => {})
  }
} catch (error) {
  console.error('File cleanup failed:', file.id, error)
}

```
  }

  // Prisma cascade will delete DB records automatically
}

```

### Anti-Patterns to Avoid

- **❌ Trusting client-provided MIME types:** Always validate with file-type
  (reads magic numbers)
- **❌ Storing files in public/ directory:** Files become publicly accessible
  without auth
- **❌ Using file extensions for validation:** Extensions can be spoofed
- **❌ Direct filesystem paths in URLs:** Exposes server structure, bypasses auth
- **❌ Not cleaning up temporary files:** Leads to disk space issues
- **❌ Synchronous file operations in Server Actions:** Blocks Node.js event loop
- **❌ Missing AbortController for upload cancellation:** Can't stop in-progress
  uploads
- **❌ Server Actions for large files (> 5MB):** Hits body size limit, no progress
  tracking

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
| --------- | ------------- | ------------- | ----- |
  | Chunked upl... | Custom chun... | TUS protoco... | Handles chu... |  
| MIME type d... | RegEx on fi... | file-type (... | Reads magic... |
  | Image thumb... | Canvas API ... | Sharp | 30x faster,... |  
| Drag & drop UI | Native HTML... | react-dropzone | Accessibili... |
  | File path t... | String mani... | path.join()... | Prevents ..... |  
  | Virus scanning | Custom sign... | ClamAV (cla... | 8M+ malware... |  
  | Upload prog... | Manual perc... | XMLHttpRequ... | Handles net... |  
| Concurrent ... | Custom queue | p-limit (npm) | Handles bac... |

**Key insight:** File upload security is complex—path traversal, malware, MIME
spoofing, zip bombs, executable disguised as images. Use battle-tested
libraries, not custom validation logic.

## Common Pitfalls

### Pitfall 1: Server Actions Body Size Limit on Vercel

**What goes wrong:** Files > 1MB (default) or > 5MB (configured) fail with 413
error on Vercel, even though they work locally

**Why it happens:** Next.js Server Actions have configurable body size limits.
Vercel enforces stricter limits than local dev. The default is 1MB, configurable
to ~5MB, but not more.

**How to avoid:**

- Configure `experimental.serverActions.bodySizeLimit` in next.config.ts
- For files > 5MB, use dedicated API routes with TUS protocol instead of Server
  Actions
- Test with production-sized files in development

**Warning signs:**

- Upload works in dev but fails on Vercel
- 413 Payload Too Large errors
- Uploads silently fail with no error

### Pitfall 2: MIME Type Spoofing

**What goes wrong:** User uploads malicious.exe renamed to photo.jpg, server
accepts it based on extension or client-provided Content-Type, malware reaches
server

**Why it happens:** File extensions and HTTP Content-Type headers are
client-controlled and trivially spoofed. Validating only these checks nothing.

**How to avoid:**

- Use file-type library to read file magic numbers (binary signature)
- Validate MIME type AFTER reading file content, not before
- Whitelist allowed types, never blacklist dangerous types
- Reject files if magic number doesn't match extension

**Warning signs:**

- Using `file.type` from FormData for validation
- Checking file extension with RegEx
- Not reading file buffer before validation

**Code example:**

```typescript

// ❌ WRONG: Trusts client
const file = formData.get('file') as File
if (!file.type.startsWith('image/')) {
  throw new Error('Only images allowed')
}

// ✅ CORRECT: Reads magic number
const buffer = Buffer.from(await file.arrayBuffer())
const type = await fileTypeFromBuffer(buffer)
if (!type || !type.mime.startsWith('image/')) {
  throw new Error('Invalid image file')
}

```markdown

### Pitfall 3: Path Traversal Attacks

**What goes wrong:** User uploads file named `../../../etc/passwd`, server
writes to attacker-controlled location, overwrites critical files or reads
sensitive data

**Why it happens:** Filenames are user input and can contain directory traversal
sequences. Direct concatenation creates vulnerable paths.

**How to avoid:**

- NEVER use user-provided filenames directly in filesystem paths
- Generate random UUIDs for stored filenames
- Use path.join() and validate no '..' segments exist
- Store files in isolated upload directory outside webroot

**Warning signs:**

- Concatenating strings to build file paths
- Using `file.name` directly in `fs.writeFile`
- Not sanitizing filenames

**Code example:**

```typescript

// ❌ WRONG: Vulnerable to traversal
const userFilename = file.name // Could be "../../../evil"
await fs.writeFile(`./uploads/${userFilename}`, buffer)

// ✅ CORRECT: UUID + validation
const safeFilename = `${crypto.randomUUID()}.${type.ext}`
const uploadDir = path.join(process.cwd(), 'uploads', userId, taskId)
await fs.mkdir(uploadDir, { recursive: true })
await fs.writeFile(path.join(uploadDir, safeFilename), buffer)

```

### Pitfall 4: Missing File Cleanup on Task Deletion

**What goes wrong:** Tasks deleted but files remain on disk, wasting storage.
Orphaned files grow unbounded.

**Why it happens:** Prisma cascade delete removes DB records but doesn't trigger
filesystem cleanup. Files must be manually deleted.

**How to avoid:**

- Create cleanup middleware called BEFORE task deletion
- Use Prisma's onDelete: Cascade for DB records
- Implement background cleanup job for orphaned files
- Delete both main files and thumbnails

**Warning signs:**

- Uploads directory growing indefinitely
- Deleting tasks doesn't reduce disk usage
- No cleanup logic in delete handlers

### Pitfall 5: Blocking Event Loop with Synchronous File Ops

**What goes wrong:** Server becomes unresponsive during file uploads, other
requests time out, poor concurrency

**Why it happens:** Using `fs.readFileSync` or `fs.writeFileSync` blocks Node.js
event loop. Single-threaded server freezes.

**How to avoid:**

- Always use `fs.promises` (async/await)
- Never use synchronous fs methods in request handlers
- Use streams for large files instead of loading entire buffer

**Warning signs:**

- High response times during uploads
- Other endpoints slow down during file operations
- CPU spikes to 100% with single upload

### Pitfall 6: No Upload Cancellation

**What goes wrong:** Users can't stop in-progress uploads, wasted bandwidth,
poor UX when user realizes they selected wrong file

**Why it happens:** Not implementing AbortController pattern, no way to signal
upload should stop

**How to avoid:**

- Use AbortController with fetch() or TUS client
- Store upload instances in state for cancellation
- Provide cancel button with progress bar
- Clean up partial uploads on cancel

**Warning signs:**

- No cancel button on upload progress UI
- Uploads continue after user navigates away
- No way to stop multi-file batch upload

### Pitfall 7: Storing Files in Public Directory

**What goes wrong:** All uploaded files become publicly accessible without
authentication, anyone can access any file by guessing URLs

**Why it happens:** Misunderstanding Next.js public/ directory behavior—anything
there is served directly by web server

**How to avoid:**

- Store uploads outside public/ directory
- Serve files through authenticated API routes
- Check task ownership before serving files
- Use non-guessable UUIDs for filenames

**Warning signs:**

- Files stored in public/uploads/
- Direct filesystem URLs in image src attributes
- No authentication checks on file serving

## Code Examples

Verified patterns from official sources:

### Complete File Upload Flow (Server Action + Validation + Storage)

```typescript

// Source: Strapi Next.js 15 Tutorial + file-type docs
// https://strapi.io/blog/epic-next-js-15-tutorial-part-5-file-upload-using-server-actions
// https://www.npmjs.com/package/file-type

'use server'

import { auth } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { fileTypeFromBuffer } from 'file-type'
import fs from 'fs/promises'
import path from 'path'
import { generateThumbnail } from '@/lib/thumbnail-generator'
import { revalidatePath } from 'next/cache'

const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB (Server Action limit)
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'application/pdf']

export async function uploadFile(formData: FormData) {
  // 1. Authenticate
  const session = await auth()
  if (!session?.user?.id) {

```
return { error: 'Unauthorized' }

```
  }

  // 2. Extract form data
  const file = formData.get('file') as File
  const taskId = formData.get('taskId') as string

  if (!file || !taskId) {

```
return { error: 'Missing file or taskId' }

```
  }

  // 3. Validate size
  if (file.size > MAX_FILE_SIZE) {

```
return { error: `File too large. Max size: ${MAX_FILE_SIZE / 1024 / 1024}MB` }

```
  }

  // 4. Read file content
  const buffer = Buffer.from(await file.arrayBuffer())

  // 5. Validate MIME type by content (security-critical)
  const fileType = await fileTypeFromBuffer(buffer)

  if (!fileType || !ALLOWED_TYPES.includes(fileType.mime)) {

```
return {
  error: `Invalid file type. Detected: ${fileType?.mime || 'unknown'}`,
}

```
  }

  // 6. Verify task ownership
  const task = await prisma.task.findUnique({

```
where: { id: taskId },
select: { userId: true },

```
  })

  if (!task || task.userId !== session.user.id) {

```
return { error: 'Task not found or access denied' }

```
  }

  // 7. Create upload directory
  const uploadDir = path.join(

```
process.cwd(),
'uploads',
session.user.id,
taskId

```
  )
  await fs.mkdir(uploadDir, { recursive: true })

  // 8. Generate unique filename
  const storedFilename = `${crypto.randomUUID()}.${fileType.ext}`
  const filePath = path.join(uploadDir, storedFilename)

  // 9. Write file to disk
  await fs.writeFile(filePath, buffer)

  // 10. Generate thumbnail for images
  let thumbnailPath: string | null = null
  if (fileType.mime.startsWith('image/')) {

```
thumbnailPath = await generateThumbnail(
  filePath,
  session.user.id,
  taskId,
  storedFilename.replace(path.extname(storedFilename), '')
)

```
  }

  // 11. Save metadata to database
  const attachment = await prisma.fileAttachment.create({

```
data: {
  taskId,
  userId: session.user.id,
  filename: file.name, // Original name for display
  storedFilename,      // UUID-based name on disk
  mimeType: fileType.mime,
  size: file.size,
  thumbnailPath,
},

```
  })

  // 12. Revalidate cache
  revalidatePath(`/tasks/${taskId}`)

  return {

```
success: true,
id: attachment.id,
filename: file.name,
size: file.size,

```
  }
}

```markdown

### Drag & Drop Component with Progress

```typescript

// Source: react-dropzone docs + TUS tutorial
// https://react-dropzone.js.org/
// https://tus.io/

'use client'

import { useDropzone } from 'react-dropzone'
import * as tus from 'tus-js-client'
import { useState } from 'react'

interface UploadState {
  filename: string
  progress: number
  status: 'uploading' | 'complete' | 'error'
  error?: string
}

export function FileUploader({ taskId }: { taskId: string }) {
  const [uploads, setUploads] = useState<Map<string, tus.Upload>>(new Map())
  const [uploadStates, setUploadStates] = useState<Map<string, UploadState>>(new Map())

  const onDrop = async (acceptedFiles: File[]) => {

```
for (const file of acceptedFiles) {
  // Client-side size validation
  if (file.size > 25 * 1024 * 1024) {
    setUploadStates((prev) => {
      const next = new Map(prev)
      next.set(file.name, {
        filename: file.name,
        progress: 0,
        status: 'error',
        error: 'File exceeds 25MB limit',
      })
      return next
    })
    continue
  }

  // Initialize state
  setUploadStates((prev) => {
    const next = new Map(prev)
    next.set(file.name, {
      filename: file.name,
      progress: 0,
      status: 'uploading',
    })
    return next
  })

  // Create TUS upload
  const upload = new tus.Upload(file, {
    endpoint: '/api/files/upload',
    retryDelays: [0, 3000, 5000, 10000, 20000], // Retry strategy
    chunkSize: 5 * 1024 * 1024, // 5MB chunks
    metadata: {
      filename: file.name,
      filetype: file.type,
      taskId,
    },
    onProgress: (bytesUploaded, bytesTotal) => {
      const progress = (bytesUploaded / bytesTotal) * 100
      setUploadStates((prev) => {
        const next = new Map(prev)
        const state = next.get(file.name)
        if (state) {
          next.set(file.name, { ...state, progress })
        }
        return next
      })
    },
    onSuccess: () => {
      setUploadStates((prev) => {
        const next = new Map(prev)
        const state = next.get(file.name)
        if (state) {
          next.set(file.name, { ...state, status: 'complete', progress: 100 })
        }
        return next
      })
      uploads.delete(file.name)
    },
    onError: (error) => {
      setUploadStates((prev) => {
        const next = new Map(prev)
        const state = next.get(file.name)
        if (state) {
          next.set(file.name, {
            ...state,
            status: 'error',
            error: error.message,
          })
        }
        return next
      })
    },
  })

  uploads.set(file.name, upload)
  setUploads(new Map(uploads))

  // Start upload
  upload.start()
}

```
  }

  const cancelUpload = (filename: string) => {

```
const upload = uploads.get(filename)
if (upload) {
  upload.abort()
  uploads.delete(filename)
  setUploads(new Map(uploads))
  setUploadStates((prev) => {
    const next = new Map(prev)
    next.delete(filename)
    return next
  })
}

```
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({

```
onDrop,
maxSize: 25 * 1024 * 1024,
multiple: true,

```
  })

  return (

```
<div className="space-y-4">
  <div
    {...getRootProps()}
    className={`
      border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
      transition-colors
      ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
    `}
  >
    <input {...getInputProps()} />
    {isDragActive ? (
      <p className="text-blue-600">Drop files here...</p>
    ) : (
      <div>
        <p className="text-gray-600">Drag & drop files here, or click to select</p>
        <p className="text-sm text-gray-400 mt-2">Max 25MB per file</p>
      </div>
    )}
  </div>

  {/* Upload progress list */}
  {Array.from(uploadStates.values()).map((state) => (
    <div key={state.filename} className="border rounded-lg p-4">
      <div className="flex justify-between items-center mb-2">
        <span className="font-medium truncate">{state.filename}</span>
        {state.status === 'uploading' && (
          <button
            onClick={() => cancelUpload(state.filename)}
            className="text-red-600 hover:text-red-700 text-sm"
          >
            Cancel
          </button>
        )}
      </div>

      {state.status === 'uploading' && (
        <div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${state.progress}%` }}
            />
          </div>
          <p className="text-sm text-gray-500 mt-1">
            {state.progress.toFixed(1)}%
          </p>
        </div>
      )}

      {state.status === 'complete' && (
        <p className="text-green-600 text-sm">✓ Upload complete</p>
      )}

      {state.status === 'error' && (
        <p className="text-red-600 text-sm">✗ {state.error}</p>
      )}
    </div>
  ))}
</div>

```
  )
}

```

### File Deletion with Cleanup

```typescript

// Source: Prisma docs + Node.js fs best practices
// https://www.prisma.io/docs/orm/prisma-schema/data-model/relations/referential-actions

'use server'

import { auth } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import fs from 'fs/promises'
import path from 'path'
import { revalidatePath } from 'next/cache'

export async function deleteFile(fileId: string) {
  const session = await auth()
  if (!session?.user?.id) {

```
return { error: 'Unauthorized' }

```
  }

  // Get file metadata
  const file = await prisma.fileAttachment.findUnique({

```
where: { id: fileId },
include: { task: true },

```
  })

  if (!file) {

```
return { error: 'File not found' }

```
  }

  // Verify ownership
  if (file.task.userId !== session.user.id) {

```
return { error: 'Access denied' }

```
  }

  // Delete from filesystem (both main file and thumbnail)
  try {

```
const filePath = path.join(
  process.cwd(),
  'uploads',
  file.userId,
  file.taskId,
  file.storedFilename
)
await fs.unlink(filePath).catch(() => {}) // Ignore if doesn't exist

if (file.thumbnailPath) {
  await fs.unlink(file.thumbnailPath).catch(() => {})
}

```
  } catch (error) {

```
console.error('Filesystem cleanup failed:', error)
// Continue to delete DB record even if file cleanup fails

```
  }

  // Delete from database
  await prisma.fileAttachment.delete({

```
where: { id: fileId },

```
  })

  revalidatePath(`/tasks/${file.taskId}`)

  return { success: true }
}

```markdown

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
| -------------- | ------------------ | -------------- | -------- |
  | Multer midd... | Server Acti... | Next.js 13 ... | Simpler cod... |  
  | jimp for im... | Sharp with ... | Sharp 0.30+... | 30x faster,... |  
  | Custom chun... | TUS protocol | TUS 1.0 (2020) | Standard pr... |  
| Extension-b... | Magic numbe... | Security be... | Prevents MI... |
| react-beaut... | react-dropzone | N/A (differ... | react-dropz... |
  | Blacklist d... | Whitelist a... | OWASP guide... | More secure... |  
| Client-side... | Server-side... | TUS protocol | More reliab... |

**Deprecated/outdated:**

- **Multer for Server Actions**: Server Actions handle FormData natively, no
  middleware needed (still valid for API routes)
- **Formidable**: Older parsing library, replaced by native FormData support in
  Next.js App Router
- **react-beautiful-dnd**: No longer maintained (archived by Atlassian), fork is
  hello-pangea/dnd

## Open Questions

Things that couldn't be fully resolved:

1. **Virus scanning approach**
   - What we know: ClamAV is standard, pompelmi offers in-process scanning, cloud

```
 APIs exist (Verisys)

```
   - What's unclear: Best practice for this scale (single user task tracker vs

```
 multi-tenant SaaS)

```
   - Recommendation: Start without virus scanning (out of scope for v1), add

```
 pompelmi if needed in v2. Context specifies "security scanning" but
 single-user task tracker has lower risk than public file hosting.

```
2. **Chunked upload strategy**
   - What we know: Context requires 25MB files + resume capability, Server

```
 Actions max out ~5MB

```
   - What's unclear: Whether to implement TUS protocol (complex but standard) or

```
 custom chunking (simpler but more code)

```
   - Recommendation: Use TUS protocol via tus-js-client + @tus/server. It's

```
 battle-tested and handles edge cases we'd miss in custom implementation.

```
3. **Thumbnail generation timing**
   - What we know: Sharp is fast but synchronous operations block event loop
   - What's unclear: Generate thumbnails synchronously on upload or queue for

```
 background processing

```
   - Recommendation: Synchronous for phase 5 (simpler), move to background queue

```
 if performance issues arise. Sharp is fast enough (<500ms for most images).

```
4. **Storage scalability**
   - What we know: Local filesystem chosen in CONTEXT.md
   - What's unclear: File size limits over time, backup strategy, what happens at

```
 10GB+ of files

```
   - Recommendation: Local filesystem is fine for v1. If storage becomes issue,

```
 migrate to S3-compatible storage in v2 (Prisma schema already tracks paths,
 easy to migrate).

```
## Sources

### Primary (HIGH confidence)

- [Next.js 15 Tutorial Part 5: File Upload with Server
  Actions](https://strapi.io/blog/epic-next-js-15-tutorial-part-5-file-upload-using-server-actions)
  - Official tutorial on Server Actions file upload
- [file-type npm package](https://www.npmjs.com/package/file-type) -
  Content-based MIME detection
- [react-dropzone GitHub](https://github.com/react-dropzone/react-dropzone) -
  Official documentation
- [Sharp documentation](https://sharp.pixelplumbing.com/) - Official Sharp docs
- [TUS Protocol Specification](https://tus.io/protocols/resumable-upload) -
  Official resumable upload protocol
- [Prisma Referential
  Actions](https://www.prisma.io/docs/orm/prisma-schema/data-model/relations/referential-actions)
  - Cascade delete documentation

### Secondary (MEDIUM confidence)

- [Top 5 Drag-and-Drop Libraries for React in
  2026](https://puckeditor.com/blog/top-5-drag-and-drop-libraries-for-react) -
  Library comparison
- [pompelmi - Fast File Upload Security](https://pompelmi.github.io/pompelmi/) -
  In-process malware scanning
- [How To Get the MIME Type of a File in
  Node.js](https://dev.to/victrexx2002/how-to-get-the-mime-type-of-a-file-in-nodejs-p6c)
  - MIME detection methods
- [File Upload Protection Best Practices -
  OPSWAT](https://www.opswat.com/blog/file-upload-protection-best-practices) -
  Security guidelines

### Tertiary (LOW confidence)

- [GitHub:
  nextjs-chunk-upload-action](https://github.com/a179346/nextjs-chunk-upload-action)
  - Community chunking implementation
- [How to Upload Multiple File With Feature Cancellation &
  Retry](https://dev.to/devinekadeni/how-to-upload-multiple-file-with-feature-cancellation-retry-using-reactjs-18cd)
  - Cancellation patterns

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - All libraries verified with Context7/official docs,
  widely used in production
- Architecture: HIGH - Patterns from official Next.js tutorials, TUS protocol
  spec, Prisma docs
- Pitfalls: HIGH - OWASP security guidelines, real CVEs, documented in official
  sources

**Research date:** 2026-01-25
**Valid until:** 2026-02-25 (30 days - Next.js ecosystem stable, patterns
established)
