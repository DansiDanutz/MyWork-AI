// Server component - force dynamic to prevent SSG
export const dynamic = 'force-dynamic';
export const runtime = 'edge';

import AutomationDetailClient from './AutomationDetailClient';

export default function AutomationDetailPage() {
  return <AutomationDetailClient />;
}
