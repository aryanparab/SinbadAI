'use client';

import { useAuth } from '../../lib/auth';
import { useRouter } from 'next/navigation';

export default function Navbar() {
  const { session, isLoggedIn, signIn, signOut } = useAuth();
  const router = useRouter();

  return (
    <div className="flex justify-between items-center p-4 border-b">
      <button onClick={()=> router.push("/")} ><h1  className="text-xl font-bold">Sinbad AI</h1></button>
      <div>
        {isLoggedIn ? (
          <>
            <span className="mr-4">Welcome, {session?.user?.name}</span>
            <button onClick={() => signOut()}>Logout</button>
          </>
        ) : (
          <button onClick={() => signIn("google")}>Login with Google</button>
        )}
      </div>
    </div>
  );
}
