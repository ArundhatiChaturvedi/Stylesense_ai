import React, { createContext, useContext, useState, useEffect } from 'react';
import { styleSenseAPI, UserStatus } from '../app/services/api';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface UserContextType {
  userId: string;
  userStatus: UserStatus | null;
  isLoading: boolean;
  error: string | null;
  refreshUserStatus: () => Promise<void>;
  setUserId: (id: string) => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [userId, setUserIdState] = useState<string>('test_user'); // Default user
  const [userStatus, setUserStatus] = useState<UserStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshUserStatus = async () => {
    if (!userId) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const status = await styleSenseAPI.getUserStatus(userId);
      setUserStatus(status);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get user status');
      console.error('Error fetching user status:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const setUserId = async (id: string) => {
    setUserIdState(id);
    await AsyncStorage.setItem('user_id', id);
    setUserStatus(null);
  };

  useEffect(() => {
    const loadUserId = async () => {
      try {
        const storedUserId = await AsyncStorage.getItem('user_id');
        if (storedUserId) {
          setUserIdState(storedUserId);
        }
      } catch (err) {
        console.error('Error loading user ID:', err);
      }
    };
    
    loadUserId();
  }, []);

  useEffect(() => {
    if (userId) {
      refreshUserStatus();
    }
  }, [userId]);

  return (
    <UserContext.Provider value={{
      userId,
      userStatus,
      isLoading,
      error,
      refreshUserStatus,
      setUserId
    }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};