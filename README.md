# 🌱 AgriSaarthi AI

> **Smart Advice. Better Farming.**

AI-powered multi-agent farming advisory system.
Hackathon Project — Problem Statement 14: AI Agent for Smart Farming Advice.

---

## 🚀 Quick Start (30-second demo)

### Prerequisites
- Docker Desktop installed and running

### 1. Clone / enter the project
```bash
cd AgriSaarthi
```

### 2. Start all services
```bash
docker compose up --build
```

### 3. Pull the Llama model (first time only)
```bash
docker exec agrisaarthi-ollama ollama pull llama3.2:3b
```

### 4. Open the app
```
http://localhost:5173
```

### 5. Demo flow
1. Click **"Load Demo Farm (Ramesh)"**
2. Dashboard loads with Ramesh's farm in Belagavi
3. Click **AI Advisor**
4. Ask: *"Should I irrigate my tomato crop today?"*
5. Watch the 4 agents run and synthesize the answer
6. Try **Crop Health** — upload an image or click Analyze
7. Check **Weather** and **Farm Timeline**

---

## 🏗 Architecture

```
             FARMER
                ↓
          FARM PROFILE
                ↓
        FARM SUPERVISOR
                ↓
    ┌───────┬───────┬───────┐
    ↓       ↓       ↓       ↓
  CROP   WEATHER   PEST    RAG
 AGENT    AGENT   AGENT   AGENT
    └───────┴───────┴───────┘
                ↓
        OLLAMA + LLAMA
                ↓
       FARM RECOMMENDATION
                ↓
          POSTGRESQL
```

### Future IBM deployment:
```
OLLAMA + LLAMA  →  IBM watsonx.ai + GRANITE
```
Switch via: `AI_PROVIDER=ibm` in backend environment.

---

## 🤖 AI Provider Abstraction

```
AIProvider (abstract)
   │
   ├── OllamaProvider   → LOCAL (default)
   │       └── llama3.2:3b
   │
   └── IBMWatsonxProvider  → PRODUCTION
           └── watsonx.ai
                └── ibm/granite-13b-instruct-v2
```

**Switch provider:** Set in `docker-compose.yml` or `.env`:
```env
AI_PROVIDER=ollama     # default — works without any API keys
AI_PROVIDER=ibm        # requires IBM credentials below
```

**IBM credentials (when AI_PROVIDER=ibm):**
```env
IBM_WATSONX_API_KEY=your_key
IBM_WATSONX_PROJECT_ID=your_project_id
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
IBM_GRANITE_MODEL=ibm/granite-13b-instruct-v2
```

---

## 🌿 Four Specialized Agents

| Agent | Handles |
|-------|---------|
| 🌱 **Crop Advisory Agent** | Crop stages, fertilizer, harvesting |
| 🌦 **Weather & Irrigation Agent** | Rain probability, temperature, irrigation decisions |
| 🐛 **Pest & Disease Agent** | Disease/pest identification, image analysis |
| 📚 **Agricultural RAG Agent** | Knowledge base retrieval via pgvector similarity search |

### Supervisor routing logic
| Query contains | Agents activated |
|----------------|-----------------|
| irrigate / water / rain | Weather + RAG |
| fertilize / nutrient / harvest | Crop + RAG |
| disease / pest / leaf / spot | Pest + RAG |
| Any query | RAG always included |

---

## 📁 Project Structure

```
AgriSaarthi/
├── docker-compose.yml
├── scripts/
│   └── init.sql              ← DB init + demo seed data
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   ├── knowledge_base/       ← Agricultural knowledge documents
│   │   ├── tomato_cultivation.txt
│   │   ├── crop_diseases_and_pests.txt
│   │   ├── irrigation_management.txt
│   │   └── fertilizer_management.txt
│   └── app/
│       ├── main.py           ← FastAPI app + knowledge base seeding
│       ├── config.py         ← Settings (AI provider, DB, etc.)
│       ├── agents/
│       │   ├── supervisor.py ← Farm Supervisor (routing + synthesis)
│       │   ├── crop_agent.py
│       │   ├── weather_agent.py
│       │   ├── pest_agent.py
│       │   └── rag_agent.py
│       ├── providers/
│       │   └── ai_provider.py ← OllamaProvider + IBMWatsonxProvider
│       ├── rag/
│       │   └── pipeline.py   ← Chunking + embeddings + pgvector search
│       ├── db/
│       │   ├── database.py
│       │   └── models.py     ← All SQLAlchemy models
│       └── api/
│           ├── farm.py
│           ├── advisor.py
│           ├── crop_health.py
│           ├── weather.py
│           ├── timeline.py
│           └── health.py
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── tailwind.config.js
    └── src/
        ├── App.tsx
        ├── pages/
        │   ├── LandingPage.tsx
        │   ├── Dashboard.tsx
        │   ├── Advisor.tsx
        │   ├── CropHealth.tsx
        │   ├── Weather.tsx
        │   ├── Timeline.tsx
        │   └── FarmSetup.tsx
        ├── components/
        │   └── Layout.tsx
        ├── hooks/
        │   └── useFarm.tsx
        ├── api/
        │   └── client.ts
        └── types/
            └── index.ts
```

---

## 🔌 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/farm/demo` | Load demo farm (Ramesh) |
| POST | `/api/farm/setup` | Create/update farm profile |
| GET | `/api/farm/{id}` | Get farm data |
| POST | `/api/advisor/ask` | Ask AI advisor (main endpoint) |
| GET | `/api/advisor/history/{farm_id}` | Chat history |
| POST | `/api/crop-health/analyze` | Crop image/symptom analysis |
| GET | `/api/weather/{farm_id}` | Weather + irrigation recommendation |
| GET | `/api/weather/demo/current` | Demo weather data |
| GET | `/api/timeline/{farm_id}` | Farm timeline events |
| GET | `/api/health` | System health + agent status |

API docs: `http://localhost:8000/docs`

---

## 🗄 Database Schema

```sql
users              → farm owners
farms              → farm profiles
crops              → active/past crops per farm
soil_records       → soil moisture, pH, nutrients
weather_records    → temperature, rain probability (demo/live)
crop_health        → image analysis results
ai_recommendations → saved AI advice
knowledge_documents → RAG source documents
knowledge_chunks   → pgvector embeddings (384-dim)
agent_runs         → agent execution logs
farm_timeline      → farm event history
```

---

## 📊 RAG Pipeline

```
Agricultural Documents (.txt)
        ↓
Text Chunking (400 chars, 80 overlap)
        ↓
Embeddings (all-MiniLM-L6-v2, 384-dim)
        ↓
PostgreSQL + pgvector (cosine similarity)
        ↓
Top-K relevant chunks retrieved
        ↓
Ollama / IBM Granite generates grounded answer
        ↓
Sources cited in response
```

Knowledge base covers: Tomato, Rice, Wheat, Irrigation, Fertilizers, Diseases, Pests.

---

## 🌐 Pages

| Route | Page |
|-------|------|
| `/` | Landing page |
| `/setup` | Farm setup form |
| `/dashboard` | Farm overview + action plan + agent status |
| `/advisor` | AI chat interface |
| `/crop-health` | Image upload + disease detection |
| `/weather` | Weather + irrigation recommendation |
| `/timeline` | Crop history events |

---

## ⚙️ Local Development (without Docker)

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Start PostgreSQL locally + set DATABASE_URL in .env
# Start Ollama locally: ollama serve
# Pull model: ollama pull llama3.2:3b
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

---

## 🔮 Future Improvements

- Voice input/output for farmers
- Live weather API integration (OpenWeatherMap / IMD)
- Real vision model for crop disease detection (LLaVA / plant disease CNN)
- GPS-based farm mapping
- Market price integration
- SMS alerts for critical farm events
- Multi-language support (Kannada, Hindi, Marathi)
- Advanced yield prediction models
- Government scheme recommendations
- Farmer community Q&A

---

## 📝 Notes on Demo Data

- **Weather**: Demo data shown when live API not configured. Clearly labelled.
- **Crop Health**: Demo analysis clearly labelled as non-vision-model result.
- **Farm Profile**: Pre-seeded demo farm for Ramesh, Belagavi, Karnataka.
- All demo data is clearly indicated in the UI — never presented as live data.

---

Made with ❤️ for Indian farmers · AgriSaarthi AI v1.0
