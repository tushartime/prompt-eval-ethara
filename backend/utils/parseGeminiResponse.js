export const parseGeminiResponse = (text) => {
  let cleaned = text.replace(/```json\s*/g, "").replace(/```\s*/g, "");

  const jsonMatch = cleaned.match(/\{[\s\S]*\}/);
  if (!jsonMatch) {
    throw new Error("No valid JSON found in response");
  }

  cleaned = jsonMatch[0];

  try {
    return JSON.parse(cleaned);
  } catch (error) {
    throw new Error(`JSON parse failed: ${error.message}`);
  }
};

export const validateEvaluationStructure = (data) => {
  const requiredDimensions = [
    "correctness", "completeness", "coherence", "relevance",
    "helpfulness", "creativity", "style_presentation"
  ];

  const errors = [];

  for (const model of ["chatgpt", "gemini"]) {
    if (!data[model]) {
      errors.push(`Missing ${model} object`);
      continue;
    }

    for (const dim of requiredDimensions) {
      if (!data[model][dim]) {
        errors.push(`Missing ${model}.${dim}`);
      } else if (typeof data[model][dim].score !== "number") {
        errors.push(`${model}.${dim}.score must be a number`);
      } else if (data[model][dim].score < 1 || data[model][dim].score > 5) {
        errors.push(`${model}.${dim}.score must be between 1-5`);
      } else if (!data[model][dim].explanation || data[model][dim].explanation.length < 50) {
        errors.push(`${model}.${dim}.explanation too short (min 50 chars)`);
      } else if (data[model][dim].explanation.length > 250) {
        errors.push(`${model}.${dim}.explanation too long (max 250 chars)`);
      }
    }
  }

  return errors;
};
