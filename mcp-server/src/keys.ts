#!/usr/bin/env node
import { createKey, revokeKey, listKeys } from "./auth.js";

const [command, ...args] = process.argv.slice(2);

switch (command) {
  case "create": {
    const name = args[0];
    if (!name) {
      console.error("Usage: keys create <name>");
      console.error('Example: keys create "alice@company.com"');
      process.exit(1);
    }
    const result = createKey(name);
    console.log(`\nAPI key created for: ${name}`);
    console.log(`ID:  ${result.id}`);
    console.log(`Key: ${result.key}`);
    console.log(`\nSave this key — it cannot be shown again.`);
    break;
  }

  case "revoke": {
    const id = args[0];
    if (!id) {
      console.error("Usage: keys revoke <id>");
      process.exit(1);
    }
    const revoked = revokeKey(id);
    if (revoked) {
      console.log(`Key ${id} has been revoked.`);
    } else {
      console.error(`Key ${id} not found.`);
      process.exit(1);
    }
    break;
  }

  case "list": {
    const keys = listKeys();
    if (keys.length === 0) {
      console.log("No API keys found.");
      break;
    }
    console.log("\nAPI Keys:\n");
    console.log(
      "ID               Name                     Created                  Status"
    );
    console.log(
      "───────────────  ───────────────────────  ───────────────────────  ────────"
    );
    for (const key of keys) {
      const status = key.revokedAt ? `REVOKED ${key.revokedAt}` : "ACTIVE";
      console.log(
        `${key.id.padEnd(17)}${key.name.padEnd(25)}${key.createdAt.padEnd(25)}${status}`
      );
    }
    console.log();
    break;
  }

  default:
    console.log("saas-converter key management\n");
    console.log("Commands:");
    console.log('  create <name>   Create a new API key (e.g., "alice@company.com")');
    console.log("  revoke <id>     Revoke an API key by ID");
    console.log("  list            List all API keys");
}
