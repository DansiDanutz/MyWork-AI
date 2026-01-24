"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useUser, RedirectToSignIn } from "@clerk/nextjs"
import {
  LayoutDashboard,
  Package,
  ShoppingBag,
  BarChart3,
  Settings,
  Wallet,
  Brain,
} from "lucide-react"
import { cn } from "@/lib/utils"

const sidebarLinks = [
  {
    href: "/dashboard",
    label: "Overview",
    icon: LayoutDashboard,
  },
  {
    href: "/dashboard/products",
    label: "My Products",
    icon: Package,
  },
  {
    href: "/dashboard/purchases",
    label: "Purchases",
    icon: ShoppingBag,
  },
  {
    href: "/dashboard/analytics",
    label: "Analytics",
    icon: BarChart3,
  },
  {
    href: "/dashboard/payouts",
    label: "Payouts",
    icon: Wallet,
  },
  {
    href: "/dashboard/brain",
    label: "Brain Contributions",
    icon: Brain,
  },
  {
    href: "/dashboard/settings",
    label: "Settings",
    icon: Settings,
  },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { isLoaded, isSignedIn } = useUser()
  const pathname = usePathname()

  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500" />
      </div>
    )
  }

  if (!isSignedIn) {
    return <RedirectToSignIn />
  }

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 border-r border-gray-800 bg-gray-900/50 hidden lg:block">
        <div className="sticky top-16 p-4">
          <nav className="space-y-1">
            {sidebarLinks.map((link) => {
              const isActive = pathname === link.href ||
                (link.href !== "/dashboard" && pathname.startsWith(link.href))

              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                    isActive
                      ? "bg-gray-800 text-white"
                      : "text-gray-400 hover:text-white hover:bg-gray-800/50"
                  )}
                >
                  <link.icon className="h-5 w-5" />
                  {link.label}
                </Link>
              )
            })}
          </nav>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 min-h-screen">
        {children}
      </main>
    </div>
  )
}
