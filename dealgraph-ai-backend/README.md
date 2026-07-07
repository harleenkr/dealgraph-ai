# DealGraph AI: Multi-Agent Revenue Risk & Approval Assistant

DealGraph AI is an enterprise-ready backend that analyzes high-value business deals using a multi-agent architecture powered by Google Gemini. It identifies revenue risks, approval gaps, policy violations, and creates a live knowledge graph.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd dealgraph-ai-backend
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**
    Copy `.env.example` to `.env` and set your `GEMINI_API_KEY`.
    ```bash
    cp .env.example .env
    ```

4.  **Run the application locally:**
    ```bash
    uvicorn main:app --reload
    ```

5.  **Test the endpoint:**
    ```bash
    curl -X POST http://127.0.0.1:8000/analyze-deal \
         -H "Content-Type: application/json" \
         -d @data/sample_deal.json
    ```
