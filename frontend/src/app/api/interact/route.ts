import { NextRequest, NextResponse } from "next/server";
export const maxDuration = 300;
export async function POST(req: NextRequest) {
  try {
    const base = (process.env.BACKEND_URL || "http://127.0.0.1:8000").replace(/\/game\/(init|interact)\/?$/, "").replace(/\/$/, "");
    const response = await fetch(`${base}/game/interact`, {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify(await req.json()), signal: AbortSignal.timeout(240000), cache: "no-store"
    });
    return NextResponse.json(await response.json(), {status: response.status});
  } catch {
    return NextResponse.json({detail: "The connection was interrupted. Refresh to recover the latest save before retrying."}, {status: 502});
  }
}
