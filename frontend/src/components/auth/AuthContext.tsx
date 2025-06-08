import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '@/lib/api';

interface User {
  id: number;
  email: string;
  name: string;
  is_active: boolean;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  skipAuth: () => Promise<void>;
  error: string | null;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = !!user;

  const clearError = () => setError(null);

  // Check if user is already logged in
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      fetchCurrentUser();
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const response = await apiClient.getCurrentUser();
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch current user:', error);
      apiClient.clearToken();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.login(email, password);
      
      // Fetch user data after successful login
      const userResponse = await apiClient.getCurrentUser();
      setUser(userResponse.data);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'ログインに失敗しました');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, name: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await apiClient.register(email, password, name);
      
      // Auto-login after successful registration
      await login(email, password);
    } catch (error) {
      setError(error instanceof Error ? error.message : '登録に失敗しました');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    apiClient.logout();
    setUser(null);
    setError(null);
  };

  const skipAuth = async () => {
    // When AUTH_BYPASS is enabled in backend, we can get the dev user without authentication
    setIsLoading(true);
    setError(null);
    
    try {
      // Clear any existing token first
      apiClient.clearToken();
      
      // Try to fetch current user - backend will return dev user when AUTH_BYPASS is true
      const response = await apiClient.getCurrentUser();
      setUser(response.data);
    } catch (error) {
      setError(error instanceof Error ? error.message : '接続に失敗しました');
      console.error('Failed to skip auth:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    skipAuth,
    error,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;