import { GoogleGenerativeAI } from "@google/generative-ai";
import { parseGeminiResponse, validateEvaluationStructure } from "../utils/parseGeminiResponse.js";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

const DIMENSIONS = [
  "correctness", "completeness", "coherence", "relevance",
  "helpfulness", "creativity", "style_presentation"
];

const DIMENSION_WEIGHTS = {
  correctness: 0.25,
  completeness: 0.15,
  coherence: 0.15,
  relevance: 0.15,
  helpfulness: 0.15,
  creativity: 0.05,
  style_presentation: 0.10
};

const calculateWeightedAggregate = (scores) => {
  let total = 0;
  for (const dim of DIMENSIONS) {
    total += scores[dim].score * DIMENSION_WEIGHTS[dim];
  }
  return Number(total.toFixed(2));
};

const buildJudgePrompt = (prompt, chatgptResponse, geminiResponse) => {
  return `You are an impartial RLHF (Reinforcement Learning from Human Feedback) evaluator. Your role is to objectively assess AI responses.

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
${prompt}

**ChatGPT Response:**
${chatgptResponse}

**Gemini Response:**
${geminiResponse}

**Output Requirements:**
- Return ONLY valid JSON (no markdown, no backticks, no explanatory text)
- Each explanation must be 100-250 characters
- Be strict and impartial in scoring
- Consider the weighted importance of each dimension

Return JSON matching this exact schema:
{
  "chatgpt": {
    "correctness": { "score": number, "explanation": "string" },
    "completeness": { "score": number, "explanation": "string" },
    "coherence": { "score": number, "explanation": "string" },
    "relevance": { "score": number, "explanation": "string" },
    "helpfulness": { "score": number, "explanation": "string" },
    "creativity": { "score": number, "explanation": "string" },
    "style_presentation": { "score": number, "explanation": "string" }
  },
  "gemini": {
    "correctness": { "score": number, "explanation": "string" },
    "completeness": { "score": number, "explanation": "string" },
    "coherence": { "score": number, "explanation": "string" },
    "relevance": { "score": number, "explanation": "string" },
    "helpfulness": { "score": number, "explanation": "string" },
    "creativity": { "score": number, "explanation": "string" },
    "style_presentation": { "score": number, "explanation": "string" }
  }
}`;
};

export const evaluateResponses = async (prompt, chatgptResponse, geminiResponse, retryCount = 1) => {
  const model = genAI.getGenerativeModel({
    model: process.env.GEMINI_MODEL || "gemini-2.0-flash",
    generationConfig: {
      temperature: 0.2,
      topP: 0.9,
      topK: 40,
      maxOutputTokens: 8192,
    }
  });

  const judgePrompt = buildJudgePrompt(prompt, chatgptResponse, geminiResponse);

  try {
    const result = await model.generateContent(judgePrompt);
    const responseText = result.response.text();

    const parsed = parseGeminiResponse(responseText);

    const validationErrors = validateEvaluationStructure(parsed);
    if (validationErrors.length > 0) {
      throw new Error(`Invalid response structure: ${validationErrors.join(", ")}`);
    }

    const chatgptAggregate = calculateWeightedAggregate(parsed.chatgpt);
    const geminiAggregate = calculateWeightedAggregate(parsed.gemini);

    let winner = "tie";
    if (chatgptAggregate > geminiAggregate) winner = "chatgpt";
    else if (geminiAggregate > chatgptAggregate) winner = "gemini";

    return {
      chatgpt: {
        ...parsed.chatgpt,
        aggregate_score: chatgptAggregate
      },
      gemini: {
        ...parsed.gemini,
        aggregate_score: geminiAggregate
      },
      winner
    };

  } catch (error) {
    if (retryCount > 0) {
      console.log(`Retrying evaluation... (${retryCount} attempts left)`);
      await new Promise(resolve => setTimeout(resolve, 1000));
      return evaluateResponses(prompt, chatgptResponse, geminiResponse, retryCount - 1);
    }
    throw error;
  }
};
