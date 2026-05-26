# AI Response Evaluator

An RLHF-powered platform that evaluates ChatGPT and Gemini responses across 7 dimensions using Gemini 2.0 Flash as an impartial AI judge.

## Features

- **7-Dimension RLHF Evaluation**: Correctness, Completeness, Coherence, Relevance, Helpfulness, Creativity, Style & Presentation
- **Weighted Scoring**: 25% weight on correctness, progressive importance across dimensions
- **Rich Animations**: Framer Motion with scroll-triggered reveals, parallax effects, and sequential loading states
- **Interactive Visualizations**: Radar charts + bar charts for comprehensive comparison
- **Winner Declaration**: Animated winner banner with confetti celebration
- **Production Ready**: Rate limiting, input sanitization, error handling, accessibility support

## Quick Start

### Prerequisites

- Node.js 18+
- Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

### Installation

```bash
cd prompt-evaluator

# Backend setup
cd backend
npm install
cp .env.example .env
# Add your GEMINI_API_KEY to .env
npm run dev

# Frontend setup (new terminal)
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:5173

### Environment Variables

**Backend (`backend/.env`)**

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
PORT=3001
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX=10
FRONTEND_URL=http://localhost:5173
```

**Frontend (`frontend/.env`)**

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

- **Frontend**: React 18, Vite, Tailwind CSS, Framer Motion, Recharts
- **Backend**: Node.js, Express, Google Generative AI SDK

## Usage

1. Enter your prompt (min 20 chars)
2. Paste ChatGPT and Gemini responses (min 50 chars each)
3. Click "Run Evaluation"
4. View comprehensive results with radar chart, bar chart, and dimension scores

## Security

- Input sanitization (XSS protection)
- Rate limiting (10 requests/minute)
- API key secured in backend only
- Request timeout handling
- Error recovery with retry logic

## License

MIT
