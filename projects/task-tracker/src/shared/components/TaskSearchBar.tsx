"use client";

import { useQueryState } from "nuqs";
import { useEffect, useState, useTransition } from "react";
import { taskSearchParams } from "@/app/(app)/tasks/search-params";

/**
 * TaskSearchBar: Debounced search input that updates URL state
 *
 * Features:
 * - 500ms debounce delay for optimal UX
 * - Updates URL query param 'q' via nuqs
 * - Shows loading state during transitions
 * - Clears search with X button
 */
export function TaskSearchBar() {
  const [isPending, startTransition] = useTransition();

  // URL state for search query
  const [query, setQuery] = useQueryState("q", taskSearchParams.q);

  // Local state for immediate UI feedback
  const [localQuery, setLocalQuery] = useState(query);

  // Sync local state with URL state on mount/navigation
  useEffect(() => {
    setLocalQuery(query);
  }, [query]);

  // Debounced update to URL state
  useEffect(() => {
    const timer = setTimeout(() => {
      if (localQuery !== query) {
        startTransition(() => {
          setQuery(localQuery || null); // null removes param from URL
        });
      }
    }, 500); // 500ms debounce

    return () => clearTimeout(timer);
  }, [localQuery, query, setQuery]);

  const handleClear = () => {
    setLocalQuery("");
    startTransition(() => {
      setQuery(null);
    });
  };

  return (
    <div className="relative">
      {/* Search icon */}
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <svg
          className="h-5 w-5 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      </div>

      {/* Search input */}
      <input
        type="text"
        placeholder="Search tasks..."
        value={localQuery}
        onChange={(e) => setLocalQuery(e.target.value)}
        className="
          w-full pl-10 pr-10 py-2
          bg-white dark:bg-gray-800
          border border-gray-300 dark:border-gray-600
          rounded-lg
          text-gray-900 dark:text-white
          placeholder-gray-500 dark:placeholder-gray-400
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
          transition-colors
        "
      />

      {/* Loading spinner or clear button */}
      <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
        {isPending ? (
          <svg
            className="animate-spin h-5 w-5 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        ) : localQuery ? (
          <button
            onClick={handleClear}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            aria-label="Clear search"
          >
            <svg
              className="h-5 w-5"
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
        ) : null}
      </div>
    </div>
  );
}
