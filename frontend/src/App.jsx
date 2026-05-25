import { useState } from "react";
import { AnimatePresence } from "framer-motion";
import Hero from "./components/Hero.jsx";
import InputForm from "./components/InputForm.jsx";
import LoadingOverlay from "./components/LoadingOverlay.jsx";
import ResultsDashboard from "./components/ResultsDashboard.jsx";
import ErrorState from "./components/ErrorState.jsx";
import { useEvaluate } from "./hooks/useEvaluate.js";

export default function App() {
  const {
    loading,
    loadingStep,
    loadingSteps,
    results,
    error,
    evaluate,
    reset
  } = useEvaluate();

  const [showResults, setShowResults] = useState(false);

  const handleEvaluate = async (formData) => {
    const outcome = await evaluate(
      formData.prompt,
      formData.chatgptResponse,
      formData.geminiResponse
    );

    if (outcome.success) {
      setShowResults(true);
      setTimeout(() => {
        document.getElementById("results")?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } else {
      setShowResults(false);
    }
  };

  const handleReset = () => {
    reset();
    setShowResults(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleRetry = () => {
    reset();
    setShowResults(false);
  };

  return (
    <div className="relative">
      <Hero />

      <InputForm onSubmit={handleEvaluate} isSubmitting={loading} />

      <AnimatePresence>
        {loading && (
          <LoadingOverlay
            step={loadingStep}
            steps={loadingSteps}
            progress={(loadingStep / (loadingSteps.length - 1)) * 100}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {error && !loading && (
          <div className="px-6 pb-20">
            <ErrorState message={error} onRetry={handleRetry} />
          </div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {results && showResults && !loading && (
          <div id="results">
            <ResultsDashboard results={results} onReset={handleReset} />
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
