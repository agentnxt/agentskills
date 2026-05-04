import fs from "node:fs";
import path from "node:path";

const rootDir = process.cwd();
const skillsDir = path.join(rootDir, "skills");
const outputPath = path.join(rootDir, "registry.json");

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function findSkillDirs(root) {
  const results = [];
  if (!fs.existsSync(root)) {
    return results;
  }

  const ignored = new Set(["node_modules", ".git", "dist", "build", "coverage"]);

  function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    const hasManifest = entries.some((entry) => entry.isFile() && entry.name === "skill.json");

    if (hasManifest) {
      results.push(dir);
      return;
    }

    for (const entry of entries) {
      if (entry.isDirectory() && !ignored.has(entry.name) && !entry.name.startsWith(".")) {
        walk(path.join(dir, entry.name));
      }
    }
  }

  walk(root);
  return results.sort();
}

function buildIndex() {
  const skills = [];

  if (!fs.existsSync(skillsDir)) {
    throw new Error("skills/ directory is missing.");
  }

  for (const skillDir of findSkillDirs(skillsDir)) {
    const manifestPath = path.join(skillDir, "skill.json");
    const manifest = readJson(manifestPath);
    const relativeSkillDir = path.relative(rootDir, skillDir);

    skills.push({
      id: manifest.id,
      name: manifest.name,
      version: manifest.version,
      description: manifest.description,
      status: manifest.status,
      license: manifest.license,
      tags: manifest.tags || [],
      categories: manifest.categories || [],
      runtime: manifest.runtime,
      dependencies: manifest.dependencies || [],
      permissions: manifest.permissions,
      outputs: manifest.outputs || [],
      homepage: manifest.homepage,
      repository: manifest.repository,
      path: relativeSkillDir,
      manifest: `${relativeSkillDir}/skill.json`,
      skill: `${relativeSkillDir}/${manifest.entrypoints?.skill || "SKILL.md"}`,
      readme: manifest.entrypoints?.readme ? `${relativeSkillDir}/${manifest.entrypoints.readme}` : undefined,
      maintainers: manifest.maintainers || []
    });
  }

  return {
    schemaVersion: "1.0.0",
    generatedAt: new Date().toISOString(),
    skillCount: skills.length,
    skills
  };
}

const index = buildIndex();
fs.writeFileSync(outputPath, `${JSON.stringify(index, null, 2)}\n`, "utf8");
console.log(`Wrote skill registry index with ${index.skillCount} skill(s) to registry.json.`);
