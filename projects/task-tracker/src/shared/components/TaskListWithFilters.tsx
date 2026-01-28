"use client";

import { TaskSearchBar } from "./TaskSearchBar";
import { TaskFilters } from "./TaskFilters";
import { TaskList } from "./TaskList";
import { EmptyState } from "./EmptyState";
import { useQueryStates } from "nuqs";
import { taskSearchParams } from "@/app/(app)/tasks/search-params";
import type { Tag, Task } from "@prisma/client";

type TaskWithTags = Task & { tags: Tag[] };

type TaskListWithFiltersProps = {
  tasks: TaskWithTags[];
  tags: Tag[];
};

/**
 * TaskListWithFilters: Combined task list with search and filter UI
 *
 * Features:
 * - Search bar with debounced input
 * - Filter sidebar with status and tag options
 * - URL state persistence via nuqs
 * - Responsive layout (stacked on mobile, sidebar on desktop)
 * - Empty state when no results match filters
 * - Clear filters button
 *
 * This component combines TaskSearchBar, TaskFilters, and TaskList
 * into a cohesive interface for task discovery.
 *
 * URL Parameters:
 * - q: Search query string
 * - status: Array of status filters (TODO, IN_PROGRESS, DONE)
 * - tags: Array of tag IDs
 *
 * Example URL: /tasks?q=meeting&status=TODO,IN_PROGRESS&tags=work-id,urgent-id
 */
export function TaskListWithFilters({ tasks, tags }: TaskListWithFiltersProps) {
  const [filters] = useQueryStates(taskSearchParams);

  const hasActiveFilters =
    filters.q ||
    (filters.status && filters.status.length > 0) ||
    (filters.tags && filters.tags.length > 0);

  // Show different empty state when filters are active
  const isEmpty = tasks.length === 0;

  return (
    <div className="space-y-6">
      {/* Search bar */}
      <TaskSearchBar />

      {/* Two-column layout: filters sidebar + task list */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filter sidebar */}
        <aside className="lg:col-span-1">
          <TaskFilters tags={tags} />
        </aside>

        {/* Task list */}
        <main className="lg:col-span-3">
          {isEmpty ? (
            hasActiveFilters ? (
              // Empty state for filtered results
              <EmptyState
                title="No tasks found"
                description="Try adjusting your search query or filters to find what you're looking for."
                icon={
                  <svg
                    className="mx-auto h-24 w-24 text-gray-400 dark:text-gray-600 mb-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                }
              />
            ) : (
              // Empty state for no tasks at all
              <EmptyState
                title="No tasks yet!"
                description="Create your first task to get started organizing your work."
                action={{ label: "Create your first task", href: "/tasks/new" }}
              />
            )
          ) : (
            <TaskList tasks={tasks} />
          )}
        </main>
      </div>
    </div>
  );
}
