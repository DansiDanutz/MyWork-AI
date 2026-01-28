// Server component - force dynamic to prevent SSG
export const dynamic = "force-dynamic";
export const runtime = "edge";

import YouTubeBotClient from "./YouTubeBotClient";

export default function YouTubeBotPage() {
  return <YouTubeBotClient />;
}
