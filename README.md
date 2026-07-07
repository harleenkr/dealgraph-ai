# DealGraph AI 🚀

DealGraph AI is a next-generation, multi-agent enterprise platform designed to automate and augment the analysis of complex software deals, Master Services Agreements (MSAs), and commercial contracts. By leveraging parallel AI agents, the platform dramatically accelerates the deal review process, identifies hidden risks, and empowers Sales, Legal, and Deal Desk teams to close compliant deals faster.

## 🌟 Key Features

*   **Multi-Agent Orchestration:** Powered by Gemini, the system spawns specialized autonomous agents working in parallel to review different aspects of a deal:
    *   **Legal Agent:** Analyzes the MSA for compliance, indemnification, and liability risks.
    *   **Trust & Safety Agent:** Evaluates the deal for completeness, groundedness, consistency, safety, and explainability.
    *   **Deal Desk Agent:** Checks discounting limits, payment terms, and overall deal economics.
    *   **Compliance Agent:** Verifies SOC2, GDPR, and ASC-606 revenue recognition requirements.
*   **Dynamic Knowledge Graph:** Visualizes the complex relationships between the Customer, the MSA, Legal clauses, and Pricing structures using an interactive React Flow diagram.
*   **Executive Decision Brief:** Automatically generates a comprehensive, C-level summary of the deal, including risk scores, automated recommendations, and key findings from all agents.
*   **Automated Redlining:** Generates a downloadable, redlined Word document (.docx) proposing specific revisions to the uploaded MSA to mitigate identified risks.
*   **Email Drafting:** Automatically drafts highly contextual email communications for internal approvals (e.g., to the VP of Sales) or external negotiations.
*   **Historical Analytics Dashboard:** A robust dashboard featuring interactive charts (Recharts) to track deal volume, win/loss ratios, average deal sizes, and revenue protection metrics over time.
*   **One-Click PDF Export:** Instantly generates a clean, downloadable PDF report of the live deal analysis, complete with a snapshot of the knowledge graph and the full executive brief.

## 🏗️ Architecture

The application is built using a modern, decoupled architecture designed for scalability and cloud deployment.

### Backend (Python / FastAPI)
*   **Framework:** FastAPI for high-performance asynchronous API endpoints.
*   **AI Engine:** Integrates with Gemini 2.5 Flash for agentic reasoning and natural language generation.
*   **Database:** SQLite for storing historical deal analytics and metrics.
*   **Structure:**
    *   `main.py`: The entry point for the API, handling routing and orchestration.
    *   `database.py`: Manages the SQLite connection and analytics queries.
    *   `tools/`: Contains individual agent logic and specialized processing tools.

### Frontend (React / Vite)
*   **Framework:** React 18 powered by Vite for lightning-fast HMR and optimized builds.
*   **Styling:** A premium, "Deep Space" dark mode UI utilizing custom CSS, glassmorphism, and responsive grid layouts. No heavy CSS frameworks.
*   **Visualization:** 
    *   `reactflow`: For the interactive Knowledge Graph.
    *   `recharts`: For the Historical Analytics dashboard.
    *   `lucide-react`: For clean, modern iconography.
*   **PDF Generation:** Utilizes `jspdf` and `html-to-image` for client-side report generation.

## 🚀 Deployment

The repository is fully prepared for continuous deployment via **Google Cloud Run**.

1.  **Dockerized:** Both the frontend and backend contain optimized `Dockerfile`s.
    *   The frontend uses a multi-stage build, compiling the React app and serving it via a lightweight Nginx container (`nginx.conf` included).
    *   The backend is packaged using a slim Python 3.11 image and served via Uvicorn.
2.  **Environment Configuration:** The frontend dynamically targets the backend URL using the `VITE_API_URL` environment variable defined in the cloud configuration.
3.  **Continuous Integration:** By linking this GitHub repository directly to Google Cloud Run, any pushes to the `main` branch will automatically trigger a new build and deployment for both services.

## 🛠️ Local Development

### Prerequisites
*   Node.js (v20+)
*   Python (3.11+)

### Running the Backend
```bash
cd dealgraph-ai-backend
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8080
```

### Running the Frontend
```bash
cd dealgraph-ai-frontend
npm install
# Create a .env file with VITE_API_URL=http://localhost:8080
npm run dev
```
