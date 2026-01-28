import fs from "fs/promises";
import path from "path";

// Base upload directory (relative to project root)
const UPLOAD_BASE = path.join(process.cwd(), "uploads");
const TEMP_DIR = path.join(UPLOAD_BASE, "temp");

/**
 * Get the upload directory for a specific user and task.
 * Creates the directory if it doesn't exist.
 */
export async function getUploadDir(
  userId: string,
  taskId: string,
): Promise<string> {
  const dir = path.join(UPLOAD_BASE, userId, taskId);
  await fs.mkdir(dir, { recursive: true });
  return dir;
}

/**
 * Get the thumbnail directory for a specific user and task.
 * Creates the directory if it doesn't exist.
 */
export async function getThumbnailDir(
  userId: string,
  taskId: string,
): Promise<string> {
  const dir = path.join(UPLOAD_BASE, userId, taskId, "thumbs");
  await fs.mkdir(dir, { recursive: true });
  return dir;
}

/**
 * Get the temp directory for TUS uploads.
 * Creates if doesn't exist.
 */
export async function getTempDir(): Promise<string> {
  await fs.mkdir(TEMP_DIR, { recursive: true });
  return TEMP_DIR;
}

/**
 * Ensure base upload directories exist.
 * Call on server startup.
 */
export async function ensureUploadDir(): Promise<void> {
  await fs.mkdir(UPLOAD_BASE, { recursive: true });
  await fs.mkdir(TEMP_DIR, { recursive: true });
}

/**
 * Save a file buffer to the user's upload directory.
 * Returns the stored filename (UUID-based).
 */
export async function saveFile(
  buffer: Buffer,
  userId: string,
  taskId: string,
  extension: string,
): Promise<{ storedFilename: string; filePath: string }> {
  const uploadDir = await getUploadDir(userId, taskId);
  const storedFilename = `${crypto.randomUUID()}.${extension}`;
  const filePath = path.join(uploadDir, storedFilename);

  await fs.writeFile(filePath, buffer);

  return { storedFilename, filePath };
}

/**
 * Move a file from temp to final location (for TUS uploads).
 */
export async function moveFromTemp(
  tempFilename: string,
  userId: string,
  taskId: string,
  extension: string,
): Promise<{ storedFilename: string; filePath: string }> {
  const tempPath = path.join(TEMP_DIR, tempFilename);
  const uploadDir = await getUploadDir(userId, taskId);
  const storedFilename = `${crypto.randomUUID()}.${extension}`;
  const filePath = path.join(uploadDir, storedFilename);

  await fs.rename(tempPath, filePath);

  // Clean up TUS metadata files
  try {
    await fs.unlink(`${tempPath}.json`).catch(() => {});
  } catch {
    // Ignore cleanup errors
  }

  return { storedFilename, filePath };
}

/**
 * Delete a file and its thumbnail if exists.
 */
export async function deleteFile(
  userId: string,
  taskId: string,
  storedFilename: string,
  thumbnailPath?: string | null,
): Promise<void> {
  const filePath = path.join(UPLOAD_BASE, userId, taskId, storedFilename);

  try {
    await fs.unlink(filePath);
  } catch (error) {
    // File might already be deleted, log but don't fail
    console.warn("Failed to delete file:", filePath, error);
  }

  // Delete thumbnail if exists
  if (thumbnailPath) {
    try {
      const thumbPath = thumbnailPath.startsWith("/")
        ? thumbnailPath
        : path.join(UPLOAD_BASE, thumbnailPath);
      await fs.unlink(thumbPath);
    } catch {
      // Thumbnail might not exist, ignore
    }
  }
}

/**
 * Delete all files for a task (cleanup when task is deleted).
 * Prisma cascade handles DB records, this handles filesystem.
 */
export async function deleteTaskFiles(
  userId: string,
  taskId: string,
): Promise<void> {
  const taskDir = path.join(UPLOAD_BASE, userId, taskId);

  try {
    await fs.rm(taskDir, { recursive: true, force: true });
  } catch (error) {
    console.warn("Failed to delete task directory:", taskDir, error);
  }
}

/**
 * Read a file from storage.
 * Returns null if file doesn't exist.
 */
export async function readFile(
  userId: string,
  taskId: string,
  storedFilename: string,
): Promise<Buffer | null> {
  const filePath = path.join(UPLOAD_BASE, userId, taskId, storedFilename);

  try {
    return await fs.readFile(filePath);
  } catch {
    return null;
  }
}

/**
 * Get the full file path for a stored file.
 */
export function getFilePath(
  userId: string,
  taskId: string,
  storedFilename: string,
): string {
  return path.join(UPLOAD_BASE, userId, taskId, storedFilename);
}

/**
 * Check if a file exists.
 */
export async function fileExists(
  userId: string,
  taskId: string,
  storedFilename: string,
): Promise<boolean> {
  const filePath = getFilePath(userId, taskId, storedFilename);

  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

/**
 * Clean up old temp files (older than 24 hours).
 * Run periodically to prevent temp directory bloat.
 */
export async function cleanupTempFiles(): Promise<number> {
  const maxAge = 24 * 60 * 60 * 1000; // 24 hours in ms
  const now = Date.now();
  let deleted = 0;

  try {
    const files = await fs.readdir(TEMP_DIR);

    for (const file of files) {
      if (file === ".gitkeep") continue;

      const filePath = path.join(TEMP_DIR, file);
      const stats = await fs.stat(filePath);

      if (now - stats.mtimeMs > maxAge) {
        await fs.unlink(filePath).catch(() => {});
        deleted++;
      }
    }
  } catch (error) {
    console.warn("Temp cleanup error:", error);
  }

  return deleted;
}
