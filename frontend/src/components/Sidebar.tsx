import React from 'react';
import { LayoutDashboard, History, Settings, Cpu, ShieldCheck, UserCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export type NavSection = 'dashboard' | 'history' | 'admin' | 'settings';

interface SidebarProps {
  activeSection: NavSection;
  onSectionChange: (section: NavSection) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeSection, onSectionChange }) => {
  const { user } = useAuth();
  
  const menuItems = [
    { id: 'dashboard', label: 'Requirement Analysis', icon: <LayoutDashboard size={20} /> },
    { id: 'history', label: 'Analysis Archive', icon: <History size={20} /> },
  ];

  if (user?.role === 'admin') {
    menuItems.push({ id: 'admin', label: 'Site Governance', icon: <ShieldCheck size={20} /> });
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-logo" style={{ marginBottom: '4rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{ 
          width: '40px', height: '40px', background: 'var(--accent-gold)', 
          borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <Cpu size={24} color="#000" />
        </div>
        <span style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-1px' }}>AI-RADA</span>
      </div>

      <nav style={{ flex: 1 }}>
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {menuItems.map((item) => (
            <li
              key={item.id}
              className={`nav-item ${activeSection === item.id ? 'active' : ''}`}
              onClick={() => onSectionChange(item.id as NavSection)}
              style={{ 
                display: 'flex', alignItems: 'center', gap: '1rem', 
                padding: '1rem 1.25rem', borderRadius: '12px', cursor: 'pointer',
                fontWeight: 600, fontSize: '0.9rem'
              }}
            >
              {item.icon}
              {item.label}
            </li>
          ))}
        </ul>
      </nav>

      <div className="sidebar-footer" style={{ borderTop: '1px solid var(--border-navy)', paddingTop: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'rgba(255,255,255,0.4)', fontSize: '0.85rem', fontWeight: 600 }}>
          <UserCircle size={18} /> {user?.email}
        </div>
        <div style={{ marginTop: '1rem', fontSize: '0.7rem', color: 'rgba(255,255,255,0.2)', fontWeight: 800, letterSpacing: '0.1em' }}>
          v2.5.0 STABLE
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
