import React, { useState, useRef } from 'react';
import { Upload, Play, Trash2, AlertTriangle, FileText, Cpu, CheckCircle, ChevronRight, Activity, Terminal, Shield, Zap, Search, Layers, Globe } from 'lucide-react';
import ModuleToggles from './ModuleToggles';
import AnalysisResults from './AnalysisResults';
import { analyzeText, uploadFile } from '../services/api';
import type { AnalysisResponse } from '../services/api';

interface DashboardProps {
  initialData?: AnalysisResponse | null;
  onReset?: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ initialData, onReset }) => {
  const [inputText, setInputText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedModules, setSelectedModules] = useState<string[]>(['ambiguity', 'classification', 'uml']);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(initialData || null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleAnalyze = async () => {
    if (!inputText && !selectedFile) {
      setError('System requires input text or a specification document to initialize pipeline.');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      let result: AnalysisResponse;
      if (selectedFile) {
        result = await uploadFile(selectedFile, selectedModules);
      } else {
        result = await analyzeText(inputText, selectedModules);
      }
      setAnalysisData(result);
      
      // Save to History
      const historyEntry = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        title: selectedFile ? selectedFile.name : (inputText.slice(0, 30) + '...'),
        summary: result.summary,
        data: result
      };
      const existingHistory = JSON.parse(localStorage.getItem('ai_rada_history') || '[]');
      localStorage.setItem('ai_rada_history', JSON.stringify([historyEntry, ...existingHistory].slice(0, 20)));
    } catch (err: any) {
      setError(err.message || 'Analysis pipeline execution failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
      setInputText('');
      setError(null);
    }
  };

  return (
    <div className="dashboard-view animate-up">
      <header style={{ marginBottom: '4rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', fontWeight: 800, color: 'var(--accent-gold)', textTransform: 'uppercase', letterSpacing: '0.2em', marginBottom: '0.75rem' }}>
          <Activity size={14} /> Analysis Center
        </div>
        <h1 style={{ fontSize: '3.5rem', fontWeight: 800, letterSpacing: '-0.04em' }}>Requirement Engineering</h1>
        <p style={{ color: 'var(--text-sub)', fontSize: '1.1rem' }}>Automated requirement analysis and diagram generation.</p>
      </header>

      {!analysisData ? (
        <>
          {/* Quick Insights Row */}
          <div className="grid-3" style={{ marginBottom: '3rem', gap: '2rem' }}>
             <InsightCard 
                icon={<Search size={24} color="var(--accent-gold)"/>} 
                title="Requirement Analysis" 
                value="Operational" 
                desc="Automatic classification"
             />
             <InsightCard 
                icon={<Zap size={24} color="var(--accent-gold)"/>} 
                title="AI Reasoning" 
                value="Online" 
                desc="Smart logic refinement"
             />
             <InsightCard 
                icon={<Layers size={24} color="var(--accent-gold)"/>} 
                title="Design Generation" 
                value="Enabled" 
                desc="Automated UML construction"
             />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1.8fr 1fr', gap: '3rem' }}>
            <section className="card" style={{ padding: '3rem', border: 'none', background: 'white', display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontWeight: 800, fontSize: '1.2rem' }}>
                  <Terminal size={20} color="var(--bg-navy)" /> Requirements Input
                </div>
                <div style={{ display: 'flex', gap: '1rem', color: 'var(--text-ghost)', fontSize: '0.75rem', fontWeight: 800 }}>
                  <span>{inputText.length} CH</span>
                  <span>{inputText.split(/\s+/).filter(x => x).length} WD</span>
                </div>
              </div>

              <textarea
                className="textarea"
                placeholder="Paste your software requirements here..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                disabled={isLoading || !!selectedFile}
                style={{ minHeight: '400px', fontSize: '1rem', flex: 1 }}
              />

              <div style={{ marginTop: '2.5rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                <button 
                  className="btn-gold" 
                  onClick={handleAnalyze} 
                  disabled={isLoading || (!inputText && !selectedFile)}
                  style={{ height: '4.5rem', fontSize: '1.1rem', borderRadius: '16px', width: '100%' }}
                >
                  {isLoading ? (
                    <>
                      <div className="spinner-small" /> ANALYZING...
                    </>
                  ) : (
                    <>
                      START ANALYSIS <ChevronRight size={20} />
                    </>
                  )}
                </button>
                
                <div 
                  onClick={() => fileInputRef.current?.click()}
                  style={{ 
                    border: '2px dashed var(--border-main)', 
                    borderRadius: '16px', 
                    height: '4.5rem', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    cursor: 'pointer',
                    background: selectedFile ? 'rgba(245, 179, 1, 0.05)' : 'transparent',
                    color: selectedFile ? 'var(--accent-gold)' : 'var(--text-sub)',
                    fontWeight: 800,
                    fontSize: '0.85rem',
                    textAlign: 'center',
                    padding: '0 1rem',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}
                >
                  <Upload size={20} style={{ marginRight: '0.75rem', flexShrink: 0 }} /> 
                  {selectedFile ? selectedFile.name : 'BATCH UPLOAD'}
                </div>
                <input type="file" ref={fileInputRef} onChange={handleFileChange} style={{ display: 'none' }} />
              </div>
            </section>

            <aside>
              <div className="card" style={{ padding: '2.5rem', marginBottom: '2.5rem', background: 'var(--bg-navy)', color: 'white', border: 'none' }}>
                <div style={{ fontWeight: 800, fontSize: '1.1rem', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'white' }}>
                  <Cpu size={20} color="var(--accent-gold)" /> Analysis Modules
                </div>
                <ModuleToggles selectedModules={selectedModules} onChange={setSelectedModules} />
              </div>

              {/* Neural Architecture Card */}
              <div className="card" style={{ padding: '2.5rem', border: 'none', background: 'white', boxShadow: '0 10px 30px rgba(0,0,0,0.05)' }}>
                 <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                    <Shield size={20} color="var(--bg-navy)" />
                    <span style={{ fontWeight: 800, fontSize: '1rem' }}>System Architecture</span>
                 </div>
                 <div style={{ position: 'relative', height: '120px', background: '#f8fafc', borderRadius: '12px', overflow: 'hidden', padding: '1rem', border: '1px solid #eee' }}>
                    <div style={{ display: 'flex', gap: '1rem', height: '100%', alignItems: 'center', justifyContent: 'center' }}>
                        <div className="pulse-bar" style={{ animationDelay: '0s' }}></div>
                        <div className="pulse-bar" style={{ animationDelay: '0.2s', height: '40px' }}></div>
                        <div className="pulse-bar" style={{ animationDelay: '0.4s', height: '20px' }}></div>
                    </div>
                    <div style={{ position: 'absolute', bottom: '0.75rem', left: '0.75rem', fontSize: '0.65rem', fontWeight: 800, color: 'var(--text-ghost)', textTransform: 'uppercase' }}>
                       AI Engine: Active
                    </div>
                 </div>
                 <p style={{ marginTop: '1.5rem', fontSize: '0.85rem', color: 'var(--text-sub)', lineHeight: '1.6' }}>
                    Powered by AI models to accurately analyze your requirements.
                 </p>
              </div>

              {error && (
                <div style={{ 
                  marginTop: '2.5rem', padding: '1.5rem', borderRadius: '20px', 
                  background: 'rgba(239, 68, 68, 0.05)', color: 'var(--danger)', 
                  border: '1px solid rgba(239, 68, 68, 0.1)', fontWeight: 700,
                  display: 'flex', gap: '1rem', fontSize: '0.9rem'
                }}>
                  <AlertTriangle size={20} /> {error}
                </div>
              )}
            </aside>
          </div>
        </>
      ) : (
        <div className="animate-up">
          <div style={{ marginBottom: '3rem' }}>
            <button 
              className="btn-gold" 
              onClick={() => {
                setAnalysisData(null);
                if (onReset) onReset();
              }}
              style={{ padding: '0.8rem 2rem', borderRadius: '12px', background: 'white', border: '1px solid var(--border-main)', fontSize: '0.85rem' }}
            >
              ← BACK TO ANALYSIS CENTER
            </button>
          </div>
          <AnalysisResults data={analysisData} />
        </div>
      )}

      <style dangerouslySetInnerHTML={{ __html: `
        .spinner-small {
          width: 24px; height: 24px;
          border: 3px solid rgba(0,0,0,0.1);
          border-top-color: #000;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
          margin-right: 1rem;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .pulse-bar {
           width: 12px; height: 30px; background: var(--accent-gold); border-radius: 4px;
           animation: pulse-height 1.5s infinite ease-in-out;
        }
        @keyframes pulse-height {
           0%, 100% { height: 20px; opacity: 0.5; }
           50% { height: 50px; opacity: 1; }
        }
      `}} />
    </div>
  );
};

const InsightCard = ({ icon, title, value, desc }: any) => (
   <div className="card" style={{ padding: '1.5rem 2rem', margin: 0, display: 'flex', alignItems: 'center', gap: '1.5rem', border: '1px solid #f1f5f9' }}>
      <div style={{ 
         width: '48px', height: '48px', background: '#f8fafc', 
         borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center' 
      }}>
         {icon}
      </div>
      <div>
         <div style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--text-ghost)', textTransform: 'uppercase', marginBottom: '0.2rem' }}>{title}</div>
         <div style={{ fontSize: '1.1rem', fontWeight: 800 }}>{value}</div>
         <div style={{ fontSize: '0.75rem', color: 'var(--text-sub)', fontWeight: 500 }}>{desc}</div>
      </div>
   </div>
);

export default Dashboard;
