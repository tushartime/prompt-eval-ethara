import rateLimit from "express-rate-limit";

const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || "60000"),
  max: parseInt(process.env.RATE_LIMIT_MAX || "10"),
  message: {
    success: false,
    error: "Too many requests. Please try again later.",
    code: "RATE_LIMIT_EXCEEDED"
  },
  standardHeaders: true,
  legacyHeaders: false
});

export default limiter;
