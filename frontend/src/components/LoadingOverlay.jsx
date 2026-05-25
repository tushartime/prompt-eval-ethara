import { motion, AnimatePresence } from "framer-motion";
import { Brain, CheckCircle } from "lucide-react";

export default function LoadingOverlay({ step, steps, progress }) {
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/95 backdrop-blur-md z-50 flex items-center justify-center"
      >
        <div className="text-center max-w-md mx-auto px-6">
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              rotate: [0, 360]
            }}
            transition={{
              scale: { duration: 2, repeat: Infinity },
              rotate: { duration: 20, repeat: Infinity, ease: "linear" }
            }}
            className="mb-8"
          >
            <Brain className="w-20 h-20 text-primary mx-auto" />
          </motion.div>

          <motion.h3
            key={step}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-2xl font-bold mb-4"
          >
            {steps[step]}
          </motion.h3>

          <div className="w-full h-2 bg-border rounded-full overflow-hidden mb-6">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5 }}
              className="h-full bg-gradient-to-r from-primary to-secondary rounded-full"
            />
          </div>

          <div className="space-y-2">
            {steps.map((s, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0.3 }}
                animate={{ opacity: idx <= step ? 1 : 0.3 }}
                className="flex items-center gap-3 text-sm"
              >
                {idx < step ? (
                  <CheckCircle className="w-4 h-4 text-success" />
                ) : idx === step ? (
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                    className="w-4 h-4 bg-primary rounded-full"
                  />
                ) : (
                  <div className="w-4 h-4 border-2 border-border rounded-full" />
                )}
                <span className={idx === step ? "text-primary" : "text-gray-400"}>
                  {s}
                </span>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
