import { motion } from "framer-motion";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from "recharts";
import { useScrollAnimation } from "../hooks/useScrollAnimation.js";

export default function BarChartComponent({ chatgptAggregate, geminiAggregate }) {
  const { ref, isInView } = useScrollAnimation(0.2);

  const data = [
    { name: "ChatGPT", score: chatgptAggregate, color: "#3B82F6" },
    { name: "Gemini", score: geminiAggregate, color: "#8B5CF6" }
  ];

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-card border border-border rounded-lg p-3 shadow-xl">
          <p className="text-white font-semibold">{payload[0].payload.name}</p>
          <p className="text-2xl font-bold text-primary">
            {payload[0].value.toFixed(2)}/5.00
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, x: -30 }}
      animate={isInView ? { opacity: 1, x: 0 } : {}}
      transition={{ duration: 0.6 }}
      className="glass-card p-6 h-[400px]"
    >
      <h3 className="text-xl font-bold mb-4 text-center">Aggregate Score Comparison</h3>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={data} layout="vertical" margin={{ left: 40 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            type="number"
            domain={[0, 5]}
            tick={{ fill: "#9CA3AF" }}
            label={{ value: "Score (1-5)", position: "bottom", fill: "#9CA3AF" }}
          />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fill: "#9CA3AF", fontSize: 14, fontWeight: "bold" }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar
            dataKey="score"
            animationDuration={1000}
            animationBegin={300}
            radius={[0, 8, 8, 0]}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </motion.div>
  );
}
