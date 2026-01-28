import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/shared/lib/auth";
import {
  exportEventsForBrain,
  getAnalyticsSummary,
} from "@/shared/lib/analytics/queries";
import { getRetentionStats } from "@/shared/lib/analytics/retention";
import type { EventType } from "@/shared/lib/analytics/types";

/**
 * GET /api/analytics/export
 *
 * Export analytics data for brain analysis.
 * Requires authentication.
 *
 * Query parameters:
 * - startDate: ISO date string (required)
 * - endDate: ISO date string (required)
 * - eventTypes: Comma-separated event types (optional)
 * - format: 'json' (default) or 'summary'
 *
 * Examples:
 * GET /api/analytics/export?startDate=2026-01-01&endDate=2026-01-31
 * GET /api/analytics/export?startDate=2026-01-01&endDate=2026-01-31&eventTypes=task_created,task_updated
 * GET /api/analytics/export?format=summary
 */
export async function GET(request: NextRequest) {
  // Require authentication
  const session = await auth();
  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const searchParams = request.nextUrl.searchParams;
  const format = searchParams.get("format") || "json";

  // Handle summary format
  if (format === "summary") {
    const days = parseInt(searchParams.get("days") || "7", 10);
    const [summary, retention] = await Promise.all([
      getAnalyticsSummary(days),
      getRetentionStats(),
    ]);

    return NextResponse.json({
      summary,
      retention,
      exportedAt: new Date().toISOString(),
    });
  }

  // Validate required parameters for full export
  const startDateStr = searchParams.get("startDate");
  const endDateStr = searchParams.get("endDate");

  if (!startDateStr || !endDateStr) {
    return NextResponse.json(
      { error: "Missing required parameters: startDate and endDate" },
      { status: 400 },
    );
  }

  const startDate = new Date(startDateStr);
  const endDate = new Date(endDateStr);

  // Validate dates
  if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
    return NextResponse.json(
      { error: "Invalid date format. Use ISO 8601 (YYYY-MM-DD)" },
      { status: 400 },
    );
  }

  if (startDate > endDate) {
    return NextResponse.json(
      { error: "startDate must be before endDate" },
      { status: 400 },
    );
  }

  // Parse optional event types filter
  const eventTypesStr = searchParams.get("eventTypes");
  const eventTypes = eventTypesStr
    ? (eventTypesStr.split(",") as EventType[])
    : undefined;

  // Export data
  const events = await exportEventsForBrain(startDate, endDate, eventTypes);

  return NextResponse.json({
    meta: {
      startDate: startDate.toISOString(),
      endDate: endDate.toISOString(),
      eventTypes: eventTypes || "all",
      count: events.length,
      exportedAt: new Date().toISOString(),
    },
    events,
  });
}
