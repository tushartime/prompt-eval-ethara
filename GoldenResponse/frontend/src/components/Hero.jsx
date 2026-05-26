import { motion, useScroll, useTransform } from "framer-motion";
import { Sparkles, ChevronDown } from "lucide-react";
import { useRef } from "react";

export default function Hero() {
  const targetRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: targetRef,
    offset: ["start start", "end start"]
  });

  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.5], [1, 0.8]);
  const y = useTransform(scrollYProgress, [0, 0.5], [0, 100]);

  const words = "Evaluate AI Responses. Objectively.".split(" ");

  return (
    <section ref={targetRef} className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <div className="absolute inset-0 gradient-mesh animate-gradient" />

      <motion.div
        className="absolute top-20 left-10 w-64 h-64 bg-primary/20 rounded-full blur-3xl"
        animate={{ y: [0, -30, 0], x: [0, 20, 0] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute bottom-20 right-10 w-96 h-96 bg-secondary/20 rounded-full blur-3xl"
        animate={{ y: [0, 30, 0], x: [0, -20, 0] }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 1 }}
      />

      <motion.div
        style={{ opacity, scale, y }}
        className="relative z-10 text-center px-6 max-w-6xl mx-auto"
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 backdrop-blur-sm border border-primary/20 mb-8"
        >
          <Sparkles className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium tracking-wide text-primary">
            Powered by Gemini 2.0 Flash
          </span>
        </motion.div>

        <h1 className="text-6xl md:text-8xl font-bold tracking-tight mb-6">
          {words.map((word, i) => (
            <motion.span
              key={i}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: i * 0.1, type: "spring", stiffness: 100 }}
              className="inline-block mr-4"
            >
              {word === "Objectively." ? (
                <span className="bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
                  {word}
                </span>
              ) : word}
            </motion.span>
          ))}
        </h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.8 }}
          className="text-gray-400 text-xl md:text-2xl max-w-3xl mx-auto leading-relaxed"
        >
          Compare ChatGPT and Gemini across <span className="text-primary font-semibold">7 RLHF dimensions</span>.
          Let our impartial AI judge determine the superior response.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.6 }}
          className="absolute bottom-10 left-1/2 -translate-x-1/2"
        >
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
          >
            <ChevronDown className="w-8 h-8 text-gray-400" />
          </motion.div>
        </motion.div>
      </motion.div>
    </section>
  );
}
