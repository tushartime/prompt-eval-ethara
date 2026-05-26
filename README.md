# AI Response Evaluator

[![GitHub](https://img.shields.io/badge/GitHub-prompt--eval--ethara-blue)](https://github.com/tushartime/prompt-eval-ethara)

An RLHF-powered platform that compares **ChatGPT** and **Gemini** responses across **7 dimensions**, using **Gemini 2.0 Flash** as an impartial AI judge. Results include per-dimension scores, explanations, weighted aggregate scores, charts, and a declared winner.

## Features

- **7-Dimension RLHF Evaluation**: Correctness, Completeness, Coherence, Relevance, Helpfulness, Creativity, Style & Presentation
- **Weighted Scoring**: Correctness 25%, other dimensions 5–15% each (see table below)
- **Rich UI**: Scroll storytelling, Framer Motion animations, radar + bar charts, confetti winner celebration (Node option)
- **Production safeguards**: Input sanitization, rate limiting (10 req/min), JSON validation, retry on parse failure

## Repository layout

```
.
├── goldenresponse.py      # Option A: single-file FastAPI app + embedded React UI
├── GoldenResponse/        # Option B: full-stack Node + React/Vite project
│   ├── backend/           # Express API + Gemini judge
│   └── frontend/          # React 18 + Vite + Tailwind + Framer Motion
├── prompt.md              # Product / build specification
├── justification.md       # Evaluation rubric notes
└── README.md
```

## Choose how to run

| | **Option A — Python** | **Option B — Node + React** |
|---|------------------------|-----------------------------|
| **Best for** | Quick local demo, one command | Production-style split frontend/backend |
| **Entry point** | `goldenresponse.py` | `GoldenResponse/backend` + `GoldenResponse/frontend` |
| **UI URL** | http://localhost:3001 | http://localhost:5173 |
| **API** | Same server (port 3001) | http://localhost:3001/api/evaluate |

---

## Option A: Standalone Python (FastAPI)

### Prerequisites

- Python 3.9+
- [Gemini API key](https://aistudio.google.com/apikey)

### Setup

1. Create a `.env` file in the **repo root**:

   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.0-flash
   PORT=3001
   RATE_LIMIT_WINDOW_MS=60000
   RATE_LIMIT_MAX=10
   ```

2. Install dependencies:

   ```bash
   pip install fastapi uvicorn python-dotenv google-genai
   ```

   If `google-genai` is unavailable, install the legacy SDK instead:

   ```bash
   pip install google-generativeai
   ```

3. Start the server:

   ```bash
   python goldenresponse.py
   ```

4. Open **http://localhost:3001** in your browser.

---

## Option B: Full-stack Node.js + React/Vite

### Prerequisites

- Node.js 18+
- [Gemini API key](https://aistudio.google.com/apikey)

### Backend

```bash
cd GoldenResponse/backend
npm install
```

Copy env file (PowerShell: `copy .env.example .env` · macOS/Linux: `cp .env.example .env`), then set `GEMINI_API_KEY` in `GoldenResponse/backend/.env`.

```bash
npm run dev
```

API runs at **http://localhost:3001** (health check: `/health`).

### Frontend (new terminal)

```bash
cd GoldenResponse/frontend
npm install
```

Copy env file, then start:

```bash
npm run dev
```

Open **http://localhost:5173**.

---

## Environment variables

**Option A — root `.env`**

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
PORT=3001
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX=10
```

**Option B — `GoldenResponse/backend/.env`**

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
PORT=3001
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX=10
FRONTEND_URL=http://localhost:5173
```

**Option B — `GoldenResponse/frontend/.env`**

```env
VITE_API_URL=http://localhost:3001
```

## Usage

1. Enter your **prompt** (20–4000 characters).
2. Paste **ChatGPT** and **Gemini** responses (50–4000 characters each).
3. Click **Run Evaluation**.
4. Review dimension scores, aggregate totals, charts, and the winner.

## Evaluation dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Correctness | 25% | Factual accuracy, no hallucinations |
| Completeness | 15% | How thoroughly the prompt is addressed |
| Coherence | 15% | Logical flow and structure |
| Relevance | 15% | Staying on topic |
| Helpfulness | 15% | Practical utility |
| Creativity | 5% | Originality and depth |
| Style & Presentation | 10% | Clarity and formatting |

Likert scale: **1** (poor) → **5** (excellent).

## Tech stack

- **Option A**: Python, FastAPI, Uvicorn, embedded React UI (CDN), Tailwind CSS (CDN), Chart.js, canvas-confetti
- **Option B**: React 18, Vite, Tailwind CSS, Framer Motion, Recharts, Express, `@google/generative-ai`

## Security

- HTML stripped from inputs (XSS mitigation)
- Rate limiting (10 requests/minute per IP)
- `GEMINI_API_KEY` never exposed to the browser (Option B)
- Judge output validated as JSON before returning to the client
- One automatic retry if JSON parsing fails

## License

MIT
