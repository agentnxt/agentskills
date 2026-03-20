import { AxiosInstance } from "axios";
import { ok, err } from "../utils.js";

type GetClient = () => AxiosInstance;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function registerAccountsTools(server: any, getClient: GetClient) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const tool = (name: string, desc: string, schema: object, fn: (a: any) => Promise<unknown>) => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    server.tool(name, desc, schema, async (args: any) => {
      try {
        return ok(await fn(args));
      } catch (e) {
        return err(e);
      }
    });
  };

  // ═══════════════════════════════════════════════════════════════
  // MY ACCOUNT — Profile
  // ═══════════════════════════════════════════════════════════════

  tool("account_get_profile", "Get the current user's full profile [Accounts API]", {
    type: "object", properties: {},
  }, async () => getClient().get("/my-account").then((r) => r.data));

  tool("account_update_profile", "Update the current user's basic profile fields [Accounts API]", {
    type: "object",
    properties: {
      name: { type: "string" },
      avatar: { type: "string" },
    },
  }, async (a) => getClient().patch("/my-account", a).then((r) => r.data));

  tool("account_update_other_profile", "Update the current user's extended profile [Accounts API]", {
    type: "object",
    properties: { profile: { type: "object" } },
  }, async (a) => getClient().patch("/my-account/profile", a).then((r) => r.data));

  tool("account_get_logto_config", "Get the current user's logto config [Accounts API]", {
    type: "object", properties: {},
  }, async () => getClient().get("/my-account/logto-config").then((r) => r.data));

  tool("account_update_logto_config", "Update the current user's logto config [Accounts API]", {
    type: "object",
    properties: { config: { type: "object" } },
  }, async (a) => getClient().patch("/my-account/logto-config", a).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // MY ACCOUNT — Password
  // ═══════════════════════════════════════════════════════════════

  tool("account_update_password", "Update the current user's password [Accounts API]", {
    type: "object", required: ["password", "verificationRecordId"],
    properties: {
      password: { type: "string" },
      verificationRecordId: { type: "string", description: "ID from a completed verification" },
    },
  }, async (a) => getClient().post("/my-account/password", a).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // MY ACCOUNT — Email & Phone
  // ═══════════════════════════════════════════════════════════════

  tool("account_update_primary_email", "Update the current user's primary email [Accounts API]", {
    type: "object", required: ["verificationRecordId", "newIdentifierVerificationRecordId"],
    properties: {
      verificationRecordId: { type: "string" },
      newIdentifierVerificationRecordId: { type: "string" },
    },
  }, async (a) => getClient().post("/my-account/primary-email", a).then((r) => r.data));

  tool("account_delete_primary_email", "Delete the current user's primary email [Accounts API]", {
    type: "object", required: ["verificationRecordId"],
    properties: { verificationRecordId: { type: "string" } },
  }, async (a) => getClient().delete("/my-account/primary-email", { data: a }).then((r) => r.data));

  tool("account_update_primary_phone", "Update the current user's primary phone [Accounts API]", {
    type: "object", required: ["verificationRecordId", "newIdentifierVerificationRecordId"],
    properties: {
      verificationRecordId: { type: "string" },
      newIdentifierVerificationRecordId: { type: "string" },
    },
  }, async (a) => getClient().post("/my-account/primary-phone", a).then((r) => r.data));

  tool("account_delete_primary_phone", "Delete the current user's primary phone [Accounts API]", {
    type: "object", required: ["verificationRecordId"],
    properties: { verificationRecordId: { type: "string" } },
  }, async (a) => getClient().delete("/my-account/primary-phone", { data: a }).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // MY ACCOUNT — Social Identities
  // ═══════════════════════════════════════════════════════════════

  tool("account_add_identity", "Link a social identity to the current user [Accounts API]", {
    type: "object", required: ["verificationRecordId", "newIdentifierVerificationRecordId"],
    properties: {
      verificationRecordId: { type: "string" },
      newIdentifierVerificationRecordId: { type: "string" },
    },
  }, async (a) => getClient().post("/my-account/identities", a).then((r) => r.data));

  tool("account_delete_identity", "Remove a linked social identity [Accounts API]", {
    type: "object", required: ["target", "verificationRecordId"],
    properties: {
      target: { type: "string", description: "Social connector target (e.g. github, google)" },
      verificationRecordId: { type: "string" },
    },
  }, async ({ target, verificationRecordId }) =>
    getClient().delete(`/my-account/identities/${target}`, { data: { verificationRecordId } }).then((r) => r.data));

  tool("account_get_social_identity_access_token", "Get access token from a linked social provider [Accounts API]", {
    type: "object", required: ["target"],
    properties: { target: { type: "string" } },
  }, async (a) =>
    getClient().get(`/my-account/social-identity-access-token/${a.target}`).then((r) => r.data));

  tool("account_get_enterprise_sso_access_token", "Get access token from a linked enterprise SSO provider [Accounts API]", {
    type: "object", required: ["ssoConnectorId"],
    properties: { ssoConnectorId: { type: "string" } },
  }, async (a) =>
    getClient().get(`/my-account/enterprise-sso-identity-access-token/${a.ssoConnectorId}`).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // MY ACCOUNT — MFA Settings
  // ═══════════════════════════════════════════════════════════════

  tool("account_get_mfa_settings", "Get the current user's MFA settings [Accounts API]", {
    type: "object", properties: {},
  }, async () => getClient().get("/my-account/mfa-settings").then((r) => r.data));

  tool("account_update_mfa_settings", "Update the current user's MFA settings [Accounts API]", {
    type: "object",
    properties: { isMfaRequired: { type: "boolean" } },
  }, async (a) => getClient().patch("/my-account/mfa-settings", a).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // MY ACCOUNT — MFA Verifications
  // ═══════════════════════════════════════════════════════════════

  tool("account_get_mfa_verifications", "List MFA verifications for the current user [Accounts API]", {
    type: "object", properties: {},
  }, async () => getClient().get("/my-account/mfa-verifications").then((r) => r.data));

  tool("account_add_mfa_verification", "Add a new MFA verification method [Accounts API]", {
    type: "object", required: ["type", "verificationRecordId", "newBindingVerificationRecordId"],
    properties: {
      type: { type: "string", enum: ["Totp", "WebAuthn", "BackupCode"] },
      verificationRecordId: { type: "string" },
      newBindingVerificationRecordId: { type: "string" },
      name: { type: "string", description: "Friendly name for the verification" },
    },
  }, async (a) => getClient().post("/my-account/mfa-verifications", a).then((r) => r.data));

  tool("account_update_mfa_verification_name", "Update the name of a MFA verification [Accounts API]", {
    type: "object", required: ["verificationId", "name"],
    properties: {
      verificationId: { type: "string" },
      name: { type: "string" },
    },
  }, async ({ verificationId, name }) =>
    getClient().patch(`/my-account/mfa-verifications/${verificationId}`, { name }).then((r) => r.data));

  tool("account_delete_mfa_verification", "Remove a MFA verification method [Accounts API]", {
    type: "object", required: ["verificationId", "verificationRecordId"],
    properties: {
      verificationId: { type: "string" },
      verificationRecordId: { type: "string" },
    },
  }, async ({ verificationId, verificationRecordId }) =>
    getClient().delete(`/my-account/mfa-verifications/${verificationId}`, { data: { verificationRecordId } }).then((r) => r.data));

  tool("account_generate_totp_secret", "Generate a new TOTP secret for binding [Accounts API]", {
    type: "object", properties: {},
  }, async () =>
    getClient().post("/my-account/mfa-verifications/totp-secret").then((r) => r.data));

  tool("account_generate_backup_codes", "Generate new backup codes [Accounts API]", {
    type: "object", required: ["verificationRecordId"],
    properties: { verificationRecordId: { type: "string" } },
  }, async (a) =>
    getClient().post("/my-account/mfa-verifications/backup-codes/generate", a).then((r) => r.data));

  tool("account_get_backup_codes", "Get the current user's backup codes [Accounts API]", {
    type: "object", properties: {},
  }, async () =>
    getClient().get("/my-account/mfa-verifications/backup-codes").then((r) => r.data));
}
