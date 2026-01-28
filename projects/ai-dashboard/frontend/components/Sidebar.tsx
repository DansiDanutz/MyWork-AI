"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LuHouse,
  LuVideo,
  LuNewspaper,
  LuFolderGit2,
  LuBot,
  LuSettings,
  LuActivity,
} from "react-icons/lu";

const navigation = [
  { name: "Dashboard", href: "/", icon: LuHouse },
  { name: "AI Videos", href: "/videos", icon: LuVideo },
  { name: "AI News", href: "/news", icon: LuNewspaper },
  { name: "GitHub Projects", href: "/projects", icon: LuFolderGit2 },
  { name: "YouTube Bot", href: "/youtube-bot", icon: LuBot },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 w-64 bg-gray-900 text-white h-screen flex flex-col overflow-y-auto">
      {/* Logo */}
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <LuActivity className="w-6 h-6" />
          </div>
          <div>
            <h1 className="font-bold text-lg">AI Dashboard</h1>
            <p className="text-xs text-gray-400">Your AI Command Center</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? "bg-blue-600 text-white"
                      : "text-gray-300 hover:bg-gray-800 hover:text-white"
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span>{item.name}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-800">
        <Link
          href="/settings"
          className="flex items-center gap-3 px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg transition-colors"
        >
          <LuSettings className="w-5 h-5" />
          <span>Settings</span>
        </Link>
      </div>
    </aside>
  );
}
