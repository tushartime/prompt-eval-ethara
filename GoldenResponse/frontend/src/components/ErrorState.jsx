import { motion } from "framer-motion";
import { AlertTriangle, RefreshCw } from "lucide-react";

export default function ErrorState({ message, onRetry }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-card p-12 text-center max-w-2xl mx-auto"
    >
      <motion.div
        animate={{ rotate: [0, 10, -10, 0] }}
        transition={{ duration: 0.5, repeat: 2 }}
      >
        <AlertTriangle className="w-20 h-20 text-danger mx-auto mb-6" />
      </motion.div>

      <h3 className="text-2xl font-bold mb-4">Evaluation Failed</h3>
      <p className="text-gray-400 mb-8">{message}</p>

      {onRetry && (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onRetry}
          className="flex items-center gap-2 mx-auto px-6 py-3 bg-primary hover:bg-primary/80
            rounded-xl transition-all"
        >
          <RefreshCw className="w-4 h-4" />
          Try Again
        </motion.button>
      )}
    </motion.div>
  );
}
