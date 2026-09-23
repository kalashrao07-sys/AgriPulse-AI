import React, { createContext, useContext, useState, useCallback } from 'react';
import type { FarmData } from '../types';
import { farmApi } from '../api/client';

interface FarmContextType {
  farm: FarmData | null;
  loading: boolean;
  error: string | null;
  loadDemoFarm: () => Promise<void>;
  setFarm: (farm: FarmData) => void;
}

const FarmContext = createContext<FarmContextType | null>(null);

export const FarmProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [farm, setFarm] = useState<FarmData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDemoFarm = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await farmApi.loadDemo();
      setFarm(data);
    } catch (e) {
      setError('Could not load demo farm. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <FarmContext.Provider value={{ farm, loading, error, loadDemoFarm, setFarm }}>
      {children}
    </FarmContext.Provider>
  );
};

export const useFarm = () => {
  const ctx = useContext(FarmContext);
  if (!ctx) throw new Error('useFarm must be used within FarmProvider');
  return ctx;
};
