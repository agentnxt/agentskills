import { randomBytes, createHash } from "crypto";
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const KEYS_FILE = join(__dirname, "..", "data", "keys.json");

export interface ApiKey {
  id: string;
  name: string;
  hash: string;
  createdAt: string;
  revokedAt: string | null;
}

interface KeyStore {
  keys: ApiKey[];
}

function ensureDataDir(): void {
  const dataDir = dirname(KEYS_FILE);
  if (!existsSync(dataDir)) {
    mkdirSync(dataDir, { recursive: true });
  }
}

function loadKeys(): KeyStore {
  if (!existsSync(KEYS_FILE)) return { keys: [] };
  return JSON.parse(readFileSync(KEYS_FILE, "utf-8"));
}

function saveKeys(store: KeyStore): void {
  writeFileSync(KEYS_FILE, JSON.stringify(store, null, 2));
}

function hashKey(key: string): string {
  return createHash("sha256").update(key).digest("hex");
}

export function createKey(name: string): { key: string; id: string } {
  ensureDataDir();
  const store = loadKeys();
  const id = randomBytes(8).toString("hex");
  const rawKey = `scs_${randomBytes(32).toString("hex")}`;
  const hash = hashKey(rawKey);

  store.keys.push({
    id,
    name,
    hash,
    createdAt: new Date().toISOString(),
    revokedAt: null,
  });

  saveKeys(store);
  return { key: rawKey, id };
}

export function revokeKey(id: string): boolean {
  const store = loadKeys();
  const key = store.keys.find((k) => k.id === id);
  if (!key) return false;
  key.revokedAt = new Date().toISOString();
  saveKeys(store);
  return true;
}

export function listKeys(): Array<Omit<ApiKey, "hash">> {
  const store = loadKeys();
  return store.keys.map(({ hash, ...rest }) => rest);
}

export function validateKey(rawKey: string): { valid: boolean; name?: string } {
  const store = loadKeys();
  const hash = hashKey(rawKey);
  const key = store.keys.find((k) => k.hash === hash);
  if (!key) return { valid: false };
  if (key.revokedAt) return { valid: false };
  return { valid: true, name: key.name };
}
