"use client";

import { XMarkIcon } from "@heroicons/react/24/outline";

type TagBadgeProps = {
  name: string;
  color?: string;
  onRemove?: () => void;
  size?: "sm" | "md";
};

export function TagBadge({
  name,
  color = "#6b7280",
  onRemove,
  size = "sm",
}: TagBadgeProps) {
  const sizeClasses = {
    sm: "text-xs px-2 py-0.5",
    md: "text-sm px-2.5 py-1",
  };

  return (
    <span
      className={`
        inline-flex items-center gap-1
        ${sizeClasses[size]}
        rounded-full
        font-medium
        transition-colors
      `}
      style={{
        backgroundColor: `${color}20`, // 20% opacity background
        color: color,
        borderColor: `${color}40`, // 40% opacity border
        borderWidth: "1px",
      }}
    >
      <span
        className="w-2 h-2 rounded-full flex-shrink-0"
        style={{ backgroundColor: color }}
      />
      {name}
      {onRemove && (
        <button
          type="button"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onRemove();
          }}
          className="
            ml-0.5 -mr-1
            rounded-full p-0.5
            hover:bg-black/10 dark:hover:bg-white/10
            transition-colors
          "
          aria-label={`Remove ${name} tag`}
        >
          <XMarkIcon className="h-3 w-3" />
        </button>
      )}
    </span>
  );
}
