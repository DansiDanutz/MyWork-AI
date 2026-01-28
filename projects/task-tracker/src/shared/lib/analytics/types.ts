import { z } from "zod";

// Page views
const PageViewEventSchema = z.object({
  type: z.literal("page_view"),
  userId: z.string(),
  properties: z.object({
    path: z.string(),
    referrer: z.string().optional(),
  }),
});

// Task events (for future phases)
const TaskCreatedEventSchema = z.object({
  type: z.literal("task_created"),
  userId: z.string(),
  properties: z.object({
    taskId: z.string(),
    hasDescription: z.boolean(),
    category: z.string().optional(),
  }),
});

const TaskUpdatedEventSchema = z.object({
  type: z.literal("task_updated"),
  userId: z.string(),
  properties: z.object({
    taskId: z.string(),
    fieldsChanged: z.array(z.string()),
    newStatus: z.string().optional(),
  }),
});

const TaskDeletedEventSchema = z.object({
  type: z.literal("task_deleted"),
  userId: z.string(),
  properties: z.object({
    taskId: z.string(),
  }),
});

// Tag events (for Phase 4)
const TagCreatedEventSchema = z.object({
  type: z.literal("tag_created"),
  userId: z.string(),
  properties: z.object({
    tagId: z.string(),
    tagName: z.string(),
  }),
});

const TagDeletedEventSchema = z.object({
  type: z.literal("tag_deleted"),
  userId: z.string(),
  properties: z.object({
    tagId: z.string(),
    tagName: z.string(),
  }),
});

const TaskTagsUpdatedEventSchema = z.object({
  type: z.literal("task_tags_updated"),
  userId: z.string(),
  properties: z.object({
    taskId: z.string(),
    tagCount: z.number(),
  }),
});

const TagAddedToTaskEventSchema = z.object({
  type: z.literal("tag_added_to_task"),
  userId: z.string(),
  properties: z.object({
    taskId: z.string(),
    tagName: z.string(),
  }),
});

// File events (for future phases)
const FileUploadedEventSchema = z.object({
  type: z.literal("file_uploaded"),
  userId: z.string(),
  properties: z.object({
    fileId: z.string(),
    taskId: z.string(),
    fileSize: z.number(),
    mimeType: z.string(),
  }),
});

// Search events
const SearchPerformedEventSchema = z.object({
  type: z.literal("search_performed"),
  userId: z.string(),
  properties: z.object({
    query: z.string(),
    resultCount: z.number(),
    searchType: z.string(),
  }),
});

const FilterAppliedEventSchema = z.object({
  type: z.literal("filter_applied"),
  userId: z.string(),
  properties: z.object({
    filters: z.object({
      status: z.number(),
      tags: z.number(),
      hasDateRange: z.boolean(),
    }),
    resultCount: z.number(),
  }),
});

// Auth events
const LoginEventSchema = z.object({
  type: z.literal("login"),
  userId: z.string(),
  properties: z.object({
    provider: z.string(),
    isNewUser: z.boolean(),
  }),
});

const LogoutEventSchema = z.object({
  type: z.literal("logout"),
  userId: z.string(),
  properties: z.object({}),
});

// Profile events
const ProfileUpdatedEventSchema = z.object({
  type: z.literal("profile_updated"),
  userId: z.string(),
  properties: z.object({
    fieldsChanged: z.array(z.string()),
  }),
});

// Feedback events
const FeedbackSubmittedEventSchema = z.object({
  type: z.literal("feedback_submitted"),
  userId: z.string().nullable(),
  properties: z.object({
    feedback: z.string(),
    feedbackType: z.enum(["bug", "idea", "other"]),
    page: z.string(),
    userAgent: z.string().nullable(),
    timestamp: z.string(),
  }),
});

// Discriminated union for type-safe event handling
export const AnalyticsEventSchema = z.discriminatedUnion("type", [
  PageViewEventSchema,
  TaskCreatedEventSchema,
  TaskUpdatedEventSchema,
  TaskDeletedEventSchema,
  TagCreatedEventSchema,
  TagDeletedEventSchema,
  TaskTagsUpdatedEventSchema,
  TagAddedToTaskEventSchema,
  FileUploadedEventSchema,
  SearchPerformedEventSchema,
  FilterAppliedEventSchema,
  LoginEventSchema,
  LogoutEventSchema,
  ProfileUpdatedEventSchema,
  FeedbackSubmittedEventSchema,
]);

export type AnalyticsEvent = z.infer<typeof AnalyticsEventSchema>;
export type EventType = AnalyticsEvent["type"];

// Export individual schemas for type inference
export {
  PageViewEventSchema,
  TaskCreatedEventSchema,
  TaskUpdatedEventSchema,
  TaskDeletedEventSchema,
  TagCreatedEventSchema,
  TagDeletedEventSchema,
  TaskTagsUpdatedEventSchema,
  TagAddedToTaskEventSchema,
  FileUploadedEventSchema,
  SearchPerformedEventSchema,
  FilterAppliedEventSchema,
  LoginEventSchema,
  LogoutEventSchema,
  ProfileUpdatedEventSchema,
  FeedbackSubmittedEventSchema,
};
