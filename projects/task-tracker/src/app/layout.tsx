import type { Metadata } from "next";
import "./globals.css";
import { WebVitalsReporter } from "@/shared/components/WebVitalsReporter";

export const metadata: Metadata = {
  title: "Task Tracker",
  description: "A task tracking application built with Next.js",
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
      </body>
    </html>
  );
}
