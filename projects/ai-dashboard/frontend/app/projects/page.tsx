// Server component - force dynamic to prevent SSG
export const dynamic = 'force-dynamic';
export const runtime = 'edge';

import ProjectsClient from './ProjectsClient';

export default function ProjectsPage() {
  return <ProjectsClient />;
}
