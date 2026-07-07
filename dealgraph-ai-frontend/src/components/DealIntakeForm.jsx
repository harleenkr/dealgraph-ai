import React, { useState, useRef } from 'react';
import { Send, Loader2, UploadCloud, RefreshCw } from 'lucide-react';

export default function DealIntakeForm({ onSubmit, isLoading }) {
  const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

  const [formData, setFormData] = useState({
    customer_name: '',
    industry: '',
    country: '',
    deal_value: '',
    discount_requested: '',
    contract_term_months: '',
    payment_terms: '',
    custom_sla: false,
    renewal_risk: '',
    region: 'NA',
    sales_stage: 'Negotiation',
    msa_pdf_path: ''
  });

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({ ...formData, [e.target.name]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...formData,
      deal_value: Number(formData.deal_value),
      discount_requested: Number(formData.discount_requested),
      contract_term_months: Number(formData.contract_term_months),
    });
  };

  const [isSimulatingOCR, setIsSimulatingOCR] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsSimulatingOCR(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE_URL}/parse-msa`, {
            method: 'POST',
            body: formData,
        });
        
        if (!response.ok) throw new Error("Failed to parse PDF");
        
        const data = await response.json();
        if (data.status === 'success') {
            setFormData(prev => ({
                ...prev,
                ...data.extracted_data
            }));
        } else {
            alert("Error parsing PDF: " + data.message);
        }
    } catch (error) {
        console.error("Upload error:", error);
        alert("Failed to connect to backend for PDF parsing.");
    } finally {
        setIsSimulatingOCR(false);
        if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const [isSyncingCRM, setIsSyncingCRM] = useState(false);
  const handleCRMSync = async () => {
    setIsSyncingCRM(true);
    try {
        const response = await fetch(`${API_BASE_URL}/sync-salesforce`);
        if (!response.ok) throw new Error("Failed to sync with Salesforce");
        const data = await response.json();
        if (data.status === 'success') {
            setFormData(prev => ({
                ...prev,
                ...data.data
            }));
        } else {
            alert("Error syncing with Salesforce: " + data.message);
        }
    } catch (error) {
        console.error("Sync error:", error);
        alert("Failed to connect to backend for Salesforce sync.");
    } finally {
        setIsSyncingCRM(false);
    }
  };

  return (
    <div className="glass-panel">
      <div style={{ marginBottom: '1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
          <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent-blue)' }}></div>
            Deal Intake Form
          </h2>
          <div style={{ display: 'flex', gap: '10px', width: '100%', justifyContent: 'center' }}>
            <button 
                type="button" 
                onClick={handleCRMSync} 
                disabled={isSyncingCRM || isSimulatingOCR}
                style={{ background: 'rgba(52, 168, 83, 0.1)', border: '1px solid var(--accent-green)', color: 'var(--accent-green)', padding: '0.5rem 1rem', borderRadius: '8px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', transition: 'all 0.2s', flex: 1, justifyContent: 'center' }}
            >
                {isSyncingCRM ? <><Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} /> Syncing CRM...</> : <><RefreshCw size={14} /> Sync from Salesforce</>}
            </button>
            <input 
                type="file" 
                accept=".pdf" 
                style={{ display: 'none' }} 
                ref={fileInputRef} 
                onChange={handleFileUpload} 
            />
            <button 
                type="button" 
                onClick={() => fileInputRef.current?.click()} 
                disabled={isSimulatingOCR || isSyncingCRM}
                style={{ background: 'rgba(66, 133, 244, 0.1)', border: '1px dashed var(--accent-blue)', color: 'var(--accent-blue)', padding: '0.5rem 1rem', borderRadius: '8px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', transition: 'all 0.2s', flex: 1, justifyContent: 'center' }}
            >
                {isSimulatingOCR ? <><Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} /> Parsing PDF...</> : <><UploadCloud size={14} /> Upload MSA (PDF)</>}
            </button>
          </div>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Customer Name</label>
          <input className="input-field" type="text" name="customer_name" value={formData.customer_name} onChange={handleChange} required />
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div className="form-group">
            <label>Industry</label>
            <select className="input-field" name="industry" value={formData.industry} onChange={handleChange} required>
              <option value="" disabled>Select Industry</option>
              <option value="Technology">Technology</option>
              <option value="Financial Services">Financial Services</option>
              <option value="Healthcare">Healthcare</option>
              <option value="Manufacturing">Manufacturing</option>
              <option value="Retail">Retail</option>
            </select>
          </div>
          <div className="form-group">
            <label>Country</label>
            <select className="input-field" name="country" value={formData.country} onChange={handleChange} required>
              <option value="" disabled>Select Country</option>
              <option value="United States">United States</option>
              <option value="United Kingdom">United Kingdom</option>
              <option value="Germany">Germany</option>
              <option value="Japan">Japan</option>
              <option value="Australia">Australia</option>
              <option value="Canada">Canada</option>
            </select>
          </div>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div className="form-group">
            <label>Deal Value ($)</label>
            <input className="input-field" type="number" name="deal_value" value={formData.deal_value} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Discount (%)</label>
            <input className="input-field" type="number" name="discount_requested" value={formData.discount_requested} onChange={handleChange} required />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div className="form-group">
            <label>Contract Term (Months)</label>
            <input className="input-field" type="number" name="contract_term_months" value={formData.contract_term_months} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Payment Terms</label>
            <select className="input-field" name="payment_terms" value={formData.payment_terms} onChange={handleChange} required>
              <option value="" disabled>Select Terms</option>
              <option value="Net 30">Net 30</option>
              <option value="Net 60">Net 60</option>
              <option value="Net 90">Net 90</option>
            </select>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
           <div className="form-group">
            <label>Renewal Risk</label>
            <select className="input-field" name="renewal_risk" value={formData.renewal_risk} onChange={handleChange} required>
              <option value="" disabled>Select Risk</option>
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
            </select>
          </div>
          <div className="form-group" style={{ display: 'flex', alignItems: 'center', marginTop: '1.5rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', margin: 0 }}>
              <input type="checkbox" name="custom_sla" checked={formData.custom_sla} onChange={handleChange} />
              Requires Custom SLA
            </label>
          </div>
        </div>

        <button type="submit" className="btn-primary" disabled={isLoading} style={{ width: '100%', marginTop: '1.5rem', padding: '1rem' }}>
          {isLoading ? <><Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> Analyzing Deal...</> : <><Send size={18} /> Run Multi-Agent Analysis</>}
        </button>
      </form>
      <style>{`
        @keyframes spin { 100% { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
