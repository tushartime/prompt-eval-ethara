export const validateForm = (prompt, chatgptResponse, geminiResponse) => {
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

export const getCharColor = (length, min, max) => {
  if (length === 0) return "text-gray-500";
  if (length < min) return "text-danger";
  if (length > max) return "text-danger";
  return "text-success";
};
