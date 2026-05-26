import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, AlertCircle } from "lucide-react";
import { validateForm, getCharColor } from "../utils/validate.js";
import { useScrollAnimation, staggerContainer, staggerItem } from "../hooks/useScrollAnimation.js";

export default function InputForm({ onSubmit, isSubmitting }) {
  const [formData, setFormData] = useState({
    prompt: "",
    chatgptResponse: "",
    geminiResponse: ""
  });

  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const { ref, isInView } = useScrollAnimation(0.2);

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
    <motion.section
      ref={ref}
      initial="hidden"
      animate={isInView ? "show" : "hidden"}
      variants={staggerContainer}
      className="max-w-5xl mx-auto px-6 py-20"
    >
      <form onSubmit={handleSubmit} className="space-y-8">
        {fields.map((field, index) => {
          const value = formData[field.name];
          const length = value.length;
          const status = getFieldStatus(field.name, field.min, field.max);
          const showError = errors[field.name] && touched[field.name];

          return (
            <motion.div
              key={field.name}
              variants={staggerItem}
              custom={index}
              className="glass-card p-6"
            >
              <div className="flex justify-between items-center mb-3">
                <label className="text-lg font-semibold text-white">
                  {field.label}
                  <span className="text-danger ml-1">*</span>
                </label>
                <div className="flex gap-4 text-sm">
                  <span className={getCharColor(length, field.min, field.max)}>
                    {length} / {field.max} chars
                  </span>
                  {length > 0 && length < field.min && (
                    <span className="text-warning">
                      Need {field.min - length} more
                    </span>
                  )}
                </div>
              </div>

              <AnimatePresence mode="wait">
                <motion.div
                  key={status}
                  animate={showError ? { x: [-10, 10, -10, 10, 0] } : {}}
                  transition={{ duration: 0.4 }}
                >
                  <textarea
                    name={field.name}
                    value={value}
                    onChange={handleChange}
                    onBlur={() => handleBlur(field.name)}
                    placeholder={field.placeholder}
                    rows={field.rows}
                    className={`w-full bg-background border-2 rounded-xl p-4 text-gray-200
                      focus:outline-none focus:ring-2 focus:ring-primary transition-all resize-none
                      ${status === "error" ? "border-danger focus:ring-danger" : "border-border focus:border-primary"}
                      ${status === "success" ? "border-success" : ""}`}
                  />
                </motion.div>
              </AnimatePresence>

              <AnimatePresence>
                {showError && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="flex items-center gap-2 mt-2 text-danger text-sm"
                  >
                    <AlertCircle className="w-4 h-4" />
                    <span>{errors[field.name]}</span>
                  </motion.div>
                )}
              </AnimatePresence>

              {length > 0 && (
                <div className="mt-3 h-1 bg-border rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(100, (length / field.max) * 100)}%` }}
                    className={`h-full transition-all ${
                      length < field.min ? "bg-warning" :
                      length > field.max ? "bg-danger" : "bg-success"
                    }`}
                  />
                </div>
              )}
            </motion.div>
          );
        })}

        <motion.div variants={staggerItem} className="flex justify-center pt-6">
          <motion.button
            type="submit"
            disabled={isSubmitting}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            animate={!isSubmitting ? {
              boxShadow: ["0 0 0 0 rgba(139, 92, 246, 0.4)", "0 0 0 20px rgba(139, 92, 246, 0)"]
            } : {}}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="bg-gradient-to-r from-primary to-accent px-10 py-4 rounded-xl font-semibold text-lg
              flex items-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed
              hover:shadow-lg hover:shadow-primary/25 transition-all"
          >
            {isSubmitting ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                />
                Evaluating...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Run Evaluation
              </>
            )}
          </motion.button>
        </motion.div>
      </form>
    </motion.section>
  );
}
