"use client";

import { useActionState, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { createTask } from "@/app/actions/tasks";
import { addTagToTask } from "@/app/actions/tags";
import { TagInput } from "./TagInput";
import { Tag } from "@prisma/client";
import Link from "next/link";

type TaskFormWithTagsProps = {
  availableTags: Tag[];
};

type FormState = {
  success: boolean;
  error?: string;
  data?: { taskId: string };
} | null;

export function TaskFormWithTags({ availableTags }: TaskFormWithTagsProps) {
  const router = useRouter();
  const [selectedTags, setSelectedTags] = useState<Tag[]>([]);
  const [localTags, setLocalTags] = useState<Tag[]>(availableTags);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [state, formAction, isPending] = useActionState<FormState, FormData>(
    async (_prevState, formData) => {
      setIsSubmitting(true);
      try {
        const result = await createTask(formData);

        // If task created successfully and we have tags, add them
        if (result.success && result.data?.taskId && selectedTags.length > 0) {
          // Add each tag to the task
          for (const tag of selectedTags) {
            await addTagToTask(result.data.taskId, tag.name);
          }
        }

        if (result.success) {
          router.push("/tasks");
        }

        return result;
      } finally {
        setIsSubmitting(false);
      }
    },
    null,
  );

  const handleAddTag = useCallback(
    async (tagName: string) => {
      // Check if tag already exists in local list
      const existingTag = localTags.find(
        (t) => t.name.toLowerCase() === tagName.toLowerCase(),
      );

      if (existingTag) {
        // Check if already selected
        if (!selectedTags.some((t) => t.id === existingTag.id)) {
          setSelectedTags((prev) => [...prev, existingTag]);
        }
      } else {
        // Create a temporary tag for display (will be created on submit)
        const tempTag: Tag = {
          id: `temp-${Date.now()}`,
          name: tagName,
          color: TAG_COLORS[Math.floor(Math.random() * TAG_COLORS.length)],
          userId: "",
          createdAt: new Date(),
        };
        setSelectedTags((prev) => [...prev, tempTag]);
        setLocalTags((prev) => [...prev, tempTag]);
      }
    },
    [localTags, selectedTags],
  );

  const handleRemoveTag = useCallback((tagId: string) => {
    setSelectedTags((prev) => prev.filter((t) => t.id !== tagId));
  }, []);

  return (
    <form action={formAction} className="space-y-6 max-w-2xl">
      {/* Title field */}
      <div>
        <label
          htmlFor="title"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Title <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="title"
          name="title"
          required
          maxLength={200}
          disabled={isPending || isSubmitting}
          className={`
            w-full px-3 py-2
            border rounded-md
            text-gray-900 dark:text-gray-100
            bg-white dark:bg-gray-800
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
            disabled:opacity-50 disabled:cursor-not-allowed
            ${state && !state.success ? "border-red-500" : "border-gray-300 dark:border-gray-600"}
          `}
          placeholder="e.g., Complete project proposal"
        />
        {state && !state.success && (
          <p className="mt-2 text-sm text-red-600 dark:text-red-400">
            {state.error}
          </p>
        )}
      </div>

      {/* Description field */}
      <div>
        <label
          htmlFor="description"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Description <span className="text-gray-500 text-xs">(optional)</span>
        </label>
        <textarea
          id="description"
          name="description"
          rows={4}
          maxLength={2000}
          disabled={isPending || isSubmitting}
          className="
            w-full px-3 py-2
            border border-gray-300 dark:border-gray-600 rounded-md
            text-gray-900 dark:text-gray-100
            bg-white dark:bg-gray-800
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
            disabled:opacity-50 disabled:cursor-not-allowed
            resize-vertical
          "
          placeholder="Add any additional details about this task..."
        />
      </div>

      {/* Tags field */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Tags <span className="text-gray-500 text-xs">(optional)</span>
        </label>
        <TagInput
          selectedTags={selectedTags}
          availableTags={localTags}
          onAddTag={handleAddTag}
          onRemoveTag={handleRemoveTag}
          disabled={isPending || isSubmitting}
        />
      </div>

      {/* Button row */}
      <div className="flex items-center gap-3">
        {/* Submit button */}
        <button
          type="submit"
          disabled={isPending || isSubmitting}
          className="
            px-4 py-2
            bg-blue-600 text-white
            rounded-md font-medium
            hover:bg-blue-700
            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-colors
          "
        >
          {isPending || isSubmitting ? "Creating..." : "Create Task"}
        </button>

        {/* Cancel button */}
        <Link
          href="/tasks"
          className="
            px-4 py-2
            border border-gray-300 dark:border-gray-600
            text-gray-700 dark:text-gray-300
            rounded-md font-medium
            hover:bg-gray-50 dark:hover:bg-gray-800
            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500
            transition-colors
          "
        >
          Cancel
        </Link>
      </div>

      {/* Success message (shown after successful creation, before redirect) */}
      {state && state.success && (
        <div className="rounded-md bg-green-50 dark:bg-green-900/20 p-4">
          <p className="text-sm text-green-800 dark:text-green-200">
            Task created successfully! Redirecting...
          </p>
        </div>
      )}
    </form>
  );
}

// Preset colors for new tags
const TAG_COLORS = [
  "#3b82f6", // blue
  "#10b981", // green
  "#f59e0b", // amber
  "#ef4444", // red
  "#8b5cf6", // purple
  "#ec4899", // pink
  "#06b6d4", // cyan
  "#f97316", // orange
];
