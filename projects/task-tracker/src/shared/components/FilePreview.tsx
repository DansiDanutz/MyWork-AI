"use client";

import { useEffect, useCallback } from "react";
import { formatFileSize } from "@/shared/lib/file-validation";

interface FilePreviewProps {
  fileId: string;
  filename: string;
  mimeType: string;
  size: number;
  onClose: () => void;
  onDownload: () => void;
  onDelete?: () => void;
}

export function FilePreview({
  fileId,
  filename,
  mimeType,
  size,
  onClose,
  onDownload,
  onDelete,
}: FilePreviewProps) {
  const isImage = mimeType.startsWith("image/");
  const isPdf = mimeType === "application/pdf";

  // Handle escape key
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    },
    [onClose],
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "unset";
    };
  }, []);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80"
      onClick={onClose}
    >
      <div
        className="bg-zinc-900 rounded-lg shadow-xl max-w-4xl max-h-[90vh] w-full mx-4 flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-700">
          <div className="min-w-0 flex-1">
            <h3 className="text-lg font-medium text-zinc-100 truncate">
              {filename}
            </h3>
            <p className="text-sm text-zinc-400">{formatFileSize(size)}</p>
          </div>

          <div className="flex items-center gap-2 ml-4">
            <button
              onClick={onDownload}
              className="px-3 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              Download
            </button>
            {onDelete && (
              <button
                onClick={onDelete}
                className="px-3 py-1.5 text-sm bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                Delete
              </button>
            )}
            <button
              onClick={onClose}
              className="p-1.5 text-zinc-400 hover:text-zinc-200 transition-colors"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4 flex items-center justify-center min-h-[300px]">
          {isImage ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={`/api/files/download/${fileId}`}
              alt={filename}
              className="max-w-full max-h-full object-contain"
            />
          ) : isPdf ? (
            <iframe
              src={`/api/files/download/${fileId}`}
              className="w-full h-full min-h-[500px]"
              title={filename}
            />
          ) : (
            <div className="text-center">
              <svg
                className="w-20 h-20 mx-auto text-zinc-500 mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1}
                  d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                />
              </svg>
              <p className="text-zinc-400 mb-4">
                Preview not available for this file type
              </p>
              <button
                onClick={onDownload}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                Download to view
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
