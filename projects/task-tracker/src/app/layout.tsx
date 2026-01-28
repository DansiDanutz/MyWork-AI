import type { Metadata } from "next";
import "./globals.css";
import { WebVitalsReporter } from "@/shared/components/WebVitalsReporter";
import { FeedbackWidget } from "@/shared/components/FeedbackWidget";

export const metadata: Metadata = {
  title: "Task Tracker - Simple Task Management for Developers",
  description:
    "A minimal, fast task tracker that gets out of your way. Create tasks, attach files, swipe to complete. Free to use with GitHub login.",
  keywords: [
    "task tracker",
    "todo app",
    "task management",
    "developer tools",
    "productivity",
  ],
  authors: [{ name: "MyWork AI" }],
  openGraph: {
    title: "Task Tracker - Simple Task Management for Developers",
    description:
      "A minimal, fast task tracker that gets out of your way. Create tasks, attach files, swipe to complete.",
    type: "website",
    siteName: "Task Tracker",
  },
  twitter: {
    card: "summary_large_image",
    title: "Task Tracker - Simple Task Management for Developers",
    description:
      "A minimal, fast task tracker that gets out of your way. Create tasks, attach files, swipe to complete.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <WebVitalsReporter />
        {children}
        <FeedbackWidget />
      </body>
    </html>
  );
}
