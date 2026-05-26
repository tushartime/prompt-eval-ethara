# AI Response Evaluator

An RLHF-powered platform that evaluates ChatGPT and Gemini responses across 7 dimensions using Gemini 2.0 Flash as an impartial AI judge.

## Features

- **7-Dimension RLHF Evaluation**: Correctness, Completeness, Coherence, Relevance, Helpfulness, Creativity, Style & Presentation
- **Weighted Scoring**: 25% weight on correctness, progressive importance across dimensions
- **Rich Animations**: Framer Motion with scroll-triggered reveals, parallax effects, and sequential loading states
- **Interactive Visualizations**: Radar charts + bar charts for comprehensive comparison
- **Winner Declaration**: Animated winner banner with confetti celebration
- **Production Ready**: Rate limiting, input sanitization, error handling, accessibility support

## Project Options

This repository offers two distinct ways to run and deploy the platform:

1. **Option A: Standalone Python (FastAPI + React SPA)**: A single-file python script (`goldenresponse.py`) that serves both a beautiful React+Tailwind single-page dashboard and the evaluation API. Great for simple setups.
2. **Option B: Full-Stack Node.js & React/Vite**: A structured production folder (`GoldenResponse/`) with an Express API backend and an isolated React/Vite/Tailwind frontend.

---

## ⚡ Option A: Standalone Python Setup

### Prerequisites
- Python 3.9+
- Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

### Running the App
1. Create a `.env` file at the root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   PORT=3001
   ```
2. Install Python dependencies:
   ```bash
   pip install fastapi uvicorn google-genai python-dotenv
   ```
3. Start the server:
   ```bash
   python goldenresponse.py
   ```
4. Open your browser to **http://localhost:3001** to view the interactive dashboard.

---

## 💻 Option B: Full-Stack Node.js & Vite/React Setup

### Prerequisites
- Node.js 18+
- Gemini API key

### Running the App
1. Navigate into the folder:
   ```bash
   cd GoldenResponse
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   npm install
   cp .env.example .env
   # Add your GEMINI_API_KEY to backend/.env
   npm run dev
   ```

3. **Frontend Setup** (in a new terminal tab):
   ```bash
   cd GoldenResponse/frontend
   npm install
   cp .env.example .env
   npm run dev
   ```
4. Open your browser to **http://localhost:5173**.

---

## Environment Variables

**Backend (`GoldenResponse/backend/.env`)**
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
PORT=3001
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX=10
FRONTEND_URL=http://localhost:5173
```

**Frontend (`GoldenResponse/frontend/.env`)**
```env
VITE_API_URL=http://localhost:3001
```

## Evaluation Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Correctness | 25% | Factual accuracy, no hallucinations |
| Completeness | 15% | How thoroughly prompt is addressed |
| Coherence | 15% | Logical flow and structure |
| Relevance | 15% | Staying on topic |
| Helpfulness | 15% | Practical utility |
| Creativity | 5% | Originality and depth |
| Style & Presentation | 10% | Clarity and formatting |

## Tech Stack

- **Option A**: Python, FastAPI, Uvicorn, React 18 (CDN), Tailwind CSS (CDN), Chart.js (CDN), Canvas-Confetti (CDN)
- **Option B**: React 18, Vite, Tailwind CSS, Framer Motion, Recharts, Express, Node.js, `@google/generative-ai`

## Security

- Input sanitization (XSS protection)
- Rate limiting (10 requests/minute)
- API key secured in backend only
- Request timeout handling
- Error recovery with retry logic

## License

MIT

