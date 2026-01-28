import { Suspense } from "react";
import Link from "next/link";
import {
  getTasksByUser,
  verifySession,
  getTagsByUser,
  searchTasks,
  filterTasks,
} from "@/shared/lib/dal";
import { TaskListWithFilters } from "@/shared/components/TaskListWithFilters";
import { searchParamsCache } from "./search-params";
import { TaskStatus } from "@prisma/client";

/**
 * Tasks Page: Full task discovery experience
 *
 * Features:
 * - Search bar with debounced input
 * - Filter sidebar (status, tags)
 * - Task list with status grouping
 * - URL state persistence
 * - Responsive layout
 * - Loading states with Suspense
 *
 * URL Parameters:
 * - q: Search query
 * - status: Status filters (array)
 * - tags: Tag filters (array)
 */

// Loading skeleton for full page content
function TasksLoadingSkeleton() {
  return (
    <div className="space-y-6">
      {/* Search bar skeleton */}
      <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse" />

      {/* Two-column layout skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filter sidebar skeleton */}
        <aside className="lg:col-span-1">
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 animate-pulse">
            <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-24 mb-4" />
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded" />
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded" />
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded" />
            </div>
          </div>
        </aside>

        {/* Task list skeleton */}
        <main className="lg:col-span-3">
          <div className="space-y-8 animate-pulse">
            {[1, 2, 3].map((section) => (
              <div key={section}>
                <div className="h-7 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-4" />
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[1, 2, 3].map((card) => (
                    <div
                      key={card}
                      className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                    >
                      <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-3" />
                      <div className="space-y-2 mb-4">
                        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full" />
                        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6" />
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-24" />
                        <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-16" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}

// Server Component that fetches data and renders TaskListWithFilters
async function TasksContent({
  searchQuery,
  statusFilters,
  tagFilters,
}: {
  searchQuery: string;
  statusFilters: string[];
  tagFilters: string[];
}) {
  const { userId } = await verifySession();

  // Fetch tags for filter sidebar
  const tags = await getTagsByUser(userId);

  // Fetch tasks based on search/filter state
  let tasks;

  if (searchQuery.trim().length > 0) {
    // Search with filters
    const searchResults = await searchTasks(userId, searchQuery.trim());
    tasks = searchResults;

    // Apply status filter to search results
    if (statusFilters.length > 0) {
      tasks = tasks.filter((task) => statusFilters.includes(task.status));
    }

    // Apply tag filter to search results
    if (tagFilters.length > 0) {
      tasks = tasks.filter((task) =>
        task.tags.some((tag) => tagFilters.includes(tag.id)),
      );
    }
  } else if (statusFilters.length > 0 || tagFilters.length > 0) {
    // Filter without search
    const filterObj: {
      status?: TaskStatus[];
      tagIds?: string[];
    } = {};

    if (statusFilters.length > 0) {
      filterObj.status = statusFilters as TaskStatus[];
    }

    if (tagFilters.length > 0) {
      filterObj.tagIds = tagFilters;
    }

    tasks = await filterTasks(userId, filterObj);
  } else {
    // No filters, get all tasks
    tasks = await getTasksByUser(userId);
  }

  return <TaskListWithFilters tasks={tasks} tags={tags} />;
}

export default async function TasksPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  // Parse URL search params
  const params = await searchParams;
  const { q, status, tags } = searchParamsCache.parse(params);

  return (
    <div>
      {/* Page header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          My Tasks
        </h1>

        {/* New Task button */}
        <Link
          href="/tasks/new"
          className="
            inline-flex items-center justify-center
            px-4 py-2
            bg-blue-600 text-white
            rounded-md font-medium
            hover:bg-blue-700
            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
            dark:bg-blue-500 dark:hover:bg-blue-600
            transition-colors
          "
        >
          <svg
            className="w-5 h-5 mr-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          New Task
        </Link>
      </div>

      {/* Task discovery interface with search, filters, and list */}
      <Suspense fallback={<TasksLoadingSkeleton />}>
        <TasksContent
          searchQuery={q}
          statusFilters={status}
          tagFilters={tags}
        />
      </Suspense>
    </div>
  );
}
