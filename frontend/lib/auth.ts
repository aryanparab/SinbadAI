'use client';

import { useSession, signIn, signOut } from 'next-auth/react';
import type { Session } from 'next-auth';

interface UseAuthReturn {
  session: Session | null;
  isLoggedIn: boolean;
  isLoading: boolean;
  signIn: typeof signIn;
  signOut: typeof signOut;
}

export function useAuth(): UseAuthReturn {
  const { data: session, status } = useSession();
  
  return {
    session,
    isLoggedIn: status === 'authenticated',
    isLoading: status === 'loading',
    signIn,
    signOut
  };
}