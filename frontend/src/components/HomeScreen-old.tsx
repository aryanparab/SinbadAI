"use client";

import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useGameContext } from '@/components/GameContext';


export default function HomeScreen() {
  const { data: session } = useSession();
  const session_id = session?.user?.email || "guest_session";
  const router = useRouter();

  const [hasSavedGame, setHasSavedGame] = useState(false);
  const [loading, setLoading] = useState(true);
  const [worldName, setWorldName] = useState("");
  const [lastNarration, setLastNarration] = useState("");
  const { setGameData } = useGameContext();
  const [loaded,setLoaded] = useState<any>(null);

  useEffect(() => {
    const checkMemory = async () => {
      const res = await fetch("/api/init", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id, action: "load" }),
      });
      const data = await res.json();
      if (data.status === "loaded") {
        setHasSavedGame(true);
        setLastNarration(data.scene_state || "");
        setLoaded(data.latest_memory_data);
      }
      setLoading(false);
    };

    if (session_id) {
      checkMemory();
    }
  }, [session_id]);

  const handleNewGame = async () => {
  if (!worldName.trim()) return;

  await fetch("/api/init", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id, action: "new", world: worldName }),
  });

  localStorage.removeItem("loadedMemory"); // 🧹 clear memory on new game
  setGameData({ worldName });
  router.push("/game");
};
const handleLoadGame = () => {
  localStorage.setItem("loadedMemory", JSON.stringify(loaded)); // 👍
  setGameData({ loaded: loaded });
  router.push("/game");
};

  if (loading) return <div className="p-4">Loading...</div>;

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-900 to-black text-white p-8">
      <h1 className="text-4xl font-bold mb-6">🧙‍♂️ Welcome to Sinbad AI</h1>

      {hasSavedGame ? (
        <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full max-w-lg mb-6">
          <h2 className="text-xl font-semibold mb-2">🗂 Resume Previous Game</h2>
          <p className="text-sm text-gray-300 mb-4">
            <strong>Last memory:</strong> <br />
            {lastNarration}
          </p>
          <button
            onClick={handleLoadGame}
            className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg transition"
          >
            Load Game
          </button>
        </div>
      ) : null}

      <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full max-w-lg">
        <h2 className="text-xl font-semibold mb-2">🌍 Start New Game</h2>
        <input
          type="text"
          value={worldName}
          onChange={(e) => setWorldName(e.target.value)}
          placeholder="Enter world name (e.g. apocalypse)"
          className="w-full p-2 rounded-md mb-4 bg-gray-900 border border-gray-600 text-white"
        />
        <button
          onClick={handleNewGame}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition"
        >
          Start New Game
        </button>
      </div>
    </div>
  );
}
