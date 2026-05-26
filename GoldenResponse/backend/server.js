import express from "express";
import dotenv from "dotenv";
import cors from "cors";
import evaluateRoute from "./routes/evaluate.js";
import limiter from "./middleware/rateLimiter.js";

dotenv.config();

const app = express();

app.use(cors({
  origin: process.env.FRONTEND_URL || "http://localhost:5173"
}));

app.use(express.json({ limit: "1mb" }));
app.use(limiter);
app.use("/api/evaluate", evaluateRoute);

app.get("/health", (_, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

const PORT = process.env.PORT || 3001;

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
