import { PageLayout } from '../components/layout/PageLayout';

export function AdminPage() {
  return (
    <PageLayout title="Admin">
      <h2 className="text-xl font-semibold text-primary">Admin Route</h2>
      <p className="mt-2 text-slate-600">Only admin users can access this route.</p>
    </PageLayout>
  );
}
