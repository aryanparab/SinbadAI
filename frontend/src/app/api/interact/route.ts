// ✅ New App Router format
import { NextRequest, NextResponse } from 'next/server';
import { stringify } from 'querystring';

export async function POST(req: NextRequest) {
  try {
    const data = await req.json();
   
    // Your existing backend logic here (send data to FastAPI or run logic)
    const response = await fetch('http://localhost:8000/game/interact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    const result = await response.json();
    return NextResponse.json(result);

  } catch (error) {
    console.error("❌ Error in /api/interact:", error);
    return NextResponse.json({ error: 'Failed to process interaction' }, { status: 500 });
  }
}
