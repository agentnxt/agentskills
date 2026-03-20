import { AxiosInstance } from "axios";
import { buildQuery, ok, err } from "../utils.js";

type GetClient = () => Promise<AxiosInstance>;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function registerManagementTools(server: any, getClient: GetClient) {
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
  // USERS
  // ═══════════════════════════════════════════════════════════════

  tool("list_users", "List users with optional filters and pagination", {
    type: "object",
    properties: {
      page: { type: "number", description: "Page number (1-based)" },
      page_size: { type: "number", description: "Results per page" },
      keyword: { type: "string", description: "Search by username, email, phone, or name" },
      is_suspended: { type: "boolean" },
    },
  }, async (a) => (await getClient()).get(`/users${buildQuery(a)}`).then((r) => r.data));

  tool("get_user", "Get a user by ID", {
    type: "object", required: ["userId"],
    properties: { userId: { type: "string" } },
  }, async (a) => (await getClient()).get(`/users/${a.userId}`).then((r) => r.data));

  tool("create_user", "Create a new user", {
    type: "object",
    properties: {
      primaryEmail: { type: "string" },
      primaryPhone: { type: "string" },
      username: { type: "string" },
      password: { type: "string" },
      name: { type: "string" },
      avatar: { type: "string" },
      customData: { type: "object" },
      profile: { type: "object" },
    },
  }, async (a) => (await getClient()).post("/users", a).then((r) => r.data));

  tool("update_user", "Update a user's profile", {
    type: "object", required: ["userId"],
    properties: {
      userId: { type: "string" },
      name: { type: "string" },
      avatar: { type: "string" },
      customData: { type: "object" },
      profile: { type: "object" },
      username: { type: "string" },
    },
  }, async ({ userId, ...body }) => (await getClient()).patch(`/users/${userId}`, body).then((r) => r.data));

  tool("delete_user", "Delete a user permanently", {
    type: "object", required: ["userId"],
    properties: { userId: { type: "string" } },
  }, async (a) => (await getClient()).delete(`/users/${a.userId}`).then((r) => r.data));

  tool("suspend_user", "Suspend or unsuspend a user", {
    type: "object", required: ["userId", "isSuspended"],
    properties: { userId: { type: "string" }, isSuspended: { type: "boolean" } },
  }, async ({ userId, isSuspended }) =>
    (await getClient()).patch(`/users/${userId}/is-suspended`, { isSuspended }).then((r) => r.data));

  tool("update_user_password", "Update a user's password", {
    type: "object", required: ["userId", "password"],
    properties: { userId: { type: "string" }, password: { type: "string" } },
  }, async ({ userId, password }) =>
    (await getClient()).patch(`/users/${userId}/password`, { password }).then((r) => r.data));

  tool("verify_user_password", "Verify a user's current password", {
    type: "object", required: ["userId", "password"],
    properties: { userId: { type: "string" }, password: { type: "string" } },
  }, async ({ userId, password }) =>
    (await getClient()).post(`/users/${userId}/password/verify`, { password }).then((r) => r.data));

  tool("get_user_roles", "Get roles assigned to a user", {
    type: "object", required: ["userId"],
    properties: {
      userId: { type: "string" },
      page: { type: "number" },
      page_size: { type: "number" },
    },
  }, async ({ userId, ...q }) =>
    (await getClient()).get(`/users/${userId}/roles${buildQuery(q)}`).then((r) => r.data));

  tool("assign_user_roles", "Assign roles to a user", {
    type: "object", required: ["userId", "roleIds"],
    properties: {
      userId: { type: "string" },
      roleIds: { type: "array", items: { type: "string" } },
    },
  }, async ({ userId, roleIds }) =>
    (await getClient()).post(`/users/${userId}/roles`, { roleIds }).then((r) => r.data));

  tool("replace_user_roles", "Replace all roles for a user", {
    type: "object", required: ["userId", "roleIds"],
    properties: {
      userId: { type: "string" },
      roleIds: { type: "array", items: { type: "string" } },
    },
  }, async ({ userId, roleIds }) =>
    (await getClient()).put(`/users/${userId}/roles`, { roleIds }).then((r) => r.data));

  tool("remove_user_role", "Remove a role from a user", {
    type: "object", required: ["userId", "roleId"],
    properties: { userId: { type: "string" }, roleId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/users/${a.userId}/roles/${a.roleId}`).then((r) => r.data));

  tool("get_user_identities", "Get a user's social identities", {
    type: "object", required: ["userId"],
    properties: { userId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/users/${a.userId}/identities`).then((r) => r.data));

  tool("update_user_identity", "Update a user's social identity", {
    type: "object", required: ["userId", "target"],
    properties: {
      userId: { type: "string" },
      target: { type: "string" },
      identityUserId: { type: "string" },
      details: { type: "object" },
    },
  }, async ({ userId, target, ...body }) =>
    (await getClient()).put(`/users/${userId}/identities/${target}`, body).then((r) => r.data));

  tool("delete_user_identity", "Delete a user's social identity", {
    type: "object", required: ["userId", "target"],
    properties: { userId: { type: "string" }, target: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/users/${a.userId}/identities/${a.target}`).then((r) => r.data));

  tool("get_user_organizations", "Get organizations a user belongs to", {
    type: "object", required: ["userId"],
    properties: {
      userId: { type: "string" },
      page: { type: "number" },
      page_size: { type: "number" },
    },
  }, async ({ userId, ...q }) =>
    (await getClient()).get(`/users/${userId}/organizations${buildQuery(q)}`).then((r) => r.data));

  tool("get_user_mfa_verifications", "Get a user's MFA verifications", {
    type: "object", required: ["userId"],
    properties: { userId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/users/${a.userId}/mfa-verifications`).then((r) => r.data));

  tool("delete_user_mfa_verification", "Delete a user's MFA verification", {
    type: "object", required: ["userId", "verificationId"],
    properties: { userId: { type: "string" }, verificationId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/users/${a.userId}/mfa-verifications/${a.verificationId}`).then((r) => r.data));

  tool("get_user_logs", "Get audit logs for a specific user", {
    type: "object", required: ["userId"],
    properties: {
      userId: { type: "string" },
      page: { type: "number" },
      page_size: { type: "number" },
    },
  }, async ({ userId, ...q }) =>
    (await getClient()).get(`/users/${userId}/logs${buildQuery(q)}`).then((r) => r.data));

  tool("get_user_custom_data", "Get a user's custom data", {
    type: "object", required: ["userId"],
    properties: { userId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/users/${a.userId}/custom-data`).then((r) => r.data));

  tool("update_user_custom_data", "Update a user's custom data", {
    type: "object", required: ["userId", "customData"],
    properties: { userId: { type: "string" }, customData: { type: "object" } },
  }, async ({ userId, customData }) =>
    (await getClient()).patch(`/users/${userId}/custom-data`, { customData }).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // APPLICATIONS
  // ═══════════════════════════════════════════════════════════════

  tool("list_applications", "List all applications", {
    type: "object",
    properties: {
      page: { type: "number" },
      page_size: { type: "number" },
      keyword: { type: "string" },
      type: { type: "string", enum: ["Native", "SPA", "Traditional", "MachineToMachine", "Protected"] },
      is_third_party: { type: "boolean" },
    },
  }, async (a) => (await getClient()).get(`/applications${buildQuery(a)}`).then((r) => r.data));

  tool("create_application", "Create an application", {
    type: "object", required: ["name", "type"],
    properties: {
      name: { type: "string" },
      type: { type: "string", enum: ["Native", "SPA", "Traditional", "MachineToMachine", "Protected"] },
      description: { type: "string" },
      oidcClientMetadata: { type: "object" },
      customClientMetadata: { type: "object" },
      isThirdParty: { type: "boolean" },
    },
  }, async (a) => (await getClient()).post("/applications", a).then((r) => r.data));

  tool("get_application", "Get an application by ID", {
    type: "object", required: ["applicationId"],
    properties: { applicationId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/applications/${a.applicationId}`).then((r) => r.data));

  tool("update_application", "Update an application", {
    type: "object", required: ["applicationId"],
    properties: {
      applicationId: { type: "string" },
      name: { type: "string" },
      description: { type: "string" },
      oidcClientMetadata: { type: "object" },
      customClientMetadata: { type: "object" },
      isThirdParty: { type: "boolean" },
    },
  }, async ({ applicationId, ...body }) =>
    (await getClient()).patch(`/applications/${applicationId}`, body).then((r) => r.data));

  tool("delete_application", "Delete an application", {
    type: "object", required: ["applicationId"],
    properties: { applicationId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/applications/${a.applicationId}`).then((r) => r.data));

  tool("list_application_secrets", "List secrets for an application", {
    type: "object", required: ["applicationId"],
    properties: { applicationId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/applications/${a.applicationId}/secrets`).then((r) => r.data));

  tool("create_application_secret", "Add a secret to an application", {
    type: "object", required: ["applicationId"],
    properties: {
      applicationId: { type: "string" },
      name: { type: "string" },
      expiresAt: { type: "number", description: "Unix timestamp in ms" },
    },
  }, async ({ applicationId, ...body }) =>
    (await getClient()).post(`/applications/${applicationId}/secrets`, body).then((r) => r.data));

  tool("delete_application_secret", "Delete an application secret", {
    type: "object", required: ["applicationId", "secretName"],
    properties: { applicationId: { type: "string" }, secretName: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/applications/${a.applicationId}/secrets/${a.secretName}`).then((r) => r.data));

  tool("update_application_secret", "Update an application secret", {
    type: "object", required: ["applicationId", "secretName"],
    properties: {
      applicationId: { type: "string" },
      secretName: { type: "string" },
      name: { type: "string" },
      expiresAt: { type: "number" },
    },
  }, async ({ applicationId, secretName, ...body }) =>
    (await getClient()).patch(`/applications/${applicationId}/secrets/${secretName}`, body).then((r) => r.data));

  tool("get_application_roles", "Get API resource roles for an application", {
    type: "object", required: ["applicationId"],
    properties: {
      applicationId: { type: "string" },
      page: { type: "number" },
      page_size: { type: "number" },
    },
  }, async ({ applicationId, ...q }) =>
    (await getClient()).get(`/applications/${applicationId}/roles${buildQuery(q)}`).then((r) => r.data));

  tool("assign_application_roles", "Assign API resource roles to an application", {
    type: "object", required: ["applicationId", "roleIds"],
    properties: {
      applicationId: { type: "string" },
      roleIds: { type: "array", items: { type: "string" } },
    },
  }, async ({ applicationId, roleIds }) =>
    (await getClient()).post(`/applications/${applicationId}/roles`, { roleIds }).then((r) => r.data));

  tool("replace_application_roles", "Replace all roles for an application", {
    type: "object", required: ["applicationId", "roleIds"],
    properties: {
      applicationId: { type: "string" },
      roleIds: { type: "array", items: { type: "string" } },
    },
  }, async ({ applicationId, roleIds }) =>
    (await getClient()).put(`/applications/${applicationId}/roles`, { roleIds }).then((r) => r.data));

  tool("remove_application_role", "Remove a role from an application", {
    type: "object", required: ["applicationId", "roleId"],
    properties: { applicationId: { type: "string" }, roleId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/applications/${a.applicationId}/roles/${a.roleId}`).then((r) => r.data));

  tool("list_application_consent_scopes", "List user consent scopes of an application", {
    type: "object", required: ["applicationId"],
    properties: { applicationId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/applications/${a.applicationId}/user-consent-scopes`).then((r) => r.data));

  tool("get_application_sign_in_experience", "Get app-level sign-in experience", {
    type: "object", required: ["applicationId"],
    properties: { applicationId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/applications/${a.applicationId}/sign-in-experience`).then((r) => r.data));

  tool("update_application_sign_in_experience", "Update app-level sign-in experience", {
    type: "object", required: ["applicationId"],
    properties: {
      applicationId: { type: "string" },
      color: { type: "object" },
      branding: { type: "object" },
    },
  }, async ({ applicationId, ...body }) =>
    (await getClient()).put(`/applications/${applicationId}/sign-in-experience`, body).then((r) => r.data));

  tool("list_application_custom_domains", "List custom domains for a protected app", {
    type: "object", required: ["applicationId"],
    properties: { applicationId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/applications/${a.applicationId}/protected-app-metadata/custom-domains`).then((r) => r.data));

  tool("add_application_custom_domain", "Add a custom domain to a protected app", {
    type: "object", required: ["applicationId", "domain"],
    properties: { applicationId: { type: "string" }, domain: { type: "string" } },
  }, async ({ applicationId, domain }) =>
    (await getClient()).post(`/applications/${applicationId}/protected-app-metadata/custom-domains`, { domain }).then((r) => r.data));

  tool("delete_application_custom_domain", "Remove a custom domain from a protected app", {
    type: "object", required: ["applicationId", "domain"],
    properties: { applicationId: { type: "string" }, domain: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/applications/${a.applicationId}/protected-app-metadata/custom-domains/${a.domain}`).then((r) => r.data));

  tool("get_application_organizations", "Get organizations an application belongs to", {
    type: "object", required: ["applicationId"],
    properties: { applicationId: { type: "string" }, page: { type: "number" }, page_size: { type: "number" } },
  }, async ({ applicationId, ...q }) =>
    (await getClient()).get(`/applications/${applicationId}/organizations${buildQuery(q)}`).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // ORGANIZATIONS
  // ═══════════════════════════════════════════════════════════════

  tool("list_organizations", "List all organizations", {
    type: "object",
    properties: {
      page: { type: "number" },
      page_size: { type: "number" },
      keyword: { type: "string" },
    },
  }, async (a) => (await getClient()).get(`/organizations${buildQuery(a)}`).then((r) => r.data));

  tool("create_organization", "Create an organization", {
    type: "object", required: ["name"],
    properties: {
      name: { type: "string" },
      description: { type: "string" },
      customData: { type: "object" },
      isMfaRequired: { type: "boolean" },
    },
  }, async (a) => (await getClient()).post("/organizations", a).then((r) => r.data));

  tool("get_organization", "Get an organization by ID", {
    type: "object", required: ["organizationId"],
    properties: { organizationId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/organizations/${a.organizationId}`).then((r) => r.data));

  tool("update_organization", "Update an organization", {
    type: "object", required: ["organizationId"],
    properties: {
      organizationId: { type: "string" },
      name: { type: "string" },
      description: { type: "string" },
      customData: { type: "object" },
      isMfaRequired: { type: "boolean" },
    },
  }, async ({ organizationId, ...body }) =>
    (await getClient()).patch(`/organizations/${organizationId}`, body).then((r) => r.data));

  tool("delete_organization", "Delete an organization", {
    type: "object", required: ["organizationId"],
    properties: { organizationId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/organizations/${a.organizationId}`).then((r) => r.data));

  tool("list_organization_users", "List users in an organization", {
    type: "object", required: ["organizationId"],
    properties: {
      organizationId: { type: "string" },
      page: { type: "number" },
      page_size: { type: "number" },
      keyword: { type: "string" },
    },
  }, async ({ organizationId, ...q }) =>
    (await getClient()).get(`/organizations/${organizationId}/users${buildQuery(q)}`).then((r) => r.data));

  tool("add_organization_users", "Add users to an organization", {
    type: "object", required: ["organizationId", "userIds"],
    properties: {
      organizationId: { type: "string" },
      userIds: { type: "array", items: { type: "string" } },
    },
  }, async ({ organizationId, userIds }) =>
    (await getClient()).post(`/organizations/${organizationId}/users`, { userIds }).then((r) => r.data));

  tool("replace_organization_users", "Replace all users in an organization", {
    type: "object", required: ["organizationId", "userIds"],
    properties: {
      organizationId: { type: "string" },
      userIds: { type: "array", items: { type: "string" } },
    },
  }, async ({ organizationId, userIds }) =>
    (await getClient()).put(`/organizations/${organizationId}/users`, { userIds }).then((r) => r.data));

  tool("remove_organization_user", "Remove a user from an organization", {
    type: "object", required: ["organizationId", "userId"],
    properties: { organizationId: { type: "string" }, userId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/organizations/${a.organizationId}/users/${a.userId}`).then((r) => r.data));

  tool("get_organization_user_roles", "Get roles for a user in an organization", {
    type: "object", required: ["organizationId", "userId"],
    properties: { organizationId: { type: "string" }, userId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/organizations/${a.organizationId}/users/${a.userId}/roles`).then((r) => r.data));

  tool("assign_organization_user_roles", "Assign roles to a user in an organization", {
    type: "object", required: ["organizationId", "userId", "organizationRoleIds"],
    properties: {
      organizationId: { type: "string" },
      userId: { type: "string" },
      organizationRoleIds: { type: "array", items: { type: "string" } },
    },
  }, async ({ organizationId, userId, organizationRoleIds }) =>
    (await getClient()).post(`/organizations/${organizationId}/users/${userId}/roles`, { organizationRoleIds }).then((r) => r.data));

  tool("replace_organization_user_roles", "Replace all roles for a user in an organization", {
    type: "object", required: ["organizationId", "userId", "organizationRoleIds"],
    properties: {
      organizationId: { type: "string" },
      userId: { type: "string" },
      organizationRoleIds: { type: "array", items: { type: "string" } },
    },
  }, async ({ organizationId, userId, organizationRoleIds }) =>
    (await getClient()).put(`/organizations/${organizationId}/users/${userId}/roles`, { organizationRoleIds }).then((r) => r.data));

  tool("remove_organization_user_role", "Remove a role from a user in an organization", {
    type: "object", required: ["organizationId", "userId", "organizationRoleId"],
    properties: {
      organizationId: { type: "string" },
      userId: { type: "string" },
      organizationRoleId: { type: "string" },
    },
  }, async (a) =>
    (await getClient()).delete(`/organizations/${a.organizationId}/users/${a.userId}/roles/${a.organizationRoleId}`).then((r) => r.data));

  tool("get_organization_user_scopes", "Get scopes for a user in an organization", {
    type: "object", required: ["organizationId", "userId"],
    properties: { organizationId: { type: "string" }, userId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/organizations/${a.organizationId}/users/${a.userId}/scopes`).then((r) => r.data));

  tool("list_organization_applications", "List applications in an organization", {
    type: "object", required: ["organizationId"],
    properties: {
      organizationId: { type: "string" },
      page: { type: "number" },
      page_size: { type: "number" },
    },
  }, async ({ organizationId, ...q }) =>
    (await getClient()).get(`/organizations/${organizationId}/applications${buildQuery(q)}`).then((r) => r.data));

  tool("add_organization_applications", "Add applications to an organization", {
    type: "object", required: ["organizationId", "applicationIds"],
    properties: {
      organizationId: { type: "string" },
      applicationIds: { type: "array", items: { type: "string" } },
    },
  }, async ({ organizationId, applicationIds }) =>
    (await getClient()).post(`/organizations/${organizationId}/applications`, { applicationIds }).then((r) => r.data));

  tool("remove_organization_application", "Remove an application from an organization", {
    type: "object", required: ["organizationId", "applicationId"],
    properties: { organizationId: { type: "string" }, applicationId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/organizations/${a.organizationId}/applications/${a.applicationId}`).then((r) => r.data));

  tool("get_organization_application_roles", "Get roles for an application in an organization", {
    type: "object", required: ["organizationId", "applicationId"],
    properties: { organizationId: { type: "string" }, applicationId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/organizations/${a.organizationId}/applications/${a.applicationId}/roles`).then((r) => r.data));

  tool("assign_organization_application_roles", "Assign roles to an application in an organization", {
    type: "object", required: ["organizationId", "applicationId", "organizationRoleIds"],
    properties: {
      organizationId: { type: "string" },
      applicationId: { type: "string" },
      organizationRoleIds: { type: "array", items: { type: "string" } },
    },
  }, async ({ organizationId, applicationId, organizationRoleIds }) =>
    (await getClient()).post(`/organizations/${organizationId}/applications/${applicationId}/roles`, { organizationRoleIds }).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // ORGANIZATION ROLES
  // ═══════════════════════════════════════════════════════════════

  tool("list_organization_roles", "List all organization roles", {
    type: "object",
    properties: { page: { type: "number" }, page_size: { type: "number" }, keyword: { type: "string" } },
  }, async (a) => (await getClient()).get(`/organization-roles${buildQuery(a)}`).then((r) => r.data));

  tool("create_organization_role", "Create an organization role", {
    type: "object", required: ["name"],
    properties: {
      name: { type: "string" },
      description: { type: "string" },
      type: { type: "string", enum: ["User", "MachineToMachine"] },
      organizationScopeIds: { type: "array", items: { type: "string" } },
      resourceScopeIds: { type: "array", items: { type: "string" } },
    },
  }, async (a) => (await getClient()).post("/organization-roles", a).then((r) => r.data));

  tool("get_organization_role", "Get an organization role by ID", {
    type: "object", required: ["organizationRoleId"],
    properties: { organizationRoleId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/organization-roles/${a.organizationRoleId}`).then((r) => r.data));

  tool("update_organization_role", "Update an organization role", {
    type: "object", required: ["organizationRoleId"],
    properties: {
      organizationRoleId: { type: "string" },
      name: { type: "string" },
      description: { type: "string" },
    },
  }, async ({ organizationRoleId, ...body }) =>
    (await getClient()).patch(`/organization-roles/${organizationRoleId}`, body).then((r) => r.data));

  tool("delete_organization_role", "Delete an organization role", {
    type: "object", required: ["organizationRoleId"],
    properties: { organizationRoleId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/organization-roles/${a.organizationRoleId}`).then((r) => r.data));

  tool("list_organization_role_scopes", "List organization scopes for an org role", {
    type: "object", required: ["organizationRoleId"],
    properties: { organizationRoleId: { type: "string" }, page: { type: "number" }, page_size: { type: "number" } },
  }, async ({ organizationRoleId, ...q }) =>
    (await getClient()).get(`/organization-roles/${organizationRoleId}/scopes${buildQuery(q)}`).then((r) => r.data));

  tool("assign_organization_role_scopes", "Assign organization scopes to an org role", {
    type: "object", required: ["organizationRoleId", "organizationScopeIds"],
    properties: {
      organizationRoleId: { type: "string" },
      organizationScopeIds: { type: "array", items: { type: "string" } },
    },
  }, async ({ organizationRoleId, organizationScopeIds }) =>
    (await getClient()).post(`/organization-roles/${organizationRoleId}/scopes`, { organizationScopeIds }).then((r) => r.data));

  tool("replace_organization_role_scopes", "Replace organization scopes for an org role", {
    type: "object", required: ["organizationRoleId", "organizationScopeIds"],
    properties: {
      organizationRoleId: { type: "string" },
      organizationScopeIds: { type: "array", items: { type: "string" } },
    },
  }, async ({ organizationRoleId, organizationScopeIds }) =>
    (await getClient()).put(`/organization-roles/${organizationRoleId}/scopes`, { organizationScopeIds }).then((r) => r.data));

  tool("remove_organization_role_scope", "Remove an organization scope from an org role", {
    type: "object", required: ["organizationRoleId", "organizationScopeId"],
    properties: { organizationRoleId: { type: "string" }, organizationScopeId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/organization-roles/${a.organizationRoleId}/scopes/${a.organizationScopeId}`).then((r) => r.data));

  tool("list_organization_role_resource_scopes", "List resource scopes for an org role", {
    type: "object", required: ["organizationRoleId"],
    properties: { organizationRoleId: { type: "string" }, page: { type: "number" }, page_size: { type: "number" } },
  }, async ({ organizationRoleId, ...q }) =>
    (await getClient()).get(`/organization-roles/${organizationRoleId}/resource-scopes${buildQuery(q)}`).then((r) => r.data));

  tool("assign_organization_role_resource_scopes", "Assign resource scopes to an org role", {
    type: "object", required: ["organizationRoleId", "scopeIds"],
    properties: {
      organizationRoleId: { type: "string" },
      scopeIds: { type: "array", items: { type: "string" } },
    },
  }, async ({ organizationRoleId, scopeIds }) =>
    (await getClient()).post(`/organization-roles/${organizationRoleId}/resource-scopes`, { scopeIds }).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // ORGANIZATION SCOPES
  // ═══════════════════════════════════════════════════════════════

  tool("list_organization_scopes", "List all organization scopes", {
    type: "object",
    properties: { page: { type: "number" }, page_size: { type: "number" }, keyword: { type: "string" } },
  }, async (a) => (await getClient()).get(`/organization-scopes${buildQuery(a)}`).then((r) => r.data));

  tool("create_organization_scope", "Create an organization scope", {
    type: "object", required: ["name"],
    properties: { name: { type: "string" }, description: { type: "string" } },
  }, async (a) => (await getClient()).post("/organization-scopes", a).then((r) => r.data));

  tool("get_organization_scope", "Get an organization scope by ID", {
    type: "object", required: ["organizationScopeId"],
    properties: { organizationScopeId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/organization-scopes/${a.organizationScopeId}`).then((r) => r.data));

  tool("update_organization_scope", "Update an organization scope", {
    type: "object", required: ["organizationScopeId"],
    properties: {
      organizationScopeId: { type: "string" },
      name: { type: "string" },
      description: { type: "string" },
    },
  }, async ({ organizationScopeId, ...body }) =>
    (await getClient()).patch(`/organization-scopes/${organizationScopeId}`, body).then((r) => r.data));

  tool("delete_organization_scope", "Delete an organization scope", {
    type: "object", required: ["organizationScopeId"],
    properties: { organizationScopeId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/organization-scopes/${a.organizationScopeId}`).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // ORGANIZATION INVITATIONS
  // ═══════════════════════════════════════════════════════════════

  tool("list_organization_invitations", "List all organization invitations", {
    type: "object",
    properties: { organizationId: { type: "string" }, page: { type: "number" }, page_size: { type: "number" } },
  }, async (a) => (await getClient()).get(`/organization-invitations${buildQuery(a)}`).then((r) => r.data));

  tool("create_organization_invitation", "Create an organization invitation", {
    type: "object", required: ["organizationId", "invitee"],
    properties: {
      organizationId: { type: "string" },
      invitee: { type: "string", description: "Email of the invitee" },
      expiresAt: { type: "number", description: "Unix timestamp in ms" },
      organizationRoleIds: { type: "array", items: { type: "string" } },
    },
  }, async (a) => (await getClient()).post("/organization-invitations", a).then((r) => r.data));

  tool("get_organization_invitation", "Get an organization invitation by ID", {
    type: "object", required: ["invitationId"],
    properties: { invitationId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/organization-invitations/${a.invitationId}`).then((r) => r.data));

  tool("delete_organization_invitation", "Delete an organization invitation", {
    type: "object", required: ["invitationId"],
    properties: { invitationId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/organization-invitations/${a.invitationId}`).then((r) => r.data));

  tool("update_organization_invitation_status", "Accept or revoke an organization invitation", {
    type: "object", required: ["invitationId", "status"],
    properties: {
      invitationId: { type: "string" },
      status: { type: "string", enum: ["Accepted", "Revoked"] },
    },
  }, async ({ invitationId, status }) =>
    (await getClient()).put(`/organization-invitations/${invitationId}/status`, { status }).then((r) => r.data));

  tool("resend_organization_invitation", "Resend an organization invitation email", {
    type: "object", required: ["invitationId"],
    properties: { invitationId: { type: "string" } },
  }, async (a) =>
    (await getClient()).post(`/organization-invitations/${a.invitationId}/message`).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // ROLES
  // ═══════════════════════════════════════════════════════════════

  tool("list_roles", "List all roles", {
    type: "object",
    properties: {
      page: { type: "number" },
      page_size: { type: "number" },
      keyword: { type: "string" },
      type: { type: "string", enum: ["User", "MachineToMachine"] },
    },
  }, async (a) => (await getClient()).get(`/roles${buildQuery(a)}`).then((r) => r.data));

  tool("create_role", "Create a role", {
    type: "object", required: ["name", "type"],
    properties: {
      name: { type: "string" },
      description: { type: "string" },
      type: { type: "string", enum: ["User", "MachineToMachine"] },
      scopeIds: { type: "array", items: { type: "string" } },
    },
  }, async (a) => (await getClient()).post("/roles", a).then((r) => r.data));

  tool("get_role", "Get a role by ID", {
    type: "object", required: ["roleId"],
    properties: { roleId: { type: "string" } },
  }, async (a) => (await getClient()).get(`/roles/${a.roleId}`).then((r) => r.data));

  tool("update_role", "Update a role", {
    type: "object", required: ["roleId"],
    properties: {
      roleId: { type: "string" },
      name: { type: "string" },
      description: { type: "string" },
    },
  }, async ({ roleId, ...body }) =>
    (await getClient()).patch(`/roles/${roleId}`, body).then((r) => r.data));

  tool("delete_role", "Delete a role", {
    type: "object", required: ["roleId"],
    properties: { roleId: { type: "string" } },
  }, async (a) => (await getClient()).delete(`/roles/${a.roleId}`).then((r) => r.data));

  tool("get_role_scopes", "Get scopes assigned to a role", {
    type: "object", required: ["roleId"],
    properties: { roleId: { type: "string" }, page: { type: "number" }, page_size: { type: "number" } },
  }, async ({ roleId, ...q }) =>
    (await getClient()).get(`/roles/${roleId}/scopes${buildQuery(q)}`).then((r) => r.data));

  tool("assign_role_scopes", "Assign scopes to a role", {
    type: "object", required: ["roleId", "scopeIds"],
    properties: { roleId: { type: "string" }, scopeIds: { type: "array", items: { type: "string" } } },
  }, async ({ roleId, scopeIds }) =>
    (await getClient()).post(`/roles/${roleId}/scopes`, { scopeIds }).then((r) => r.data));

  tool("remove_role_scope", "Remove a scope from a role", {
    type: "object", required: ["roleId", "scopeId"],
    properties: { roleId: { type: "string" }, scopeId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/roles/${a.roleId}/scopes/${a.scopeId}`).then((r) => r.data));

  tool("get_role_users", "Get users assigned to a role", {
    type: "object", required: ["roleId"],
    properties: { roleId: { type: "string" }, page: { type: "number" }, page_size: { type: "number" } },
  }, async ({ roleId, ...q }) =>
    (await getClient()).get(`/roles/${roleId}/users${buildQuery(q)}`).then((r) => r.data));

  tool("get_role_applications", "Get M2M applications assigned to a role", {
    type: "object", required: ["roleId"],
    properties: { roleId: { type: "string" }, page: { type: "number" }, page_size: { type: "number" } },
  }, async ({ roleId, ...q }) =>
    (await getClient()).get(`/roles/${roleId}/applications${buildQuery(q)}`).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // API RESOURCES
  // ═══════════════════════════════════════════════════════════════

  tool("list_resources", "List all API resources", {
    type: "object",
    properties: { page: { type: "number" }, page_size: { type: "number" }, keyword: { type: "string" } },
  }, async (a) => (await getClient()).get(`/resources${buildQuery(a)}`).then((r) => r.data));

  tool("create_resource", "Create an API resource", {
    type: "object", required: ["name", "indicator"],
    properties: {
      name: { type: "string" },
      indicator: { type: "string", description: "Unique URI for the resource" },
      isDefault: { type: "boolean" },
      accessTokenTtl: { type: "number" },
    },
  }, async (a) => (await getClient()).post("/resources", a).then((r) => r.data));

  tool("get_resource", "Get an API resource by ID", {
    type: "object", required: ["resourceId"],
    properties: { resourceId: { type: "string" } },
  }, async (a) => (await getClient()).get(`/resources/${a.resourceId}`).then((r) => r.data));

  tool("update_resource", "Update an API resource", {
    type: "object", required: ["resourceId"],
    properties: {
      resourceId: { type: "string" },
      name: { type: "string" },
      accessTokenTtl: { type: "number" },
      isDefault: { type: "boolean" },
    },
  }, async ({ resourceId, ...body }) =>
    (await getClient()).patch(`/resources/${resourceId}`, body).then((r) => r.data));

  tool("delete_resource", "Delete an API resource", {
    type: "object", required: ["resourceId"],
    properties: { resourceId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/resources/${a.resourceId}`).then((r) => r.data));

  tool("list_resource_scopes", "List scopes for an API resource", {
    type: "object", required: ["resourceId"],
    properties: { resourceId: { type: "string" }, page: { type: "number" }, page_size: { type: "number" } },
  }, async ({ resourceId, ...q }) =>
    (await getClient()).get(`/resources/${resourceId}/scopes${buildQuery(q)}`).then((r) => r.data));

  tool("create_resource_scope", "Create a scope for an API resource", {
    type: "object", required: ["resourceId", "name"],
    properties: { resourceId: { type: "string" }, name: { type: "string" }, description: { type: "string" } },
  }, async ({ resourceId, ...body }) =>
    (await getClient()).post(`/resources/${resourceId}/scopes`, body).then((r) => r.data));

  tool("update_resource_scope", "Update a scope in an API resource", {
    type: "object", required: ["resourceId", "scopeId"],
    properties: {
      resourceId: { type: "string" },
      scopeId: { type: "string" },
      name: { type: "string" },
      description: { type: "string" },
    },
  }, async ({ resourceId, scopeId, ...body }) =>
    (await getClient()).patch(`/resources/${resourceId}/scopes/${scopeId}`, body).then((r) => r.data));

  tool("delete_resource_scope", "Delete a scope from an API resource", {
    type: "object", required: ["resourceId", "scopeId"],
    properties: { resourceId: { type: "string" }, scopeId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/resources/${a.resourceId}/scopes/${a.scopeId}`).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // CONNECTORS
  // ═══════════════════════════════════════════════════════════════

  tool("list_connectors", "List all connectors", {
    type: "object",
    properties: { page: { type: "number" }, page_size: { type: "number" }, target: { type: "string" } },
  }, async (a) => (await getClient()).get(`/connectors${buildQuery(a)}`).then((r) => r.data));

  tool("create_connector", "Create a connector", {
    type: "object", required: ["connectorId"],
    properties: {
      connectorId: { type: "string" },
      config: { type: "object" },
      metadata: { type: "object" },
      syncProfile: { type: "boolean" },
    },
  }, async (a) => (await getClient()).post("/connectors", a).then((r) => r.data));

  tool("get_connector", "Get a connector by ID", {
    type: "object", required: ["connectorId"],
    properties: { connectorId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/connectors/${a.connectorId}`).then((r) => r.data));

  tool("update_connector", "Update a connector", {
    type: "object", required: ["connectorId"],
    properties: {
      connectorId: { type: "string" },
      config: { type: "object" },
      metadata: { type: "object" },
      syncProfile: { type: "boolean" },
    },
  }, async ({ connectorId, ...body }) =>
    (await getClient()).patch(`/connectors/${connectorId}`, body).then((r) => r.data));

  tool("delete_connector", "Delete a connector", {
    type: "object", required: ["connectorId"],
    properties: { connectorId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/connectors/${a.connectorId}`).then((r) => r.data));

  tool("test_connector", "Test a passwordless connector", {
    type: "object", required: ["connectorId"],
    properties: {
      connectorId: { type: "string" },
      phone: { type: "string" },
      email: { type: "string" },
    },
  }, async ({ connectorId, ...body }) =>
    (await getClient()).post(`/connectors/${connectorId}/test`, body).then((r) => r.data));

  tool("list_connector_factories", "List all connector factories", {
    type: "object",
    properties: { keyword: { type: "string" }, type: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/connector-factories${buildQuery(a)}`).then((r) => r.data));

  tool("get_connector_factory", "Get a connector factory by ID", {
    type: "object", required: ["factoryId"],
    properties: { factoryId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/connector-factories/${a.factoryId}`).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // WEBHOOKS (HOOKS)
  // ═══════════════════════════════════════════════════════════════

  tool("list_hooks", "List all webhooks", {
    type: "object",
    properties: { page: { type: "number" }, page_size: { type: "number" }, keyword: { type: "string" } },
  }, async (a) => (await getClient()).get(`/hooks${buildQuery(a)}`).then((r) => r.data));

  tool("create_hook", "Create a webhook", {
    type: "object", required: ["name", "events", "config"],
    properties: {
      name: { type: "string" },
      events: { type: "array", items: { type: "string" } },
      config: { type: "object", description: "{ url, headers?, retries? }" },
      enabled: { type: "boolean" },
    },
  }, async (a) => (await getClient()).post("/hooks", a).then((r) => r.data));

  tool("get_hook", "Get a webhook by ID", {
    type: "object", required: ["hookId"],
    properties: { hookId: { type: "string" } },
  }, async (a) => (await getClient()).get(`/hooks/${a.hookId}`).then((r) => r.data));

  tool("update_hook", "Update a webhook", {
    type: "object", required: ["hookId"],
    properties: {
      hookId: { type: "string" },
      name: { type: "string" },
      events: { type: "array", items: { type: "string" } },
      config: { type: "object" },
      enabled: { type: "boolean" },
    },
  }, async ({ hookId, ...body }) =>
    (await getClient()).patch(`/hooks/${hookId}`, body).then((r) => r.data));

  tool("delete_hook", "Delete a webhook", {
    type: "object", required: ["hookId"],
    properties: { hookId: { type: "string" } },
  }, async (a) => (await getClient()).delete(`/hooks/${a.hookId}`).then((r) => r.data));

  tool("test_hook", "Test a webhook by sending a test event", {
    type: "object", required: ["hookId"],
    properties: { hookId: { type: "string" }, event: { type: "string" } },
  }, async ({ hookId, ...body }) =>
    (await getClient()).post(`/hooks/${hookId}/test`, body).then((r) => r.data));

  tool("get_hook_recent_logs", "Get recent logs for a webhook", {
    type: "object", required: ["hookId"],
    properties: { hookId: { type: "string" }, page: { type: "number" }, page_size: { type: "number" } },
  }, async ({ hookId, ...q }) =>
    (await getClient()).get(`/hooks/${hookId}/recent-logs${buildQuery(q)}`).then((r) => r.data));

  tool("update_hook_signing_key", "Regenerate the signing key for a webhook", {
    type: "object", required: ["hookId"],
    properties: { hookId: { type: "string" } },
  }, async (a) =>
    (await getClient()).patch(`/hooks/${a.hookId}/signing-key`).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // SIGN-IN EXPERIENCE
  // ═══════════════════════════════════════════════════════════════

  tool("get_sign_in_experience", "Get sign-in experience settings", {
    type: "object", properties: {},
  }, async () => (await getClient()).get("/sign-in-exp").then((r) => r.data));

  tool("update_sign_in_experience", "Update sign-in experience settings", {
    type: "object",
    properties: {
      color: { type: "object" },
      branding: { type: "object" },
      signInMode: { type: "string", enum: ["SignIn", "Register", "SignInAndRegister"] },
      signUp: { type: "object" },
      signIn: { type: "object" },
      socialSignInConnectorTargets: { type: "array", items: { type: "string" } },
      mfa: { type: "object" },
      passwordPolicy: { type: "object" },
      customCss: { type: "string" },
    },
  }, async (a) => (await getClient()).patch("/sign-in-exp", a).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // AUDIT LOGS
  // ═══════════════════════════════════════════════════════════════

  tool("list_logs", "Get audit logs with filters", {
    type: "object",
    properties: {
      page: { type: "number" },
      page_size: { type: "number" },
      userId: { type: "string" },
      applicationId: { type: "string" },
      logKey: { type: "string" },
      startTimeExclusive: { type: "number" },
      endTimeInclusive: { type: "number" },
    },
  }, async (a) => (await getClient()).get(`/logs${buildQuery(a)}`).then((r) => r.data));

  tool("get_log", "Get a single audit log entry", {
    type: "object", required: ["logId"],
    properties: { logId: { type: "string" } },
  }, async (a) => (await getClient()).get(`/logs/${a.logId}`).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // CONFIGS
  // ═══════════════════════════════════════════════════════════════

  tool("get_admin_console_config", "Get admin console configuration", {
    type: "object", properties: {},
  }, async () => (await getClient()).get("/configs/admin-console").then((r) => r.data));

  tool("update_admin_console_config", "Update admin console configuration", {
    type: "object",
    properties: { language: { type: "string" }, sessionDuration: { type: "number" } },
  }, async (a) => (await getClient()).patch("/configs/admin-console", a).then((r) => r.data));

  tool("get_oidc_keys", "Get OIDC signing or cookie keys", {
    type: "object", required: ["keyType"],
    properties: { keyType: { type: "string", enum: ["private-keys", "cookie-keys"] } },
  }, async (a) =>
    (await getClient()).get(`/configs/oidc/${a.keyType}`).then((r) => r.data));

  tool("rotate_oidc_keys", "Rotate OIDC keys", {
    type: "object", required: ["keyType"],
    properties: {
      keyType: { type: "string", enum: ["private-keys", "cookie-keys"] },
      signingKeyAlgorithm: { type: "string", enum: ["EC", "RSA"] },
    },
  }, async ({ keyType, ...body }) =>
    (await getClient()).post(`/configs/oidc/${keyType}/rotate`, body).then((r) => r.data));

  tool("delete_oidc_key", "Delete an OIDC key by ID", {
    type: "object", required: ["keyType", "keyId"],
    properties: {
      keyType: { type: "string", enum: ["private-keys", "cookie-keys"] },
      keyId: { type: "string" },
    },
  }, async (a) =>
    (await getClient()).delete(`/configs/oidc/${a.keyType}/${a.keyId}`).then((r) => r.data));

  tool("list_jwt_customizers", "List all JWT customizers", {
    type: "object", properties: {},
  }, async () => (await getClient()).get("/configs/jwt-customizer").then((r) => r.data));

  tool("get_jwt_customizer", "Get a JWT customizer", {
    type: "object", required: ["tokenTypePath"],
    properties: { tokenTypePath: { type: "string", enum: ["access-token", "client-credentials"] } },
  }, async (a) =>
    (await getClient()).get(`/configs/jwt-customizer/${a.tokenTypePath}`).then((r) => r.data));

  tool("upsert_jwt_customizer", "Create or update a JWT customizer", {
    type: "object", required: ["tokenTypePath"],
    properties: {
      tokenTypePath: { type: "string", enum: ["access-token", "client-credentials"] },
      script: { type: "string" },
      environmentVariables: { type: "object" },
      contextSample: { type: "object" },
    },
  }, async ({ tokenTypePath, ...body }) =>
    (await getClient()).put(`/configs/jwt-customizer/${tokenTypePath}`, body).then((r) => r.data));

  tool("delete_jwt_customizer", "Delete a JWT customizer", {
    type: "object", required: ["tokenTypePath"],
    properties: { tokenTypePath: { type: "string", enum: ["access-token", "client-credentials"] } },
  }, async (a) =>
    (await getClient()).delete(`/configs/jwt-customizer/${a.tokenTypePath}`).then((r) => r.data));

  tool("test_jwt_customizer", "Test a JWT customizer script", {
    type: "object", required: ["tokenTypePath"],
    properties: {
      tokenTypePath: { type: "string", enum: ["access-token", "client-credentials"] },
      token: { type: "object" },
      context: { type: "object" },
      environmentVariables: { type: "object" },
    },
  }, async ({ tokenTypePath, ...body }) =>
    (await getClient()).post(`/configs/jwt-customizer/${tokenTypePath}/test`, body).then((r) => r.data));

  tool("get_id_token_config", "Get ID token claims configuration", {
    type: "object", properties: {},
  }, async () => (await getClient()).get("/configs/id-token").then((r) => r.data));

  tool("upsert_id_token_config", "Update ID token claims configuration", {
    type: "object",
    properties: { claims: { type: "array", items: { type: "string" } } },
  }, async (a) => (await getClient()).put("/configs/id-token", a).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // DOMAINS
  // ═══════════════════════════════════════════════════════════════

  tool("list_domains", "List all custom domains", {
    type: "object", properties: {},
  }, async () => (await getClient()).get("/domains").then((r) => r.data));

  tool("create_domain", "Add a custom domain", {
    type: "object", required: ["domain"],
    properties: { domain: { type: "string" } },
  }, async (a) => (await getClient()).post("/domains", a).then((r) => r.data));

  tool("get_domain", "Get a custom domain by ID", {
    type: "object", required: ["domainId"],
    properties: { domainId: { type: "string" } },
  }, async (a) => (await getClient()).get(`/domains/${a.domainId}`).then((r) => r.data));

  tool("delete_domain", "Delete a custom domain", {
    type: "object", required: ["domainId"],
    properties: { domainId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/domains/${a.domainId}`).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // DASHBOARD
  // ═══════════════════════════════════════════════════════════════

  tool("get_total_user_count", "Get total number of registered users", {
    type: "object", properties: {},
  }, async () => (await getClient()).get("/dashboard/users/total").then((r) => r.data));

  tool("get_new_user_counts", "Get new user registration counts over time", {
    type: "object", properties: {},
  }, async () => (await getClient()).get("/dashboard/users/new").then((r) => r.data));

  tool("get_active_user_counts", "Get active user counts over time", {
    type: "object", properties: {},
  }, async () => (await getClient()).get("/dashboard/users/active").then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // CUSTOM PHRASES (i18n)
  // ═══════════════════════════════════════════════════════════════

  tool("list_custom_phrases", "List all custom i18n phrases", {
    type: "object", properties: {},
  }, async () => (await getClient()).get("/custom-phrases").then((r) => r.data));

  tool("get_custom_phrase", "Get custom phrases for a language", {
    type: "object", required: ["languageTag"],
    properties: { languageTag: { type: "string", description: "e.g. en, zh-CN" } },
  }, async (a) =>
    (await getClient()).get(`/custom-phrases/${a.languageTag}`).then((r) => r.data));

  tool("upsert_custom_phrase", "Create or replace custom phrases for a language", {
    type: "object", required: ["languageTag", "translation"],
    properties: { languageTag: { type: "string" }, translation: { type: "object" } },
  }, async ({ languageTag, translation }) =>
    (await getClient()).put(`/custom-phrases/${languageTag}`, translation).then((r) => r.data));

  tool("delete_custom_phrase", "Delete custom phrases for a language", {
    type: "object", required: ["languageTag"],
    properties: { languageTag: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/custom-phrases/${a.languageTag}`).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // CUSTOM PROFILE FIELDS
  // ═══════════════════════════════════════════════════════════════

  tool("list_custom_profile_fields", "List all custom profile fields", {
    type: "object", properties: {},
  }, async () => (await getClient()).get("/custom-profile-fields").then((r) => r.data));

  tool("create_custom_profile_field", "Create a custom profile field", {
    type: "object", required: ["name", "type"],
    properties: {
      name: { type: "string" },
      type: { type: "string", enum: ["Text", "Number", "Date", "Checkbox", "Select", "Url"] },
      label: { type: "object" },
      description: { type: "object" },
      required: { type: "boolean" },
      config: { type: "object" },
    },
  }, async (a) => (await getClient()).post("/custom-profile-fields", a).then((r) => r.data));

  tool("get_custom_profile_field", "Get a custom profile field by name", {
    type: "object", required: ["fieldName"],
    properties: { fieldName: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/custom-profile-fields/${a.fieldName}`).then((r) => r.data));

  tool("update_custom_profile_field", "Update a custom profile field", {
    type: "object", required: ["fieldName"],
    properties: {
      fieldName: { type: "string" },
      label: { type: "object" },
      description: { type: "object" },
      required: { type: "boolean" },
      config: { type: "object" },
    },
  }, async ({ fieldName, ...body }) =>
    (await getClient()).put(`/custom-profile-fields/${fieldName}`, body).then((r) => r.data));

  tool("delete_custom_profile_field", "Delete a custom profile field", {
    type: "object", required: ["fieldName"],
    properties: { fieldName: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/custom-profile-fields/${a.fieldName}`).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // ONE-TIME TOKENS
  // ═══════════════════════════════════════════════════════════════

  tool("list_one_time_tokens", "List all one-time tokens", {
    type: "object",
    properties: { page: { type: "number" }, page_size: { type: "number" } },
  }, async (a) => (await getClient()).get(`/one-time-tokens${buildQuery(a)}`).then((r) => r.data));

  tool("create_one_time_token", "Create a one-time token for magic link / invite", {
    type: "object", required: ["email"],
    properties: {
      email: { type: "string" },
      expiresIn: { type: "number", description: "TTL in seconds" },
      context: { type: "object" },
    },
  }, async (a) => (await getClient()).post("/one-time-tokens", a).then((r) => r.data));

  tool("get_one_time_token", "Get a one-time token by ID", {
    type: "object", required: ["tokenId"],
    properties: { tokenId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/one-time-tokens/${a.tokenId}`).then((r) => r.data));

  tool("delete_one_time_token", "Delete a one-time token", {
    type: "object", required: ["tokenId"],
    properties: { tokenId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/one-time-tokens/${a.tokenId}`).then((r) => r.data));

  tool("verify_one_time_token", "Verify a one-time token value", {
    type: "object", required: ["token", "email"],
    properties: { token: { type: "string" }, email: { type: "string" } },
  }, async (a) => (await getClient()).post("/one-time-tokens/verify", a).then((r) => r.data));

  tool("update_one_time_token_status", "Update the status of a one-time token", {
    type: "object", required: ["tokenId", "status"],
    properties: {
      tokenId: { type: "string" },
      status: { type: "string", enum: ["Active", "Inactive"] },
    },
  }, async ({ tokenId, status }) =>
    (await getClient()).put(`/one-time-tokens/${tokenId}/status`, { status }).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // EMAIL TEMPLATES
  // ═══════════════════════════════════════════════════════════════

  tool("list_email_templates", "List all email templates", {
    type: "object",
    properties: { page: { type: "number" }, page_size: { type: "number" } },
  }, async (a) => (await getClient()).get(`/email-templates${buildQuery(a)}`).then((r) => r.data));

  tool("get_email_template", "Get an email template by ID", {
    type: "object", required: ["templateId"],
    properties: { templateId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/email-templates/${a.templateId}`).then((r) => r.data));

  tool("update_email_template", "Update an email template", {
    type: "object", required: ["templateId"],
    properties: {
      templateId: { type: "string" },
      subject: { type: "string" },
      content: { type: "string" },
      contentType: { type: "string", enum: ["text/html", "text/plain"] },
    },
  }, async ({ templateId, ...body }) =>
    (await getClient()).patch(`/email-templates/${templateId}`, body).then((r) => r.data));

  tool("delete_email_template", "Delete an email template", {
    type: "object", required: ["templateId"],
    properties: { templateId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/email-templates/${a.templateId}`).then((r) => r.data));

  tool("replace_email_templates", "Replace multiple email templates at once", {
    type: "object", required: ["templates"],
    properties: { templates: { type: "array", items: { type: "object" } } },
  }, async ({ templates }) =>
    (await getClient()).put("/email-templates", templates).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // CAPTCHA PROVIDER
  // ═══════════════════════════════════════════════════════════════

  tool("get_captcha_provider", "Get captcha provider configuration", {
    type: "object", properties: {},
  }, async () => (await getClient()).get("/captcha-provider").then((r) => r.data));

  tool("update_captcha_provider", "Set captcha provider (Turnstile, reCAPTCHA, etc.)", {
    type: "object",
    properties: {
      type: { type: "string", enum: ["Turnstile", "RecaptchaEnterprise"] },
      config: { type: "object" },
    },
  }, async (a) => (await getClient()).put("/captcha-provider", a).then((r) => r.data));

  tool("delete_captcha_provider", "Remove captcha provider", {
    type: "object", properties: {},
  }, async () => (await getClient()).delete("/captcha-provider").then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // ACCOUNT CENTER
  // ═══════════════════════════════════════════════════════════════

  tool("get_account_center_settings", "Get account center (self-service portal) settings", {
    type: "object", properties: {},
  }, async () => (await getClient()).get("/account-center").then((r) => r.data));

  tool("update_account_center_settings", "Update account center settings", {
    type: "object",
    properties: {
      enabled: { type: "boolean" },
      fields: { type: "object", description: "Map of field name to { enabled }" },
    },
  }, async (a) => (await getClient()).patch("/account-center", a).then((r) => r.data));

  // ═══════════════════════════════════════════════════════════════
  // SSO CONNECTORS (Enterprise)
  // ═══════════════════════════════════════════════════════════════

  tool("list_sso_connectors", "List all enterprise SSO connectors", {
    type: "object",
    properties: { page: { type: "number" }, page_size: { type: "number" } },
  }, async (a) => (await getClient()).get(`/sso-connectors${buildQuery(a)}`).then((r) => r.data));

  tool("create_sso_connector", "Create an enterprise SSO connector", {
    type: "object", required: ["providerName", "connectorName"],
    properties: {
      providerName: { type: "string" },
      connectorName: { type: "string" },
      config: { type: "object" },
      domains: { type: "array", items: { type: "string" } },
      syncProfile: { type: "boolean" },
    },
  }, async (a) => (await getClient()).post("/sso-connectors", a).then((r) => r.data));

  tool("get_sso_connector", "Get an enterprise SSO connector by ID", {
    type: "object", required: ["ssoConnectorId"],
    properties: { ssoConnectorId: { type: "string" } },
  }, async (a) =>
    (await getClient()).get(`/sso-connectors/${a.ssoConnectorId}`).then((r) => r.data));

  tool("update_sso_connector", "Update an enterprise SSO connector", {
    type: "object", required: ["ssoConnectorId"],
    properties: {
      ssoConnectorId: { type: "string" },
      connectorName: { type: "string" },
      config: { type: "object" },
      domains: { type: "array", items: { type: "string" } },
      syncProfile: { type: "boolean" },
    },
  }, async ({ ssoConnectorId, ...body }) =>
    (await getClient()).patch(`/sso-connectors/${ssoConnectorId}`, body).then((r) => r.data));

  tool("delete_sso_connector", "Delete an enterprise SSO connector", {
    type: "object", required: ["ssoConnectorId"],
    properties: { ssoConnectorId: { type: "string" } },
  }, async (a) =>
    (await getClient()).delete(`/sso-connectors/${a.ssoConnectorId}`).then((r) => r.data));

  tool("list_sso_connector_providers", "List all available SSO provider factories", {
    type: "object", properties: {},
  }, async () => (await getClient()).get("/sso-connector-providers").then((r) => r.data));
}
