import React from 'react';
import { User, Globe } from 'lucide-react';

const TeamView: React.FC = () => {
  const team = [
    { name: 'Qasim Khan', role: 'Full-Stack Engineer', bio: 'Orchestrating seamless data flow between the Edge Node and our internal Synthesis cluster.' },
    { name: 'Mavia Ahmad Khan', role: 'Technical Documentation', bio: 'Structuring architectural blueprints and formal system documentation for neural validation.' },
    { name: 'Farhan Shah', role: 'AI & Neural Developer', bio: 'Optimizing high-entropy signal processing and local BERT inference layers for real-time analysis.' },
  ];

  return (
    <div className="animate-in">
      <header style={{ marginBottom: '4rem' }}>
        <div style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--accent-primary)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.75rem' }}>
          The Minds Behind AI-RADA
        </div>
        <h1 style={{ fontSize: '3.5rem', fontWeight: 800, letterSpacing: '-0.04em' }}>Development Team</h1>
        <p style={{ color: 'var(--text-sub)', fontSize: '1.1rem' }}>Final Year Software Engineering Project Members.</p>
      </header>

      <div className="grid-3" style={{ gap: '3rem' }}>
        {team.map((member, idx) => (
          <div key={idx} className="card" style={{ 
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
            <h3 style={{ fontSize: '1.7rem', fontWeight: 800, marginBottom: '0.75rem' }}>{member.name}</h3>
            <div style={{ 
              color: 'var(--accent-gold)', fontWeight: 800, fontSize: '0.85rem', 
              marginBottom: '2rem', textTransform: 'uppercase', letterSpacing: '0.1em',
              background: 'rgba(245,179,1,0.08)', padding: '0.4rem 1rem', borderRadius: '99px',
              display: 'inline-block'
            }}>{member.role}</div>
            <p style={{ color: 'var(--text-sub)', fontSize: '0.95rem', lineHeight: '1.8', marginBottom: '2.5rem' }}>
              {member.bio}
            </p>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem' }}>
              <div style={{ width: '40px', height: '40px', background: '#f8fafc', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
                <User size={20} color="var(--text-ghost)" />
              </div>
              <div style={{ width: '40px', height: '40px', background: '#f8fafc', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
                <Globe size={20} color="var(--text-ghost)" />
              </div>
            </div>
          </div>
        ))}
      </div>

      <section style={{ marginTop: '5rem', textAlign: 'center' }} className="card">
         <h2 style={{ fontSize: '2rem', marginBottom: '1.5rem' }}>Academic Vision</h2>
         <p style={{ color: 'var(--text-sub)', maxWidth: '800px', margin: '0 auto', lineHeight: '1.8', fontSize: '1.1rem' }}>
           AI-RADA was developed as a submission for the final year software engineering degree, aiming to revolutionize the way requirements are handled in the SDLC. Our goal is to bridge the gap between human language and formal system design using state-of-the-art neural architectures.
         </p>
      </section>
    </div>
  );
};

export default TeamView;
