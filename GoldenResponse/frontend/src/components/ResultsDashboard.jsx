import { motion } from "framer-motion";
import ScoreCard from "./ScoreCard.jsx";
import RadarChartComponent from "./RadarChart.jsx";
import BarChartComponent from "./BarChart.jsx";
import WinnerBanner from "./WinnerBanner.jsx";

export default function ResultsDashboard({ results, onReset }) {
  const dimensions = [
    "correctness", "completeness", "coherence", "relevance",
    "helpfulness", "creativity", "style_presentation"
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-12 pb-20"
    >
      <WinnerBanner
        winner={results.winner}
        chatgpt={results.chatgpt}
        gemini={results.gemini}
        onReset={onReset}
      />

      <div className="grid md:grid-cols-2 gap-8 max-w-7xl mx-auto px-6">
        <RadarChartComponent
          chatgpt={results.chatgpt}
          gemini={results.gemini}
        />
        <BarChartComponent
          chatgptAggregate={results.chatgpt.aggregate_score}
          geminiAggregate={results.gemini.aggregate_score}
        />
      </div>

      <div className="max-w-7xl mx-auto px-6">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl font-bold text-center mb-8"
        >
          Detailed Dimension Analysis
        </motion.h2>

        <div className="grid md:grid-cols-2 gap-8">
          <div>
            <motion.h3
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-2xl font-bold mb-6 text-center bg-gradient-to-r from-blue-500 to-cyan-500 bg-clip-text text-transparent"
            >
              ChatGPT
            </motion.h3>
            <div className="space-y-4">
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
            <motion.h3
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-2xl font-bold mb-6 text-center bg-gradient-to-r from-purple-500 to-pink-500 bg-clip-text text-transparent"
            >
              Gemini
            </motion.h3>
            <div className="space-y-4">
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
    </motion.div>
  );
}
