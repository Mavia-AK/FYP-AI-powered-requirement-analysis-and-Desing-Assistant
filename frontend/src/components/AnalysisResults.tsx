import React, { useState } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, Legend
} from 'recharts';
import { 
  AlertCircle, Download, 
  BarChart3, Layers, FileSpreadsheet, Image as ImageIcon,
  Code, Copy, Check, Info, FileText, ExternalLink, Target, Zap, Activity, Cpu
} from 'lucide-react';
import type { AnalysisResponse } from '../services/api';

interface AnalysisResultsProps {
  data: AnalysisResponse;
}

type TabType = 'overview' | 'analytics' | 'table' | 'uml';

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ data }) => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [umlSubTab, setUmlSubTab] = useState<'visual' | 'plantuml' | 'mermaid'>('visual');
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const { summary, results, uml_data } = data;

  const handleCopy = (text: string, type: string) => {
    navigator.clipboard.writeText(text);
    setCopied(type);
    setTimeout(() => setCopied(null), 2000);
  };

  const handleExport = async (format: 'pdf' | 'docx') => {
    setIsExporting(true);
    try {
      const response = await fetch(`http://localhost:8000/api/export/${format}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          results: results,
          uml_base64: uml_data?.png_base64
        })
      });
      
      if (!response.ok) throw new Error('Export failed');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `AI_RADA_Report.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert('Failed to generate export file.');
      console.error(err);
    } finally {
      setIsExporting(false);
    }
  };

  const validityData = [
    { name: 'Valid Requirements', value: summary['Valid Requirements'] },
    { name: 'Redundant/Invalid Noise', value: summary['Invalid Requirements'] },
  ];

  return (
    <div className="results-container animate-in">
      {/* Floating Glass Navigation */}
      <div className="tab-group" style={{ 
        marginBottom: '4rem', padding: '0.6rem', 
        background: 'white', border: '1px solid var(--border-main)',
        boxShadow: 'var(--shadow-soft)', borderRadius: '16px'
      }}>
        <button className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>
          <Activity size={18} /> Executive Summary
        </button>
        <button className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`} onClick={() => setActiveTab('analytics')}>
          <BarChart3 size={18} /> Neural Metrics
        </button>
        <button className={`tab-btn ${activeTab === 'table' ? 'active' : ''}`} onClick={() => setActiveTab('table')}>
          <FileText size={18} /> Detailed Audit
        </button>
        {uml_data?.png_base64 && (
          <button className={`tab-btn ${activeTab === 'uml' ? 'active' : ''}`} onClick={() => setActiveTab('uml')}>
            <ImageIcon size={18} /> Architecture Model
          </button>
        )}
      </div>

      <div className="tab-content">
        {activeTab === 'overview' && (
          <div className="animate-in">
          <div className="grid-4" style={{ marginBottom: '4rem', gap: '1.5rem' }}>
            <ResultStat 
              icon={<FileText size={22}/>} 
              label="Total Volume" 
              value={summary['Total Requirements']} 
              sub="Total Requirements Processed"
            />
            <ResultStat 
              icon={<Target size={22}/>} 
              label="Valid Baseline" 
              value={summary['Valid Requirements']} 
              color="var(--accent-blue)"
              sub="Valid Requirements"
            />
            <ResultStat 
              icon={<Zap size={22}/>} 
              label="Quality Score" 
              value={summary['Average RQI Score'] || 0} 
              color="var(--accent-gold)"
              sub="Avg Requirement Quality"
            />
            <ResultStat 
              icon={<AlertCircle size={22}/>} 
              label="Noise Level" 
              value={summary['Invalid Requirements']} 
              color="#ef4444"
              sub="Invalid Requirements"
            />
          </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '3rem' }}>
              <div className="card" style={{ padding: '3rem', display: 'flex', flexDirection: 'column' }}>
                <h3 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '2rem', letterSpacing: '-0.02em' }}>Analysis Summary</h3>
                <div style={{ color: 'var(--text-sub)', fontSize: '1.05rem', lineHeight: '1.8', flex: 1 }}>
                  <p style={{ marginBottom: '1.5rem' }}>
                    The system has successfully analyzed <strong>{summary['Total Requirements']}</strong> requirements. 
                    The accuracy of this document is <strong style={{ color: 'var(--text-main)' }}>{((summary['Valid Requirements'] / summary['Total Requirements']) * 100).toFixed(1)}%</strong>.
                  </p>
                  <p style={{ marginBottom: '3rem' }}>
                    Found <strong style={{ color: 'var(--accent-gold)' }}>{summary['Ambiguous Requirements'] || 0}</strong> ambiguous statements that need to be clarified.
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '1.5rem', position: 'relative' }}>
                  <button 
                    className="btn-gold" 
                    onClick={() => setShowExportMenu(!showExportMenu)}
                    disabled={isExporting}
                    style={{ flex: 1, height: '3.5rem', borderRadius: '12px', fontSize: '0.9rem' }}
                  >
                    {isExporting ? <span className="spinner-small" style={{ borderColor: 'rgba(0,0,0,0.2)', borderTopColor: '#000', width: 16, height: 16, display: 'inline-block', marginRight: '0.5rem', verticalAlign: 'middle' }}></span> : <Download size={18} style={{ marginRight: '0.5rem' }}/>}
                    {isExporting ? 'GENERATING...' : 'EXPORT REPORT'}
                  </button>
                  {showExportMenu && (
                    <div style={{ position: 'absolute', top: '110%', left: 0, width: 'calc(50% - 0.75rem)', background: 'white', borderRadius: '12px', boxShadow: 'var(--shadow-float)', border: '1px solid var(--border-main)', zIndex: 10, overflow: 'hidden' }}>
                      <div className="export-option" onClick={() => { handleExport('pdf'); setShowExportMenu(false); }} style={{ padding: '1rem', cursor: 'pointer', borderBottom: '1px solid var(--border-main)', fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                        <FileText size={16} style={{ marginRight: '0.5rem' }} /> Export as PDF
                      </div>
                      <div className="export-option" onClick={() => { handleExport('docx'); setShowExportMenu(false); }} style={{ padding: '1rem', cursor: 'pointer', fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                        <FileText size={16} style={{ marginRight: '0.5rem' }} /> Export as Word (.docx)
                      </div>
                    </div>
                  )}
                  <button 
                    className="btn-gold" 
                    onClick={() => {
                      navigator.clipboard.writeText(window.location.href);
                      alert('Shareable dashboard link copied to clipboard!');
                    }}
                    style={{ flex: 1, height: '3.5rem', borderRadius: '12px', fontSize: '0.9rem', background: 'transparent', border: '2px solid var(--accent-gold)', color: 'var(--accent-gold)' }}
                  >
                    <ExternalLink size={18} style={{ marginRight: '0.5rem' }}/> SHARE DASHBOARD
                  </button>
                </div>
              </div>
              <div className="card" style={{ padding: '3rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <h3 style={{ width: '100%', fontSize: '1.4rem', fontWeight: 800, marginBottom: '2rem' }}>Project Health</h3>
                <div style={{ width: '100%', height: 320, position: 'relative' }}>
                  <ResponsiveContainer>
                    <PieChart>
                      <Pie 
                        data={validityData} cx="50%" cy="50%" 
                        innerRadius={85} outerRadius={115} 
                        paddingAngle={8} dataKey="value" stroke="none"
                        animationBegin={0} animationDuration={1000}
                      >
                        <Cell fill="var(--bg-navy)" />
                        <Cell fill="#f1f5f9" />
                      </Pie>
                      <Tooltip 
                        contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 40px rgba(0,0,0,0.1)', fontWeight: 700 }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                  <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center', pointerEvents: 'none' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--bg-navy)' }}>
                      {((summary['Valid Requirements'] / summary['Total Requirements']) * 100).toFixed(0)}%
                    </div>
                    <div style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--text-ghost)', textTransform: 'uppercase' }}>Verified</div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '2.5rem', marginTop: '1rem' }}>
                  <LegendItem label="Valid" color="var(--bg-navy)" />
                  <LegendItem label="Invalid" color="#f1f5f9" />
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="animate-in grid-2">
            <div className="card">
              <h3 className="card-title">Structural Taxonomy (FR/NFR)</h3>
              <div style={{ height: 400 }}>
                <ResponsiveContainer>
                  <BarChart data={[
                    { name: 'Functional (FR)', count: summary['Functional (FR)'] },
                    { name: 'Non-Functional (NFR)', count: summary['Non-Functional (NFR)'] }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-main)" />
                    <XAxis dataKey="name" stroke="var(--text-ghost)" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="var(--text-ghost)" fontSize={12} tickLine={false} axisLine={false} />
                    <Tooltip cursor={{ fill: 'var(--bg-sub)' }} />
                    <Bar dataKey="count" fill="var(--text-main)" radius={[8, 8, 0, 0]} barSize={80} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="card">
              <h3 className="card-title">Quality Distribution Profile</h3>
              <div style={{ height: 400 }}>
                <ResponsiveContainer>
                  <PieChart>
                    <Pie data={[
                      { name: 'Pristine/Clear', value: summary['Clear Requirements'] },
                      { name: 'Vulnerable/Ambiguous', value: summary['Ambiguous Requirements'] }
                    ]} cx="50%" cy="50%" innerRadius={100} outerRadius={130} paddingAngle={5} dataKey="value" stroke="none">
                      <Cell fill="var(--accent-primary)" />
                      <Cell fill="var(--accent-secondary)" />
                    </Pie>
                    <Tooltip />
                    <Legend verticalAlign="bottom" height={36} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'table' && (
          <div className="animate-in card" style={{ padding: '0' }}>
            <div className="table-container" style={{ maxHeight: '750px' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th style={{ width: '100px' }}>UUID</th>
                    <th>Requirement Specification</th>
                    <th style={{ width: '180px' }}>Requirement Type</th>
                    <th style={{ width: '140px' }}>Ambiguity</th>
                    <th>Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((item, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: 800, color: 'var(--accent-primary)', fontSize: '0.85rem' }}>
                        ID-{item['#'].toString().padStart(4, '0')}
                      </td>
                      <td style={{ maxWidth: '400px', fontWeight: 600, color: 'var(--text-main)', paddingRight: '2rem' }}>
                        {item['Requirement']}
                      </td>
                      <td>
                        {item['Type'] ? (
                          <span className={`badge ${item['Type'].includes('NFR') ? 'badge-blue' : 'badge-gold'}`} style={{ width: 'fit-content', borderRadius: '6px', fontSize: '0.75rem' }}>
                            {item['Type']}
                          </span>
                        ) : <span style={{ color: 'var(--text-ghost)', fontSize: '0.85rem' }}>N/A</span>}
                      </td>
                      <td>
                        {item['Ambiguity'] ? (
                          <span className={`badge ${item['Ambiguity'] === 'Clear' ? 'badge-success' : 'badge-danger'}`} style={{ width: 'fit-content', borderRadius: '6px', fontSize: '0.75rem' }}>
                            {item['Ambiguity']}
                          </span>
                        ) : <span style={{ color: 'var(--text-ghost)', fontSize: '0.85rem' }}>N/A</span>}
                      </td>
                      <td>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-sub)', background: 'var(--bg-sub)', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid var(--border-main)', lineHeight: '1.4' }}>
                          {item['Reason'] || item['Val. Reason'] || 'No reason provided.'}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'uml' && uml_data?.png_base64 && (
          <div className="animate-in card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem' }}>
              <div>
                <h3 className="card-title" style={{ marginBottom: '0.5rem' }}>Architectural Model</h3>
                <p style={{ color: 'var(--text-ghost)', fontSize: '0.9rem', fontWeight: 600 }}>Extracted from optimized requirement clusters.</p>
              </div>
              <div className="tab-group">
                <button className={`tab-btn ${umlSubTab === 'visual' ? 'active' : ''}`} onClick={() => setUmlSubTab('visual')}>Diagram View</button>
                <button className={`tab-btn ${umlSubTab === 'plantuml' ? 'active' : ''}`} onClick={() => setUmlSubTab('plantuml')}>PlantUML</button>
                <button className={`tab-btn ${umlSubTab === 'mermaid' ? 'active' : ''}`} onClick={() => setUmlSubTab('mermaid')}>Mermaid</button>
              </div>
            </div>

            <div style={{ background: 'var(--bg-sub)', borderRadius: '24px', padding: '3rem', border: '1px solid var(--border-main)' }}>
              {umlSubTab === 'visual' && (
                <div style={{ textAlign: 'center' }}>
                  <div style={{ background: 'white', padding: '2rem', borderRadius: '16px', boxShadow: 'var(--shadow-float)', display: 'inline-block' }}>
                    <img src={`data:image/png;base64,${uml_data.png_base64}`} alt="System Architecture" style={{ maxWidth: '100%', maxHeight: '650px', width: 'auto', height: 'auto', objectFit: 'contain' }} />
                  </div>
                  <div style={{ marginTop: '3rem' }}>
                    <button className="btn-gold" onClick={() => {
                      const link = document.createElement('a'); link.href = `data:image/png;base64,${uml_data.png_base64}`;
                      link.download = 'ai-rada-architecture.png'; link.click();
                    }} style={{ borderRadius: '12px', padding: '0.8rem 2rem', fontSize: '0.9rem' }}>
                      <Download size={18} style={{ marginRight: '0.5rem' }}/> EXPORT VECTOR ASSET
                    </button>
                  </div>
                </div>
              )}
              {(umlSubTab === 'plantuml' || umlSubTab === 'mermaid') && (
                <div style={{ position: 'relative' }}>
                  <button className="btn btn-outline" style={{ position: 'absolute', top: '1.5rem', right: '1.5rem', fontSize: '0.8rem', background: 'white', border: 'none', boxShadow: 'var(--shadow-soft)' }} onClick={() => handleCopy(umlSubTab === 'plantuml' ? uml_data.plantuml : uml_data.mermaid, umlSubTab)}>
                    {copied === umlSubTab ? <Check size={16} color="var(--accent-primary)"/> : <Copy size={16}/>} {copied === umlSubTab ? 'Copied' : 'Copy Engine Code'}
                  </button>
                  <pre style={{ background: '#0f172a', color: '#f1f5f9', padding: '4rem 2.5rem', borderRadius: '16px', overflowX: 'auto', fontSize: '1rem', lineHeight: '1.7', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <code>{umlSubTab === 'plantuml' ? uml_data.plantuml : uml_data.mermaid}</code>
                  </pre>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const ResultStat = ({ icon, label, value, color, sub }: any) => (
  <div className="card" style={{ padding: '2.5rem', display: 'flex', flexDirection: 'column', border: '1px solid #f1f5f9', boxShadow: '0 10px 30px rgba(0,0,0,0.02)' }}>
    <div style={{ color: color || 'var(--bg-navy)', marginBottom: '1.5rem', background: '#f8fafc', width: '44px', height: '44px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      {icon}
    </div>
    <div style={{ fontSize: '2.2rem', fontWeight: 800, marginBottom: '0.5rem', color: 'var(--text-main)' }}>{value}</div>
    <div style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-main)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.25rem' }}>{label}</div>
    <div style={{ fontSize: '0.7rem', color: 'var(--text-ghost)', fontWeight: 500 }}>{sub}</div>
  </div>
);

const LegendItem = ({ label, color }: any) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-sub)' }}>
    <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: color }}></span>
    {label}
  </div>
);

export default AnalysisResults;
