// Server component - force dynamic to prevent SSG
export const dynamic = "force-dynamic";
export const runtime = "edge";

import VideosClient from "./VideosClient";

export default function VideosPage() {
  return <VideosClient />;
}
