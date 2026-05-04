import fs from "node:fs";
import path from "node:path";

const rootDir = process.cwd();
const skillsDir = path.join(rootDir, "skills");
const schemaPath = path.join(rootDir, "schemas", "skill.schema.json");
const strict = process.argv.includes("--strict") || process.env.REGISTRY_STRICT === "1";

const errors = [];
const warnings = [];

function relative(filePath) {
  return path.relative(rootDir, filePath) || ".";
}

function readJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (error) {
    errors.push(`${relative(filePath)} is not valid JSON: ${error.message}`);
    return null;
  }
}

function isObject(value) {
  return value && typeof value === "object" && !Array.isArray(value);
}

function expect(condition, message) {
  if (!condition) {
    errors.push(message);
  }
}

function warn(condition, message) {
  if (!condition) {
    warnings.push(message);
  }
}

function expectStrict(condition, message) {
  if (strict) {
    expect(condition, message);
  } else {
    warn(condition, `${message} Run with --strict to enforce this as an error.`);
  }
}

function findSkillDirs(root) {
  const results = [];
  if (!fs.existsSync(root)) {
    return results;
  }

  const ignored = new Set(["node_modules", ".git", "dist", "build", "coverage"]);

  function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    const hasSkill = entries.some((entry) => entry.isFile() && entry.name === "SKILL.md");
    const hasManifest = entries.some((entry) => entry.isFile() && entry.name === "skill.json");

    if (hasSkill || hasManifest) {
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

function skillIdFromDir(dir) {
  return path.basename(dir);
}

function validateManifest(skillId, manifest, skillDir) {
  const label = `${relative(path.join(skillDir, "skill.json"))}`;

  expect(manifest.schemaVersion === "1.0.0", `${label}: schemaVersion must be "1.0.0".`);
  expect(manifest.id === skillId, `${label}: id must match folder name "${skillId}".`);
  expect(typeof manifest.name === "string" && manifest.name.trim().length > 0, `${label}: name is required.`);
  expect(typeof manifest.version === "string" && manifest.version.trim().length > 0, `${label}: version is required.`);
  expect(typeof manifest.description === "string" && manifest.description.trim().length >= 20, `${label}: description must be at least 20 characters.`);
  expect(["experimental", "active", "maintenance", "deprecated"].includes(manifest.status), `${label}: status must be experimental, active, maintenance, or deprecated.`);
  expect(typeof manifest.license === "string" && manifest.license.trim().length > 0, `${label}: license is required.`);

  expect(isObject(manifest.entrypoints), `${label}: entrypoints object is required.`);
  if (isObject(manifest.entrypoints)) {
    expect(typeof manifest.entrypoints.skill === "string" && manifest.entrypoints.skill.trim().length > 0, `${label}: entrypoints.skill is required.`);
    const skillPath = path.join(skillDir, manifest.entrypoints.skill || "SKILL.md");
    expect(fs.existsSync(skillPath), `${label}: entrypoints.skill points to missing file ${manifest.entrypoints.skill}.`);
    if (manifest.entrypoints.readme) {
      const readmePath = path.join(skillDir, manifest.entrypoints.readme);
      expect(fs.existsSync(readmePath), `${label}: entrypoints.readme points to missing file ${manifest.entrypoints.readme}.`);
    }
  }

  expect(isObject(manifest.runtime), `${label}: runtime object is required.`);
  if (isObject(manifest.runtime)) {
    expect(["claude-skill", "markdown", "node", "python", "mixed", "hosted", "other"].includes(manifest.runtime.type), `${label}: runtime.type is invalid.`);
  }

  expect(isObject(manifest.permissions), `${label}: permissions object is required.`);
  if (isObject(manifest.permissions)) {
    expect(["none", "optional", "required"].includes(manifest.permissions.network), `${label}: permissions.network is invalid.`);
    expect(["none", "read", "read-write"].includes(manifest.permissions.filesystem), `${label}: permissions.filesystem is invalid.`);
    expect(["none", "optional", "required"].includes(manifest.permissions.shell), `${label}: permissions.shell is invalid.`);
    expect(Array.isArray(manifest.permissions.secrets), `${label}: permissions.secrets must be an array.`);
    warn(manifest.permissions.network !== "required" || manifest.permissions.notes, `${label}: network is required; add permissions.notes explaining why.`);
    warn(manifest.permissions.shell !== "required" || manifest.permissions.notes, `${label}: shell is required; add permissions.notes explaining why.`);
    warn(manifest.permissions.filesystem !== "read-write" || manifest.permissions.notes, `${label}: filesystem is read-write; add permissions.notes explaining scope.`);
  }

  expect(Array.isArray(manifest.maintainers) && manifest.maintainers.length > 0, `${label}: maintainers must include at least one maintainer.`);
  if (Array.isArray(manifest.maintainers)) {
    manifest.maintainers.forEach((maintainer, index) => {
      expect(isObject(maintainer), `${label}: maintainers[${index}] must be an object.`);
      if (isObject(maintainer)) {
        expect(typeof maintainer.name === "string" && maintainer.name.trim().length > 0, `${label}: maintainers[${index}].name is required.`);
      }
    });
  }

  if (Array.isArray(manifest.tags)) {
    const duplicates = manifest.tags.filter((tag, index) => manifest.tags.indexOf(tag) !== index);
    expect(duplicates.length === 0, `${label}: tags must be unique.`);
  }
}

if (!fs.existsSync(schemaPath)) {
  errors.push("schemas/skill.schema.json is missing.");
}

if (!fs.existsSync(skillsDir)) {
  errors.push("skills/ directory is missing.");
} else {
  const skillDirs = findSkillDirs(skillsDir);
  warn(skillDirs.length > 0, "No skill directories with SKILL.md or skill.json found under skills/.");

  for (const skillDir of skillDirs) {
    const skillId = skillIdFromDir(skillDir);
    const skillPath = path.join(skillDir, "SKILL.md");
    const manifestPath = path.join(skillDir, "skill.json");

    expect(/^[a-z0-9][a-z0-9-]{1,80}[a-z0-9]$/.test(skillId), `${relative(skillDir)}: folder name should be lowercase kebab-case.`);
    expectStrict(fs.existsSync(skillPath), `${relative(skillDir)}: SKILL.md is required.`);
    expectStrict(fs.existsSync(manifestPath), `${relative(skillDir)}: skill.json is required.`);

    if (fs.existsSync(manifestPath)) {
      const manifest = readJson(manifestPath);
      if (manifest) {
        validateManifest(skillId, manifest, skillDir);
      }
    }
  }
}

for (const warning of warnings) {
  console.warn(`Warning: ${warning}`);
}

if (errors.length) {
  console.error("\nSkill registry validation failed:\n");
  for (const error of errors) {
    console.error(`- ${error}`);
  }
  process.exit(1);
}

console.log(strict ? "Skill registry validation passed in strict mode." : "Skill registry validation passed. Warnings may remain for legacy skill folders.");
