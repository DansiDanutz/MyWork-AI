"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";
import { verifySession } from "@/shared/lib/dal";
import { prisma } from "@/shared/lib/db";

// Validation schema for profile updates
const profileSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  bio: z.string().max(500).optional(),
});

export type ProfileUpdateResult = {
  success: boolean;
  error?: string;
  field?: string;
};

/**
 * Update a single profile field.
 * Used for auto-save pattern - called on individual field changes.
 */
export async function updateProfileField(
  field: "name" | "bio",
  value: string,
): Promise<ProfileUpdateResult> {
  try {
    const { userId } = await verifySession();

    // Validate the specific field
    const validation = profileSchema.shape[field]?.safeParse(value);
    if (validation && !validation.success) {
      return {
        success: false,
        error: validation.error.issues[0]?.message || "Invalid value",
        field,
      };
    }

    // Update only the changed field
    await prisma.user.update({
      where: { id: userId },
      data: { [field]: value || null },
    });

    revalidatePath("/settings/profile");
    return { success: true };
  } catch (error) {
    console.error("Profile update error:", error);
    return {
      success: false,
      error: "Failed to save changes. Please try again.",
      field,
    };
  }
}

/**
 * Update multiple profile fields at once.
 * Used for form submission or bulk updates.
 */
export async function updateProfile(
  formData: FormData,
): Promise<ProfileUpdateResult> {
  try {
    const { userId } = await verifySession();

    const data = {
      name: formData.get("name") as string | null,
      bio: formData.get("bio") as string | null,
    };

    // Validate all fields
    const validation = profileSchema.safeParse(data);
    if (!validation.success) {
      const firstError = validation.error.issues[0];
      return {
        success: false,
        error: firstError?.message || "Invalid input",
        field: firstError?.path[0] as string,
      };
    }

    await prisma.user.update({
      where: { id: userId },
      data: {
        name: data.name || null,
        bio: data.bio || null,
      },
    });

    revalidatePath("/settings/profile");
    return { success: true };
  } catch (error) {
    console.error("Profile update error:", error);
    return {
      success: false,
      error: "Failed to save changes. Please try again.",
    };
  }
}
