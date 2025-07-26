import './globals.css';
import type { Metadata } from 'next';
import { getServerSession } from 'next-auth';
import { authOptions } from './api/auth/[...nextauth]/route';
import SessionProviderWrapper from '@/components/SessionProviderWrapper';
import Navbar from '@/components/Navbar'; // ✅ Import Navbar
import { GameProvider } from '@/components/GameContext'; 

export const metadata: Metadata = {
  title: 'RPG Game',
  description: 'Immersive RPG game powered by AI',
};

// ✅ Import here

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const session = await getServerSession(authOptions);

  return (
    <html lang="en">
      <body>
        <SessionProviderWrapper session={session}>
          <GameProvider> {/* ✅ Now your context wraps the app */}
            <Navbar />
            {children}
          </GameProvider>
        </SessionProviderWrapper>
      </body>
    </html>
  );
}
