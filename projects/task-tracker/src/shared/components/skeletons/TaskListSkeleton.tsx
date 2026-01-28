import { TaskCardSkeleton } from "./TaskCardSkeleton";

/**
 * TaskListSkeleton: Loading placeholder for TaskList component
 *
 * Renders 3 sections (To Do, In Progress, Done) with 3 task cards each
 * Matches TaskList's grid layout structure
 */
export function TaskListSkeleton() {
  const sections = ["To Do", "In Progress", "Done"];

  return (
    <div className="space-y-8">
      {sections.map((section) => (
        <div key={section}>
          {/* Section heading skeleton */}
          <div className="h-7 w-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-4" />

          {/* Task cards grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((cardIndex) => (
              <TaskCardSkeleton key={cardIndex} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
