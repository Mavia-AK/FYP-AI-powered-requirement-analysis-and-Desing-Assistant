import React, { useState, useEffect } from 'react';
import { 
  Users, Activity, AlertTriangle, ShieldCheck, Trash2, 
  RefreshCcw, Search, BarChart3, Clock, Database 
} from 'lucide-react';

interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: number;
}

interface Stats {
  total_users: number;
  total_requests: number;
  error_rate: number;
  avg_latency: number;
}

const AdminDashboard: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [usersRes, statsRes] = await Promise.all([
        fetch('http://localhost:8000/api/admin/users'),
        fetch('http://localhost:8000/api/admin/stats')
      ]);
      setUsers(await usersRes.json());
      setStats(await statsRes.json());
    } catch (err) {
      console.error('Admin data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const deleteUser = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    try {
      await fetch(`http://localhost:8000/api/admin/users/${id}`, { method: 'DELETE' });
      fetchData();
    } catch (err) {
      console.error('Delete user error:', err);
    }
  };

  const formatLatency = (ms: number) => {
    if (ms > 1000) return `${(ms / 1000).toFixed(2)}s`;
    return `${ms.toFixed(1)}ms`;
  };

  return (
    <div className="animate-up">
      <header style={{ marginBottom: '4rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <div style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--accent-gold)', textTransform: 'uppercase', letterSpacing: '0.2em', marginBottom: '0.5rem' }}>
            Infrastructure & Governance
          </div>
          <h1 style={{ fontSize: '3.5rem', fontWeight: 800, letterSpacing: '-0.04em' }}>Site Governance</h1>
        </div>
        <button className="btn-gold" onClick={fetchData} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.8rem 1.5rem' }}>
          {loading ? <RefreshCcw size={18} className="spin" /> : <RefreshCcw size={18} />} 
          REFRESH METRICS
        </button>
      </header>

      {/* Stats Grid */}
      <div className="grid-4" style={{ marginBottom: '4rem', gap: '1.5rem' }}>
        <AdminStat 
          icon={<Users size={22}/>} 
          label="Total Users" 
          value={stats?.total_users || 0} 
          sub="Registered accounts"
        />
        <AdminStat 
          icon={<Activity size={22}/>} 
          label="Total Requests" 
          value={stats?.total_requests || 0} 
          sub="Pipeline executions"
        />
        <AdminStat 
          icon={<Clock size={22}/>} 
          label="Avg Latency" 
          value={formatLatency(stats?.avg_latency || 0)} 
          color="var(--accent-blue)" 
          sub="Neural processing time"
        />
        <AdminStat 
          icon={<AlertTriangle size={22}/>} 
          label="Error Rate" 
          value={`${stats?.error_rate || 0}%`} 
          color={stats?.error_rate && stats.error_rate > 5 ? '#ef4444' : '#10b981'} 
          sub="System reliability"
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '3rem' }}>
        {/* User Management */}
        <section className="card" style={{ padding: '0' }}>
          <div style={{ padding: '2rem', borderBottom: '1px solid var(--border-main)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <ShieldCheck size={20} color="var(--accent-gold)" /> User Registry
            </h3>
            <div style={{ position: 'relative' }}>
               <Search size={16} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-ghost)' }} />
               <input type="text" placeholder="Filter users..." style={{ padding: '0.5rem 1rem 0.5rem 2.5rem', borderRadius: '8px', border: '1px solid var(--border-main)', fontSize: '0.9rem' }} />
            </div>
          </div>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Full Name</th>
                  <th>Email Address</th>
                  <th>Role</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(user => (
                  <tr key={user.id}>
                    <td style={{ fontWeight: 800, color: 'var(--text-ghost)' }}>#{user.id}</td>
                    <td style={{ fontWeight: 700 }}>{user.full_name}</td>
                    <td>{user.email}</td>
                    <td>
                      <span className={`badge ${user.role === 'admin' ? 'badge-warning' : 'badge-primary'}`}>
                        {user.role.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <button 
                        onClick={() => deleteUser(user.id)}
                        style={{ background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer' }}
                      >
                        <Trash2 size={18} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Site Health */}
        <aside>
          <div className="card" style={{ background: 'var(--bg-navy)', color: 'white', border: 'none' }}>
             <h3 style={{ color: 'white', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <BarChart3 size={20} color="var(--accent-gold)" /> Infrastructure Health
             </h3>
             <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <HealthItem label="Database Engine" status="Healthy" />
                <HealthItem label="BERT Inference Core" status="Active" />
                <HealthItem label="Gemini Reasoning Node" status="Connected" />
                <HealthItem label="UML Synthesis Core" status="Standby" />
             </div>
             <div style={{ marginTop: '3rem', padding: '1.5rem', background: 'rgba(255,255,255,0.05)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.8rem', fontWeight: 800, color: 'var(--accent-gold)', marginBottom: '0.5rem' }}>
                   <Database size={14} /> PERSISTENCE LAYER
                </div>
                <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.5)' }}>SQLite v3.45.0 (airada.db)</div>
             </div>
          </div>
        </aside>
      </div>
    </div>
  );
};

const AdminStat = ({ icon, label, value, color, sub }: any) => (
  <div className="card" style={{ padding: '2.5rem', display: 'flex', flexDirection: 'column', border: '1px solid #f1f5f9', boxShadow: '0 10px 30px rgba(0,0,0,0.02)' }}>
    <div style={{ color: color || 'var(--bg-navy)', marginBottom: '1.5rem', background: '#f8fafc', width: '44px', height: '44px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      {icon}
    </div>
    <div style={{ fontSize: '2.2rem', fontWeight: 800, marginBottom: '0.5rem', color: 'var(--text-main)' }}>{value}</div>
    <div style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-main)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.25rem' }}>{label}</div>
    <div style={{ fontSize: '0.7rem', color: 'var(--text-ghost)', fontWeight: 500 }}>{sub}</div>
  </div>
);

const HealthItem = ({ label, status }: any) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
    <span style={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)', fontWeight: 600 }}>{label}</span>
    <span style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--accent-gold)', background: 'rgba(245,179,1,0.1)', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>
      {status.toUpperCase()}
    </span>
  </div>
);

export default AdminDashboard;
