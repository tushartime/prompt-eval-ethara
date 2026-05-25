Prompt

Context and Role
You're putting this together as a full-stack dev with a focus on modern web apps and AI integration. Your job is to design and deliver a production-ready Prompt Evaluation website—responsive, accessible, and refined. Use Framer Motion for immersive, scroll-driven storytelling animations without sacrificing performance, accessibility, or production quality.

The site compares ChatGPT and Gemini responses using an RLHF-style 7-dimension scoring system. A neutral AI judge (Gemini 2.0 Flash via the Google Generative AI API) scores both sides. Each response gets a Likert score (1–5) per dimension, a brief explanation (100–200 characters), and a weighted aggregate score. Results show up in an animated comparison dashboard with a clear winner callout.

Objective
Build a complete full-stack Prompt Evaluation platform that:

Accepts a user prompt, a ChatGPT response, and a Gemini response.


Sends both responses to gemini-2.0-flash for unbiased RLHF evaluation.


Scores both responses across 7 evaluation dimensions.


Returns Likert scores (1–5), short explanations, and aggregate scores for each model.


Displays results inside an animated comparison dashboard.


Declares the winning model based on the final aggregate score.



AI Judge Configuration
Model
gemini-2.0-flash


API
Google Generative AI SDK (@google/generative-ai)


API Key
Keep the key in `.env` only:

GEMINI_API_KEY=your_key_here


Judge Role
The judge should act as a strict, impartial RLHF evaluator—no favoritism toward either model.


Judge Prompt Rules
Return raw JSON only.


No markdown, backticks, or extra text.


Strip any wrapper text before parsing.


Use temperature: 0.2 for stable, consistent scoring.


Expected JSON Output

{
  "chatgpt": {
    "correctness": { "score": 1, "explanation": "string 100–200 chars" },
    "completeness": { "score": 1, "explanation": "string 100–200 chars" },
    "coherence": { "score": 1, "explanation": "string 100–200 chars" },
    "relevance": { "score": 1, "explanation": "string 100–200 chars" },
    "helpfulness": { "score": 1, "explanation": "string 100–200 chars" },
    "creativity": { "score": 1, "explanation": "string 100–200 chars" },
    "style_presentation": { "score": 1, "explanation": "string 100–200 chars" },
    "aggregate_score": 0.0
  },
  "gemini": {
    "correctness": { "score": 1, "explanation": "string 100–200 chars" },
    "completeness": { "score": 1, "explanation": "string 100–200 chars" },
    "coherence": { "score": 1, "explanation": "string 100–200 chars" },
    "relevance": { "score": 1, "explanation": "string 100–200 chars" },
    "helpfulness": { "score": 1, "explanation": "string 100–200 chars" },
    "creativity": { "score": 1, "explanation": "string 100–200 chars" },
    "style_presentation": { "score": 1, "explanation": "string 100–200 chars" },
    "aggregate_score": 0.0
  },
  "winner": "chatgpt | gemini | tie"
}


Aggregate Score
Take the mean of all 7 dimension scores.


Round to 2 decimal places.


Winner Logic
Higher aggregate score wins.


If scores are equal, return "tie".



Evaluation Dimensions
Correctness — How accurate the answer is; watch for hallucinations.


Completeness — Whether the response fully answers the prompt.


Coherence — Logical flow and internal consistency.


Relevance — Stays on topic without drifting.


Helpfulness — Practical value and actionability.


Creativity — Originality and depth of ideas.


Style & Presentation — Clarity, formatting, readability, and tone.


Likert Scale
1 = Poor


2 = Fair


3 = Average


4 = Good


5 = Excellent



UI and Animation Requirements
Scroll-Based Storytelling
Use Framer Motion for scroll-triggered animations.


Add parallax, fade-ins, and staggered transitions where they help the narrative.


Animate sections in sequence so the page feels like a story, not a static form.


Smooth transitions between:


Hero Section


Input Section


Loading / Processing


Results Dashboard


Winner Summary


Required Framer Motion features: useInView, motion.div, AnimatePresence, useAnimation.


Animations should:


Stay performant (avoid layout thrashing).


Prefer GPU-friendly properties (transform, opacity).


Never block scroll or typing.


Honor prefers-reduced-motion.



Layout Requirements
The app needs:

Hero section with animated heading and word-by-word reveal.


Input section with three animated textareas and live character counters.


Loading state with full-screen overlay and sequential progress steps.


Results dashboard with side-by-side score cards and charts.


Winner section with animated banner, confetti, and a re-evaluate control.


Overall layout:

Fully responsive (mobile, tablet, desktop).


Accessible (ARIA labels, semantic HTML, keyboard navagation).


Tuned for performance.



Section Details
Hero Section
Animated heading: "Evaluate AI Responses. Objectively."


Word-by-word reveal on the headline.


Scroll indicator with a subtle bounce.


Animated gradient mesh background.


Input Section
Three animated textareas: Prompt (min 20 chars), ChatGPT response (min 50), Gemini response (min 50).


Live character counter on each field.


Animated validation errors when somethings off.


Evaluate button with hover pulse animation.


Loading State
Full-screen loading overlay.


Pulsing Gemini brain icon.


Sequential loading steps (tell the user whats happening).


Smooth animated progress bar.


Results Dashboard
Side-by-side score cards with count-up animation.


Animated Likert dots and fade-in explanations.


Color-coded borders: Green (≥ 4), Amber (= 3), Red (≤ 2).


Radar / spider chart plus aggregate comparison bar chart.


Winner Section
Animated winner banner with confetti burst and trophy animation.


Aggregate score comparison.


“Re-evaluate” reset button with exit animation.



Input and Validation Requirements
Form Fields
Prompt (required, minimum 20 characters).


ChatGPT response (required, minimum 50 characters).


Gemini response (required, minimum 50 characters).


Validation
Client-side validation with clear error messages.


Show inline animated validation errors.


Block the API call until validation passess.


Character counters on all textareas.



Backend Requirements
API Endpoint
POST /api/evaluate for evaluation requests.


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


Compute aggregate scores if the model didn't return them.


Return structured results.


Success Response

{
  "success": true,
  "data": {},
  "timestamp": "ISO string"
}

Error Response

{
  "success": false,
  "error": "Descriptive error message",
  "code": "VALIDATION_ERROR | API_ERROR | PARSE_ERROR"
}

Security
Guard against XSS.


Rate limit to 10 requests per minute per IP.


Never send GEMINI_API_KEY to the frontend.


Validate all judge JSON before it reaches the client.


Log backend failures with timestamps and input hashes (not raw secrets).



Data Processing Requirements
Sanitize inputs against XSS and injection.


Strip HTML and script tags.


Enforce minimum lengths: prompt 20 characters, responses 50 characters.


Truncate inputs at 4000 characters.


Parse Gemini JSON safely.


Ensure all 7 dimensions are present in the reponse.


Compute aggregate scores if missing.


Always return structured JSON with clear success or error payloads.



Output Requirements
Fully animated evaluation flow with scroll-based storytelling.


Structured RLHF scoring across 7 dimensions.


Visual comparison charts (radar and bar).


Winner announcement with confetti and trophy animations.


Loading states and graceful error handling.


Clear confirmation when results are ready.



Error Handling and Documentation
Frontend: graceful validation errors with animated inline messages.


Backend: structured error responses for validation failures.


Return 400 for validation issues and 502 for Gemini API failures.


Retry once if JSON parsing fail.


30-second timeout on judge calls.


Log backend failures appropriately.


Document:


Folder structure


Setup instructions


Environment variable configuration


Deployment steps



Performance and Scalability
Keep the bundle lean.


Lazy-load heavy pieces (charts, confetti).


Don't let animations hurt scroll or input.


Handle concurrent evaluations without clogging up the API.


Rate limit to prevent abuse.


Accessibility and SEO basics covered.



Technology Stack
Use the following:
Frontend:
React 18+ (or Next.js)


Vite


Framer Motion


Tailwind CSS (or equivalent styling solution)


Recharts or Chart.js for charts


canvas-confetti for winner celebration


Backend:
Node.js + Express (or Next.js API routes)


Google Generative AI SDK (@google/generative-ai)


express-rate-limit for rate limiting


DOMPurify or sanitize-html for input sanitization


dotenv for environment configuration


Optional:
MongoDB for storing evaluation history



Folder Structure

prompt-evaluator/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── index.html
├── backend/
│   ├── routes/
│   ├── services/
│   ├── middleware/
│   ├── utils/
│   └── server.js
├── .env
├── .env.example
└── README.md



Environment Variables

GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
PORT=3001
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX=10
NODE_ENV=development



Setup Instructions

# Clone repository
git clone <repo>
cd prompt-evaluator

# Backend setup
cd backend
npm install
cp ../.env.example ../.env
# Add GEMINI_API_KEY
npm run dev

# Frontend setup
cd ../frontend
npm install
cp .env.example .env
npm run dev



Deployment Steps
Add GEMINI_API_KEY to production secrets.


Build frontend: npm run build


Deploy backend to Railway, Render, or Fly.io.


Set VITE_API_URL in frontend environment variables.


Enable CORS only for the frontend domain.


Set NODE_ENV=production.
