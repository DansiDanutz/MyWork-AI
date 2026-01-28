import { NextRequest, NextResponse } from "next/server";

type WebVitalsMetric = {
  name: "CLS" | "FCP" | "INP" | "LCP" | "TTFB";
  value: number;
  rating: "good" | "needs-improvement" | "poor";
  id: string;
  navigationType: string;
  delta: number;
};

// Thresholds from Google Core Web Vitals
const THRESHOLDS = {
  LCP: { good: 2500, poor: 4000 },
  INP: { good: 200, poor: 500 },
  CLS: { good: 0.1, poor: 0.25 },
  FCP: { good: 1800, poor: 3000 },
  TTFB: { good: 800, poor: 1800 },
};

export async function POST(request: NextRequest) {
  try {
    const metric: WebVitalsMetric = await request.json();

    // Log for monitoring (in production, send to analytics service)
    const threshold = THRESHOLDS[metric.name as keyof typeof THRESHOLDS];
    const status = threshold
      ? metric.value <= threshold.good
        ? "GOOD"
        : metric.value <= threshold.poor
          ? "NEEDS_IMPROVEMENT"
          : "POOR"
      : "UNKNOWN";

    console.log(
      `[Vitals] ${metric.name}: ${metric.value.toFixed(2)} (${status}) - ${metric.navigationType}`,
    );

    // In a real app, you would store this in database or send to analytics
    // For now, we just log it for verification

    return NextResponse.json({ received: true });
  } catch (error) {
    console.error("[Vitals] Error processing metric:", error);
    return NextResponse.json({ error: "Invalid metric" }, { status: 400 });
  }
}
