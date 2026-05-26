import os
import re
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# Load env variables from root .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="AI Response Evaluator")

# Add CORS middleware to support cross-origin API calls if necessary
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory rate limiting dictionary: {ip_address: [request_timestamps]}
rate_limit_cache: Dict[str, List[float]] = {}

def is_rate_limited(ip: str, limit: int, window_ms: int) -> bool:
    """Checks whether the client IP has exceeded the allowed request limit in the specified window."""
    now = time.time()
    window_sec = window_ms / 1000.0
    
    if ip not in rate_limit_cache:
        rate_limit_cache[ip] = []
        
    # Keep only timestamps within the current window
    rate_limit_cache[ip] = [t for t in rate_limit_cache[ip] if now - t < window_sec]
    
    if len(rate_limit_cache[ip]) >= limit:
        return True
        
    rate_limit_cache[ip].append(now)
    return False

def sanitize_input(text: str) -> str:
    """Strips all HTML tags to prevent XSS attacks, matching sanitize-html in node."""
    if not text:
        return ""
    # Strip HTML tags
    cleaned = re.sub(r'<[^>]*>', '', text)
    return cleaned.strip()

def validate_lengths(prompt: str, chatgpt_response: str, gemini_response: str) -> List[str]:
    """Validates the min/max characters of the prompt and model responses."""
    errors = []
    if len(prompt) < 20:
        errors.append("Prompt must be at least 20 characters")
    if len(chatgpt_response) < 50:
        errors.append("ChatGPT response must be at least 50 characters")
    if len(gemini_response) < 50:
        errors.append("Gemini response must be at least 50 characters")
        
    if len(prompt) > 4000:
        errors.append("Prompt exceeds 4000 characters")
    if len(chatgpt_response) > 4000:
        errors.append("ChatGPT response exceeds 4000 characters")
    if len(gemini_response) > 4000:
        errors.append("Gemini response exceeds 4000 characters")
        
    return errors

# Dimension evaluation constants
DIMENSIONS = [
    "correctness", "completeness", "coherence", "relevance",
    "helpfulness", "creativity", "style_presentation"
]

DIMENSION_WEIGHTS = {
    "correctness": 0.25,
    "completeness": 0.15,
    "coherence": 0.15,
    "relevance": 0.15,
    "helpfulness": 0.15,
    "creativity": 0.05,
    "style_presentation": 0.10
}

def calculate_weighted_aggregate(scores: Dict[str, Any]) -> float:
    """Calculates the weighted average aggregate score out of 5.00."""
    total = 0.0
    for dim in DIMENSIONS:
        total += float(scores[dim]["score"]) * DIMENSION_WEIGHTS[dim]
    return round(total, 2)

def call_gemini(api_key: str, model_name: str, prompt: str) -> str:
    """Invokes Gemini using either the modern google-genai SDK or the legacy google-generativeai SDK."""
    try:
        # Try new SDK
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                top_p=0.9,
                top_k=40,
                max_output_tokens=8192,
            )
        )
        return response.text
    except Exception as e1:
        # Fallback to legacy SDK
        try:
            import google.generativeai as genai_legacy
            genai_legacy.configure(api_key=api_key)
            model = genai_legacy.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
            )
            return response.text
        except Exception as e2:
            raise RuntimeError(
                f"Failed to generate content with both Gemini SDK architectures.\n"
                f"google-genai Error: {e1}\n"
                f"google-generativeai Error: {e2}"
            )

def parse_gemini_response(text: str) -> Dict[str, Any]:
    """Cleans and extracts JSON object from Gemini response."""
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    
    # Locate JSON boundaries
    json_match = re.search(r'\{[\s\S]*\}', cleaned)
    if json_match:
        cleaned = json_match.group(0)
    else:
        raise ValueError("No valid JSON found in raw Gemini response text.")
        
    return json.loads(cleaned)

def validate_evaluation_structure(data: Dict[str, Any]) -> List[str]:
    """Checks the generated output structure and value limits, matching the original JS validation."""
    errors = []
    for model in ["chatgpt", "gemini"]:
        if model not in data:
            errors.append(f"Missing {model} evaluation block")
            continue
            
        model_data = data[model]
        for dim in DIMENSIONS:
            if dim not in model_data:
                errors.append(f"Missing dimension '{dim}' in {model}")
                continue
                
            dim_data = model_data[dim]
            if "score" not in dim_data:
                errors.append(f"Missing score in {model}.{dim}")
            elif not isinstance(dim_data["score"], (int, float)):
                errors.append(f"Score in {model}.{dim} must be a number")
            elif dim_data["score"] < 1 or dim_data["score"] > 5:
                errors.append(f"Score in {model}.{dim} must be between 1 and 5")
                
            if "explanation" not in dim_data:
                errors.append(f"Missing explanation in {model}.{dim}")
            elif not isinstance(dim_data["explanation"], str):
                errors.append(f"Explanation in {model}.{dim} must be a string")
            elif len(dim_data["explanation"]) < 50:
                errors.append(f"Explanation in {model}.{dim} is too short (min 50 chars)")
            elif len(dim_data["explanation"]) > 250:
                errors.append(f"Explanation in {model}.{dim} is too long (max 250 chars)")
                
    return errors

def evaluate_responses(
    prompt: str,
    chatgpt_response: str,
    gemini_response: str,
    api_key: str,
    model_name: str,
    retry_count: int = 1
) -> Dict[str, Any]:
    """Instructs Gemini to evaluate the responses, validating output structure with retries."""
    judge_prompt = f"""You are an impartial RLHF (Reinforcement Learning from Human Feedback) evaluator. Your role is to objectively assess AI responses.

Evaluate the ChatGPT and Gemini responses against the user's prompt using these 7 dimensions:

1. **correctness** (weight: 25%): Factual accuracy, absence of hallucinations, truthfulness
2. **completeness** (weight: 15%): How thoroughly all aspects of the prompt are addressed
3. **coherence** (weight: 15%): Logical flow, structure, internal consistency
4. **relevance** (weight: 15%): How closely the response stays on topic
5. **helpfulness** (weight: 15%): Practical utility, actionability, solution quality
6. **creativity** (weight: 5%): Originality, novel thinking, expressive depth
7. **style_presentation** (weight: 10%): Clarity, formatting, tone, readability

Likert Scale (1-5):
- 1 = Poor (significant issues)
- 2 = Fair (below average)
- 3 = Average (acceptable)
- 4 = Good (above average)
- 5 = Excellent (exceptional)

**User Prompt:**
{prompt}

**ChatGPT Response:**
{chatgpt_response}

**Gemini Response:**
{gemini_response}

**Output Requirements:**
- Return ONLY valid JSON (no markdown, no backticks, no explanatory text)
- Each explanation must be 100-250 characters
- Be strict and impartial in scoring
- Consider the weighted importance of each dimension

Return JSON matching this exact schema:
{{
  "chatgpt": {{
    "correctness": {{ "score": number, "explanation": "string" }},
    "completeness": {{ "score": number, "explanation": "string" }},
    "coherence": {{ "score": number, "explanation": "string" }},
    "relevance": {{ "score": number, "explanation": "string" }},
    "helpfulness": {{ "score": number, "explanation": "string" }},
    "creativity": {{ "score": number, "explanation": "string" }},
    "style_presentation": {{ "score": number, "explanation": "string" }}
  }},
  "gemini": {{
    "correctness": {{ "score": number, "explanation": "string" }},
    "completeness": {{ "score": number, "explanation": "string" }},
    "coherence": {{ "score": number, "explanation": "string" }},
    "relevance": {{ "score": number, "explanation": "string" }},
    "helpfulness": {{ "score": number, "explanation": "string" }},
    "creativity": {{ "score": number, "explanation": "string" }},
    "style_presentation": {{ "score": number, "explanation": "string" }}
  }}
}}"""

    try:
        raw_output = call_gemini(api_key, model_name, judge_prompt)
        parsed = parse_gemini_response(raw_output)
        
        # Verify structure
        struct_errors = validate_evaluation_structure(parsed)
        if struct_errors:
            raise ValueError(f"Output verification failed: {', '.join(struct_errors)}")
            
        # Calculate aggregates
        chatgpt_aggregate = calculate_weighted_aggregate(parsed["chatgpt"])
        gemini_aggregate = calculate_weighted_aggregate(parsed["gemini"])
        
        winner = "tie"
        if chatgpt_aggregate > gemini_aggregate:
            winner = "chatgpt"
        elif gemini_aggregate > chatgpt_aggregate:
            winner = "gemini"
            
        # Add aggregates to the final dictionary
        parsed["chatgpt"]["aggregate_score"] = chatgpt_aggregate
        parsed["gemini"]["aggregate_score"] = gemini_aggregate
        
        return {
            "chatgpt": parsed["chatgpt"],
            "gemini": parsed["gemini"],
            "winner": winner
        }
    except Exception as e:
        if retry_count > 0:
            print(f"Retrying evaluation due to error: {e}. {retry_count} retries left.")
            time.sleep(1)
            return evaluate_responses(prompt, chatgpt_response, gemini_response, api_key, model_name, retry_count - 1)
        raise e


@app.post("/api/evaluate")
async def evaluate_endpoint(request: Request):
    """Processes post evaluation, applying rate-limits, input cleaning, validation, and calling the judge."""
    ip = request.client.host if request.client else "127.0.0.1"
    
    rate_limit_max = int(os.getenv("RATE_LIMIT_MAX", "10"))
    rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW_MS", "60000"))
    
    if is_rate_limited(ip, rate_limit_max, rate_limit_window):
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": "Too many requests. Please try again later.",
                "code": "RATE_LIMIT_EXCEEDED"
            }
        )
        
    start_time = time.time()
    
    try:
        body = await request.json()
        prompt = body.get("prompt", "")
        chatgpt_response = body.get("chatgptResponse", "")
        gemini_response = body.get("geminiResponse", "")
        
        # Sanitization
        prompt = sanitize_input(prompt)
        chatgpt_response = sanitize_input(chatgpt_response)
        gemini_response = sanitize_input(gemini_response)
        
        # Length Validation
        validation_errors = validate_lengths(prompt, chatgpt_response, gemini_response)
        if validation_errors:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": validation_errors[0],
                    "code": "VALIDATION_ERROR",
                    "details": validation_errors
                }
            )
            
        # Truncation
        truncated_prompt = prompt[:4000]
        truncated_chatgpt = chatgpt_response[:4000]
        truncated_gemini = gemini_response[:4000]
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "error": "AI service API key is not configured. Please set GEMINI_API_KEY in your .env file.",
                    "code": "API_AUTH_ERROR"
                }
            )
            
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        
        evaluation_data = evaluate_responses(
            truncated_prompt,
            truncated_chatgpt,
            truncated_gemini,
            api_key,
            model_name
        )
        
        duration = int((time.time() - start_time) * 1000)
        
        return {
            "success": True,
            "data": evaluation_data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "duration_ms": duration
        }
        
    except Exception as error:
        error_msg = str(error)
        print("Evaluation error details:", error_msg)
        
        status_code = 500
        error_code = "INTERNAL_ERROR"
        error_display = "Evaluation failed. Please try again."
        
        if "JSON" in error_msg or "parse" in error_msg or "structure" in error_msg:
            status_code = 502
            error_code = "PARSE_ERROR"
            error_display = "Failed to parse AI judge response."
        elif "api key" in error_msg.lower() or "auth" in error_msg.lower() or "credentials" in error_msg.lower():
            status_code = 503
            error_code = "API_AUTH_ERROR"
            error_display = "AI service authentication failed."
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower() or "429" in error_msg.lower():
            status_code = 429
            error_code = "QUOTA_EXCEEDED"
            error_display = "API quota exceeded. Please try later."
            
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "error": error_display,
                "code": error_code
            }
        )

@app.get("/health")
def health_endpoint():
    """Simple healthcheck endpoint."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"}

@app.get("/", response_class=HTMLResponse)
def index_endpoint():
    """Serves the complete React + Tailwind + Chart.js Single Page UI."""
    html_content = """<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Response Evaluator</title>
  <!-- Google Fonts: Inter -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Chart.js CDN -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <!-- Canvas Confetti CDN -->
  <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
  
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            background: "#050816",
            card: "#111827",
            border: "#1F2937",
            primary: "#8B5CF6",
            secondary: "#06B6D4",
            accent: "#3B82F6",
            success: "#22C55E",
            warning: "#F59E0B",
            danger: "#EF4444"
          },
          fontFamily: {
            sans: ["Inter", "system-ui", "sans-serif"]
          }
        }
      }
    }
  </script>
  
  <style>
    body {
      background-color: #050816;
      color: #ffffff;
      font-family: 'Inter', system-ui, sans-serif;
    }
    
    .glass-card {
      background: rgba(17, 24, 39, 0.85);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(31, 41, 55, 0.5);
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
      border-radius: 1.25rem;
    }
    
    .gradient-mesh {
      background: radial-gradient(circle at 10% 20%, rgba(139, 92, 246, 0.15) 0%, transparent 45%),
                  radial-gradient(circle at 90% 10%, rgba(6, 182, 212, 0.15) 0%, transparent 45%),
                  radial-gradient(circle at 50% 90%, rgba(59, 130, 246, 0.1) 0%, transparent 50%);
    }
    
    @keyframes gradient-move {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }
    .animate-gradient {
      background-size: 200% 200%;
      animation: gradient-move 15s ease infinite;
    }
    
    @keyframes floating {
      0%, 100% { transform: translateY(0px) scale(1); }
      50% { transform: translateY(-15px) scale(1.05); }
    }
    .animate-float {
      animation: floating 8s ease-in-out infinite;
    }
    
    @keyframes spin-brain {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    .animate-spin-slow {
      animation: spin-brain 25s linear infinite;
    }

    @keyframes shake {
      10%, 90% { transform: translateX(-1px); }
      20%, 80% { transform: translateX(2px); }
      30%, 50%, 70% { transform: translateX(-4px); }
      40%, 60% { transform: translateX(4px); }
    }
    .animate-shake {
      animation: shake 0.5s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
    }

    /* Spring-like entries */
    .fade-in-up {
      animation: fadeInUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      opacity: 0;
      transform: translateY(20px);
    }
    @keyframes fadeInUp {
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
  </style>

  <!-- React 18 & ReactDOM 18 -->
  <script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js" crossorigin></script>
  <!-- Babel compiler for in-browser JSX support -->
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
</head>
<body class="relative min-h-screen overflow-x-hidden">

  <!-- Floating animated glow background blobs -->
  <div class="fixed inset-0 pointer-events-none z-0 overflow-hidden">
    <div class="absolute inset-0 gradient-mesh animate-gradient"></div>
    <div class="absolute top-20 left-10 w-72 h-72 bg-primary/10 rounded-full blur-3xl animate-float"></div>
    <div class="absolute bottom-20 right-10 w-96 h-96 bg-secondary/10 rounded-full blur-3xl animate-float" style="animation-delay: 2s;"></div>
  </div>

  <div id="root" class="relative z-10"></div>

  <script type="text/babel">
    const { useState, useEffect, useRef } = React;

    // Component-level SVGs for clean, zero-dependency visual assets
    function SparklesIcon({ className }) {
      return (
        <svg className={className} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275Z"/>
          <path d="m5 3 1 2.5L8.5 6 6 7 5 9.5 4 7 1.5 6 4 5.5Z"/>
          <path d="m19 17 1 2.5 2.5.5-2.5 1-1 2.5-1-2.5-2.5-1 2.5-1Z"/>
        </svg>
      );
    }

    function TrophyIcon({ className }) {
      return (
        <svg className={className} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/>
          <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/>
          <path d="M4 22h16"/>
          <path d="M10 14.66V17c0 .55-.45 1-1 1H4v2h16v-2h-5c-.55 0-1-.45-1-1v-2.34"/>
          <path d="M12 2a6 6 0 0 1 6 6v3.5c0 1.63-1.23 3.34-3.5 3.5h-5C7.23 12.84 6 11.13 6 9.5V8a6 6 0 0 1 6-6Z"/>
        </svg>
      );
    }

    function SendIcon({ className }) {
      return (
        <svg className={className} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="m22 2-7 20-4-9-9-4Z"/>
          <path d="M22 2 11 13"/>
        </svg>
      );
    }

    function AlertCircleIcon({ className }) {
      return (
        <svg className={className} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" x2="12" y1="8" y2="12"/>
          <line x1="12" x2="12.01" y1="16" y2="16"/>
        </svg>
      );
    }

    function RefreshCwIcon({ className }) {
      return (
        <svg className={className} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
          <path d="M21 3v5h-5"/>
          <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
          <path d="M3 21v-5h5"/>
        </svg>
      );
    }

    function ChevronDownIcon({ className }) {
      return (
        <svg className={className} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="m6 9 6 6 6-6"/>
        </svg>
      );
    }

    function BrainIcon({ className }) {
      return (
        <svg className={className} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 22a7 7 0 0 0 7-7c0-2.96-1.5-4.15-2.5-5.5a8 8 0 0 1-1.5-4.5 3 3 0 0 0-6 0c0 1.63-.5 3-1.5 4.5C6.5 10.85 5 12.04 5 15a7 7 0 0 0 7 7z"/>
          <path d="M12 6v12"/>
          <path d="M8 14h8"/>
        </svg>
      );
    }

    function CheckCircleIcon({ className }) {
      return (
        <svg className={className} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
          <path d="m9 11 3 3L22 4"/>
        </svg>
      );
    }

    function AlertTriangleIcon({ className }) {
      return (
        <svg className={className} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
          <line x1="12" x2="12" y1="9" y2="13"/>
          <line x1="12" x2="12.01" y1="17" y2="17"/>
        </svg>
      );
    }

    // Hero Section Component
    function Hero() {
      const handleScrollDown = () => {
        document.getElementById("input-form")?.scrollIntoView({ behavior: "smooth" });
      };

      return (
        <section className="relative min-h-screen flex flex-col items-center justify-center text-center px-6 z-10">
          <div className="fade-in-up flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 backdrop-blur-sm border border-primary/20 mb-8" style={{ animationDelay: "0.1s" }}>
            <SparklesIcon className="w-4 h-4 text-primary animate-pulse" />
            <span className="text-sm font-medium tracking-wide text-primary">
              Powered by Gemini 2.0 Flash
            </span>
          </div>

          <h1 className="fade-in-up text-5xl md:text-7xl font-extrabold tracking-tight mb-6 leading-none max-w-4xl" style={{ animationDelay: "0.3s" }}>
            Evaluate AI Responses. <br/>
            <span className="bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
              Objectively.
            </span>
          </h1>

          <p className="fade-in-up text-gray-400 text-lg md:text-xl max-w-2xl mx-auto leading-relaxed mb-12" style={{ animationDelay: "0.5s" }}>
            Compare ChatGPT and Gemini across <span className="text-primary font-semibold">7 RLHF dimensions</span>.
            Let our impartial AI judge determine the superior response.
          </p>

          <button
            onClick={handleScrollDown}
            className="fade-in-up mt-4 p-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-full transition-all duration-300 group hover:border-primary/50 shadow-lg shadow-black/30"
            style={{ animationDelay: "0.7s" }}
          >
            <ChevronDownIcon className="w-6 h-6 text-gray-400 group-hover:text-primary transition-colors" />
          </button>
        </section>
      );
    }

    // InputForm validation functions
    const validateForm = (prompt, chatgptResponse, geminiResponse) => {
      const errors = {};

      if (!prompt || prompt.trim().length === 0) {
        errors.prompt = "Prompt is required";
      } else if (prompt.length < 20) {
        errors.prompt = `Prompt must be at least 20 characters (currently ${prompt.length})`;
      } else if (prompt.length > 4000) {
        errors.prompt = `Prompt exceeds 4000 characters (currently ${prompt.length})`;
      }

      if (!chatgptResponse || chatgptResponse.trim().length === 0) {
        errors.chatgptResponse = "ChatGPT response is required";
      } else if (chatgptResponse.length < 50) {
        errors.chatgptResponse = `ChatGPT response must be at least 50 characters (currently ${chatgptResponse.length})`;
      } else if (chatgptResponse.length > 4000) {
        errors.chatgptResponse = `ChatGPT response exceeds 4000 characters (currently ${chatgptResponse.length})`;
      }

      if (!geminiResponse || geminiResponse.trim().length === 0) {
        errors.geminiResponse = "Gemini response is required";
      } else if (geminiResponse.length < 50) {
        errors.geminiResponse = `Gemini response must be at least 50 characters (currently ${geminiResponse.length})`;
      } else if (geminiResponse.length > 4000) {
        errors.geminiResponse = `Gemini response exceeds 4000 characters (currently ${geminiResponse.length})`;
      }

      return {
        isValid: Object.keys(errors).length === 0,
        errors
      };
    };

    const getCharColor = (length, min, max) => {
      if (length === 0) return "text-gray-500";
      if (length < min) return "text-danger";
      if (length > max) return "text-danger";
      return "text-success";
    };

    // InputForm Component
    function InputForm({ onSubmit, isSubmitting }) {
      const [formData, setFormData] = useState({
        prompt: "",
        chatgptResponse: "",
        geminiResponse: ""
      });

      const [errors, setErrors] = useState({});
      const [touched, setTouched] = useState({});
      const [shakeField, setShakeField] = useState("");

      const fields = [
        {
          name: "prompt",
          label: "User Prompt",
          placeholder: "Enter the prompt you want to evaluate...",
          min: 20,
          max: 4000,
          rows: 5
        },
        {
          name: "chatgptResponse",
          label: "ChatGPT Response",
          placeholder: "Paste ChatGPT's response here...",
          min: 50,
          max: 4000,
          rows: 8
        },
        {
          name: "geminiResponse",
          label: "Gemini Response",
          placeholder: "Paste Gemini's response here...",
          min: 50,
          max: 4000,
          rows: 8
        }
      ];

      const handleChange = (e) => {
        const { name, value } = e.target;
        const next = { ...formData, [name]: value };
        setFormData(next);

        if (errors[name]) {
          const validation = validateForm(next.prompt, next.chatgptResponse, next.geminiResponse);
          setErrors(prev => ({ ...prev, [name]: validation.errors[name] }));
        }
      };

      const handleBlur = (name) => {
        setTouched(prev => ({ ...prev, [name]: true }));

        const validation = validateForm(
          formData.prompt,
          formData.chatgptResponse,
          formData.geminiResponse
        );

        if (validation.errors[name]) {
          setErrors(prev => ({ ...prev, [name]: validation.errors[name] }));
        }
      };

      const handleSubmit = (e) => {
        e.preventDefault();

        const validation = validateForm(
          formData.prompt,
          formData.chatgptResponse,
          formData.geminiResponse
        );

        if (!validation.isValid) {
          setErrors(validation.errors);
          setTouched({ prompt: true, chatgptResponse: true, geminiResponse: true });

          const firstErrorField = Object.keys(validation.errors)[0];
          setShakeField(firstErrorField);
          setTimeout(() => setShakeField(""), 600);

          const element = document.querySelector(`[name="${firstErrorField}"]`);
          element?.scrollIntoView({ behavior: "smooth", block: "center" });
          return;
        }

        onSubmit(formData);
      };

      const getFieldStatus = (name, min, max) => {
        const value = formData[name];
        const length = value.length;
        const isTouched = touched[name];

        if (!isTouched || length === 0) return "neutral";
        if (length < min || length > max) return "error";
        return "success";
      };

      return (
        <section id="input-form" class="max-w-5xl mx-auto px-6 py-20 relative z-10 fade-in-up">
          <form onSubmit={handleSubmit} className="space-y-8">
            {fields.map((field, index) => {
              const value = formData[field.name];
              const length = value.length;
              const status = getFieldStatus(field.name, field.min, field.max);
              const showError = errors[field.name] && touched[field.name];
              const isShaking = shakeField === field.name;

              return (
                <div
                  key={field.name}
                  className={`glass-card p-6 transition-all duration-300 ${isShaking ? "animate-shake border-danger/60" : ""}`}
                >
                  <div className="flex justify-between items-center mb-3">
                    <label className="text-lg font-semibold text-white">
                      {field.label}
                      <span className="text-danger ml-1">*</span>
                    </label>
                    <div className="flex gap-4 text-sm font-medium">
                      <span className={getCharColor(length, field.min, field.max)}>
                        {length} / {field.max} chars
                      </span>
                      {length > 0 && length < field.min && (
                        <span className="text-warning animate-pulse">
                          Need {field.min - length} more
                        </span>
                      )}
                    </div>
                  </div>

                  <div>
                    <textarea
                      name={field.name}
                      value={value}
                      onChange={handleChange}
                      onBlur={() => handleBlur(field.name)}
                      placeholder={field.placeholder}
                      rows={field.rows}
                      className={`w-full bg-background border-2 rounded-xl p-4 text-gray-200
                        focus:outline-none focus:ring-2 focus:ring-primary transition-all duration-300 resize-none
                        ${status === "error" ? "border-danger focus:ring-danger" : "border-border focus:border-primary"}
                        ${status === "success" ? "border-success" : ""}`}
                    />
                  </div>

                  {showError && (
                    <div className="flex items-center gap-2 mt-2 text-danger text-sm font-medium animate-pulse">
                      <AlertCircleIcon className="w-4 h-4" />
                      <span>{errors[field.name]}</span>
                    </div>
                  )}

                  {length > 0 && (
                    <div className="mt-4 h-1.5 bg-border rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-300 ${
                          length < field.min ? "bg-warning" :
                          length > field.max ? "bg-danger" : "bg-success"
                        }`}
                        style={{ width: `${Math.min(100, (length / field.max) * 100)}%` }}
                      />
                    </div>
                  )}
                </div>
              );
            })}

            <div className="flex justify-center pt-6">
              <button
                type="submit"
                disabled={isSubmitting}
                className="bg-gradient-to-r from-primary via-accent to-secondary px-12 py-4 rounded-xl font-bold text-lg
                  flex items-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed
                  hover:shadow-xl hover:shadow-primary/20 hover:scale-[1.03] active:scale-[0.98] transition-all duration-300 border border-white/10"
              >
                {isSubmitting ? (
                  <>
                    <div className="w-5 h-5 border-3 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Evaluating Responses...</span>
                  </>
                ) : (
                  <>
                    <SendIcon className="w-5 h-5" />
                    <span>Run Evaluation</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </section>
      );
    }

    // LoadingOverlay Component
    function LoadingOverlay({ step, steps, progress }) {
      return (
        <div className="fixed inset-0 bg-black/95 backdrop-blur-md z-50 flex items-center justify-center">
          <div className="text-center max-w-md w-full px-6 flex flex-col items-center">
            
            <div className="mb-8 relative flex items-center justify-center">
              <div className="absolute inset-0 bg-primary/20 rounded-full blur-2xl animate-pulse-slow"></div>
              <div className="relative animate-spin-slow">
                <BrainIcon className="w-24 h-24 text-primary" />
              </div>
            </div>

            <h3 className="text-2xl font-bold mb-4 text-white min-h-[36px] transition-all duration-300 animate-pulse">
              {steps[step]}
            </h3>

            <div className="w-full h-2.5 bg-border rounded-full overflow-hidden mb-8 border border-white/5">
              <div
                className="h-full bg-gradient-to-r from-primary to-secondary rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>

            <div className="space-y-3 w-full text-left glass-card p-6">
              {steps.map((s, idx) => (
                <div
                  key={idx}
                  className={`flex items-center gap-3 text-sm transition-all duration-300 ${idx <= step ? "opacity-100" : "opacity-35"}`}
                >
                  {idx < step ? (
                    <CheckCircleIcon className="w-4 h-4 text-success" />
                  ) : idx === step ? (
                    <div className="w-4 h-4 bg-primary rounded-full animate-ping" />
                  ) : (
                    <div className="w-4 h-4 border-2 border-border rounded-full" />
                  )}
                  <span className={`font-medium ${idx === step ? "text-primary text-base font-semibold" : "text-gray-400"}`}>
                    {s}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    }

    // ErrorState Component
    function ErrorState({ message, onRetry }) {
      return (
        <div className="glass-card p-8 md:p-12 text-center max-w-2xl mx-auto border-danger/20 relative overflow-hidden fade-in-up">
          <div className="absolute inset-0 bg-danger/5 pointer-events-none"></div>
          <div className="animate-shake">
            <AlertTriangleIcon className="w-20 h-20 text-danger mx-auto mb-6" />
          </div>

          <h3 className="text-2xl font-bold mb-4 text-white">Evaluation Failed</h3>
          <p className="text-gray-400 mb-8 max-w-lg mx-auto leading-relaxed">{message}</p>

          {onRetry && (
            <button
              onClick={onRetry}
              className="flex items-center gap-2 mx-auto px-8 py-3 bg-danger hover:bg-danger/80
                rounded-xl font-semibold shadow-lg shadow-danger/25 transition-all duration-300 hover:scale-[1.03]"
            >
              <RefreshCwIcon className="w-4 h-4" />
              <span>Try Again</span>
            </button>
          )}
        </div>
      );
    }

    // WinnerBanner Component
    function WinnerBanner({ winner, chatgpt, gemini, onReset }) {
      useEffect(() => {
        if (winner === "tie") return;

        const duration = 3000;
        const animationEnd = Date.now() + duration;
        const defaults = { startVelocity: 35, spread: 360, ticks: 60, zIndex: 1000 };

        const randomInRange = (min, max) => Math.random() * (max - min) + min;

        const interval = setInterval(() => {
          const timeLeft = animationEnd - Date.now();

          if (timeLeft <= 0) {
            return clearInterval(interval);
          }

          const particleCount = 50 * (timeLeft / duration);

          confetti({
            ...defaults,
            particleCount,
            origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
          });
          confetti({
            ...defaults,
            particleCount,
            origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
          });
        }, 250);

        return () => clearInterval(interval);
      }, [winner]);

      const getWinnerColor = () => {
        if (winner === "chatgpt") return "from-blue-500 to-cyan-500";
        if (winner === "gemini") return "from-purple-500 to-pink-500";
        return "from-gray-500 to-gray-700";
      };

      const getWinnerGlow = () => {
        if (winner === "chatgpt") return "bg-blue-500/10";
        if (winner === "gemini") return "bg-purple-500/10";
        return "bg-gray-500/10";
      };

      const winnerName = winner === "chatgpt" ? "ChatGPT" : winner === "gemini" ? "Gemini" : "Tie";

      return (
        <div className="glass-card p-10 md:p-14 text-center relative overflow-hidden max-w-5xl mx-auto px-6 fade-in-up">
          <div className={`absolute inset-0 bg-gradient-to-r ${getWinnerColor()} opacity-[0.08]`} />
          <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] h-[80%] rounded-full blur-3xl pointer-events-none ${getWinnerGlow()}`} />

          <div className="relative z-10 flex flex-col items-center">
            <div className="p-4 bg-white/5 rounded-full border border-white/10 mb-6 backdrop-blur-sm animate-float">
              <TrophyIcon className={`w-20 h-20 ${
                winner === "chatgpt" ? "text-blue-500" :
                winner === "gemini" ? "text-purple-500" :
                "text-gray-500"
              }`} />
            </div>

            <h2 className="text-4xl md:text-6xl font-extrabold mb-4 tracking-tight">
              {winner === "tie" ? (
                <span className="bg-gradient-to-r from-gray-400 to-gray-600 bg-clip-text text-transparent">
                  It's a Tie!
                </span>
              ) : (
                <span className={`bg-gradient-to-r ${getWinnerColor()} bg-clip-text text-transparent`}>
                  {winnerName} Wins!
                </span>
              )}
            </h2>

            <div className="flex justify-center items-center gap-10 md:gap-14 mt-8 mb-10 w-full max-w-md">
              <div className="text-center flex-1">
                <p className="text-gray-400 text-sm font-semibold tracking-wider uppercase mb-1">ChatGPT</p>
                <p className="text-4xl md:text-5xl font-black text-blue-500">
                  {chatgpt.aggregate_score.toFixed(2)}
                </p>
              </div>

              <div className="text-2xl font-bold text-gray-600 tracking-wider">VS</div>

              <div className="text-center flex-1">
                <p className="text-gray-400 text-sm font-semibold tracking-wider uppercase mb-1">Gemini</p>
                <p className="text-4xl md:text-5xl font-black text-purple-500">
                  {gemini.aggregate_score.toFixed(2)}
                </p>
              </div>
            </div>

            <button
              onClick={onReset}
              className="flex items-center gap-2 px-8 py-3.5 bg-white/10 hover:bg-white/20 rounded-xl
                transition-all duration-300 text-gray-300 hover:text-white border border-white/10 shadow-lg"
            >
              <RefreshCwIcon className="w-4 h-4" />
              <span className="font-semibold text-sm">Evaluate Another Prompt</span>
            </button>
          </div>
        </div>
      );
    }

    // RadarChart Component (replaces recharts)
    function RadarChartComponent({ chatgpt, gemini }) {
      const canvasRef = useRef(null);
      const chartRef = useRef(null);
      const dimensions = [
        "correctness", "completeness", "coherence", "relevance",
        "helpfulness", "creativity", "style_presentation"
      ];
      
      const formatDimension = (dim) => {
        return dim.split("_").map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(" ");
      };

      useEffect(() => {
        if (!canvasRef.current) return;

        if (chartRef.current) {
          chartRef.current.destroy();
        }

        const ctx = canvasRef.current.getContext('2d');
        chartRef.current = new Chart(ctx, {
          type: 'radar',
          data: {
            labels: dimensions.map(formatDimension),
            datasets: [
              {
                label: 'ChatGPT',
                data: dimensions.map(dim => chatgpt[dim].score),
                borderColor: '#3B82F6',
                backgroundColor: 'rgba(59, 130, 246, 0.25)',
                borderWidth: 2,
                pointBackgroundColor: '#3B82F6',
                pointBorderColor: '#050816',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#3B82F6'
              },
              {
                label: 'Gemini',
                data: dimensions.map(dim => gemini[dim].score),
                borderColor: '#8B5CF6',
                backgroundColor: 'rgba(139, 92, 246, 0.25)',
                borderWidth: 2,
                pointBackgroundColor: '#8B5CF6',
                pointBorderColor: '#050816',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#8B5CF6'
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              r: {
                min: 0,
                max: 5,
                ticks: {
                  stepSize: 1,
                  color: '#6B7280',
                  backdropColor: 'transparent',
                  font: {
                    size: 10
                  }
                },
                grid: {
                  color: '#1F2937'
                },
                angleLines: {
                  color: '#1F2937'
                },
                pointLabels: {
                  color: '#9CA3AF',
                  font: {
                    size: 11,
                    family: 'Inter',
                    weight: '500'
                  }
                }
              }
            },
            plugins: {
              legend: {
                position: 'bottom',
                labels: {
                  color: '#D1D5DB',
                  font: {
                    family: 'Inter',
                    size: 12
                  },
                  padding: 15
                }
              },
              tooltip: {
                backgroundColor: '#111827',
                titleColor: '#ffffff',
                bodyColor: '#e5e7eb',
                borderColor: '#1F2937',
                borderWidth: 1,
                padding: 10,
                bodyFont: {
                  family: 'Inter'
                },
                titleFont: {
                  family: 'Inter',
                  weight: 'bold'
                }
              }
            }
          }
        });

        return () => {
          if (chartRef.current) {
            chartRef.current.destroy();
          }
        };
      }, [chatgpt, gemini]);

      return (
        <div className="glass-card p-6 h-[460px] flex flex-col justify-between fade-in-up">
          <h3 className="text-xl font-bold mb-4 text-center text-white">Performance Radar Chart</h3>
          <div className="relative flex-grow h-[360px]">
            <canvas ref={canvasRef}></canvas>
          </div>
        </div>
      );
    }

    // BarChart Component (replaces recharts)
    function BarChartComponent({ chatgptAggregate, geminiAggregate }) {
      const canvasRef = useRef(null);
      const chartRef = useRef(null);

      useEffect(() => {
        if (!canvasRef.current) return;

        if (chartRef.current) {
          chartRef.current.destroy();
        }

        const ctx = canvasRef.current.getContext('2d');
        chartRef.current = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: ['ChatGPT', 'Gemini'],
            datasets: [{
              data: [chatgptAggregate, geminiAggregate],
              backgroundColor: ['#3B82F6', '#8B5CF6'],
              borderRadius: 8,
              borderWidth: 0,
              barThickness: 36
            }]
          },
          options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              x: {
                min: 0,
                max: 5,
                grid: {
                  color: '#1F2937'
                },
                ticks: {
                  color: '#9CA3AF',
                  font: {
                    family: 'Inter'
                  }
                },
                title: {
                  display: true,
                  text: 'Aggregate Weighted Score (1-5)',
                  color: '#9CA3AF',
                  font: {
                    family: 'Inter',
                    weight: '500'
                  }
                }
              },
              y: {
                grid: {
                  display: false
                },
                ticks: {
                  color: '#9CA3AF',
                  font: {
                    size: 14,
                    family: 'Inter',
                    weight: 'bold'
                  }
                }
              }
            },
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                backgroundColor: '#111827',
                borderColor: '#1F2937',
                borderWidth: 1,
                padding: 10,
                bodyFont: {
                  family: 'Inter',
                  size: 13
                },
                callbacks: {
                  label: function(context) {
                    return ` Score: ${context.raw.toFixed(2)}/5.00`;
                  }
                }
              }
            }
          }
        });

        return () => {
          if (chartRef.current) {
            chartRef.current.destroy();
          }
        };
      }, [chatgptAggregate, geminiAggregate]);

      return (
        <div className="glass-card p-6 h-[460px] flex flex-col justify-between fade-in-up">
          <h3 className="text-xl font-bold mb-4 text-center text-white">Aggregate Score Comparison</h3>
          <div className="relative flex-grow h-[360px] flex items-center">
            <canvas ref={canvasRef}></canvas>
          </div>
        </div>
      );
    }

    // ScoreCard Component
    function ScoreCard({ title, data, delay }) {
      const score = data.score;

      const getScoreColor = (sc) => {
        if (sc >= 4) return "border-success bg-success/5";
        if (sc >= 3) return "border-warning bg-warning/5";
        return "border-danger bg-danger/5";
      };

      const getScoreTextColor = (sc) => {
        if (sc >= 4) return "text-success";
        if (sc >= 3) return "text-warning";
        return "text-danger";
      };

      const formatTitle = (rawTitle) => {
        return rawTitle.split("_").map(word =>
          word.charAt(0).toUpperCase() + word.slice(1)
        ).join(" ");
      };

      return (
        <div
          className={`p-6 rounded-2xl border-2 ${getScoreColor(score)} transition-all duration-300 hover:scale-[1.02] hover:shadow-lg`}
          style={{ animationDelay: `${delay}s` }}
        >
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-lg font-semibold text-white">
              {formatTitle(title)}
            </h3>
            <div className={`text-3xl font-black ${getScoreTextColor(score)}`}>
              {score}
              <span className="text-sm font-semibold text-gray-500">/5</span>
            </div>
          </div>

          <div className="flex gap-2.5 mb-4">
            {[1, 2, 3, 4, 5].map((pip) => (
              <div
                key={pip}
                className={`w-7 h-7 rounded-full transition-all duration-500 flex items-center justify-center font-bold text-xs ${
                  pip <= score
                    ? "bg-gradient-to-br from-primary to-secondary text-white shadow-md shadow-primary/20"
                    : "bg-gray-800 text-gray-500"
                }`}
              >
                {pip}
              </div>
            ))}
          </div>

          <p className="text-gray-300 text-sm leading-relaxed border-t border-white/5 pt-3">
            {data.explanation}
          </p>
        </div>
      );
    }

    // ResultsDashboard Component
    function ResultsDashboard({ results, onReset }) {
      const dimensions = [
        "correctness", "completeness", "coherence", "relevance",
        "helpfulness", "creativity", "style_presentation"
      ];

      return (
        <div className="space-y-12 pb-24 relative z-10 px-6 max-w-7xl mx-auto">
          <WinnerBanner
            winner={results.winner}
            chatgpt={results.chatgpt}
            gemini={results.gemini}
            onReset={onReset}
          />

          <div className="grid md:grid-cols-2 gap-8">
            <RadarChartComponent
              chatgpt={results.chatgpt}
              gemini={results.gemini}
            />
            <BarChartComponent
              chatgptAggregate={results.chatgpt.aggregate_score}
              geminiAggregate={results.gemini.aggregate_score}
            />
          </div>

          <div>
            <h2 className="text-3xl font-extrabold text-center mb-10 text-white tracking-tight">
              Detailed Dimension Analysis
            </h2>

            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-2xl font-bold mb-6 text-center bg-gradient-to-r from-blue-500 to-cyan-500 bg-clip-text text-transparent tracking-wide">
                  ChatGPT Responses
                </h3>
                <div className="space-y-5">
                  {dimensions.map((dim, idx) => (
                    <ScoreCard
                      key={`chatgpt-${dim}`}
                      title={dim}
                      data={results.chatgpt[dim]}
                      delay={idx * 0.05}
                    />
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-2xl font-bold mb-6 text-center bg-gradient-to-r from-purple-500 to-pink-500 bg-clip-text text-transparent tracking-wide">
                  Gemini Responses
                </h3>
                <div className="space-y-5">
                  {dimensions.map((dim, idx) => (
                    <ScoreCard
                      key={`gemini-${dim}`}
                      title={dim}
                      data={results.gemini[dim]}
                      delay={idx * 0.05}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }

    // Main App Component
    function App() {
      const [loading, setLoading] = useState(false);
      const [loadingStep, setLoadingStep] = useState(0);
      const [results, setResults] = useState(null);
      const [error, setError] = useState(null);
      const [showResults, setShowResults] = useState(false);

      const loadingSteps = [
        "Analyzing response formats...",
        "Evaluating correctness...",
        "Checking completeness...",
        "Assessing coherence & relevance...",
        "Measuring helpfulness & creativity...",
        "Reviewing style & presentation...",
        "Calculating weighted aggregate scores..."
      ];

      const handleEvaluate = async (formData) => {
        let stepInterval;
        try {
          setLoading(true);
          setError(null);
          setResults(null);
          setShowResults(false);
          setLoadingStep(0);

          // Cycle through visual steps while request is loading
          stepInterval = setInterval(() => {
            setLoadingStep(prev => Math.min(prev + 1, loadingSteps.length - 1));
          }, 900);

          const response = await fetch("/api/evaluate", {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify(formData)
          });

          const resData = await response.json();

          if (resData.success) {
            setResults(resData.data);
            setShowResults(true);
            setTimeout(() => {
              document.getElementById("results")?.scrollIntoView({ behavior: "smooth" });
            }, 250);
          } else {
            setError(resData.error || "Evaluation failed. Please try again.");
          }
        } catch (err) {
          console.error("Evaluation exception:", err);
          setError("Failed to communicate with the evaluation server. Please check your connection.");
        } finally {
          clearInterval(stepInterval);
          setLoading(false);
          setLoadingStep(0);
        }
      };

      const handleReset = () => {
        setResults(null);
        setError(null);
        setShowResults(false);
        window.scrollTo({ top: 0, behavior: "smooth" });
      };

      const handleRetry = () => {
        setResults(null);
        setError(null);
        setShowResults(false);
      };

      return (
        <div className="relative min-h-screen pb-16">
          <Hero />

          <InputForm onSubmit={handleEvaluate} isSubmitting={loading} />

          {loading && (
            <LoadingOverlay
              step={loadingStep}
              steps={loadingSteps}
              progress={(loadingStep / (loadingSteps.length - 1)) * 100}
            />
          )}

          {error && !loading && (
            <div className="px-6 pb-20 relative z-10">
              <ErrorState message={error} onRetry={handleRetry} />
            </div>
          )}

          {results && showResults && !loading && (
            <div id="results">
              <ResultsDashboard results={results} onReset={handleReset} />
            </div>
          )}
        </div>
      );
    }

    const root = ReactDOM.createRoot(document.getElementById("root"));
    root.render(<App />);
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    # Get configuration settings
    port = int(os.getenv("PORT", "3001"))
    
    print(f"Starting server in production-ready mode...")
    print(f"Local Access: http://localhost:{port}")
    
    uvicorn.run("golden_response:app", host="0.0.0.0", port=port, reload=True)
