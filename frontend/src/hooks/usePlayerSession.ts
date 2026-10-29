"use client";
import { useEffect, useState } from "react";
export function usePlayerSession() {
  const [id, setId] = useState("");
  useEffect(() => {
    let id = localStorage.getItem("sinbad-player-id");
    if (!id) { id = crypto.randomUUID(); localStorage.setItem("sinbad-player-id", id); }
    setId(id);
  }, []);
  return id;
}
