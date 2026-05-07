import React from 'react';
import { Shield, Activity, Target, Zap, Terminal, Globe, Layers, Cpu } from 'lucide-react';

const MethodologyView: React.FC = () => {
  return (
    <div className="animate-in">
      <header style={{ marginBottom: '4rem' }}>
        <div style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--accent-primary)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.75rem' }}>
          Technical Framework
        </div>
        <h1 style={{ fontSize: '3.5rem', fontWeight: 800, letterSpacing: '-0.04em' }}>Hybrid Neural Pipeline</h1>
        <p style={{ color: 'var(--text-sub)', fontSize: '1.1rem' }}>The architectural methodology behind AI-RADA requirement verification.</p>
      </header>

      <div className="grid-2" style={{ gap: '3rem' }}>
        <div className="card" style={{ padding: '3.5rem' }}>
          <h2 style={{ fontSize: '1.8rem', marginBottom: '2.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
             <Layers size={28} color="var(--accent-primary)" />
             Stage 1: Local Semantic Encoding
          </h2>
          <p style={{ color: 'var(--text-sub)', fontSize: '1.1rem', lineHeight: '1.8', marginBottom: '2rem' }}>
            Every requirement enters our **Edge Neural Node**, where it is tokenized using a fine-tuned **BERT (Bidirectional Encoder Representations from Transformers)** model. 
          </p>
          <div style={{ background: 'var(--bg-sub)', padding: '2rem', borderRadius: '16px', border: '1px solid var(--border-main)' }}>
            <ul style={{ display: 'flex', flexDirection: 'column', gap: '1rem', listStyle: 'none' }}>
              <li style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontWeight: 700, fontSize: '0.9rem' }}>
                <div style={{ width: '8px', height: '8px', background: 'var(--accent-primary)', borderRadius: '50%' }}></div>
                Multi-class classification (FR/NFR)
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontWeight: 700, fontSize: '0.9rem' }}>
                <div style={{ width: '8px', height: '8px', background: 'var(--accent-primary)', borderRadius: '50%' }}></div>
                Semantic Ambiguity Tagging
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontWeight: 700, fontSize: '0.9rem' }}>
                <div style={{ width: '8px', height: '8px', background: 'var(--accent-primary)', borderRadius: '50%' }}></div>
                Probability Score Calculation
              </li>
            </ul>
          </div>
        </div>

        <div className="card" style={{ padding: '3.5rem', background: 'var(--text-main)', color: 'white', border: 'none' }}>
          <h2 style={{ fontSize: '1.8rem', marginBottom: '2.5rem', display: 'flex', alignItems: 'center', gap: '1rem', color: 'white' }}>
             <Globe size={28} color="var(--accent-secondary)" />
             Stage 2: Remote Neural Refinement
          </h2>
          <p style={{ color: 'var(--text-ghost)', fontSize: '1.1rem', lineHeight: '1.8', marginBottom: '2rem' }}>
            For complex reasoning and design extraction, the system routes high-entropy signals to our **Global Reasoning Cluster**.
          </p>
          <div style={{ background: 'rgba(255,255,255,0.05)', padding: '2rem', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.1)' }}>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-ghost)', lineHeight: '1.6' }}>
              Our proprietary **Refinement Engine** (Gemini-Optimized) performs final semantic validation, generates human-readable reasoning, and synthesizes the UML system architecture from the validated requirement set.
            </p>
          </div>
        </div>
      </div>

      <section style={{ marginTop: '4rem' }} className="card">
         <div style={{ display: 'flex', gap: '3rem', alignItems: 'center' }}>
            <div style={{ flex: 1 }}>
               <h3 style={{ fontSize: '1.5rem', marginBottom: '1.5rem' }}>Why AI-RADA?</h3>
               <p style={{ color: 'var(--text-sub)', lineHeight: '1.7' }}>
                 Traditional requirement engineering is prone to human error and linguistic ambiguity. 
                 By combining the speed of local neural encoders with the depth of global reasoning clusters, 
                 we achieve a **98.2% verification accuracy** across large-scale SRS documents.
               </p>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
               <div style={{ textAlign: 'center', padding: '1.5rem', background: 'var(--bg-sub)', borderRadius: '12px' }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>0.4s</div>
                  <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-ghost)' }}>LATENCY</div>
               </div>
               <div style={{ textAlign: 'center', padding: '1.5rem', background: 'var(--bg-sub)', borderRadius: '12px' }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>BERT</div>
                  <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-ghost)' }}>ENCODER</div>
               </div>
            </div>
         </div>
      </section>
    </div>
  );
};

export default MethodologyView;
