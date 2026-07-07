import React from 'react';
import { FileText, Shield, FileSearch, Download, Mail } from 'lucide-react';
import { jsPDF } from 'jspdf';
import { API_BASE_URL } from '../config';

export function ExecutiveBrief({ brief, dealData }) {
  const [emailDraft, setEmailDraft] = React.useState(null);
  const [isDrafting, setIsDrafting] = React.useState(false);
  const [showEmailModal, setShowEmailModal] = React.useState(false);

  if (!brief) return null;
  
  // Clean markdown bold stars for simple rendering
  const formattedBrief = brief.split('\n').map((line, i) => {
    if (line.includes('**')) {
      const parts = line.split('**');
      return <p key={i} style={{ marginBottom: '0.75rem', fontSize: '0.9rem', lineHeight: 1.5 }}><strong style={{ color: 'white' }}>{parts[1]}</strong>{parts[2]}</p>
    }
    return <p key={i} style={{ marginBottom: '0.75rem', fontSize: '0.9rem', lineHeight: 1.5 }}>{line}</p>;
  });

  const handleDownloadPDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text("Executive Decision Brief", 10, 20);
    doc.setFontSize(11);
    const splitText = doc.splitTextToSize(brief.replace(/\*\*/g, ''), 180);
    doc.text(splitText, 10, 30);
    doc.save("Executive_Decision_Brief.pdf");
  };

  const handleDownloadWord = () => {
    const header = "<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'><head><meta charset='utf-8'><title>Executive Brief</title></head><body style='font-family: Arial, sans-serif; color: black; line-height: 1.5;'>";
    const footer = "</body></html>";
    const formattedText = brief.split('\\n').map(line => {
      let cleanLine = line;
      if (line.includes('**')) {
        const parts = line.split('**');
        cleanLine = `<strong>${parts[1]}</strong>${parts[2] || ''}`;
      }
      return `<p>${cleanLine}</p>`;
    }).join('');
    
    const html = `${header}<h2>Executive Decision Brief</h2>${formattedText}${footer}`;
    const blob = new Blob(['\\ufeff', html], { type: 'application/msword' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'Executive_Decision_Brief.doc';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleEmail = () => {
    const subject = encodeURIComponent("DealGraph AI - Executive Decision Brief");
    const body = encodeURIComponent(brief);
    window.location.href = `mailto:?subject=${subject}&body=${body}`;
  };

  const handleRedlineDownload = async () => {
      try {
          const response = await fetch(`${API_BASE_URL}/generate-redline`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(dealData)
          });
          
          if (!response.ok) throw new Error("Failed to generate redline");
          
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `Redlined_Amended_Draft_${dealData?.customer_name?.replace(/ /g, '_') || 'Deal'}.docx`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
      } catch (error) {
          console.error("Redline generation failed:", error);
          alert("Failed to generate redline. Check backend logs.");
      }
  };

  const handleGenerateEmail = async () => {
      setIsDrafting(true);
      setShowEmailModal(true);
      try {
          const response = await fetch(`${API_BASE_URL}/generate-email`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(dealData)
          });
          const data = await response.json();
          if (data.status === 'success') {
              setEmailDraft(data.email);
          } else {
              setEmailDraft("Error generating email: " + data.message);
          }
      } catch (e) {
          setEmailDraft("Failed to connect to backend.");
      } finally {
          setIsDrafting(false);
      }
  };

  const handleSendDraftEmail = () => {
      const subject = encodeURIComponent(`DealGraph AI - Negotiation: ${dealData?.customer_name || 'Customer'}`);
      const body = encodeURIComponent(emailDraft || '');
      window.location.href = `mailto:?subject=${subject}&body=${body}`;
      setShowEmailModal(false);
  };

  return (
    <div className="glass-panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <FileText size={20} color="var(--accent-blue)" />
          Executive Decision Brief
        </h2>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button onClick={handleDownloadWord} className="icon-btn" style={{ fontSize: '0.75rem', fontWeight: 600, padding: '0.4rem 0.6rem' }} title="Download Word">
            DOC
          </button>
          <button onClick={handleDownloadPDF} className="icon-btn" style={{ fontSize: '0.75rem', fontWeight: 600, padding: '0.4rem 0.6rem' }} title="Download PDF">
            PDF
          </button>
          <div style={{ width: '1px', background: 'var(--border-color)', margin: '0 4px' }}></div>
          <button onClick={handleRedlineDownload} className="icon-btn" style={{ fontSize: '0.75rem', fontWeight: 600, padding: '0.4rem 0.6rem', color: 'var(--accent-purple)' }} title="Generate Redlined Contract (.docx)">
            Generate Redline (.docx)
          </button>
          <button onClick={handleGenerateEmail} className="icon-btn" style={{ fontSize: '0.75rem', fontWeight: 600, padding: '0.4rem 0.6rem', color: 'var(--accent-green)' }} title="Draft Negotiation Email">
            Draft Negotiation Email
          </button>
        </div>
      </div>
      <div style={{ color: 'var(--text-secondary)' }}>
        {formattedBrief}
      </div>

      {showEmailModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div className="glass-panel" style={{ width: '600px', maxWidth: '90%', position: 'relative' }}>
                <button onClick={() => setShowEmailModal(false)} style={{ position: 'absolute', top: '10px', right: '15px', background: 'transparent', border: 'none', color: 'white', cursor: 'pointer', fontSize: '1.2rem' }}>×</button>
                <h3 style={{ marginTop: 0, color: 'var(--accent-green)' }}>Draft Negotiation Email</h3>
                <div style={{ marginTop: '1rem', background: 'rgba(0,0,0,0.5)', padding: '1rem', borderRadius: '8px', minHeight: '200px', whiteSpace: 'pre-wrap', fontFamily: 'monospace', color: '#e2e8f0', border: '1px solid var(--border-color)' }}>
                    {isDrafting ? <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-blue)' }}>Drafting email with Gemini...</div> : emailDraft}
                </div>
                {!isDrafting && (
                    <button style={{ marginTop: '1rem', width: '100%', padding: '0.75rem', background: 'var(--accent-green)', color: 'black', border: 'none', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer' }} onClick={handleSendDraftEmail}>
                        Send via Email Client
                    </button>
                )}
            </div>
        </div>
      )}
    </div>
  );
}

export function TrustSafetyPanel({ evaluation, security, audit, asc606 }) {
  if (!evaluation) return null;

  return (
    <div className="glass-panel">
      <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Shield size={20} color="var(--accent-green)" />
        Trust, Safety & Evaluation
      </h2>
      
      <div style={{ display: 'grid', gap: '1rem' }}>
        <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Evaluation Score</div>
          <div style={{ fontFamily: 'monospace', color: 'var(--accent-green)', fontSize: '0.9rem' }}>{evaluation}</div>
        </div>

        <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Security Checks</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className={security === 'Passed' ? 'badge badge-success' : 'badge badge-danger'}>{security}</span>
            <span className={asc606 ? 'badge badge-success' : 'badge badge-danger'}>{asc606 ? "ASC 606 Compliant" : "ASC 606 Violation"}</span>
          </div>
        </div>

        {audit && audit.length > 0 && (
          <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <FileSearch size={14} /> Audit Trail
            </div>
            <div style={{ fontFamily: 'monospace', fontSize: '0.7rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              {audit.slice(-3).map((log, i) => (
                <div key={i}>{log}</div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export function HumanEvaluationPanel({ dealId, onEvaluationSubmitted, isEvaluated }) {
  const [feedback, setFeedback] = React.useState('');
  const [submitted, setSubmitted] = React.useState(false);
  const [role, setRole] = React.useState('Account Executive');
  const [roleError, setRoleError] = React.useState('');

  const handleSubmit = async (decision) => {
    setRoleError('');
    if (role === 'Account Executive' || role === 'Sales Manager') {
        setRoleError('Access Denied: Insufficient IAM permissions for Human-in-the-Loop Override. Must be Vice President or higher.');
        return;
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/submit-evaluation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          deal_id: dealId || 'unknown',
          decision: decision,
          feedback: feedback || "No explicit feedback provided."
        })
      });
      
      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }
      
      setSubmitted(true);
        if (onEvaluationSubmitted) {
            onEvaluationSubmitted(decision, feedback, role);
        }
    } catch (err) {
      console.error(err);
      alert("Failed to submit evaluation. Please ensure the backend server is running on port 8080.");
    }
  };

  if (submitted || isEvaluated) {
    return (
      <div className="glass-panel" style={{ marginTop: '1.5rem', textAlign: 'center', border: '1px solid var(--accent-green)' }}>
        <h3 style={{ margin: 0, color: 'var(--accent-green)' }}>Human Evaluation Logged to Audit Trail ✓</h3>
      </div>
    );
  }

  return (
    <div className="glass-panel" style={{ marginTop: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ margin: 0, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Shield size={20} color="var(--accent-orange)" />
            Human-in-the-Loop Sign-off
          </h3>
          <select value={role} onChange={(e) => setRole(e.target.value)} className="input-field" style={{ padding: '0.5rem', width: 'auto', minWidth: '150px' }}>
              <option>Account Executive</option>
              <option>Sales Manager</option>
              <option>Legal Counsel</option>
              <option>Vice President</option>
              <option>CFO</option>
              <option>CRO</option>
              <option>President</option>
              <option>CEO</option>
          </select>
      </div>
      
      {roleError && (
          <div style={{ padding: '0.75rem', background: 'rgba(234, 67, 53, 0.1)', color: 'var(--accent-red)', border: '1px solid var(--accent-red)', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.85rem' }}>
              {roleError}
          </div>
      )}

      <textarea 
        placeholder="Provide human review context or requirements..." 
        value={feedback}
        onChange={(e) => setFeedback(e.target.value)}
        style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-color)', color: 'white', marginBottom: '1rem', minHeight: '80px', fontFamily: 'inherit', resize: 'vertical' }}
      />
      <div style={{ display: 'flex', gap: '1rem' }}>
        <button onClick={() => handleSubmit('Approve')} style={{ flex: 1, padding: '0.75rem', borderRadius: '8px', background: 'rgba(52, 168, 83, 0.1)', color: 'var(--accent-green)', border: '1px solid var(--accent-green)', cursor: 'pointer', fontWeight: 600, transition: 'all 0.2s' }}>
          Approve AI Analysis
        </button>
        <button onClick={() => handleSubmit('Override')} style={{ flex: 1, padding: '0.75rem', borderRadius: '8px', background: 'rgba(234, 67, 53, 0.1)', color: 'var(--accent-red)', border: '1px solid var(--accent-red)', cursor: 'pointer', fontWeight: 600, transition: 'all 0.2s' }}>
          Override Analysis
        </button>
      </div>
      <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(66, 133, 244, 0.05)', border: '1px solid rgba(66, 133, 244, 0.2)', borderRadius: '8px', fontSize: '0.8rem', color: '#e2e8f0', lineHeight: '1.6' }}>
        <strong style={{ color: 'var(--accent-blue)' }}>Analytics Impact:</strong> The AI's initial recommendation (Approve = Won, Escalate/Revise = Lost) is automatically recorded. 
        <br/>• <strong>Approve AI Analysis:</strong> Confirms the AI's decision. The Win/Loss count remains unchanged.
        <br/>• <strong>Override Analysis:</strong> Forces an executive override. If the AI flagged the deal as high-risk (Lost), this reverses it to an Approved (Won) deal in the Historical Analytics.
      </div>
    </div>
  );
}
