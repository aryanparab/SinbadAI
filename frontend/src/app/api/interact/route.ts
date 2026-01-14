// ✅ New App Router format
import { NextRequest, NextResponse } from 'next/server';
import { stringify } from 'querystring';

export async function POST(req: NextRequest) {
  try {
    const data = await req.json();
    
    // DEBUG: Log what's being sent
    console.log("=== FRONTEND DEBUG: API/interact request ===");
    console.log("session_id:", data.session_id);
    console.log("player_choice:", data.player_choice);
    console.log("scene_tag:", data.scene_tag);
    console.log("location:", data.current_location);
    console.log("world:", data.current_world);
    console.log("==========================================");

    // Use local backend for development
    let use_path = process.env.BACKEND_URL || "http://localhost:8000/game/interact";
    console.log("Backend URL:", use_path);

    // Your existing backend logic here (send data to FastAPI or run logic)
    const response = await fetch(use_path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    // DEBUG: Log response status
    console.log("=== BACKEND RESPONSE STATUS ===");
    console.log("Status:", response.status, response.statusText);
    console.log("=============================");

    // Get response text first for debugging
    const responseText = await response.text();
    console.log("=== RAW BACKEND RESPONSE ===");
    console.log("Response length:", responseText.length);
    console.log("Response preview:", responseText.substring(0, 500) + "...");
    console.log("===========================");

    if (!response.ok) {
      console.error("❌ Backend returned error:", response.status, responseText);
      return NextResponse.json({ 
        error: 'Backend error', 
        status: response.status,
        details: responseText 
      }, { status: 500 });
    }

    // Parse JSON
    let result;
    try {
      result = JSON.parse(responseText);
    } catch (e) {
      console.error("❌ Failed to parse JSON response:", e);
      return NextResponse.json({ 
        error: 'Invalid JSON from backend',
        raw_response: responseText
      }, { status: 500 });
    }

    // DEBUG: Log parsed response structure
    console.log("=== PARSED RESPONSE STRUCTURE ===");
    console.log("scene_tag:", result.scene_tag);
    console.log("location:", result.location);
    console.log("world:", result.world);
    console.log("has_game_state:", !!result.game_state);
    console.log("has_narration_text:", !!result.narration_text);
    console.log("================================");

    // Validate required fields before sending to frontend
    const requiredFields = ['scene_tag', 'location', 'world'];
    const missingFields = requiredFields.filter(field => !result[field]);
    
    if (missingFields.length > 0) {
      console.error("❌ Missing required fields in backend response:", missingFields);
      console.error("Full response:", JSON.stringify(result, null, 2));
    }

    return NextResponse.json(result);

  } catch (error) {
    console.error("❌ Error in /api/interact:", error);
    return NextResponse.json({ error: 'Failed to process interaction', message: String(error) }, { status: 500 });
  }
}
