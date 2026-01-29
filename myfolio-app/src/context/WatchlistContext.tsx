import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { doc, updateDoc, arrayUnion, arrayRemove } from 'firebase/firestore';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { db } from '../config/firebase';
import { useAuth } from './AuthContext';
import { getWatchlistLimit } from '../config/pricing';

interface TickerData {
  symbol: string;
  name?: string;
  price?: number;
  change?: number;
  changePercent?: number;
  convictionScore?: number;
  addedAt: Date;
}

interface WatchlistContextType {
  watchlist: TickerData[];
  loading: boolean;
  addTicker: (symbol: string) => Promise<boolean>;
  removeTicker: (symbol: string) => Promise<void>;
  canAddMore: boolean;
  watchlistLimit: number;
}

const WatchlistContext = createContext<WatchlistContextType | undefined>(undefined);

const WATCHLIST_STORAGE_KEY = '@myfolio_watchlist';

export function WatchlistProvider({ children }: { children: ReactNode }) {
  const { user, profile } = useAuth();
  const [watchlist, setWatchlist] = useState<TickerData[]>([]);
  const [loading, setLoading] = useState(true);

  const watchlistLimit = profile ? getWatchlistLimit(profile.tier) : 5;
  const canAddMore = watchlist.length < watchlistLimit;

  // Load watchlist on mount
  useEffect(() => {
    loadWatchlist();
  }, [user, profile]);

  const loadWatchlist = async () => {
    setLoading(true);
    try {
      if (profile?.watchlist) {
        // Convert string array to TickerData array
        const tickerData: TickerData[] = profile.watchlist.map((symbol) => ({
          symbol: symbol.toUpperCase(),
          addedAt: new Date(),
        }));
        setWatchlist(tickerData);
      } else {
        // Load from local storage for non-authenticated users
        const stored = await AsyncStorage.getItem(WATCHLIST_STORAGE_KEY);
        if (stored) {
          setWatchlist(JSON.parse(stored));
        }
      }
    } catch (error) {
      console.error('Error loading watchlist:', error);
    }
    setLoading(false);
  };

  const addTicker = async (symbol: string): Promise<boolean> => {
    const upperSymbol = symbol.toUpperCase().trim();

    // Check if already exists
    if (watchlist.some((t) => t.symbol === upperSymbol)) {
      return false;
    }

    // Check limit
    if (!canAddMore) {
      return false;
    }

    const newTicker: TickerData = {
      symbol: upperSymbol,
      addedAt: new Date(),
    };

    const updatedWatchlist = [...watchlist, newTicker];
    setWatchlist(updatedWatchlist);

    // Persist to Firebase or local storage
    if (user && profile) {
      await updateDoc(doc(db, 'users', user.uid), {
        watchlist: arrayUnion(upperSymbol),
      });
    } else {
      await AsyncStorage.setItem(WATCHLIST_STORAGE_KEY, JSON.stringify(updatedWatchlist));
    }

    return true;
  };

  const removeTicker = async (symbol: string): Promise<void> => {
    const upperSymbol = symbol.toUpperCase();
    const updatedWatchlist = watchlist.filter((t) => t.symbol !== upperSymbol);
    setWatchlist(updatedWatchlist);

    if (user && profile) {
      await updateDoc(doc(db, 'users', user.uid), {
        watchlist: arrayRemove(upperSymbol),
      });
    } else {
      await AsyncStorage.setItem(WATCHLIST_STORAGE_KEY, JSON.stringify(updatedWatchlist));
    }
  };

  return (
    <WatchlistContext.Provider
      value={{
        watchlist,
        loading,
        addTicker,
        removeTicker,
        canAddMore,
        watchlistLimit,
      }}
    >
      {children}
    </WatchlistContext.Provider>
  );
}

export function useWatchlist() {
  const context = useContext(WatchlistContext);
  if (context === undefined) {
    throw new Error('useWatchlist must be used within a WatchlistProvider');
  }
  return context;
}
