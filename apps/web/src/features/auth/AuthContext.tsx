import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';
import type { AppUser } from '../../types/auth';

interface AuthContextValue {
  user: AppUser | null;
  login: (email: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AppUser | null>(null);

  const value = useMemo(
    () => ({
      user,
      login: (email: string) =>
        setUser({
          id: 'stub-user-id',
          email,
          isAdmin: email.endsWith('@admin.local')
        }),
      logout: () => setUser(null)
    }),
    [user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }

  return context;
}
