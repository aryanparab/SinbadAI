'use client';
import { signIn, signOut, useSession } from 'next-auth/react';
import { LogIn, LogOut, Loader2 } from 'lucide-react';

export default function AccountButton() {
  const { data: session, status } = useSession();
  if (status === 'loading') return <span className="sb-account-loading" aria-label="Checking sign-in"><Loader2 size={14} className="sb-spin"/></span>;
  return session ? <button className="sb-account-button" onClick={() => signOut({ callbackUrl: '/' })} title={`Sign out ${session.user?.email || ''}`}><span>{session.user?.name?.split(' ')[0] || 'Signed in'}</span><LogOut size={14}/></button> : <button className="sb-account-button" onClick={() => signIn('google', { callbackUrl: window.location.href })}><LogIn size={14}/><span>Sign in with Google</span></button>;
}
