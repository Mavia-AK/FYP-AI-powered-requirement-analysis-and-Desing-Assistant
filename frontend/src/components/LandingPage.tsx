import React from 'react';
import { ChevronRight, Cpu, Zap, Search, Layers, Globe, Shield, User, Terminal } from 'lucide-react';

interface LandingPageProps {
  onEnterApp: () => void;
  onLogin: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onEnterApp, onLogin }) => {
  return (
    <div style={{ backgroundColor: 'white' }}>
      {/* Navbar */}
      <nav style={{ 
        display: 'flex', justifyContent: 'space-between', alignItems: 'center', 
        padding: '1.5rem 6rem', background: 'var(--bg-navy)', color: 'white',
        position: 'sticky', top: 0, zIndex: 1000, borderBottom: '1px solid var(--border-navy)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '1.5rem', fontWeight: 800 }}>
          <div style={{ background: 'var(--accent-gold)', color: '#000', padding: '0.4rem', borderRadius: '8px' }}>
            <Cpu size={24} />
          </div>
          <span>AI-RADA</span>
        </div>
        <div style={{ display: 'flex', gap: '3rem', alignItems: 'center', fontWeight: 600, fontSize: '0.9rem' }}>
          <a href="#features" style={{ color: 'white', textDecoration: 'none' }}>Features</a>
          <a href="#methodology" style={{ color: 'white', textDecoration: 'none' }}>How it Works</a>
          <a href="#team" style={{ color: 'white', textDecoration: 'none' }}>Team</a>
          <button className="btn-gold" style={{ padding: '0.6rem 1.5rem' }} onClick={onLogin}>Sign In</button>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="hero">
        <div className="animate-up">
          <div style={{ 
            display: 'inline-flex', alignItems: 'center', gap: '0.5rem', 
            padding: '0.5rem 1.25rem', background: 'rgba(255,255,255,0.05)', 
            borderRadius: '99px', color: 'var(--accent-gold)', fontWeight: 700, 
            fontSize: '0.85rem', marginBottom: '3rem', border: '1px solid rgba(245,179,1,0.2)'
          }}>
            <Zap size={16} /> AI-POWERED REQUIREMENT CLASSIFIER
          </div>
          <h1 className="hero-tagline">
            Automated System <br />
            Design Synthesis.
          </h1>
          <p className="hero-sub">
            Bridging the gap between natural language specifications and formal architectural models using our proprietary neural processing pipeline.
          </p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem' }}>
            <button className="btn-gold" onClick={onEnterApp} style={{ fontSize: '1.1rem', padding: '1.25rem 3.5rem' }}>
              Launch Workspace <ChevronRight size={20} style={{ marginLeft: '0.5rem' }} />
            </button>
            <button style={{ 
              background: 'transparent', border: '2px solid white', color: 'white',
              fontWeight: 800, padding: '1.25rem 3.5rem', borderRadius: '8px', cursor: 'pointer'
            }}>
              View Documentation
            </button>
          </div>
        </div>
      </header>

      {/* Animated Features */}
      <section id="features" style={{ padding: '10rem 6rem', backgroundColor: '#f8fafc' }}>
        <div style={{ textAlign: 'center', marginBottom: '6rem' }}>
           <h2 style={{ fontSize: '3rem', fontWeight: 800, marginBottom: '1.5rem' }}>Core Capabilities</h2>
           <p style={{ color: 'var(--text-sub)', fontSize: '1.1rem' }}>Engineered for precision and architectural clarity.</p>
        </div>
        <div className="grid-3" style={{ gap: '3rem' }}>
          <FeatureCard 
            icon={<Search size={32} color="var(--accent-gold)" />} 
            title="Requirement Classification" 
            desc="Automatically detect and categorize FR and NFR types with 98% accuracy."
            color="#3b82f6"
          />
          <FeatureCard 
            icon={<Shield size={32} color="var(--accent-gold)" />} 
            title="Ambiguity Detection" 
            desc="Isolate vague terminology and calculate RQI scores using BERT encoders."
            color="#8b5cf6"
          />
          <FeatureCard 
            icon={<Layers size={32} color="var(--accent-gold)" />} 
            title="Use Case Generator" 
            desc="Synthesize formal UML models directly from natural language specifications."
            color="#10b981"
          />
        </div>
      </section>

      {/* Methodology Section (How it Works) */}
      <section id="methodology" style={{ padding: '10rem 6rem', background: 'var(--bg-navy)', color: 'white' }}>
        <div style={{ textAlign: 'center', marginBottom: '6rem' }}>
           <h2 style={{ fontSize: '3rem', fontWeight: 800, color: 'white' }}>How it Works</h2>
           <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: '1.1rem' }}>The AI-RADA Neural Methodology</p>
        </div>
        
        <div className="timeline">
          <TimelineItem step="01" title="Lexical Tokenization" desc="Requirements are parsed and cleaned for neural processing." />
          <TimelineItem step="02" title="Local Semantic Encoding" desc="Fine-tuned BERT models perform initial classification on the edge." />
          <TimelineItem step="03" title="Neural Pattern Refinement" desc="High-entropy signals are processed through our deep reasoning cluster for structural validation." />
          <TimelineItem step="04" title="Architectural Synthesis" desc="Validated requirement sets are transformed into structured UML designs." />
        </div>
      </section>

      {/* Team Section */}
      <section id="team" style={{ padding: '10rem 6rem', backgroundColor: 'white' }}>
        <div style={{ textAlign: 'center', marginBottom: '6rem' }}>
           <h2 style={{ fontSize: '3rem', fontWeight: 800 }}>Development Team</h2>
           <p style={{ color: 'var(--text-sub)', fontSize: '1.1rem' }}>Software Engineering Final Year Project</p>
        </div>
        <div className="grid-3" style={{ gap: '3rem' }}>
          <TeamCard name="Qasim Khan" role="Full-Stack Engineer" />
          <TeamCard name="Mavia Ahmad Khan" role="Technical Documentation" />
          <TeamCard name="Farhan Shah" role="AI & Neural Developer" />
        </div>
      </section>

      {/* Footer */}
      <footer style={{ padding: '6rem 6rem 4rem', background: 'var(--bg-navy)', color: 'white', borderTop: '1px solid var(--border-navy)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '0.5rem' }}>AI-RADA</div>
            <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.9rem' }}>Requirement Analysis & Design Assistant</p>
          </div>
          <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.85rem' }}>
            © 2026 AI-RADA PROJECT | ALL RIGHTS RESERVED
          </div>
        </div>
      </footer>
    </div>
  );
};

const FeatureCard = ({ icon, title, desc }: any) => (
  <div className="feature-card" style={{ 
    display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center',
    background: 'white', padding: '4rem 3rem', borderRadius: '32px',
    boxShadow: '0 20px 40px rgba(0,0,0,0.04)', border: '1px solid #f1f5f9'
  }}>
    <div style={{ 
      width: '80px', height: '80px', background: 'var(--bg-navy)', 
      borderRadius: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center',
      marginBottom: '2.5rem', boxShadow: '0 10px 20px rgba(0,26,58,0.2)'
    }}>
      {icon}
    </div>
    <h3 style={{ fontSize: '1.6rem', fontWeight: 800, marginBottom: '1.25rem' }}>{title}</h3>
    <p style={{ color: 'var(--text-sub)', lineHeight: '1.8', fontSize: '1rem' }}>{desc}</p>
  </div>
);

const TimelineItem = ({ step, title, desc }: any) => (
  <div className="timeline-item">
    <div className="timeline-dot"></div>
    <div style={{ fontSize: '0.9rem', fontWeight: 800, color: 'var(--accent-gold)', marginBottom: '0.5rem' }}>{step}</div>
    <h3 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '1rem', color: 'white' }}>{title}</h3>
    <p style={{ color: 'rgba(255,255,255,0.6)', lineHeight: '1.7' }}>{desc}</p>
  </div>
);

const TeamCard = ({ name, role }: any) => (
  <div className="card" style={{ 
    textAlign: 'center', padding: '4rem 3rem', borderRadius: '32px', 
    background: 'white', border: '1px solid #f1f5f9', boxShadow: '0 20px 40px rgba(0,0,0,0.04)',
    transition: 'all 0.3s ease'
  }}>
    <div style={{ 
      width: '120px', height: '120px', background: '#f8fafc', 
      borderRadius: '50%', margin: '0 auto 2.5rem', display: 'flex', 
      alignItems: 'center', justifyContent: 'center', border: '4px solid white',
      boxShadow: '0 10px 25px rgba(0,0,0,0.05)'
    }}>
      <User size={54} color="var(--text-ghost)" />
    </div>
    <h3 style={{ fontSize: '1.7rem', fontWeight: 800, marginBottom: '0.75rem' }}>{name}</h3>
    <div style={{ 
      color: 'var(--accent-gold)', fontWeight: 800, fontSize: '0.85rem', 
      marginBottom: '2rem', textTransform: 'uppercase', letterSpacing: '0.1em',
      background: 'rgba(245,179,1,0.08)', padding: '0.4rem 1rem', borderRadius: '99px',
      display: 'inline-block'
    }}>{role}</div>
    <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem' }}>
      <div style={{ width: '40px', height: '40px', background: '#f8fafc', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
        <User size={20} color="var(--text-ghost)" />
      </div>
      <div style={{ width: '40px', height: '40px', background: '#f8fafc', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
        <Globe size={20} color="var(--text-ghost)" />
      </div>
    </div>
  </div>
);

export default LandingPage;
