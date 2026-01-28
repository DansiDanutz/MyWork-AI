"use client";

import { useActionState, useTransition } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { updateTask, deleteTask } from "@/app/actions/tasks";

type Task = {
  id: string;
  title: string;
  description: string | null;
  status: "TODO" | "IN_PROGRESS" | "DONE";
};

type TaskEditFormProps = {
  task: Task;
};

type FormState = {
  success: boolean;
  error?: string;
} | null;

export function TaskEditForm({ task }: TaskEditFormProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  // Create a bound action that includes taskId
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

  // Handle delete
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
