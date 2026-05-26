import sanitizeHtml from "sanitize-html";

export const sanitizeInput = (text = "") => {
  if (!text) return "";

  return sanitizeHtml(text, {
    allowedTags: [],
    allowedAttributes: {},
    disallowedTagsMode: "discard"
  }).trim();
};

export const validateLengths = (prompt, chatgptResponse, geminiResponse) => {
  const errors = [];

  if (prompt.length < 20) {
    errors.push("Prompt must be at least 20 characters");
  }
  if (chatgptResponse.length < 50) {
    errors.push("ChatGPT response must be at least 50 characters");
  }
  if (geminiResponse.length < 50) {
    errors.push("Gemini response must be at least 50 characters");
  }
  if (prompt.length > 4000) {
    errors.push("Prompt exceeds 4000 characters");
  }
  if (chatgptResponse.length > 4000) {
    errors.push("ChatGPT response exceeds 4000 characters");
  }
  if (geminiResponse.length > 4000) {
    errors.push("Gemini response exceeds 4000 characters");
  }

  return errors;
};
