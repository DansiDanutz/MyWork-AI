"use client";

import { useReportWebVitals } from "next/web-vitals";

export function WebVitalsReporter() {
  useReportWebVitals((metric) => {
    // Log to console in development
    if (process.env.NODE_ENV === "development") {
      const { name, value, rating } = metric;
      const color =
        rating === "good"
          ? "green"
          : rating === "needs-improvement"
            ? "yellow"
            : "red";
      console.log(
        `[Web Vitals] ${name}: ${Math.round(value)}ms (${rating})`,
        `color: ${color}`,
      );
    }

    // Send to analytics endpoint
    const body = JSON.stringify({
      name: metric.name,
      value: metric.value,
      rating: metric.rating,
      id: metric.id,
      navigationType: metric.navigationType,
      delta: metric.delta,
    });

    // Use sendBeacon for reliability, fall back to fetch
    const url = "/api/analytics/vitals";
    if (navigator.sendBeacon) {
      navigator.sendBeacon(url, body);
    } else {
      fetch(url, {
        body,
        method: "POST",
        keepalive: true,
        headers: { "Content-Type": "application/json" },
      });
    }
  });

  return null;
}
