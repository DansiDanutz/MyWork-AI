"use client"

import axios from "axios"
import { uploadsApi } from "./api"

export type UploadKind = "preview_image" | "package"

export interface UploadResult {
  fileKey: string
  publicUrl?: string
}

export async function uploadFileWithPresign(
  file: File,
  kind: UploadKind,
  onProgress?: (progress: number) => void
): Promise<UploadResult> {
  const contentType = file.type || "application/octet-stream"

  const presign = await uploadsApi.createPresignedUrl({
    kind,
    filename: file.name,
    content_type: contentType,
    size_bytes: file.size,
  })

  const { upload_url, file_key, public_url } = presign.data

  await axios.put(upload_url, file, {
    headers: {
      "Content-Type": contentType,
    },
    onUploadProgress: (event) => {
      if (!onProgress || !event.total) return
      const percent = Math.round((event.loaded / event.total) * 100)
      onProgress(Math.min(100, Math.max(0, percent)))
    },
  })

  return {
    fileKey: file_key,
    publicUrl: public_url,
  }
}
