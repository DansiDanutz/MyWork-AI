// Server component - force dynamic to prevent SSG
export const dynamic = "force-dynamic";
export const runtime = "edge";

import NewsClient from "./NewsClient";

export default function NewsPage() {
  return <NewsClient />;
}
