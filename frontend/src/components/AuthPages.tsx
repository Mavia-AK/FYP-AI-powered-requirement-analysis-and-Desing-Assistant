import React, { useState } from 'react';
import { User, Lock, LogIn, Cpu, UserPlus } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface AuthProps {
  onSuccess: () => void;
  onSwitch: () => void;
}

export const Login: React.FC<AuthProps> = ({ onSuccess, onSwitch }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username: email, password })
      });
      if (!response.ok) throw new Error('Invalid credentials');
      const data = await response.json();
      login(email, data.full_name, data.role, data.access_token);
      onSuccess();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-navy)' }}>
      <div className="card animate-up" style={{ width: '100%', maxWidth: '450px', padding: '3.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
           <div style={{ background: 'var(--accent-gold)', color: '#000', padding: '0.75rem', borderRadius: '12px', display: 'inline-block', marginBottom: '1.5rem' }}>
              <Cpu size={32} />
           </div>
           <h2 style={{ fontSize: '2rem', fontWeight: 800 }}>Welcome Back</h2>
           <p style={{ color: 'var(--text-sub)', fontSize: '0.9rem' }}>Access the AI-RADA Neural Pipeline</p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="input-group">
            <label style={{ display: 'block', marginBottom: '0.75rem', fontWeight: 800, fontSize: '0.75rem', color: 'var(--text-ghost)', textTransform: 'uppercase' }}>Email Address</label>
            <div style={{ position: 'relative' }}>
              <User size={18} style={{ position: 'absolute', left: '1.25rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-ghost)' }} />
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="textarea" style={{ paddingLeft: '3.5rem', minHeight: 'auto', padding: '1rem 1rem 1rem 3.5rem' }} />
            </div>
          </div>
          <div className="input-group">
            <label style={{ display: 'block', marginBottom: '0.75rem', fontWeight: 800, fontSize: '0.75rem', color: 'var(--text-ghost)', textTransform: 'uppercase' }}>Password</label>
            <div style={{ position: 'relative' }}>
              <Lock size={18} style={{ position: 'absolute', left: '1.25rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-ghost)' }} />
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required className="textarea" style={{ paddingLeft: '3.5rem', minHeight: 'auto', padding: '1rem 1rem 1rem 3.5rem' }} />
            </div>
          </div>

          {error && <div style={{ color: 'var(--danger)', fontSize: '0.85rem', textAlign: 'center', fontWeight: 700 }}>{error}</div>}

          <button type="submit" className="btn-gold" style={{ width: '100%', padding: '1.25rem', marginTop: '1rem' }}>
            <LogIn size={20} /> Sign In to Workspace
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '2.5rem', fontSize: '0.9rem', color: 'var(--text-sub)' }}>
          Don't have an account? <span onClick={onSwitch} style={{ color: 'var(--accent-gold)', fontWeight: 800, cursor: 'pointer' }}>Register Now</span>
        </p>
      </div>
    </div>
  );
};

export const Register: React.FC<AuthProps> = ({ onSuccess, onSwitch }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name: name })
      });
      if (!response.ok) throw new Error('Registration failed');
      const data = await response.json();
      login(email, data.full_name, data.role, data.access_token);
      onSuccess();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-navy)' }}>
      <div className="card animate-up" style={{ width: '100%', maxWidth: '450px', padding: '3.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
           <h2 style={{ fontSize: '2rem', fontWeight: 800 }}>Create Account</h2>
           <p style={{ color: 'var(--text-sub)', fontSize: '0.9rem' }}>Join the AI-RADA Research Lab</p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="input-group">
            <label style={{ display: 'block', marginBottom: '0.75rem', fontWeight: 800, fontSize: '0.75rem', color: 'var(--text-ghost)', textTransform: 'uppercase' }}>Full Name</label>
            <input type="text" value={name} onChange={(e) => setName(e.target.value)} required className="textarea" style={{ minHeight: 'auto', padding: '1rem' }} />
          </div>
          <div className="input-group">
            <label style={{ display: 'block', marginBottom: '0.75rem', fontWeight: 800, fontSize: '0.75rem', color: 'var(--text-ghost)', textTransform: 'uppercase' }}>Email Address</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="textarea" style={{ minHeight: 'auto', padding: '1rem' }} />
          </div>
          <div className="input-group">
            <label style={{ display: 'block', marginBottom: '0.75rem', fontWeight: 800, fontSize: '0.75rem', color: 'var(--text-ghost)', textTransform: 'uppercase' }}>Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required className="textarea" style={{ minHeight: 'auto', padding: '1rem' }} />
          </div>

          {error && <div style={{ color: 'var(--danger)', fontSize: '0.85rem', textAlign: 'center', fontWeight: 700 }}>{error}</div>}

          <button type="submit" className="btn-gold" style={{ width: '100%', padding: '1.25rem', marginTop: '1rem' }}>
            <UserPlus size={20} /> Initialize Account
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '2.5rem', fontSize: '0.9rem', color: 'var(--text-sub)' }}>
          Already have an account? <span onClick={onSwitch} style={{ color: 'var(--accent-gold)', fontWeight: 800, cursor: 'pointer' }}>Sign In</span>
        </p>
      </div>
    </div>
  );
};
