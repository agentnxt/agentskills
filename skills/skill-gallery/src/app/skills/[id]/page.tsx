"use client";

import { use, useState } from "react";
import { skills } from "@/lib/data";
import Link from "next/link";
import {
  ArrowLeft,
  Wrench,
  MessageSquare,
  FlaskConical,
  BarChart3,
  Copy,
  Check,
  Cloud,
  Workflow,
} from "lucide-react";

const iconMap: Record<string, React.ReactNode> = {
  cloud: <Cloud className="w-8 h-8" />,
  workflow: <Workflow className="w-8 h-8" />,
};

type TabType = "tools" | "prompts" | "evals" | "benchmarks";

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={(e) => {
        e.stopPropagation();
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }}
      className="p-1.5 rounded-md hover:bg-gray-100 transition-colors"
      title="Copy prompt"
    >
      {copied ? (
        <Check className="w-4 h-4 text-emerald-500" />
      ) : (
        <Copy className="w-4 h-4 text-gray-400" />
      )}
    </button>
  );
}

export default function SkillDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [activeTab, setActiveTab] = useState<TabType>("tools");
  const skill = skills.find((s) => s.id === id);

  if (!skill) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-400 text-lg">Skill not found</p>
          <Link href="/" className="text-blue-600 text-sm mt-2 inline-block">
            Back to gallery
          </Link>
        </div>
      </div>
    );
  }

  const tabs: { key: TabType; label: string; icon: React.ReactNode; count: number }[] = [
    { key: "tools", label: "Tools", icon: <Wrench className="w-4 h-4" />, count: skill.tools.length },
    { key: "prompts", label: "Prompts", icon: <MessageSquare className="w-4 h-4" />, count: skill.prompts.length },
    { key: "evals", label: "Evals", icon: <FlaskConical className="w-4 h-4" />, count: skill.evals.length },
    { key: "benchmarks", label: "Benchmarks", icon: <BarChart3 className="w-4 h-4" />, count: skill.benchmarks.length },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-6 py-6">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to gallery
          </Link>

          <div className="flex items-start gap-4">
            <div className="w-14 h-14 bg-blue-50 rounded-xl flex items-center justify-center text-blue-600">
              {iconMap[skill.icon] || <Cloud className="w-8 h-8" />}
            </div>
            <div className="flex-grow">
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold text-gray-900">
                  {skill.display_name}
                </h1>
                <span className="text-sm text-gray-400">v{skill.version}</span>
                <span
                  className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${
                    skill.aggregate_score >= 0.9
                      ? "bg-emerald-100 text-emerald-800"
                      : skill.aggregate_score >= 0.7
                        ? "bg-amber-100 text-amber-800"
                        : "bg-red-100 text-red-800"
                  }`}
                >
                  {Math.round(skill.aggregate_score * 100)}% eval score
                </span>
              </div>
              <p className="text-gray-600 text-sm mt-1 max-w-2xl">
                {skill.long_description}
              </p>
              <div className="flex flex-wrap gap-1.5 mt-3">
                {skill.categories.map((cat) => (
                  <span
                    key={cat}
                    className="text-xs bg-gray-100 text-gray-600 px-2.5 py-0.5 rounded-full"
                  >
                    {cat}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        {/* Tabs */}
        <div className="flex gap-1 border-b border-gray-200 mb-8">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.key
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {tab.icon}
              {tab.label}
              <span className="text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded-full">
                {tab.count}
              </span>
            </button>
          ))}
        </div>

        {/* Tools Tab */}
        {activeTab === "tools" && (
          <div className="space-y-4">
            {skill.tools.map((tool, i) => (
              <div
                key={i}
                className="bg-white rounded-xl border border-gray-200 p-5"
              >
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-sm font-mono font-semibold text-gray-900">
                    {tool.name}
                  </span>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full ${
                      tool.type === "script"
                        ? "bg-purple-100 text-purple-700"
                        : tool.type === "api"
                          ? "bg-blue-100 text-blue-700"
                          : "bg-green-100 text-green-700"
                    }`}
                  >
                    {tool.type}
                  </span>
                  {tool.language && (
                    <span className="text-xs text-gray-400">
                      {tool.language}
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600">{tool.description}</p>
              </div>
            ))}
          </div>
        )}

        {/* Prompts Tab */}
        {activeTab === "prompts" && (
          <div className="space-y-4">
            {skill.prompts.map((prompt, i) => (
              <div
                key={i}
                className="bg-white rounded-xl border border-gray-200 p-5"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                      {prompt.category}
                    </span>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        prompt.complexity === "high"
                          ? "bg-red-50 text-red-600"
                          : prompt.complexity === "medium"
                            ? "bg-amber-50 text-amber-600"
                            : "bg-green-50 text-green-600"
                      }`}
                    >
                      {prompt.complexity}
                    </span>
                  </div>
                  <CopyButton text={prompt.text} />
                </div>
                <p className="text-sm text-gray-700 font-mono leading-relaxed">
                  {prompt.text}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Evals Tab */}
        {activeTab === "evals" && (
          <div className="space-y-4">
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <th className="px-5 py-3">Test Case</th>
                    <th className="px-5 py-3">With Skill</th>
                    <th className="px-5 py-3">Baseline</th>
                    <th className="px-5 py-3">Delta</th>
                    <th className="px-5 py-3">Note</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {skill.evals.map((ev, i) => {
                    const withPct = Math.round(
                      (ev.with_skill_score / ev.with_skill_total) * 100
                    );
                    const basePct = Math.round(
                      (ev.baseline_score / ev.baseline_total) * 100
                    );
                    const delta = withPct - basePct;
                    return (
                      <tr key={i}>
                        <td className="px-5 py-3.5 text-sm font-medium text-gray-900">
                          {ev.name}
                        </td>
                        <td className="px-5 py-3.5">
                          <span
                            className={`text-sm font-semibold ${
                              withPct >= 90
                                ? "text-emerald-600"
                                : withPct >= 70
                                  ? "text-amber-600"
                                  : "text-red-600"
                            }`}
                          >
                            {ev.with_skill_score}/{ev.with_skill_total} ({withPct}%)
                          </span>
                        </td>
                        <td className="px-5 py-3.5 text-sm text-gray-500">
                          {ev.baseline_score}/{ev.baseline_total} ({basePct}%)
                        </td>
                        <td className="px-5 py-3.5">
                          <span
                            className={`text-sm font-semibold ${
                              delta > 0
                                ? "text-emerald-600"
                                : delta < 0
                                  ? "text-red-600"
                                  : "text-gray-400"
                            }`}
                          >
                            {delta > 0 ? "+" : ""}
                            {delta}%
                          </span>
                        </td>
                        <td className="px-5 py-3.5 text-xs text-gray-400">
                          {ev.note || "—"}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Benchmarks Tab */}
        {activeTab === "benchmarks" && (
          <div className="space-y-4">
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <th className="px-5 py-3">LLM</th>
                    <th className="px-5 py-3">Framework</th>
                    <th className="px-5 py-3">Score</th>
                    <th className="px-5 py-3">Tokens</th>
                    <th className="px-5 py-3">Duration</th>
                    <th className="px-5 py-3">LLM Cost</th>
                    <th className="px-5 py-3">Infra Cost</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {skill.benchmarks.map((b, i) => (
                    <tr key={i}>
                      <td className="px-5 py-3.5 text-sm font-medium text-gray-900">
                        {b.llm}
                      </td>
                      <td className="px-5 py-3.5 text-sm text-gray-600">
                        {b.framework}
                      </td>
                      <td className="px-5 py-3.5">
                        <span
                          className={`text-sm font-semibold ${
                            b.eval_score >= 0.9
                              ? "text-emerald-600"
                              : b.eval_score >= 0.7
                                ? "text-amber-600"
                                : "text-red-600"
                          }`}
                        >
                          {Math.round(b.eval_score * 100)}%
                        </span>
                      </td>
                      <td className="px-5 py-3.5 text-sm text-gray-600">
                        {b.tokens.toLocaleString()}
                      </td>
                      <td className="px-5 py-3.5 text-sm text-gray-600">
                        {b.duration_seconds}s
                      </td>
                      <td className="px-5 py-3.5 text-sm text-gray-600">
                        ${b.cost_llm.toFixed(2)}
                      </td>
                      <td className="px-5 py-3.5 text-sm text-gray-600">
                        ${b.cost_infra.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-xs text-gray-400 text-center">
              More LLM/framework combinations coming soon
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
