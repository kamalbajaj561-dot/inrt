import { PageLayout } from '../components/layout/PageLayout';

export function DashboardPage() {
  return (
    <PageLayout title="Dashboard">
      <h2 className="text-xl font-semibold text-primary">Dashboard Route</h2>
      <p className="mt-2 text-slate-600">Use this page as the authenticated home for your app.</p>
    </PageLayout>
  );
}
