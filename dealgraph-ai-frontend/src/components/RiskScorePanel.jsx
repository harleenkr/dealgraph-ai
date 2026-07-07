import React from 'react';
import { Activity, ShieldAlert, Check } from 'lucide-react';

export default function RiskScorePanel({ score, recommendation, approvals }) {
  if (score === undefined) return null;

  let color = 'var(--accent-green)';
  let bgGradient = 'linear-gradient(135deg, rgba(16, 185, 129, 0.2), transparent)';
  if (score >= 50) {
    color = 'var(--accent-yellow)';
    bgGradient = 'linear-gradient(135deg, rgba(245, 158, 11, 0.2), transparent)';
  }
  if (score >= 75) {
    color = 'var(--accent-red)';
    bgGradient = 'linear-gradient(135deg, rgba(239, 68, 68, 0.2), transparent)';
  }

  return (
    <div className="glass-panel" style={{ background: bgGradient, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center', padding: '2rem' }}>
      <h3 style={{ color: 'var(--text-secondary)', marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '1px', fontSize: '0.8rem' }}>Revenue Risk Score</h3>
      
      <div style={{ position: 'relative', width: '160px', height: '160px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <svg viewBox="0 0 100 100" style={{ position: 'absolute', width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
          <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="6" />
          <circle cx="50" cy="50" r="45" fill="none" stroke={color} strokeWidth="6" strokeDasharray={`${score * 2.82} 282`} style={{ transition: 'stroke-dasharray 1s ease-out' }} />
        </svg>
        <div style={{ fontSize: '3rem', fontWeight: 700, color: color }}>
          {score}
        </div>
      </div>

      <div style={{ marginTop: '1.5rem', padding: '0.75rem', borderRadius: '8px', background: 'rgba(0,0,0,0.2)', width: '100%' }}>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Recommendation</div>
        <div style={{ fontSize: '1.1rem', fontWeight: 600, color: 'white' }}>{recommendation}</div>
      </div>

      {approvals && approvals.length > 0 && (
        <div style={{ marginTop: '1rem', width: '100%' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Required Approvals</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', justifyContent: 'center' }}>
            {approvals.map(a => (
              <span key={a} className="badge badge-warning">{a}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
