import React from 'react';
import { Bot, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

export default function AgentTimeline({ trace }) {
  if (!trace || trace.length === 0) {
    return (
      <div className="glass-panel" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <h2 style={{ marginBottom: '1.5rem' }}>Agent Timeline</h2>
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
          Awaiting analysis...
        </div>
      </div>
    );
  }

  const getIcon = (status) => {
    if (status.includes('Success') || status.includes('Pass')) return <CheckCircle size={18} color="var(--accent-green)" />;
    if (status.includes('Fail')) return <XCircle size={18} color="var(--accent-red)" />;
    return <AlertTriangle size={18} color="var(--accent-yellow)" />;
  };

  return (
    <div className="glass-panel">
      <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Bot size={20} color="var(--accent-purple)" />
        Live Agent Workflow Timeline
      </h2>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', position: 'relative' }}>
        {/* Vertical line connecting nodes */}
        <div style={{ position: 'absolute', left: '19px', top: '10px', bottom: '10px', width: '2px', background: 'linear-gradient(to bottom, var(--accent-blue), var(--accent-purple), transparent)', zIndex: 0 }}></div>
        
        {trace.map((log, i) => {
          // Log format from backend: "AgentName [Status]: Summary text"
          const match = log.match(/^(.*?) \[(.*?)\]: (.*)$/);
          let agent = "System", status = "Info", summary = log;
          if (match) {
            agent = match[1];
            status = match[2];
            summary = match[3];
          }

          return (
            <div key={i} style={{ display: 'flex', gap: '1rem', zIndex: 1 }}>
              <div style={{ 
                width: '40px', height: '40px', borderRadius: '50%', 
                background: 'var(--bg-dark)', border: '1px solid var(--border-color)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 0 10px rgba(0,0,0,0.5)'
              }}>
                {getIcon(status)}
              </div>
              <div className="timeline-card" style={{ flex: 1, padding: '0.75rem', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.25rem' }}>
                  <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--accent-blue)' }}>{agent}</span>
                  <span className={`badge ${status.includes('Fail') ? 'badge-danger' : 'badge-success'}`} style={{ whiteSpace: 'nowrap' }}>{status}</span>
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{summary}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
