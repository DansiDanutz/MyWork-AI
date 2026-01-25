// Server component - force dynamic to prevent SSG
export const dynamic = 'force-dynamic';
export const runtime = 'edge';

import SettingsClient from './SettingsClient';

export default function SettingsPage() {
  return <SettingsClient />;
}
