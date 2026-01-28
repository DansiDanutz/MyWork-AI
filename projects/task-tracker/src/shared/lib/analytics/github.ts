import "server-only";
import { prisma } from "@/shared/lib/db";

interface RateLimitInfo {
  limit: number;
  remaining: number;
  reset: number; // Unix timestamp
  used: number;
}

interface GitHubUserData {
  login: string;
  id: number;
  avatar_url: string;
  html_url: string;
  name: string | null;
  company: string | null;
  blog: string | null;
  location: string | null;
  bio: string | null;
  public_repos: number;
  public_gists: number;
  followers: number;
  following: number;
  created_at: string;
}

interface CacheEntry {
  data: GitHubUserData;
  etag: string;
  cachedAt: number;
}

// In-memory cache for rate limit efficiency
// Production would use Redis, but Map is fine for validation project
const userCache = new Map<string, CacheEntry>();
const CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours per research

/**
 * Extract rate limit info from GitHub API response headers.
 */
function parseRateLimitHeaders(response: Response): RateLimitInfo {
  return {
    limit: parseInt(response.headers.get("x-ratelimit-limit") || "5000", 10),
    remaining: parseInt(
      response.headers.get("x-ratelimit-remaining") || "0",
      10,
    ),
    reset: parseInt(response.headers.get("x-ratelimit-reset") || "0", 10),
    used: parseInt(response.headers.get("x-ratelimit-used") || "0", 10),
  };
}

/**
 * Check current rate limit status for a given access token.
 * Use this before making expensive API operations.
 *
 * @returns Current rate limit info or null if check fails
 */
export async function checkRateLimitStatus(
  accessToken: string,
): Promise<RateLimitInfo | null> {
  try {
    const response = await fetch("https://api.github.com/rate_limit", {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        Accept: "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
      },
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      console.warn("[GitHub] Rate limit check failed:", response.status);
      return null;
    }

    return parseRateLimitHeaders(response);
  } catch (error) {
    console.error("[GitHub] Rate limit check error:", error);
    return null;
  }
}

/**
 * Fetch enriched user data from GitHub API with caching and rate limit handling.
 *
 * Features:
 * - 24-hour in-memory cache to minimize API calls
 * - ETag-based conditional requests (304 responses don't count against limit)
 * - Graceful degradation when rate limited
 * - 5-second timeout to prevent hanging
 *
 * @param userId - Internal user ID (for cache key)
 * @param accessToken - GitHub OAuth access token
 * @returns GitHub user data or null if unavailable
 */
export async function enrichUserWithGitHubData(
  userId: string,
  accessToken: string,
): Promise<GitHubUserData | null> {
  const now = Date.now();
  const cached = userCache.get(userId);

  // Return cached data if still valid
  if (cached && now - cached.cachedAt < CACHE_TTL) {
    return cached.data;
  }

  try {
    const response = await fetch("https://api.github.com/user", {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        Accept: "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
        // ETag caching - 304 responses don't count against rate limit
        ...(cached?.etag ? { "If-None-Match": cached.etag } : {}),
      },
      signal: AbortSignal.timeout(5000),
    });

    const rateLimit = parseRateLimitHeaders(response);

    // Log warning when running low
    if (rateLimit.remaining < 100) {
      console.warn(
        `[GitHub] Rate limit low: ${rateLimit.remaining}/${rateLimit.limit} remaining. ` +
          `Resets at ${new Date(rateLimit.reset * 1000).toISOString()}`,
      );
    }

    // Handle 304 Not Modified - extend cache TTL
    if (response.status === 304 && cached) {
      userCache.set(userId, { ...cached, cachedAt: now });
      return cached.data;
    }

    // Handle rate limiting gracefully
    if (response.status === 403 || response.status === 429) {
      const resetTime = new Date(rateLimit.reset * 1000);
      console.error(
        `[GitHub] Rate limited until ${resetTime.toISOString()}. ` +
          `Remaining: ${rateLimit.remaining}`,
      );
      // Return stale cached data if available, otherwise null
      return cached?.data || null;
    }

    // Handle other errors
    if (!response.ok) {
      console.error(
        "[GitHub] API error:",
        response.status,
        response.statusText,
      );
      return cached?.data || null;
    }

    // Parse and cache successful response
    const data: GitHubUserData = await response.json();
    const etag = response.headers.get("etag") || "";

    userCache.set(userId, { data, etag, cachedAt: now });

    return data;
  } catch (error) {
    console.error("[GitHub] API request failed:", error);
    // Graceful degradation - return cached data if available
    return cached?.data || null;
  }
}

/**
 * Get GitHub access token for a user from their linked account.
 * The token was stored during OAuth sign-in in Phase 2.
 *
 * @param userId - Internal user ID
 * @returns Access token or null if not found
 */
export async function getGitHubAccessToken(
  userId: string,
): Promise<string | null> {
  const account = await prisma.account.findFirst({
    where: {
      userId,
      provider: "github",
    },
    select: {
      access_token: true,
    },
  });

  return account?.access_token || null;
}

/**
 * Enrich user with GitHub data using stored access token.
 * Convenience wrapper that handles token retrieval.
 *
 * @param userId - Internal user ID
 * @returns GitHub user data or null if unavailable
 */
export async function enrichUser(
  userId: string,
): Promise<GitHubUserData | null> {
  const accessToken = await getGitHubAccessToken(userId);

  if (!accessToken) {
    console.warn("[GitHub] No access token found for user:", userId);
    return null;
  }

  return enrichUserWithGitHubData(userId, accessToken);
}
