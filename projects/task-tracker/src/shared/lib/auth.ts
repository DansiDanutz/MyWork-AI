import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";
import { PrismaAdapter } from "@auth/prisma-adapter";
import { prisma } from "@/shared/lib/db";

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [
    GitHub({
      clientId: process.env.AUTH_GITHUB_ID!,
      clientSecret: process.env.AUTH_GITHUB_SECRET!,
      authorization: {
        params: {
          // Scopes: user profile + email + repo read access (per CONTEXT.md)
          scope: "read:user user:email repo",
        },
      },
    }),
  ],
  session: {
    strategy: "database", // Database sessions (not JWT) per RESEARCH.md
    maxAge: 24 * 60 * 60, // 24 hours per CONTEXT.md
    updateAge: 60 * 60, // Silent refresh every hour
  },
  callbacks: {
    async session({ session, user }) {
      // Add user ID to session for easy access
      session.user.id = user.id;
      return session;
    },
    async redirect({ url, baseUrl }) {
      // After OAuth, redirect to welcome for first-time users (per CONTEXT.md)
      // For subsequent logins, let the default behavior work
      if (url.startsWith(baseUrl)) return url;
      return `${baseUrl}/welcome`;
    },
  },
  pages: {
    signIn: "/login",
    error: "/login", // Redirect errors to login with error param (per CONTEXT.md)
  },
});
