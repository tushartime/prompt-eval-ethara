import { motion } from "framer-motion";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip
} from "recharts";
import { useScrollAnimation } from "../hooks/useScrollAnimation.js";

export default function RadarChartComponent({ chatgpt, gemini }) {
  const { ref, isInView } = useScrollAnimation(0.2);

  const dimensions = [
    "correctness", "completeness", "coherence", "relevance",
    "helpfulness", "creativity", "style_presentation"
  ];

  const formatDimension = (dim) => {
    return dim.split("_").map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(" ");
  };

  const chartData = dimensions.map(dim => ({
    dimension: formatDimension(dim),
    ChatGPT: chatgpt[dim].score,
    Gemini: gemini[dim].score,
    fullMark: 5
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-card border border-border rounded-lg p-3 shadow-xl">
          <p className="font-semibold text-white mb-2">{payload[0].payload.dimension}</p>
          {payload.map((entry, idx) => (
            <p key={idx} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value}/5
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={isInView ? { opacity: 1, scale: 1 } : {}}
      transition={{ duration: 0.6 }}
      className="glass-card p-6 h-[500px]"
    >
      <h3 className="text-xl font-bold mb-4 text-center">Performance Radar Chart</h3>
      <ResponsiveContainer width="100%" height="90%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
          <PolarGrid stroke="#374151" />
          <PolarAngleAxis
            dataKey="dimension"
            tick={{ fill: "#9CA3AF", fontSize: 11 }}
          />
          <PolarRadiusAxis angle={30} domain={[0, 5]} tick={{ fill: "#6B7280" }} />
          <Radar
            name="ChatGPT"
            dataKey="ChatGPT"
            stroke="#3B82F6"
            fill="#3B82F6"
            fillOpacity={0.3}
            animationDuration={1000}
            animationBegin={0}
          />
          <Radar
            name="Gemini"
            dataKey="Gemini"
            stroke="#8B5CF6"
            fill="#8B5CF6"
            fillOpacity={0.3}
            animationDuration={1000}
            animationBegin={200}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ paddingTop: "20px" }}
            formatter={(value) => <span className="text-gray-300">{value}</span>}
          />
        </RadarChart>
      </ResponsiveContainer>
    </motion.div>
  );
}
