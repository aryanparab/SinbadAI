import { NextRequest, NextResponse } from 'next/server';

export async function proxyGameRequest(req: NextRequest, action: 'init' | 'interact' | 'encounter') {
  const configured = process.env.BACKEND_URL?.trim();
  if (!configured && process.env.VERCEL) {
    console.error('[game-proxy] BACKEND_URL is not configured');
    return NextResponse.json({ detail: 'The game server is not configured yet. Set BACKEND_URL in Vercel and redeploy.', code: 'BACKEND_NOT_CONFIGURED' }, { status: 503 });
  }
  let base: URL;
  try {
    base = new URL((configured || 'http://127.0.0.1:8000').replace(/\/game\/(init|interact|encounter)\/?$/, '').replace(/\/$/, ''));
    if (!['http:', 'https:'].includes(base.protocol) || base.username || base.password || base.search || base.hash) throw new Error('Invalid backend origin');
  } catch {
    console.error('[game-proxy] Invalid BACKEND_URL');
    return NextResponse.json({ detail: 'The game server URL is invalid. Check BACKEND_URL in the hosting settings.', code: 'BACKEND_URL_INVALID' }, { status: 503 });
  }
  let payload;
  try { payload = await req.json(); }
  catch { return NextResponse.json({ detail: 'The action must contain valid JSON.' }, { status: 400 }); }
  try {
    const response = await fetch(`${base.toString().replace(/\/$/, '')}/game/${action}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload), signal: AbortSignal.timeout(240000), cache: 'no-store',
    });
    let data;
    try { data = await response.json(); }
    catch {
      console.error('[game-proxy] Backend returned non-JSON', { action, status: response.status });
      return NextResponse.json({ detail: 'The game server returned an unexpected response. Check its deployment and BACKEND_URL.', code: 'BACKEND_INVALID_RESPONSE' }, { status: 502 });
    }
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    const name = error instanceof Error ? error.name : 'UnknownError';
    console.error('[game-proxy] Backend request failed', { action, name });
    const timedOut = name === 'TimeoutError' || name === 'AbortError';
    return NextResponse.json({
      detail: timedOut ? 'The game server took too long to respond. Refresh to recover the latest save before retrying.' : 'The game server is unreachable. Check that the backend is running and BACKEND_URL points to its public URL. Refresh before retrying an action.',
      code: timedOut ? 'BACKEND_TIMEOUT' : 'BACKEND_UNREACHABLE',
    }, { status: timedOut ? 504 : 502 });
  }
}
