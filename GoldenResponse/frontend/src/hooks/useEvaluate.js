import { useState } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:3001";

export const useEvaluate = () => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [loadingStep, setLoadingStep] = useState(0);

  const loadingSteps = [
    "Analyzing responses...",
    "Evaluating correctness...",
    "Checking completeness...",
    "Assessing coherence & relevance...",
    "Measuring helpfulness & creativity...",
    "Reviewing style & presentation...",
    "Calculating weighted scores..."
  ];

  const evaluate = async (prompt, chatgptResponse, geminiResponse) => {
    let stepInterval;

    try {
      setLoading(true);
      setError(null);
      setResults(null);
      setLoadingStep(0);

      stepInterval = setInterval(() => {
        setLoadingStep(prev => Math.min(prev + 1, loadingSteps.length - 1));
      }, 800);

      const response = await axios.post(
        `${API_URL}/api/evaluate`,
        { prompt, chatgptResponse, geminiResponse },
        { timeout: 45000 }
      );

      if (response.data.success) {
        setResults(response.data.data);
        return { success: true, data: response.data.data };
      }

      const message = response.data.error || "Evaluation failed";
      setError(message);
      return { success: false, error: message };

    } catch (err) {
      console.error("Evaluation error:", err);

      let errorMessage = "Failed to evaluate responses. ";

      if (err.code === "ECONNABORTED") {
        errorMessage += "Request timed out. Please try again.";
      } else if (err.response?.status === 429) {
        errorMessage += "Rate limit exceeded. Please wait a moment.";
      } else if (err.response?.status === 502 || err.response?.status === 503) {
        errorMessage += "AI service temporarily unavailable. Please try again.";
      } else {
        errorMessage += err.response?.data?.error || "Please check your connection and try again.";
      }

      setError(errorMessage);
      return { success: false, error: errorMessage };

    } finally {
      clearInterval(stepInterval);
      setLoading(false);
      setLoadingStep(0);
    }
  };

  const reset = () => {
    setResults(null);
    setError(null);
  };

  return {
    loading,
    loadingStep,
    loadingSteps,
    results,
    error,
    evaluate,
    reset
  };
};
