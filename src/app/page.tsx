"use client";

import { useState } from "react";
import { skills, categories } from "@/lib/data";
import SkillCard from "@/components/SkillCard";
import { Search, Layers } from "lucide-react";

export default function Home() {
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState("All");

  const filtered = skills.filter((skill) => {
    const matchesSearch =
      search === "" ||
      skill.display_name.toLowerCase().includes(search.toLowerCase()) ||
      skill.description.toLowerCase().includes(search.toLowerCase());
    const matchesCategory =
      activeCategory === "All" || skill.categories.includes(activeCategory);
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center gap-3 mb-1">
            <Layers className="w-7 h-7 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">Skill Gallery</h1>
          </div>
          <p className="text-gray-500 text-sm">
            Browse and compare AI agent skills across LLMs, frameworks, and tools. Each skill is benchmarked with eval scores.
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <div className="relative flex-grow">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search skills..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
            />
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mb-8">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
                activeCategory === cat
                  ? "bg-blue-600 text-white"
                  : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-6 mb-6 text-sm text-gray-500">
          <span>{filtered.length} skills</span>
          <span>{filtered.reduce((acc, s) => acc + s.tools.length, 0)} tools</span>
          <span>{filtered.reduce((acc, s) => acc + s.prompts.length, 0)} prompts</span>
          <span>{filtered.reduce((acc, s) => acc + s.evals.length, 0)} evals</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((skill) => (
            <SkillCard key={skill.id} skill={skill} />
          ))}
        </div>

        {filtered.length === 0 && (
          <div className="text-center py-16 text-gray-400">
            <p className="text-lg">No skills match your search</p>
            <p className="text-sm mt-1">Try a different search term or category</p>
          </div>
        )}
      </main>

      <footer className="border-t border-gray-200 bg-white mt-16">
        <div className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between text-sm text-gray-400">
          <span>AgentNXT Skill Gallery</span>
          <span>151 variables. 9 metrics. Every skill benchmarked.</span>
        </div>
      </footer>
    </div>
  );
}
