// Server component - force dynamic to prevent SSG
export const dynamic = "force-dynamic";
export const runtime = "edge";

import DashboardClient from "./DashboardClient";

export default function DashboardPage() {
  return <DashboardClient />;
}
