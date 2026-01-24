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
  Menu,
  X,
  ChevronLeft,
  ChevronRight,
  Receipt,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useEffect, useState } from "react"

const sidebarLinks = [
  {
    href: "/dashboard",
    label: "Overview",
    icon: LayoutDashboard,
  },
  {
    href: "/my-products",
    label: "My Products",
    icon: Package,
  },
  {
    href: "/orders",
    label: "Sales",
    icon: Receipt,
  },
  {
    href: "/purchases",
    label: "Purchases",
    icon: ShoppingBag,
  },
  {
    href: "/analytics",
    label: "Analytics",
    icon: BarChart3,
  },
  {
    href: "/payouts",
    label: "Payouts",
    icon: Wallet,
  },
  {
    href: "/brain",
    label: "Brain Contributions",
    icon: Brain,
  },
  {
    href: "/settings",
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
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  // Load sidebar state from localStorage on mount
  useEffect(() => {
    const savedState = localStorage.getItem("sidebar-collapsed")
    if (savedState !== null) {
      setSidebarCollapsed(savedState === "true")
    }
  }, [])

  // Save sidebar state to localStorage when it changes
  useEffect(() => {
    localStorage.setItem("sidebar-collapsed", sidebarCollapsed.toString())
  }, [sidebarCollapsed])

  // Close mobile menu when route changes
  useEffect(() => {
    setMobileMenuOpen(false)
  }, [pathname])

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
      {/* Mobile overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed lg:sticky top-0 h-screen lg:h-auto bg-gray-900/95 border-r border-gray-800 z-50 transition-all duration-300 ease-in-out",
          "flex flex-col",
          // Mobile styles
          "lg:hidden",
          mobileMenuOpen ? "translate-x-0 w-64" : "-translate-x-full w-64",
          // Desktop styles
          "hidden lg:flex",
          sidebarCollapsed ? "w-16" : "w-64"
        )}
      >
        {/* Sidebar header with collapse toggle */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-800">
          {!sidebarCollapsed && (
            <h2 className="text-lg font-semibold text-white">Menu</h2>
          )}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className={cn(
              "hidden lg:flex p-2 rounded-lg hover:bg-gray-800 transition-colors",
              sidebarCollapsed && "mx-auto"
            )}
            aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {sidebarCollapsed ? (
              <ChevronRight className="h-5 w-5 text-gray-400" />
            ) : (
              <ChevronLeft className="h-5 w-5 text-gray-400" />
            )}
          </button>
          {/* Mobile close button */}
          <button
            onClick={() => setMobileMenuOpen(false)}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-800 transition-colors"
            aria-label="Close menu"
          >
            <X className="h-5 w-5 text-gray-400" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {sidebarLinks.map((link) => {
            const isActive = pathname === link.href ||
              (link.href !== "/dashboard" && pathname.startsWith(link.href))

            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-gray-800 text-white"
                    : "text-gray-400 hover:text-white hover:bg-gray-800/50",
                  sidebarCollapsed && "justify-center px-2"
                )}
                title={sidebarCollapsed ? link.label : undefined}
              >
                <link.icon className="h-5 w-5 flex-shrink-0" />
                {!sidebarCollapsed && (
                  <span className="truncate">{link.label}</span>
                )}
              </Link>
            )
          })}
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 min-h-screen">
        {/* Mobile header with hamburger menu */}
        <div className="lg:hidden h-16 flex items-center px-4 border-b border-gray-800 sticky top-0 bg-gray-900/95 backdrop-blur z-30">
          <button
            onClick={() => setMobileMenuOpen(true)}
            className="p-2 rounded-lg hover:bg-gray-800 transition-colors"
            aria-label="Open menu"
          >
            <Menu className="h-5 w-5 text-gray-400" />
          </button>
          <span className="ml-4 text-lg font-semibold text-white">Dashboard</span>
        </div>

        {children}
      </main>
    </div>
  )
}
