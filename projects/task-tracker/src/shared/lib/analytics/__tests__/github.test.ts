/**
 * Manual integration test for GitHub API client.
 *
 * NOTE: This is a type-checking test only. The GitHub client uses 'server-only'
 * and requires Next.js runtime environment to execute properly.
 *
 * To test at runtime:
 * 1. Create a Server Action or API route that uses enrichUser()
 * 2. Call it from a page with a valid user ID
 * 3. Check console logs for rate limit warnings
 *
 * This test verifies:
 * - TypeScript compilation succeeds
 * - Functions are properly exported
 * - Types are correctly inferred
 */

import type { checkRateLimitStatus, enrichUser } from "../github";

// Type tests (compile-time only)
// eslint-disable-next-line @typescript-eslint/no-unused-vars
type CheckRateLimitType = typeof checkRateLimitStatus;
// eslint-disable-next-line @typescript-eslint/no-unused-vars
type EnrichUserType = typeof enrichUser;

// If this compiles, the exports are working correctly
console.log("✓ GitHub API client exports are properly typed");
console.log("✓ TypeScript compilation successful");
console.log("");
console.log(
  "To test at runtime, use the functions in a Server Action or API route.",
);
console.log(
  "Example: await enrichUser(userId) in an authenticated server context.",
);
