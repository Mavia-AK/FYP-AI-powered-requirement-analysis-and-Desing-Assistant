import React, { useState, useEffect } from 'react';
import { Clock, Trash2, Calendar, FileText, ChevronRight, Inbox } from 'lucide-react';
import type { AnalysisResponse } from '../services/api';

interface HistoryEntry {
  id: number;
  timestamp: string;
  title: string;
  summary: any;
  data: AnalysisResponse;
}

interface HistoryViewProps {
  onRestore: (data: AnalysisResponse) => void;
}

const HistoryView: React.FC<HistoryViewProps> = ({ onRestore }) => {
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  useEffect(() => {
    const saved = JSON.parse(localStorage.getItem('ai_rada_history') || '[]');
    setHistory(saved);
  }, []);

  const deleteEntry = (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    const updated = history.filter(item => item.id !== id);
    setHistory(updated);
    localStorage.setItem('ai_rada_history', JSON.stringify(updated));
  };

  const formatDate = (iso: string) => {
    return new Date(iso).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="animate-up">
      <header style={{ marginBottom: '4rem' }}>
        <div style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--accent-gold)', textTransform: 'uppercase', letterSpacing: '0.2em', marginBottom: '0.75rem' }}>
          Archived Sessions
        </div>
        <h1 style={{ fontSize: '3.5rem', fontWeight: 800, letterSpacing: '-0.04em' }}>Analysis Archive</h1>
        <p style={{ color: 'var(--text-sub)', fontSize: '1.1rem' }}>Access and restore previously analyzed requirements.</p>
      </header>

      {history.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '8rem 2rem', border: '2px dashed var(--border-main)', background: 'transparent' }}>
          <div style={{ width: '80px', height: '80px', background: '#f8fafc', borderRadius: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 2rem' }}>
            <Inbox size={40} color="var(--text-ghost)" />
          </div>
          <h3 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '0.75rem' }}>Archive Empty</h3>
          <p style={{ color: 'var(--text-sub)', maxWidth: '400px', margin: '0 auto' }}>
            Start your first requirement analysis to populate this archive with historical data.
          </p>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '1.5rem' }}>
          {history.map((entry) => (
            <div 
              key={entry.id} 
              className="card history-card" 
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                padding: '2rem 3rem',
                cursor: 'pointer',
                margin: 0,
                transition: 'all 0.2s',
                border: '1px solid #f1f5f9'
              }}
              onClick={() => onRestore(entry.data)}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                <div style={{ 
                  width: '56px', 
                  height: '56px', 
                  borderRadius: '16px', 
                  backgroundColor: 'var(--bg-navy)', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  color: 'var(--accent-gold)'
                }}>
                  <FileText size={24} />
                </div>
                <div>
                  <h4 style={{ fontSize: '1.25rem', fontWeight: 800, marginBottom: '0.5rem', color: 'var(--text-main)' }}>{entry.title}</h4>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '2rem', color: 'var(--text-ghost)', fontSize: '0.85rem', fontWeight: 700 }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Calendar size={14} /> {formatDate(entry.timestamp)}
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Clock size={14} /> {entry.summary ? entry.summary['Total Requirements'] : 0} STATEMENTS
                    </span>
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
                <button className="btn-gold" style={{ padding: '0.8rem 2rem', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  RESTORE SESSION <ChevronRight size={16} />
                </button>
                <button 
                  className="btn-icon"
                  style={{ 
                    padding: '0.8rem', 
                    color: 'var(--danger)', 
                    background: 'rgba(239, 68, 68, 0.05)', 
                    border: '1px solid rgba(239, 68, 68, 0.1)',
                    borderRadius: '12px',
                    cursor: 'pointer'
                  }}
                  onClick={(e) => deleteEntry(entry.id, e)}
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <style dangerouslySetInnerHTML={{ __html: `
        .history-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 20px 40px rgba(0,0,0,0.04);
          border-color: var(--accent-gold);
        }
      `}} />
    </div>
  );
};

export default HistoryView;
