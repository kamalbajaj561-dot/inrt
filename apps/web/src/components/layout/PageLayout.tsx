import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../features/auth/AuthContext';

export function PageLayout({ title, children }: { title: string; children: ReactNode }) {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="bg-primary text-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <h1 className="text-lg font-semibold">{title}</h1>
          {user && (
            <div className="flex items-center gap-4 text-sm">
              <span>{user.email}</span>
              <button className="rounded bg-accent-500 px-3 py-1 font-medium hover:bg-accent-600" onClick={logout}>
                Logout
              </button>
            </div>
          )}
        </div>
      </header>
      <main className="mx-auto flex w-full max-w-5xl gap-6 px-6 py-8">
        <nav className="w-44 space-y-2 rounded-lg bg-white p-4 shadow">
          <Link className="block text-primary hover:text-accent-600" to="/dashboard">
            Dashboard
          </Link>
          <Link className="block text-primary hover:text-accent-600" to="/send">
            Send
          </Link>
          <Link className="block text-primary hover:text-accent-600" to="/receive">
            Receive
          </Link>
          <Link className="block text-primary hover:text-accent-600" to="/admin">
            Admin
          </Link>
        </nav>
        <section className="flex-1 rounded-lg bg-white p-6 shadow">{children}</section>
      </main>
    </div>
  );
}
