import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/shared/lib/auth";
import { prisma } from "@/shared/lib/db";
import { readFile } from "@/shared/lib/file-storage";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  try {
    // Authenticate
    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { id } = await params;

    // Find file and verify ownership
    const file = await prisma.fileAttachment.findFirst({
      where: { id, userId: session.user.id },
    });

    if (!file) {
      return NextResponse.json({ error: "File not found" }, { status: 404 });
    }

    // Read file from disk
    const buffer = await readFile(
      session.user.id,
      file.taskId,
      file.storedFilename,
    );

    if (!buffer) {
      return NextResponse.json(
        { error: "File not found on disk" },
        { status: 404 },
      );
    }

    // Determine if this should be displayed inline or downloaded
    const isInlineViewable =
      file.mimeType.startsWith("image/") || file.mimeType === "application/pdf";
    const disposition = isInlineViewable ? "inline" : "attachment";

    // Return file with appropriate headers
    return new NextResponse(buffer as unknown as BodyInit, {
      status: 200,
      headers: {
        "Content-Type": file.mimeType,
        "Content-Length": file.size.toString(),
        "Content-Disposition": `${disposition}; filename="${encodeURIComponent(file.filename)}"`,
        "Cache-Control": "private, max-age=3600", // Cache for 1 hour
      },
    });
  } catch (error) {
    console.error("Download error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}
