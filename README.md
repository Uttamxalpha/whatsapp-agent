# 🚀 Misinfo Buster  
### WhatsApp Misinformation Fact-Checker (Agentic AI + RAG)

## ⚡ Overview  
**Misinfo Buster** is a production-grade AI system that detects misinformation from WhatsApp forwards (text, images, URLs).  
It extracts factual claims, verifies them using **web search + RAG**, and returns structured verdicts.

- Supports Hindi + English  
- Handles screenshots via OCR  
- Uses multi-step agent reasoning  

---
<img width="1470" height="956" alt="Screenshot 2026-04-21 at 9 06 10 AM" src="https://github.com/user-attachments/assets/2bbe891b-1e73-486e-b262-1ab97df72a77" />
<img width="1470" height="956" alt="Screenshot 2026-04-21 at 9 05 56 AM" src="https://github.com/user-attachments/assets/23f77d7a-49bd-4ef4-ba95-9d2329ca21a1" />




## 🧠 How It Works  
Input (Text / Image / URL)
↓
OCR / Parsing
↓
Claim Extraction (LLM)
↓
Parallel Fact Checking (Web + RAG)
↓
Verdict Aggregation
↓
{ verdict, confidence, explanation, sources }

---

## 🔥 Key Features  

- Agentic pipeline using LangGraph  
- Hybrid fact-checking (Tavily + ChromaDB)  
- OCR support via EasyOCR (Hindi + English)  
- Optimized retrieval (cosine similarity ≤ 0.7)  
- Structured, explainable outputs  

---

## 🛠️ Tech Stack  

| Layer | Tech |
|------|------|
| Agents | LangGraph |
| LLM | Groq (LLaMA 3.3 70B) |
| OCR | EasyOCR |
| Search | Tavily |
| Vector DB | ChromaDB |
| Backend | FastAPI |
| UI | Streamlit |

---

## ⚙️ Quick Start  

bash
git clone https://github.com/yourusername/misinfo_buster.git
cd misinfo_buster

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Add GROQ_API_KEY & TAVILY_API_KEY

uvicorn main:app --reload
Run UI:

streamlit run streamlit_app.py
🧪 API Example
POST /api/v1/check/text
{
  "text": "5G towers spread COVID-19"
}
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/84d639a7-e828-40b1-aec8-df760a76b048" />
