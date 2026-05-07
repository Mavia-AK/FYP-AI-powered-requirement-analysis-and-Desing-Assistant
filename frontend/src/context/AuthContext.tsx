import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  email: string;
  role: 'user' | 'admin';
  full_name: string;
  token: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, full_name: string, role: string, token: string) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('airada_user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const login = (email: string, full_name: string, role: string, token: string) => {
    const userData: User = { email, full_name, role: role as any, token };
    setUser(userData);
    localStorage.setItem('airada_user', JSON.stringify(userData));
    localStorage.setItem('airada_token', token);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('airada_user');
    localStorage.removeItem('airada_token');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
