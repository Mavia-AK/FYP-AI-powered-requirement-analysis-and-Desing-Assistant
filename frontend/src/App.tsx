import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import type { NavSection } from './components/Sidebar';
import Dashboard from './components/Dashboard';
import HistoryView from './components/HistoryView';
import LandingPage from './components/LandingPage';
import { Login, Register } from './components/AuthPages';
import AdminDashboard from './components/AdminDashboard';
import { AuthProvider, useAuth } from './context/AuthContext';
import './App.css';

const AppContent: React.FC = () => {
  const [currentRoute, setCurrentRoute] = useState<'landing' | 'login' | 'register' | 'app'>('landing');
  const [activeSection, setActiveSection] = useState<NavSection>('dashboard');
  const [restoredData, setRestoredData] = useState<any>(null);
  const { user, isAuthenticated, logout } = useAuth();

  const handleRestore = (data: any) => {
    setRestoredData(data);
    setActiveSection('dashboard');
  };

  const renderSection = () => {
    switch (activeSection) {
      case 'dashboard':
        return <Dashboard initialData={restoredData} onReset={() => setRestoredData(null)} />;
      case 'history':
        return <HistoryView onRestore={handleRestore} />;
      case 'admin':
        return user?.role === 'admin' ? <AdminDashboard /> : <Dashboard />;
      default:
        return <Dashboard />;
    }
  };

  if (currentRoute === 'landing') {
    return <LandingPage onEnterApp={() => setCurrentRoute(isAuthenticated ? 'app' : 'login')} onLogin={() => setCurrentRoute('login')} />;
  }

  if (currentRoute === 'login') {
    return <Login onSuccess={() => setCurrentRoute('app')} onSwitch={() => setCurrentRoute('register')} />;
  }

  if (currentRoute === 'register') {
    return <Register onSuccess={() => setCurrentRoute('app')} onSwitch={() => setCurrentRoute('login')} />;
  }

  return (
    <div className="main-layout animate-in">
      <Sidebar activeSection={activeSection} onSectionChange={setActiveSection} />
      
      <main className="main-content">
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          paddingBottom: '2rem', 
          marginBottom: '3rem', 
          borderBottom: '1px solid var(--border-main)' 
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
             <div style={{ width: '40px', height: '40px', background: 'var(--bg-navy)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 800 }}>
                {user?.full_name?.charAt(0) || 'U'}
             </div>
             <div>
                <div style={{ fontSize: '0.9rem', fontWeight: 800 }}>{user?.full_name || 'System User'}</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-ghost)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                   {user?.role === 'admin' ? 'Administrative Access' : 'Research Analyst'}
                </div>
             </div>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button 
              className="btn-gold" 
              style={{ padding: '0.6rem 1.5rem', fontSize: '0.85rem' }}
              onClick={() => { logout(); setCurrentRoute('landing'); }}
            >
              Sign Out
            </button>
            <button 
              className="btn" 
              style={{ padding: '0.6rem 1.5rem', fontSize: '0.85rem', border: '1px solid var(--border-main)', background: 'white' }}
              onClick={() => setCurrentRoute('landing')}
            >
              Back to Home
            </button>
          </div>
        </div>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          {renderSection()}
        </div>
      </main>
    </div>
  );
};

const App: React.FC = () => (
  <AuthProvider>
    <AppContent />
  </AuthProvider>
);

export default App;
