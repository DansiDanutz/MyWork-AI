"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Tag } from "@prisma/client";
import { TagBadge } from "./TagBadge";
import { PlusIcon } from "@heroicons/react/24/outline";

type TagInputProps = {
  selectedTags: Tag[];
  availableTags: Tag[];
  onAddTag: (tagName: string) => Promise<void>;
  onRemoveTag: (tagId: string) => void;
  disabled?: boolean;
};

export function TagInput({
  selectedTags,
  availableTags,
  onAddTag,
  onRemoveTag,
  disabled = false,
}: TagInputProps) {
  const [inputValue, setInputValue] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Filter available tags based on input and exclude already selected
  const filteredTags = availableTags.filter(
    (tag) =>
      !selectedTags.some((t) => t.id === tag.id) &&
      tag.name.toLowerCase().includes(inputValue.toLowerCase()),
  );

  // Check if input matches an existing tag exactly
  const exactMatch = availableTags.find(
    (tag) => tag.name.toLowerCase() === inputValue.toLowerCase(),
  );

  // Show "create new" option if input doesn't match existing tag
  const showCreateOption = inputValue.trim() && !exactMatch;

  // Handle clicking outside to close dropdown
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        !inputRef.current?.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleAddTag = useCallback(
    async (tagName: string) => {
      if (!tagName.trim() || isAdding || disabled) return;

      setIsAdding(true);
      try {
        await onAddTag(tagName.trim());
        setInputValue("");
        setIsOpen(false);
      } finally {
        setIsAdding(false);
      }
    },
    [onAddTag, isAdding, disabled],
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && inputValue.trim()) {
        e.preventDefault();
        handleAddTag(inputValue);
      } else if (e.key === "Escape") {
        setIsOpen(false);
        inputRef.current?.blur();
      }
    },
    [inputValue, handleAddTag],
  );

  return (
    <div className="space-y-2">
      {/* Selected tags */}
      {selectedTags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {selectedTags.map((tag) => (
            <TagBadge
              key={tag.id}
              name={tag.name}
              color={tag.color || undefined}
              onRemove={disabled ? undefined : () => onRemoveTag(tag.id)}
            />
          ))}
        </div>
      )}

      {/* Input with dropdown */}
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => {
            setInputValue(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder={
            selectedTags.length > 0 ? "Add another tag..." : "Add tags..."
          }
          disabled={disabled || isAdding}
          className="
            block w-full
            px-3 py-2
            border border-gray-300 dark:border-gray-600
            rounded-md
            bg-white dark:bg-gray-800
            text-gray-900 dark:text-gray-100
            placeholder-gray-500 dark:placeholder-gray-400
            focus:ring-2 focus:ring-blue-500 focus:border-transparent
            text-sm
            disabled:opacity-50 disabled:cursor-not-allowed
          "
        />

        {/* Dropdown */}
        {isOpen && (filteredTags.length > 0 || showCreateOption) && (
          <div
            ref={dropdownRef}
            className="
              absolute z-10 mt-1 w-full
              bg-white dark:bg-gray-800
              border border-gray-200 dark:border-gray-700
              rounded-md shadow-lg
              max-h-48 overflow-y-auto
            "
          >
            {/* Create new tag option */}
            {showCreateOption && (
              <button
                type="button"
                onClick={() => handleAddTag(inputValue)}
                disabled={isAdding}
                className="
                  w-full px-3 py-2
                  text-left text-sm
                  flex items-center gap-2
                  text-blue-600 dark:text-blue-400
                  hover:bg-gray-100 dark:hover:bg-gray-700
                  disabled:opacity-50
                "
              >
                <PlusIcon className="h-4 w-4" />
                Create &quot;{inputValue.trim()}&quot;
              </button>
            )}

            {/* Existing tags */}
            {filteredTags.map((tag) => (
              <button
                key={tag.id}
                type="button"
                onClick={() => handleAddTag(tag.name)}
                disabled={isAdding}
                className="
                  w-full px-3 py-2
                  text-left text-sm
                  flex items-center gap-2
                  text-gray-700 dark:text-gray-300
                  hover:bg-gray-100 dark:hover:bg-gray-700
                  disabled:opacity-50
                "
              >
                <span
                  className="w-3 h-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: tag.color || "#6b7280" }}
                />
                {tag.name}
              </button>
            ))}
          </div>
        )}
      </div>

      {isAdding && (
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Adding tag...
        </p>
      )}
    </div>
  );
}
