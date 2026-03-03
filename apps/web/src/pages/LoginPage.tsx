import { FormEvent, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../features/auth/AuthContext';

export function LoginPage() {
  const [email, setEmail] = useState('user@example.com');
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: { pathname?: string } })?.from?.pathname ?? '/dashboard';

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    login(email);
    navigate(from, { replace: true });
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <form className="w-full max-w-md space-y-4 rounded-xl bg-white p-6 shadow" onSubmit={handleSubmit}>
        <h1 className="text-2xl font-semibold text-primary">Welcome back</h1>
        <p className="text-sm text-slate-600">Sign in to continue.</p>
        <label className="block text-sm font-medium text-slate-700" htmlFor="email">
          Email
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="w-full rounded border border-slate-300 px-3 py-2 outline-none ring-accent-500 focus:ring"
          required
        />
        <button className="w-full rounded bg-primary px-4 py-2 font-semibold text-white hover:bg-slate-800" type="submit">
          Login
        </button>
      </form>
    </div>
  );
}
