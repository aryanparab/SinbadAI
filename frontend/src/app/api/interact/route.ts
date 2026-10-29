import { NextRequest } from 'next/server';
import { proxyGameRequest } from '@/lib/backendProxy';
export const maxDuration = 300;
export async function POST(req: NextRequest) {
  return proxyGameRequest(req, 'interact');
}
