import React, { createContext, useContext, useState, useCallback } from 'react';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [streakData, setStreakData] = useState({ current_streak: 0, longest_streak: 0 });
  const [totalXP, setTotalXP] = useState(0);

  const refresh = useCallback(() => {
    setRefreshTrigger(prev => prev + 1);
  }, []);

  const navigateToDate = useCallback((date) => {
    setCurrentDate(new Date(date));
  }, []);

  const value = {
    currentDate,
    setCurrentDate,
    refreshTrigger,
    refresh,
    streakData,
    setStreakData,
    totalXP,
    setTotalXP,
    navigateToDate,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
}

export default AppContext;