Prompt

Context and Role
You’re building this as a full-stack developer who cares about modern web apps and thoughtful AI integration. Your job is to design and ship a polished AI Response Evaluation platform—fast, responsive, accessible, and genuinely nice to use. Lean on Framer Motion for scroll-driven storytelling and motion that feels intentional, not flashy, and never at the expense of performance or accessibility.
The app lets someone paste a prompt plus a ChatGPT answer and a Gemini answer, then compares them through an RLHF-style lens across seven dimensions. Gemini 2.0 Flash (via the Google Generative AI API) plays the neutral judge: each side gets a Likert score (1–5) per dimension, a short rationale (about 100–250 characters), and a weighted overall score. When the dust settles, the UI should tell the story clearly—animated comparison, charts, and a winner people can trust at a glance.

Objective
Ship a complete full-stack AI Response Evaluation platform that:
Implements scroll-based storytelling animations using Framer Motion.


Feels modern and responsive, with transitions that support the flow instead of fighting it.


Lets users paste a prompt, a ChatGPT response, and a Gemini response.


Sends everything to gemini-2.0-flash for a fair, RLHF-style evaluation.


Scores both answers across all seven dimensions, with weights that reflect how much each dimension matters.


Returns Likert scores (1–5), those short explanations, and weighted aggregate scores for each model.


Surfaces results in an animated comparison dashboard—radar and bar charts included.


Names a winner from the higher weighted aggregate (or a tie when it’s dead even).

AI Judge Configuration
Model
gemini-2.0-flash

API
Google Generative AI SDK (@google/generative-ai)

API Key
Keep the key in environment variables only—never ship it to the browser or bake it into the client bundle:
GEMINI_API_KEY=your_key_here

Judge Role
The judge should read like a careful human reviewer: strict, fair, and not rooting for either side.

Judge Prompt Rules
Return raw JSON only—no markdown fences, no backticks, no chit-chat before or after.


Strip any wrapper text before you try to parse.


Use temperature 0.2 so scores stay steady run to run.


If parsing blows up once, retry once before you give up.

Expected JSON Output
{
  "chatgpt": {
    "correctness": { "score": 1, "explanation": "string 100–250 chars" },
    "completeness": { "score": 1, "explanation": "string 100–250 chars" },
    "coherence": { "score": 1, "explanation": "string 100–250 chars" },
    "relevance": { "score": 1, "explanation": "string 100–250 chars" },
    "helpfulness": { "score": 1, "explanation": "string 100–250 chars" },
    "creativity": { "score": 1, "explanation": "string 100–250 chars" },
    "style_presentation": { "score": 1, "explanation": "string 100–250 chars" }
  },
  "gemini": {
    "correctness": { "score": 1, "explanation": "string 100–250 chars" },
    "completeness": { "score": 1, "explanation": "string 100–250 chars" },
    "coherence": { "score": 1, "explanation": "string 100–250 chars" },
    "relevance": { "score": 1, "explanation": "string 100–250 chars" },
    "helpfulness": { "score": 1, "explanation": "string 100–250 chars" },
    "creativity": { "score": 1, "explanation": "string 100–250 chars" },
    "style_presentation": { "score": 1, "explanation": "string 100–250 chars" }
  }
}

Aggregate Score
Blend the dimensions with these weights—correctness carries the most weight because wrong-but-pretty isn’t useful:
correctness: 25%, completeness: 15%, coherence: 15%, relevance: 15%, helpfulness: 15%, creativity: 5%, style_presentation: 10%.


Round the final number to two decimal places.


If the model skips aggregates, compute them yourself on the backend so the UI always has something solid to show.

Winner Logic
Whoever has the higher weighted aggregate wins.


If it’s a wash, call it "tie".

Evaluation Dimensions
Correctness — Is it actually right? Watch for hallucinations and sloppy facts (weight: 25%).


Completeness — Did it cover what the prompt asked for, not just the easy parts (weight: 15%).


Coherence — Does it hang together—structure, logic, no contradictions (weight: 15%).


Relevance — Does it stay on the rails or wander off (weight: 15%).


Helpfulness — Would a real person leave with something they can use (weight: 15%).


Creativity — Fresh angles or depth, without gimmicks for gimmicks’ sake (weight: 5%).


Style & Presentation — Clear writing, sensible formatting, tone that fits the task (weight: 10%).

Likert Scale
1 = Poor (significant issues)


2 = Fair (below average)


3 = Average (acceptable)


4 = Good (above average)


5 = Excellent (exceptional)

UI and Animation Requirements
Scroll-Based Storytelling
Use Framer Motion for scroll-triggered moments that reward scrolling instead of punishing it.


Layer in parallax, fade-ins, and staggered reveals where they help the story breathe.


Sequence sections so the page reads like a journey: landing → input → waiting → payoff.


Smooth transitions between:


Hero Section


Input Section


Loading / Processing


Results Dashboard


Winner Summary


Lean on these Framer Motion pieces where they earn their keep: useInView, motion.div, AnimatePresence, useScroll, useTransform.


Animations should:


Stay snappy—no layout thrashing from animating the wrong properties


Stick to GPU-friendly stuff (transform, opacity) whenever you can


Never make scrolling or typing feel sticky or laggy


Respect prefers-reduced-motion so nobody gets motion sick for your confetti

Layout Requirements
The application must include:


Hero section with animated introduction and word-by-word headline reveal


Input section with three animated textareas and live character counters


Loading state with full-screen overlay and sequential progress steps


Results dashboard with side-by-side score cards, radar chart, and bar chart


Winner section with animated banner, confetti celebration, and re-evaluate control


The layout must be:


Fully responsive (mobile, tablet, desktop)


Accessible (ARIA labels, semantic HTML, keyboard navigation)


Optimized for performance

Section Details
Hero Section
Animated heading: "Evaluate AI Responses. Objectively."


Word-by-word reveal on the headline.


Scroll indicator with a subtle bounce.


Animated gradient mesh background with parallax blur orbs.

Input Section
Three animated textareas: Prompt (min 20 chars), ChatGPT response (min 50), Gemini response (min 50).


Live character counter on each field with color feedback near limits.


Animated validation errors when fields are invalid.


"Run Evaluation" button with hover pulse animation.

Loading State
Full-screen loading overlay.


Pulsing brain icon.


Sequential loading steps that communicate evaluation progress.


Smooth animated progress bar.

Results Dashboard
Side-by-side score cards with count-up animation.


Animated Likert dots and fade-in explanations.


Color-coded borders: Green (≥ 4), Amber (= 3), Red (≤ 2).


Radar / spider chart plus aggregate comparison bar chart.

Winner Section
Animated winner banner with confetti burst and trophy animation.


Aggregate score comparison for both models.


"Re-evaluate" reset button with exit animation.

Input and Validation Requirements
Form Fields
Prompt (required, minimum 20 characters).


ChatGPT response (required, minimum 50 characters).


Gemini response (required, minimum 50 characters).

Validation
Validate on the client first, with messages people can act on.


Show inline animated validation errors so problems are obvious before submit.


Don’t hit the API until everything passes.


Character counters on all textareas.


Cap each field at 4000 characters so requests stay reasonable.

Backend Requirements
Implement an API endpoint to handle evaluation requests.

API Endpoint
POST /api/evaluate

Request Body
{
  "prompt": "string",
  "chatgptResponse": "string",
  "geminiResponse": "string"
}

Backend Processing Flow
Validate and sanitize all inputs.


Build the RLHF judge prompt.


Call gemini-2.0-flash.


Parse and validate the JSON response.


Compute weighted aggregate scores if the model did not return them.


Determine winner and return structured results.

Success Response
{
  "success": true,
  "data": {
    "chatgpt": { "...dimensions...", "aggregate_score": 0.0 },
    "gemini": { "...dimensions...", "aggregate_score": 0.0 },
    "winner": "chatgpt | gemini | tie"
  },
  "timestamp": "ISO string",
  "duration_ms": 0
}

Error Response
{
  "success": false,
  "error": "Descriptive error message",
  "code": "VALIDATION_ERROR | PARSE_ERROR | API_AUTH_ERROR | QUOTA_EXCEEDED | INTERNAL_ERROR"
}

Security
Clean inputs so XSS and injection don’t get a foothold.


Rate limit to 10 requests per minute per IP so one noisy client can’t burn your quota.


Never send GEMINI_API_KEY to the frontend.


Validate judge JSON before anything goes back to the browser.


Log failures with timestamps—skip logging secrets or full raw payloads if they’re sensitive.

Data Processing Requirements
Sanitize all inputs to prevent:


XSS attacks


Injection attacks


Strip HTML and script tags.


Enforce minimum lengths: prompt 20 characters, responses 50 characters.


Truncate inputs at 4000 characters.


Parse Gemini JSON safely (strip markdown fences, extract JSON object).


Ensure all 7 dimensions are present in the response.


Validate scores are integers 1–5 and explanations are 100–250 characters.


Compute weighted aggregate scores if missing.


Ensure API returns structured JSON responses:


Success message with evaluation data


Error message (if applicable)

Output Requirements
Smooth animated storytelling evaluation flow.


Structured RLHF scoring across 7 dimensions.


Visual comparison charts (radar and bar).


Winner announcement with confetti and trophy animations.


Loading states and graceful error handling.


Confirmation when results are ready via animated dashboard reveal.


Graceful error handling if the AI judge or network fails.

Error Handling and Documentation
Handle frontend form errors gracefully.


Handle backend validation errors.


Provide structured error responses.


Return 400 for validation issues and 502 for Gemini API / parse failures.


Retry once if JSON parsing fails.


30–45 second timeout on judge calls.


Log backend failures appropriately.


Document:


Folder structure


Setup instructions


Environment variable configuration


Deployment steps

Performance and Scalability
Keep the bundle lean.


Lazy-load heavy components (charts, confetti).


Ensure animations do not degrade performance.


Support concurrent evaluations without API bottlenecks.


Use rate limiting to prevent abuse.


Ensure accessibility and SEO optimization.

Technology Stack
Use the following:
Frontend:


React 18+


Vite


Framer Motion


Tailwind CSS (or equivalent styling solution)


Recharts for charts


canvas-confetti for winner celebration


lucide-react for icons


axios for API calls

Backend:


Node.js + Express


Google Generative AI SDK (@google/generative-ai)


express-rate-limit for rate limiting


sanitize-html for input sanitization


dotenv for environment configuration

Optional:


MongoDB or PostgreSQL for storing evaluation history

Folder Structure
GoldenResponse.py/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Hero.jsx
│   │   │   ├── InputForm.jsx
│   │   │   ├── LoadingOverlay.jsx
│   │   │   ├── ResultsDashboard.jsx
│   │   │   ├── ScoreCard.jsx
│   │   │   ├── RadarChart.jsx
│   │   │   ├── BarChart.jsx
│   │   │   ├── WinnerBanner.jsx
│   │   │   └── ErrorState.jsx
│   │   ├── hooks/
│   │   │   ├── useEvaluate.js
│   │   │   └── useScrollAnimation.js
│   │   ├── utils/
│   │   │   └── validate.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── index.html
├── backend/
│   ├── routes/
│   │   └── evaluate.js
│   ├── services/
│   │   └── geminiJudge.js
│   ├── middleware/
│   │   ├── rateLimiter.js
│   │   └── sanitize.js
│   ├── utils/
│   │   └── parseGeminiResponse.js
│   └── server.js
├── .env.example
└── README.md

Environment Variables
Backend (.env):
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
PORT=3001
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX=10
FRONTEND_URL=http://localhost:5173
NODE_ENV=development

Frontend (.env):
VITE_API_URL=http://localhost:3001

Setup Instructions
# Navigate to project
cd GoldenResponse.py

# Backend setup
cd backend
npm install
cp .env.example .env
# Add GEMINI_API_KEY to .env
npm run dev

# Frontend setup (new terminal)
cd ../frontend
npm install
cp .env.example .env
npm run dev

Open http://localhost:5173

Deployment Steps
Add GEMINI_API_KEY to production secrets.


Build frontend: npm run build


Deploy backend to Railway, Render, or Fly.io.


Set VITE_API_URL in frontend environment variables.


Enable CORS only for the frontend domain.


Set NODE_ENV=production.
