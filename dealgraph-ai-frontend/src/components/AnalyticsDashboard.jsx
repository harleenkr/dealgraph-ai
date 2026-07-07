import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { Loader2 } from 'lucide-react';
import { API_BASE_URL } from '../config';

const COLORS = ['#4285F4', '#EA4335', '#FBBC04', '#34A853'];

export default function AnalyticsDashboard() {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/analytics`);
        if (!response.ok) throw new Error("Failed to fetch analytics");
        const json = await response.json();
        if (json.status === 'success') {
          setData(json.data);
        } else {
          throw new Error(json.message);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (isLoading) {
      return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px', color: 'var(--accent-blue)' }}><Loader2 size={32} style={{ animation: 'spin 1s linear infinite' }} /></div>;
  }
  
  if (error) {
      return <div className="glass-panel" style={{ color: 'var(--accent-red)' }}>Error loading analytics: {error}</div>;
  }

  const { winLossData, discountData, violationData } = data;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <svg style={{ height: 0, width: 0, position: 'absolute' }}>
        <defs>
          <linearGradient id="colorWon" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#4ADE80" stopOpacity={1}/>
            <stop offset="100%" stopColor="#16A34A" stopOpacity={0.9}/>
          </linearGradient>
          <linearGradient id="colorLost" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#F87171" stopOpacity={1}/>
            <stop offset="100%" stopColor="#DC2626" stopOpacity={0.9}/>
          </linearGradient>
          <linearGradient id="colorDiscount" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#C084FC" stopOpacity={1}/>
            <stop offset="100%" stopColor="#9333EA" stopOpacity={0.9}/>
          </linearGradient>
          <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="4" stdDeviation="4" floodColor="#A855F7" floodOpacity="0.3" />
          </filter>
        </defs>
      </svg>

      <div className="glass-panel">
        <h3 style={{ marginBottom: '1.5rem', color: 'var(--accent-blue)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent-blue)' }}></div>
          Quarterly Win/Loss Trend
        </h3>
        <div style={{ height: 300, width: '100%' }}>
          <ResponsiveContainer>
            <BarChart data={winLossData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey="month" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', boxShadow: '0 10px 25px rgba(0,0,0,0.5)', color: 'white', backdropFilter: 'blur(10px)' }} itemStyle={{ color: '#e2e8f0' }} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Bar dataKey="won" fill="url(#colorWon)" name="Deals Won" radius={[6, 6, 0, 0]} label={{ position: 'top', fill: '#4ADE80', fontSize: 12, formatter: (val) => val > 0 ? val : '' }} />
              <Bar dataKey="lost" fill="url(#colorLost)" name="Deals Lost" radius={[6, 6, 0, 0]} label={{ position: 'top', fill: '#F87171', fontSize: 12, formatter: (val) => val > 0 ? val : '' }} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={{ marginBottom: '2rem', padding: '1rem', background: 'rgba(66, 133, 244, 0.05)', border: '1px solid rgba(66, 133, 244, 0.2)', borderRadius: '8px', fontSize: '0.85rem', color: '#e2e8f0', display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
        <div style={{ fontSize: '1.2rem' }}>ℹ️</div>
        <div style={{ lineHeight: '1.5' }}>
            <strong>How Win/Loss is Calculated:</strong><br/>
            Deals are instantly logged as <strong>"Lost"</strong> if the AI flags them for Escalation/Revision, and <strong>"Won"</strong> if the AI Approves them. 
            If an executive uses the <strong>Override Analysis</strong> button to force a blocked deal through, the system instantly flips that deal from Lost to Won.
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
        <div className="glass-panel">
          <h3 style={{ marginBottom: '1.5rem', color: 'var(--accent-purple)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent-purple)' }}></div>
            Avg Discount by Industry
          </h3>
          <div style={{ height: 300, width: '100%' }}>
            <ResponsiveContainer>
              <LineChart data={discountData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="industry" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', boxShadow: '0 10px 25px rgba(0,0,0,0.5)', color: 'white', backdropFilter: 'blur(10px)' }} />
                <Line type="monotone" dataKey="avgDiscount" stroke="#A855F7" strokeWidth={4} name="Avg Discount (%)" dot={{ fill: '#A855F7', strokeWidth: 2, r: 4 }} activeDot={{ r: 6, fill: 'white', stroke: '#A855F7' }} filter="url(#shadow)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel">
          <h3 style={{ marginBottom: '1.5rem', color: 'var(--accent-yellow)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent-yellow)' }}></div>
            Top Compliance Violations
          </h3>
          <div style={{ height: 300, width: '100%' }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie data={violationData} cx="50%" cy="50%" innerRadius={70} outerRadius={110} fill="#8884d8" paddingAngle={5} dataKey="value" stroke="none" label={({ name, value }) => value > 0 ? `${name}: ${value}` : ''} labelLine={false}>
                  {violationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} style={{ filter: 'drop-shadow(0px 4px 6px rgba(0,0,0,0.4))' }} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', boxShadow: '0 10px 25px rgba(0,0,0,0.5)', color: 'white', backdropFilter: 'blur(10px)' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
