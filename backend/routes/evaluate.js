import express from "express";
import { sanitizeInput, validateLengths } from "../middleware/sanitize.js";
import { evaluateResponses } from "../services/geminiJudge.js";

const router = express.Router();

router.post("/", async (req, res) => {
  const startTime = Date.now();

  try {
    let { prompt, chatgptResponse, geminiResponse } = req.body;

    prompt = sanitizeInput(prompt);
    chatgptResponse = sanitizeInput(chatgptResponse);
    geminiResponse = sanitizeInput(geminiResponse);

    const validationErrors = validateLengths(prompt, chatgptResponse, geminiResponse);
    if (validationErrors.length > 0) {
      return res.status(400).json({
        success: false,
        error: validationErrors[0],
        code: "VALIDATION_ERROR",
        details: validationErrors
      });
    }

    const truncatedPrompt = prompt.slice(0, 4000);
    const truncatedChatGPT = chatgptResponse.slice(0, 4000);
    const truncatedGemini = geminiResponse.slice(0, 4000);

    const evaluationData = await evaluateResponses(
      truncatedPrompt,
      truncatedChatGPT,
      truncatedGemini
    );

    const duration = Date.now() - startTime;

    res.status(200).json({
      success: true,
      data: evaluationData,
      timestamp: new Date().toISOString(),
      duration_ms: duration
    });

  } catch (error) {
    console.error("Evaluation error:", error);

    let statusCode = 500;
    let errorCode = "INTERNAL_ERROR";
    let errorMessage = "Evaluation failed. Please try again.";

    if (error.message.includes("JSON") || error.message.includes("parse")) {
      statusCode = 502;
      errorCode = "PARSE_ERROR";
      errorMessage = "Failed to parse AI judge response.";
    } else if (error.message.includes("API key") || error.message.includes("authentication")) {
      statusCode = 503;
      errorCode = "API_AUTH_ERROR";
      errorMessage = "AI service authentication failed.";
    } else if (error.message.includes("quota") || error.message.includes("limit")) {
      statusCode = 429;
      errorCode = "QUOTA_EXCEEDED";
      errorMessage = "API quota exceeded. Please try later.";
    }

    res.status(statusCode).json({
      success: false,
      error: errorMessage,
      code: errorCode
    });
  }
});

export default router;
