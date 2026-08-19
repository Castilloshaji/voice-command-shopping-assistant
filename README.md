# Voice Command Shopping Assistant

An intelligent, voice-activated shopping assistant application designed for seamless hands-free shopping list management, voice product search, and smart recommendations.

---

## ?? Project Overview & Purpose

The **Voice Command Shopping Assistant** allows users to interact with a smart shopping list using natural language voice commands (e.g., *"Add 2 bottles of milk"*, *"I need apples"*, *"Search for organic coffee"*).

### Key Architectural Capabilities (Target System)
1. **Multilingual Voice Recognition**: Client-side Web Speech API with selectable language codes (en-US, es-ES, r-FR, de-DE, hi-IN).
2. **Natural Language Intent Parsing**: Rule-based & pattern-matching NLP service converting natural voice transcripts into structured intents (ADD_ITEM, REMOVE_ITEM, UPDATE_QUANTITY, SEARCH_PRODUCT, SHOW_LIST, CLEAR_LIST, GET_SUGGESTIONS).
3. **Smart Deterministic Recommendations**: Explanation-backed recommendations based on historical purchase events, product seasonality, availability, and substitute matching.
4. **Product Catalog**: Filterable catalog supporting category, brand, price range, season, and substitutes.
5. **Mobile-First Responsive Interface**: Clean, accessible, minimal web interface with visual feedback and loading/error states.

---

## ??? Current Status: Phase 1 — Foundation

> [!NOTE]
> **Phase 1 Deliverable**: Architecture & Foundation Initialization.
> No feature implementation or mock UI is populated yet. Feature endpoints and complete UI components will be added in subsequent implementation phases.

### Current Implemented Features (Phase 1)
- [x] Project architecture & directory structure (ackend/, rontend/).
- [x] Minimal dependency setup (equirements.txt, package.json, 	sconfig.json, ite.config.ts).
- [x] Database ORM models (Product, ListItem, ShoppingHistory) using SQLAlchemy & SQLite.
- [x] Pydantic schemas for intents, catalog, items, and suggestions.
- [x] Health check API endpoint (GET /health).
- [x] Frontend foundation (Vite + React 18 + TypeScript), API client service abstraction, voice recognition hook/interface.
- [x] Security-checked .gitignore excluding sensitive environment files and build outputs.

---

## ?? Project Structure

`	ext
voice-command-shopping-assistant/
+-- backend/
¦   +-- app/
¦   ¦   +-- api/
¦   ¦   ¦   +-- v1/
¦   ¦   ¦       +-- health.py          # Baseline GET /health endpoint
¦   ¦   +-- core/
¦   ¦   ¦   +-- config.py              # Application settings (FastAPI / CORS / DB)
¦   ¦   ¦   +-- database.py            # SQLAlchemy engine & session factory
¦   ¦   +-- models/                    # ORM Models (Product, ListItem, ShoppingHistory)
¦   ¦   +-- schemas/                   # Pydantic validation schemas
¦   ¦   +-- services/                  # Business logic & NLP/Recommendation interfaces
¦   ¦   +-- main.py                    # FastAPI application initialization
¦   +-- tests/
¦   ¦   +-- test_health.py             # Health check verification tests
¦   +-- requirements.txt               # Minimal backend python dependencies
+-- frontend/
¦   +-- src/
¦   ¦   +-- hooks/
¦   ¦   ¦   +-- useSpeechRecognition.ts # Web Speech API hook interface
¦   ¦   +-- services/
¦   ¦   ¦   +-- api.ts                 # Backend API service client abstraction
¦   ¦   ¦   +-- voice.ts               # Browser speech synthesis/recognition abstraction
¦   ¦   +-- types/                     # TypeScript domain models (Intent, Item, Product)
¦   ¦   +-- App.tsx                    # Baseline app entry point
¦   ¦   +-- index.css                  # Modern minimalist design system & tokens
¦   ¦   +-- main.tsx                   # React root launcher
¦   +-- index.html                     # HTML root template
¦   +-- package.json                   # Minimal frontend dependencies
¦   +-- tsconfig.json                  # TypeScript configuration
¦   +-- vite.config.ts                 # Vite setup with backend proxy
+-- .gitignore                         # Environment & build output exclusion rules
+-- README.md                          # Project architecture & setup documentation
`

---

## ??? Data Models & Substitutes Handling

### Database Schema (SQLAlchemy + SQLite)
- **Product**: id, 
ame, category, rand, price, size, is_available, season, substitutes
  - *Substitutes Decision*: Stored cleanly using SQLAlchemy JSON column type (JSON string array e.g., ["Oat Milk", "Almond Milk"]) to avoid unnecessary many-to-many join tables while maintaining lightweight queryability in SQLite.
- **ListItem**: id, product_id (optional FK), item_name, category, quantity, unit, is_completed, created_at, updated_at.
- **ShoppingHistory**: id, item_name, category, quantity, purchased_at.
  - *History Decision*: Event-based records tracking discrete purchase events over time. Recommendation frequencies are derived dynamically from historical purchase timestamps.

---

## ?? Local Development Setup

### 1. Backend Setup (FastAPI)
`ash
cd backend

# Create virtual environment (optional)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install minimal dependencies
pip install -r requirements.txt

# Start backend dev server
uvicorn app.main:app --reload --port 8000
`
Health Check endpoint: http://localhost:8000/health

### 2. Frontend Setup (React + Vite)
`ash
cd frontend

# Install minimal dependencies
npm install

# Start frontend dev server
npm run dev
`
Frontend URL: http://localhost:5173

---

## ?? Planned Feature Roadmap (Phase 2+)

- [ ] **Phase 2**: Product Catalog & Seed Data
- [ ] **Phase 3**: Natural Language Processing & Intent Parsing Engine
- [ ] **Phase 4**: Shopping List API & Core Domain Logic
- [ ] **Phase 5**: Smart Recommendation Algorithm Engine
- [ ] **Phase 6**: Responsive UI & Web Speech Voice Control Integration
- [ ] **Phase 7**: End-to-End Testing & Deployment Verification
