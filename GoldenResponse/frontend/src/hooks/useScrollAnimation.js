import { useInView } from "framer-motion";
import { useRef } from "react";

export const useScrollAnimation = (threshold = 0.3) => {
  const ref = useRef(null);
  const isInView = useInView(ref, {
    once: true,
    amount: threshold,
    margin: "-100px"
  });

  return { ref, isInView };
};

export const staggerContainer = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.2
    }
  }
};

export const staggerItem = {
  hidden: { opacity: 0, y: 30 },
  show: {
    opacity: 1,
    y: 0,
    transition: {
      type: "spring",
      damping: 20,
      stiffness: 100
    }
  }
};
