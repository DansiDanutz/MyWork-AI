'use client';

import dynamic from 'next/dynamic';

const Sidebar = dynamic(() => import('./Sidebar').then(mod => mod.Sidebar), {
  ssr: false,
  loading: () => <div className="w-64 bg-gray-900 h-screen" />,
});

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 ml-64 p-8">
        {children}
      </main>
    </div>
  );
}
