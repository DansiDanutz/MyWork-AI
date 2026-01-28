import Link from "next/link";

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        Settings
      </h1>

      <div className="flex flex-col md:flex-row gap-8">
        {/* Settings navigation - tabbed per CONTEXT.md */}
        <nav className="w-full md:w-48 flex-shrink-0">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-2">
            <Link
              href="/settings/profile"
              className="block px-4 py-2 text-sm font-medium text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700 rounded-lg"
            >
              Profile
            </Link>
            {/* Future tabs: Account, Notifications, etc. */}
          </div>
        </nav>

        {/* Settings content */}
        <div className="flex-1">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
