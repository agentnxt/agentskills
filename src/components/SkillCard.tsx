"use client";

import { Skill } from "@/lib/data";
import Link from "next/link";
import {
  Cloud,
  Workflow,
  Wrench,
  MessageSquare,
  FlaskConical,
} from "lucide-react";

const iconMap: Record<string, React.ReactNode> = {
  cloud: <Cloud className="w-6 h-6" />,
  workflow: <Workflow className="w-6 h-6" />,
};

function ScoreBadge({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color =
    pct >= 90
      ? "bg-emerald-100 text-emerald-800"
      : pct >= 70
        ? "bg-amber-100 text-amber-800"
        : "bg-red-100 text-red-800";
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${color}`}>
      {pct}%
    </span>
  );
}

export default function SkillCard({ skill }: { skill: Skill }) {
  return (
    <Link href={`/skills/${skill.id}`}>
      <div className="group bg-white rounded-xl border border-gray-200 p-6 hover:border-blue-400 hover:shadow-lg transition-all cursor-pointer h-full flex flex-col">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center text-blue-600 group-hover:bg-blue-100 transition-colors">
              {iconMap[skill.icon] || <Cloud className="w-6 h-6" />}
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                {skill.display_name}
              </h3>
              <span className="text-xs text-gray-400">v{skill.version}</span>
            </div>
          </div>
          <ScoreBadge score={skill.aggregate_score} />
        </div>

        {/* Description */}
        <p className="text-sm text-gray-600 mb-4 flex-grow">
          {skill.description}
        </p>

        {/* Categories */}
        <div className="flex flex-wrap gap-1.5 mb-4">
          {skill.categories.map((cat) => (
            <span
              key={cat}
              className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full"
            >
              {cat}
            </span>
          ))}
        </div>

        {/* Stats */}
        <div className="flex items-center gap-4 text-xs text-gray-500 border-t border-gray-100 pt-3">
          <div className="flex items-center gap-1">
            <Wrench className="w-3.5 h-3.5" />
            <span>{skill.tools.length} tools</span>
          </div>
          <div className="flex items-center gap-1">
            <MessageSquare className="w-3.5 h-3.5" />
            <span>{skill.prompts.length} prompts</span>
          </div>
          <div className="flex items-center gap-1">
            <FlaskConical className="w-3.5 h-3.5" />
            <span>{skill.evals.length} evals</span>
          </div>
        </div>

        {/* Benchmark preview */}
        {skill.benchmarks.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-500">
                {skill.benchmarks[0].llm} / {skill.benchmarks[0].framework}
              </span>
              <span className="text-gray-500">
                ${skill.benchmarks[0].cost_llm.toFixed(2)}
              </span>
            </div>
          </div>
        )}
      </div>
    </Link>
  );
}
