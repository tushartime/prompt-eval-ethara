import { motion, AnimatePresence } from "framer-motion";
import { Trophy, RefreshCw } from "lucide-react";
import confetti from "canvas-confetti";
import { useEffect } from "react";

export default function WinnerBanner({ winner, chatgpt, gemini, onReset }) {
  useEffect(() => {
    if (winner === "tie") return;

    const duration = 3000;
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 1000 };

    const randomInRange = (min, max) => Math.random() * (max - min) + min;

    const interval = setInterval(() => {
      const timeLeft = animationEnd - Date.now();

      if (timeLeft <= 0) {
        return clearInterval(interval);
      }

      const particleCount = 50 * (timeLeft / duration);

      confetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
      });
      confetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
      });
    }, 250);

    return () => clearInterval(interval);
  }, [winner]);

  const getWinnerColor = () => {
    if (winner === "chatgpt") return "from-blue-500 to-cyan-500";
    if (winner === "gemini") return "from-purple-500 to-pink-500";
    return "from-gray-500 to-gray-700";
  };

  const winnerName = winner === "chatgpt" ? "ChatGPT" : winner === "gemini" ? "Gemini" : "Tie";

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -50 }}
        className="glass-card p-12 text-center relative overflow-hidden max-w-5xl mx-auto px-6"
      >
        <motion.div
          className={`absolute inset-0 bg-gradient-to-r ${getWinnerColor()} opacity-10`}
          animate={{ scale: [1, 1.1, 1] }}
          transition={{ duration: 3, repeat: Infinity }}
        />

        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: "spring", stiffness: 200, damping: 15, delay: 0.2 }}
        >
          <Trophy className={`w-24 h-24 mx-auto mb-6 ${
            winner === "chatgpt" ? "text-blue-500" :
            winner === "gemini" ? "text-purple-500" :
            "text-gray-500"
          }`} />
        </motion.div>

        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="text-4xl md:text-6xl font-bold mb-4"
        >
          {winner === "tie" ? (
            <span className="bg-gradient-to-r from-gray-400 to-gray-600 bg-clip-text text-transparent">
              It&apos;s a Tie!
            </span>
          ) : (
            <span className={`bg-gradient-to-r ${getWinnerColor()} bg-clip-text text-transparent`}>
              {winnerName} Wins!
            </span>
          )}
        </motion.h2>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="flex justify-center items-center gap-12 mt-8 mb-8"
        >
          <div className="text-center">
            <p className="text-gray-400 mb-2">ChatGPT</p>
            <motion.p
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", delay: 0.8 }}
              className="text-4xl md:text-5xl font-bold text-blue-500"
            >
              {chatgpt.aggregate_score.toFixed(2)}
            </motion.p>
          </div>

          <div className="text-3xl font-bold text-gray-600">VS</div>

          <div className="text-center">
            <p className="text-gray-400 mb-2">Gemini</p>
            <motion.p
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", delay: 0.8 }}
              className="text-4xl md:text-5xl font-bold text-purple-500"
            >
              {gemini.aggregate_score.toFixed(2)}
            </motion.p>
          </div>
        </motion.div>

        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onReset}
          className="flex items-center gap-2 mx-auto px-8 py-3 bg-white/10 hover:bg-white/20 rounded-xl
            transition-all text-gray-300 hover:text-white border border-border"
        >
          <RefreshCw className="w-4 h-4" />
          Evaluate Another Prompt
        </motion.button>
      </motion.div>
    </AnimatePresence>
  );
}
