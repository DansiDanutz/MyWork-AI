"use server";

import { trackEvent } from "@/shared/lib/analytics";
import { auth } from "@/shared/lib/auth";
import { headers } from "next/headers";

interface SubmitFeedbackInput {
  feedback: string;
  type: "bug" | "idea" | "other";
  page: string;
}

interface SubmitFeedbackResponse {
  success?: boolean;
  error?: string;
}

/**
 * Submit user feedback via analytics tracking.
 * Stores feedback as an analytics event for later review.
 */
export async function submitFeedback(
  input: SubmitFeedbackInput,
): Promise<SubmitFeedbackResponse> {
  try {
    // Validate input
    if (!input.feedback || input.feedback.trim().length === 0) {
      return { error: "Feedback text is required" };
    }

    if (input.feedback.length > 500) {
      return { error: "Feedback must be 500 characters or less" };
    }

    if (!["bug", "idea", "other"].includes(input.type)) {
      return { error: "Invalid feedback type" };
    }

    if (!input.page || input.page.trim().length === 0) {
      return { error: "Page is required" };
    }

    // Get current user from session (optional - anonymous feedback allowed)
    const session = await auth();
    const userId = session?.user?.id ?? null;

    // Get user agent
    const headersList = await headers();
    const userAgent = headersList.get("user-agent");

    // Track feedback via analytics
    trackEvent({
      type: "feedback_submitted",
      userId,
      properties: {
        feedback: input.feedback.trim(),
        feedbackType: input.type,
        page: input.page,
        userAgent,
        timestamp: new Date().toISOString(),
      },
    });

    return { success: true };
  } catch (error) {
    console.error("[Feedback] Failed to submit feedback:", error);
    return { error: "Failed to submit feedback. Please try again." };
  }
}
