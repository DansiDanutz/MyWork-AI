"use client";

import { useQueryStates } from "nuqs";
import { taskSearchParams } from "@/app/(app)/tasks/search-params";
import { Tag } from "@prisma/client";

/**
 * TaskFilters: Filter sidebar for status and tag filtering
 *
 * Features:
 * - Multi-select status filter (TODO, IN_PROGRESS, DONE)
 * - Multi-select tag filter
 * - Clear all filters button
 * - URL state persistence via nuqs
 */
export function TaskFilters({ tags }: { tags: Tag[] }) {
  const [filters, setFilters] = useQueryStates(taskSearchParams);

  const selectedStatuses = filters.status || [];
  const selectedTags = filters.tags || [];

  // Toggle status filter
  const toggleStatus = (status: string) => {
    const newStatuses = selectedStatuses.includes(status)
      ? selectedStatuses.filter((s) => s !== status)
      : [...selectedStatuses, status];

    setFilters({ status: newStatuses.length > 0 ? newStatuses : null });
  };

  // Toggle tag filter
  const toggleTag = (tagId: string) => {
    const newTags = selectedTags.includes(tagId)
      ? selectedTags.filter((t) => t !== tagId)
      : [...selectedTags, tagId];

    setFilters({ tags: newTags.length > 0 ? newTags : null });
  };

  // Clear all filters
  const clearFilters = () => {
    setFilters({
      q: null,
      status: null,
      tags: null,
    });
  };

  const hasActiveFilters =
    filters.q || selectedStatuses.length > 0 || selectedTags.length > 0;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Filters
        </h3>
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="
              text-sm text-blue-600 dark:text-blue-400
              hover:text-blue-700 dark:hover:text-blue-300
              font-medium
            "
          >
            Clear all
          </button>
        )}
      </div>

      {/* Status filter */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Status
        </h4>
        <div className="space-y-2">
          {[
            { value: "TODO", label: "To Do" },
            { value: "IN_PROGRESS", label: "In Progress" },
            { value: "DONE", label: "Done" },
          ].map(({ value, label }) => (
            <label
              key={value}
              className="flex items-center space-x-3 cursor-pointer group"
            >
              <input
                type="checkbox"
                checked={selectedStatuses.includes(value)}
                onChange={() => toggleStatus(value)}
                className="
                  w-4 h-4
                  text-blue-600 dark:text-blue-500
                  border-gray-300 dark:border-gray-600
                  rounded
                  focus:ring-2 focus:ring-blue-500 focus:ring-offset-0
                  bg-white dark:bg-gray-700
                  cursor-pointer
                "
              />
              <span className="text-sm text-gray-700 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-white">
                {label}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Tag filter */}
      {tags.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Tags
          </h4>
          <div className="space-y-2">
            {tags.map((tag) => (
              <label
                key={tag.id}
                className="flex items-center space-x-3 cursor-pointer group"
              >
                <input
                  type="checkbox"
                  checked={selectedTags.includes(tag.id)}
                  onChange={() => toggleTag(tag.id)}
                  className="
                    w-4 h-4
                    text-blue-600 dark:text-blue-500
                    border-gray-300 dark:border-gray-600
                    rounded
                    focus:ring-2 focus:ring-blue-500 focus:ring-offset-0
                    bg-white dark:bg-gray-700
                    cursor-pointer
                  "
                />
                <div className="flex items-center space-x-2">
                  {tag.color && (
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: tag.color }}
                    />
                  )}
                  <span className="text-sm text-gray-700 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-white">
                    {tag.name}
                  </span>
                </div>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Empty state for tags */}
      {tags.length === 0 && (
        <div className="text-sm text-gray-500 dark:text-gray-400">
          No tags yet. Create tags to organize your tasks.
        </div>
      )}
    </div>
  );
}
