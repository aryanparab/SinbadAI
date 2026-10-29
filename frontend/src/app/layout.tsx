import './globals.css';
import './sinbad.css';
import type { Metadata } from 'next';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../lib/authOptions';
import SessionProviderWrapper from '@/components/SessionProviderWrapper';
import Navbar from '@/components/Navbar'; // ✅ Import Navbar
import { GameProvider } from '@/components/GameContext'; 

export const metadata: Metadata = {
  title: 'Sinbad AI | Your choices. A real ending.',
  description: 'Explore an AI-generated world with a planned story arc, persistent inventory, and an ending shaped by your choices.',
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
