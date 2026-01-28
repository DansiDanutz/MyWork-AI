"use client";

import dynamic from "next/dynamic";

// Lazy load FileDropzone with loading fallback
// ssr: false because it uses browser file APIs
const FileDropzone = dynamic(
  () => import("./FileDropzone").then((mod) => mod.FileDropzone),
  {
    loading: () => (
      <div className="border-2 border-dashed border-zinc-600 rounded-lg p-8">
        <div className="animate-pulse text-center">
          <div className="h-10 w-10 bg-gray-200 dark:bg-gray-700 rounded-full mx-auto mb-4" />
          <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded mx-auto mb-2" />
          <div className="h-3 w-48 bg-gray-200 dark:bg-gray-700 rounded mx-auto" />
        </div>
      </div>
    ),
    ssr: false,
  },
);

// Re-export with same props interface
export { FileDropzone as LazyFileDropzone };
export type { FileDropzoneProps } from "./FileDropzone";
