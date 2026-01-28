import { prisma } from "@/shared/lib/db";
import { NextResponse } from "next/server";

export async function GET() {
  const timestamp = new Date().toISOString();
  const uptime = process.uptime();

  // Check database connectivity
  let databaseStatus: "healthy" | "unhealthy" = "healthy";
  let databaseError: string | undefined;

  try {
    await prisma.$queryRaw`SELECT 1`;
  } catch (error) {
    databaseStatus = "unhealthy";
    databaseError =
      error instanceof Error ? error.message : "Connection failed";
  }

  // Overall status is unhealthy if database is down
  const overallStatus: "healthy" | "unhealthy" =
    databaseStatus === "unhealthy" ? "unhealthy" : "healthy";

  const response = {
    status: overallStatus,
    checks: {
      database: databaseStatus,
      uptime: Math.floor(uptime), // seconds since process started
      timestamp,
    },
    ...(databaseError && { error: databaseError }),
  };

  const statusCode = overallStatus === "healthy" ? 200 : 503;

  return NextResponse.json(response, { status: statusCode });
}
