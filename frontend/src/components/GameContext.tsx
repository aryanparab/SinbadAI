'use client';

import { createContext, useContext, useState } from 'react';

type GameData = {
  worldName?: string;
  loaded?: any; // use proper type if available
};

type GameContextType = {
  gameData: GameData | null;
  setGameData: (data: GameData) => void;
};

const GameContext = createContext<GameContextType | undefined>(undefined);

export const GameProvider = ({ children }: { children: React.ReactNode }) => {
  const [gameData, setGameData] = useState<GameData | null>(null);

  return (
    <GameContext.Provider value={{ gameData, setGameData }}>
      {children}
    </GameContext.Provider>
  );
};

export const useGameContext = () => {
  const context = useContext(GameContext);
  if (!context) throw new Error('useGameContext must be used within GameProvider');
  return context;
};
