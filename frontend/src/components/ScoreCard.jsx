import { motion } from "framer-motion";
import CountUp from "react-countup";
import { useScrollAnimation } from "../hooks/useScrollAnimation.js";

export default function ScoreCard({ title, data, delay = 0 }) {
  const score = data.score;
  const { ref, isInView } = useScrollAnimation(0.1);

  const getScoreColor = (score) => {
    if (score >= 4) return "border-success bg-success/5";
    if (score >= 3) return "border-warning bg-warning/5";
    return "border-danger bg-danger/5";
  };

  const getScoreTextColor = (score) => {
    if (score >= 4) return "text-success";
    if (score >= 3) return "text-warning";
    return "text-danger";
  };

  const formatTitle = (title) => {
    return title.split("_").map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(" ");
  };

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, delay }}
      className={`p-6 rounded-2xl border-2 ${getScoreColor(score)} transition-all hover:scale-[1.02]`}
    >
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold text-white">
          {formatTitle(title)}
        </h3>
        <div className={`text-3xl font-bold ${getScoreTextColor(score)}`}>
          {isInView && (
            <CountUp end={score} duration={1.5} decimals={0} />
          )}
          <span className="text-base text-gray-400">/5</span>
        </div>
      </div>

      <div className="flex gap-2 mb-4">
        {[1, 2, 3, 4, 5].map((pip) => (
          <motion.div
            key={pip}
            initial={{ scale: 0 }}
            animate={isInView ? { scale: 1 } : {}}
            transition={{ delay: delay + pip * 0.05, type: "spring", stiffness: 200 }}
            className={`w-8 h-8 rounded-full transition-all ${
              pip <= score
                ? "bg-gradient-to-r from-primary to-secondary shadow-lg shadow-primary/25"
                : "bg-gray-700"
            }`}
          />
        ))}
      </div>

      <motion.p
        initial={{ opacity: 0 }}
        animate={isInView ? { opacity: 1 } : {}}
        transition={{ delay: delay + 0.3 }}
        className="text-gray-300 text-sm leading-relaxed"
      >
        {data.explanation}
      </motion.p>
    </motion.div>
  );
}
