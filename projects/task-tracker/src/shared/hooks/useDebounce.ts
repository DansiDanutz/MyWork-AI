'use client'

import { useEffect, useCallback, useRef } from 'react'

/**
 * Debounce a callback function to prevent excessive calls.
 * Used for auto-save pattern per CONTEXT.md requirements.
 *
 * @param callback - Function to debounce
 * @param delay - Delay in milliseconds (default 3000ms per RESEARCH.md recommendation)
 * @returns Debounced version of the callback
 *
 * @example
 * const handleChange = useDebounce((value: string) => {
 *   saveToServer(value)
 * }, 3000)
 */
export function useDebounce<T extends (...args: never[]) => unknown>(
  callback: T,
  delay: number = 3000
): (...args: Parameters<T>) => void {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)
  const callbackRef = useRef(callback)

  // Update callback ref on each render to capture latest closure
  useEffect(() => {
    callbackRef.current = callback
  }, [callback])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  const debouncedCallback = useCallback((...args: Parameters<T>) => {
    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    // Set new timeout
    timeoutRef.current = setTimeout(() => {
      callbackRef.current(...args)
    }, delay)
  }, [delay])

  return debouncedCallback
}
