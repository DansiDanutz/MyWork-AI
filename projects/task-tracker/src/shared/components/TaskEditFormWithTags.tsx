"use client";

import { useActionState, useState, useCallback, useTransition } from "react";
import { useRouter } from "next/navigation";
import { updateTask, deleteTask } from "@/app/actions/tasks";
import { updateTaskTags, addTagToTask } from "@/app/actions/tags";
import { TagInput } from "./TagInput";
import { LazyFileDropzone } from "./LazyFileDropzone";
import { LazyFileList } from "./LazyFileList";
import { Tag, Task, FileAttachment } from "@prisma/client";
import Link from "next/link";

type TaskWithTags = Task & {
  tags: Tag[];
  attachments: FileAttachment[];
};

type TaskEditFormWithTagsProps = {
  task: TaskWithTags;
  availableTags: Tag[];
};

type FormState = {
  success: boolean;
  error?: string;
} | null;

export function TaskEditFormWithTags({
  task,
  availableTags,
}: TaskEditFormWithTagsProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [selectedTags, setSelectedTags] = useState<Tag[]>(task.tags);
  const [localTags, setLocalTags] = useState<Tag[]>(availableTags);
  const [formError, setFormError] = useState<string>();
  const [attachments, setAttachments] = useState<FileAttachment[]>(
    task.attachments,
  );

  const updateTaskWithId = async (
    prevState: FormState,
    formData: FormData,
  ): Promise<FormState> => {
    return updateTask(task.id, formData);
  };

  const [state, formAction, pending] = useActionState<FormState, FormData>(
    updateTaskWithId,
    null,
  );

  // Handle successful update - redirect to tasks list
  if (state?.success) {
    router.push("/tasks");
  }

  const handleAddTag = useCallback(
    async (tagName: string) => {
      // Check if tag already exists
      const existingTag = localTags.find(
        (t) => t.name.toLowerCase() === tagName.toLowerCase(),
      );

      if (existingTag && !selectedTags.some((t) => t.id === existingTag.id)) {
        // Add existing tag
        const newTags = [...selectedTags, existingTag];
        setSelectedTags(newTags);

        // Update on server
        const result = await addTagToTask(task.id, existingTag.name);
        if (!result.success) {
          // Rollback on error
          setSelectedTags(selectedTags);
          setFormError(result.error);
        }
      } else if (!existingTag) {
        // Create new tag via server action
        const result = await addTagToTask(task.id, tagName);
        if (result.success && result.data) {
          const newTag: Tag = {
            id: result.data.tagId,
            name: tagName,
            color: TAG_COLORS[Math.floor(Math.random() * TAG_COLORS.length)],
            userId: task.userId,
            createdAt: new Date(),
          };
          setSelectedTags((prev) => [...prev, newTag]);
          setLocalTags((prev) => [...prev, newTag]);
        } else if (!result.success) {
          setFormError(result.error);
        }
      }
    },
    [localTags, selectedTags, task.id, task.userId],
  );

  const handleRemoveTag = useCallback(
    async (tagId: string) => {
      const newTags = selectedTags.filter((t) => t.id !== tagId);
      setSelectedTags(newTags);

      // Update on server
      const result = await updateTaskTags(
        task.id,
        newTags.map((t) => t.id),
      );
      if (!result.success) {
        // Rollback on error
        setSelectedTags(selectedTags);
        setFormError(result.error);
      }
    },
    [selectedTags, task.id],
  );

  const handleFileUploadComplete = useCallback(
    (fileId: string, filename: string) => {
      // Add the new file to the attachments list
      const newAttachment: FileAttachment = {
        id: fileId,
        filename,
        storedFilename: "", // Will be filled by server
        taskId: task.id,
        userId: task.userId,
        mimeType: "", // Will be filled by server
        size: 0, // Will be filled by server
        thumbnailPath: null,
        createdAt: new Date(),
      };
      setAttachments((prev) => [...prev, newAttachment]);
    },
    [task.id, task.userId],
  );

  const handleFileDeleted = useCallback((fileId: string) => {
    // Remove the file from the attachments list
    setAttachments((prev) => prev.filter((file) => file.id !== fileId));
  }, []);

  const handleDelete = async () => {
    if (
      !confirm(
        "Are you sure you want to delete this task? This action cannot be undone.",
      )
    ) {
      return;
    }

    startTransition(async () => {
      const result = await deleteTask(task.id);
      if (result.success) {
        router.push("/tasks");
      } else {
        alert(`Failed to delete task: ${result.error}`);
      }
    });
  };

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
          defaultValue={task.title}
          disabled={pending || isPending}
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
          defaultValue={task.description || ""}
          disabled={pending || isPending}
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

      {/* Status field */}
      <div>
        <label
          htmlFor="status"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Status <span className="text-red-500">*</span>
        </label>
        <select
          id="status"
          name="status"
          defaultValue={task.status}
          disabled={pending || isPending}
          className="
            w-full px-3 py-2
            border border-gray-300 dark:border-gray-600 rounded-md
            text-gray-900 dark:text-gray-100
            bg-white dark:bg-gray-800
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
            disabled:opacity-50 disabled:cursor-not-allowed
          "
        >
          <option value="TODO">To Do</option>
          <option value="IN_PROGRESS">In Progress</option>
          <option value="DONE">Done</option>
        </select>
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
          disabled={pending || isPending}
        />
      </div>

      {/* File attachments */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          File Attachments{" "}
          <span className="text-gray-500 text-xs">(optional)</span>
        </label>

        {/* File upload dropzone */}
        <div className="mb-4">
          <LazyFileDropzone
            taskId={task.id}
            onUploadComplete={handleFileUploadComplete}
            disabled={pending || isPending}
            maxFiles={10}
          />
        </div>

        {/* Current attachments list */}
        {attachments.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Current Files ({attachments.length})
            </h4>
            <LazyFileList
              files={attachments}
              onFileDeleted={handleFileDeleted}
              editable={true}
              compact={false}
            />
          </div>
        )}
      </div>

      {/* Error message */}
      {(state?.error || formError) && (
        <p className="text-sm text-red-600 dark:text-red-400">
          {state?.error || formError}
        </p>
      )}

      {/* Button row */}
      <div className="flex items-center gap-3">
        {/* Submit button */}
        <button
          type="submit"
          disabled={pending || isPending}
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
          {pending ? "Saving..." : "Save Changes"}
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

        {/* Spacer to push delete button to the right */}
        <div className="flex-1" />

        {/* Delete button */}
        <button
          type="button"
          onClick={handleDelete}
          disabled={pending || isPending}
          className="
            px-4 py-2
            border border-red-300 dark:border-red-600
            text-red-600 dark:text-red-400
            rounded-md font-medium
            hover:bg-red-50 dark:hover:bg-red-900/20
            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-colors
          "
        >
          {isPending ? "Deleting..." : "Delete Task"}
        </button>
      </div>
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
