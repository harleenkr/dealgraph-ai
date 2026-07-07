import React, { useState } from 'react';
import { TrendingUp, ShieldCheck, Cpu, Network, Cloud, Hexagon, Download, ExternalLink } from 'lucide-react';
import DealIntakeForm from './components/DealIntakeForm';
import AgentTimeline from './components/AgentTimeline';
import RiskScorePanel from './components/RiskScorePanel';
import KnowledgeGraph from './components/KnowledgeGraph';
import { ExecutiveBrief, TrustSafetyPanel, HumanEvaluationPanel } from './components/Panels';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import { API_BASE_URL } from './config';

const HeroSection = () => (
  <div style={{ textAlign: 'center', padding: '3rem 2rem 2rem', maxWidth: '800px', margin: '0 auto' }}>
    <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem', background: 'linear-gradient(to right, #ffffff, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
      Enterprise Deal Governance & Revenue Protection
    </h1>
    <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem', lineHeight: 1.6 }}>
      An autonomous <strong>Agentic Workflow</strong> designed to evaluate high-value commercial deals. 
      DealGraph AI delivers transparent <strong>Explainability</strong> and <strong>Enterprise Trust</strong> while 
      routing complex risk vectors to <strong>Human-in-the-loop approvals</strong>.
    </p>
  </div>
);

const KPICards = () => (
  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', maxWidth: '98%', margin: '0 auto 3rem', padding: '0 2rem' }}>
    <div className="glass-panel" style={{ textAlign: 'center', padding: '1.5rem' }}>
      <TrendingUp size={24} color="var(--accent-blue)" style={{ margin: '0 auto 0.5rem' }} />
      <div style={{ fontSize: '1.1rem', fontWeight: 600, color: 'white' }}>Revenue Protection</div>
      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Automated Margin Analysis</div>
    </div>
    <div className="glass-panel" style={{ textAlign: 'center', padding: '1.5rem' }}>
      <ShieldCheck size={24} color="var(--accent-green)" style={{ margin: '0 auto 0.5rem' }} />
      <div style={{ fontSize: '1.1rem', fontWeight: 600, color: 'white' }}>Strict Governance</div>
      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Real-time Policy Enforcement</div>
    </div>
    <div className="glass-panel" style={{ textAlign: 'center', padding: '1.5rem' }}>
      <Cpu size={24} color="var(--accent-purple)" style={{ margin: '0 auto 0.5rem' }} />
      <div style={{ fontSize: '1.1rem', fontWeight: 600, color: 'white' }}>Agentic Workflow</div>
      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Multi-agent Orchestration</div>
    </div>
    <div className="glass-panel" style={{ textAlign: 'center', padding: '1.5rem' }}>
      <Network size={24} color="var(--accent-yellow)" style={{ margin: '0 auto 0.5rem' }} />
      <div style={{ fontSize: '1.1rem', fontWeight: 600, color: 'white' }}>Explainability</div>
      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Live Knowledge Graphs</div>
    </div>
  </div>
);

const Footer = () => (
  <footer style={{ marginTop: '4rem', padding: '2rem', borderTop: '1px solid var(--border-color)', textAlign: 'center', color: 'var(--text-muted)' }}>
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
      <Cloud size={18} color="var(--accent-blue)" />
      <span style={{ fontWeight: 500, color: 'var(--text-secondary)' }}>Cloud-Ready Architecture</span>
    </div>
    <p style={{ fontSize: '0.85rem' }}>Stateless deployment ready for enterprise scale on Google Cloud Run.</p>
  </footer>
);

export default function App() {
  const [result, setResult] = useState(null);
  const [dealData, setDealData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('live');
  const [slackToast, setSlackToast] = useState(null);

  const analyzeDeal = async (formData) => {
    setIsLoading(true);
    setError(null);
    setDealData(formData);
    try {
      const response = await fetch(`${API_BASE_URL}/analyze-deal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      setResult(data);
      
      // Simulate Slack Notification for escalations
      if (data.recommendation === 'Escalate' || data.recommendation === 'Revise') {
        setTimeout(() => {
            setSlackToast(`WARNING: DealGraph AI escalated the ${formData.customer_name} deal. Executive approval required.`);
        }, 2000);
      }

    } catch (e) {
      console.error("Error calling API:", e);
      setError("Failed to connect to the DealGraph backend. Ensure the server is running on port 8080.");
    } finally {
      setIsLoading(false);
    }
  };

  const generatePdfDoc = async () => {
    const { jsPDF } = await import('jspdf');
    const { toPng } = await import('html-to-image');
    
    const doc = new jsPDF();
    doc.setFontSize(18);
    doc.setTextColor(66, 133, 244);
    doc.text("DealGraph AI - Comprehensive Deal Report", 15, 20);
    
    doc.setFontSize(12);
    doc.setTextColor(0, 0, 0);
    doc.text(`Customer: ${dealData.customer_name}`, 15, 35);
    doc.text(`Industry: ${dealData.industry}`, 15, 42);
    doc.text(`Deal Value: $${dealData.deal_value.toLocaleString()}`, 15, 49);
    doc.text(`Discount Requested: ${dealData.discount_requested}%`, 15, 56);
    
    doc.setFontSize(14);
    doc.setTextColor(66, 133, 244);
    doc.text("Risk & Evaluation", 15, 75);
    
    doc.setFontSize(11);
    doc.setTextColor(0, 0, 0);
    doc.text(`Risk Score: ${result.risk_score} / 100`, 15, 85);
    doc.text(`Recommendation: ${result.recommendation}`, 15, 92);
    
    // Wrap long evaluation text to prevent cutoff
    const splitEval = doc.splitTextToSize(`Evaluation: ${result.evaluation}`, 180);
    doc.text(splitEval, 15, 99);
    
    // Calculate new Y position based on how many lines the evaluation took
    let currentY = 99 + (splitEval.length * 6);
    
    const splitSec = doc.splitTextToSize(`Security Checks: ${result.security_checks}`, 180);
    doc.text(splitSec, 15, currentY);
    currentY += (splitSec.length * 6);
    
    doc.text(`ASC 606 Compliant: ${result.asc606 ? 'Yes' : 'No'}`, 15, currentY);
    
    // Add knowledge graph image BEFORE Executive Brief
    const kgContainer = document.getElementById('knowledge-graph-container');
    if (kgContainer) {
      const dataUrl = await toPng(kgContainer, { 
          quality: 0.95, 
          backgroundColor: '#0f172a' 
      });
      
      doc.addPage();
      doc.setFontSize(14);
      doc.setTextColor(66, 133, 244);
      doc.text("Knowledge Graph Analysis", 15, 20);
      
      const imgProps = doc.getImageProperties(dataUrl);
      const pdfWidth = doc.internal.pageSize.getWidth() - 30;
      const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
      
      doc.addImage(dataUrl, 'PNG', 15, 30, pdfWidth, pdfHeight);
    }
    
    doc.addPage();
    doc.setFontSize(14);
    doc.setTextColor(66, 133, 244);
    doc.text("Executive Brief", 15, 20);
    
    doc.setFontSize(10);
    doc.setTextColor(0, 0, 0);
    const splitBrief = doc.splitTextToSize(result.executive_brief.replace(/\*\*/g, ''), 180);
    doc.text(splitBrief, 15, 30);
    
    return doc;
  };

  const handleDownloadFullReport = async () => {
    try {
      const doc = await generatePdfDoc();
      doc.save(`DealGraph_Report_${dealData.customer_name.replace(/\s+/g, '_')}.pdf`);
    } catch (err) {
      console.error("Error generating PDF:", err);
      alert("Failed to generate PDF report.");
    }
  };

  const handleViewFullReport = async () => {
    try {
      const doc = await generatePdfDoc();
      const pdfBlob = doc.output('blob');
      const blobUrl = URL.createObjectURL(pdfBlob);
      window.open(blobUrl, '_blank');
    } catch (err) {
      console.error("Error generating PDF:", err);
      alert("Failed to view PDF report.");
    }
  };

  return (
    <div style={{ minHeight: '100vh' }}>
      <header style={{ padding: '1.25rem 2.5rem', borderBottom: '1px solid var(--border-color)', background: 'rgba(5, 5, 5, 0.85)', backdropFilter: 'blur(16px)', position: 'sticky', top: 0, zIndex: 100, display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 4px 30px rgba(0,0,0,0.5)' }}>
        <h1 className="title-gradient" style={{ fontSize: '1.6rem', display: 'flex', alignItems: 'center', gap: '0.75rem', margin: 0 }}>
          <div style={{ width: '36px', height: '36px', background: 'rgba(255,255,255,0.03)', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.1)', boxShadow: '0 0 20px rgba(66, 133, 244, 0.2), inset 0 0 10px rgba(66, 133, 244, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Hexagon size={22} color="var(--accent-blue)" strokeWidth={2.5} />
          </div>
          DealGraph AI
        </h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.85rem', color: 'var(--text-primary)', background: 'var(--bg-panel)', padding: '6px 16px', borderRadius: '24px', border: '1px solid var(--border-color)', fontWeight: 500 }}>
          <div className="status-indicator"></div>
          Agentic Governance Active
        </div>
      </header>

      <HeroSection />
      <KPICards />

      {/* Slack Toast Simulation */}
      {slackToast && (
        <div style={{ position: 'fixed', bottom: '2rem', right: '2rem', background: '#3F0E40', color: 'white', padding: '1rem 1.5rem', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '1rem', boxShadow: '0 10px 30px rgba(0,0,0,0.5)', zIndex: 1000, borderLeft: '4px solid #E01E5A', animation: 'slideIn 0.3s ease-out' }}>
            <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
                <span style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.2rem', color: '#E01E5A' }}>⚠️ Slack #deal-desk (Warning)</span>
                <span style={{ fontSize: '0.9rem' }}>{slackToast}</span>
            </div>
            <button onClick={() => setSlackToast(null)} style={{ background: 'transparent', border: 'none', color: 'white', cursor: 'pointer', opacity: 0.7, fontSize: '1.2rem', padding: '0 0.5rem' }}>×</button>
        </div>
      )}

      {/* Tabs */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginBottom: '1rem', maxWidth: '98%', margin: '0 auto', padding: '0 2rem' }}>
        <button onClick={() => setActiveTab('live')} className={activeTab === 'live' ? 'btn-primary' : 'btn-secondary'} style={{ padding: '0.5rem 1.5rem', borderRadius: '24px' }}>
            Live Deal Analysis
        </button>
        <button onClick={() => setActiveTab('analytics')} className={activeTab === 'analytics' ? 'btn-primary' : 'btn-secondary'} style={{ padding: '0.5rem 1.5rem', borderRadius: '24px' }}>
            Historical Analytics
        </button>
      </div>

      <main className="dashboard-grid">
        {activeTab === 'analytics' ? (
          <div className="full-width">
            <AnalyticsDashboard />
          </div>
        ) : (
          <>
            {/* Left Column */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <DealIntakeForm onSubmit={analyzeDeal} isLoading={isLoading} />
          {error && <div className="glass-panel" style={{ color: 'var(--accent-red)', fontSize: '0.85rem', border: '1px solid rgba(239, 68, 68, 0.3)' }}>{error}</div>}
          <AgentTimeline trace={result?.agent_trace} />
        </div>

        {/* Right Column */}
        <div className="content-grid">
          {result ? (
            <>
              <div style={{ gridColumn: '1 / -1', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
                <h2 style={{ margin: 0, color: 'var(--text-primary)' }}>Analysis Results</h2>
                <div style={{ display: 'flex', gap: '0.75rem' }}>
                  <button onClick={handleViewFullReport} className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.6rem 1.2rem', borderRadius: '8px' }}>
                    <ExternalLink size={16} /> View Full Report
                  </button>
                  <button onClick={handleDownloadFullReport} className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.6rem 1.2rem', borderRadius: '8px' }}>
                    <Download size={16} /> Export (PDF)
                  </button>
                </div>
              </div>
              <div style={{ gridColumn: '1 / 2' }}>
                <RiskScorePanel score={result.risk_score} recommendation={result.recommendation} approvals={result.approval_path} />
              </div>
              <div style={{ gridColumn: '2 / 3' }}>
                <TrustSafetyPanel evaluation={result.evaluation} security={result.security_checks} audit={result.audit_log} asc606={result.asc606} />
              </div>
              
              <KnowledgeGraph graphData={result.graph} />
              
              <div className="full-width">
                <ExecutiveBrief brief={result.executive_brief} dealData={dealData} />
                <HumanEvaluationPanel 
                  dealId={result.deal_id} 
                  isEvaluated={result.audit_log?.some(log => log.includes("HUMAN_IN_THE_LOOP"))}
                  onEvaluationSubmitted={(decision, feedback, role) => {
                    const finalFeedback = feedback || "No explicit feedback provided.";
                    setResult(prev => ({
                      ...prev,
                      audit_log: [...prev.audit_log, `[${prev.deal_id}] HUMAN_IN_THE_LOOP: ${role} - ${decision.toUpperCase()} - Feedback: '${finalFeedback}'`]
                    }));
                    if (decision === 'override') {
                        alert(`Model Auto-Tuning Triggered!\n\nLogging executive override parameters for Industry: ${dealData.industry} / Country: ${dealData.country}.\n\nUpdating Risk Score heuristics via simulated backpropagation...`);
                    }
                  }}
                />
              </div>
            </>
          ) : (
            <div className="glass-panel full-width" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: '400px', color: 'var(--text-muted)' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.2 }}>📊</div>
                <h3>Awaiting Deal Submission</h3>
                <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>Submit a deal to trigger the multi-agent orchestration workflow.</p>
              </div>
            </div>
          )}
        </div>
        </>
        )}
      </main>

      <Footer />
      <style>{`
        @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
      `}</style>
    </div>
  );
}
