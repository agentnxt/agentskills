import axios from "axios";
let managementToken = null;
let tokenExpiry = 0;
export async function getManagementClient(config) {
    if (!managementToken || Date.now() >= tokenExpiry) {
        const res = await axios.post(`${config.endpoint}/oidc/token`, new URLSearchParams({
            grant_type: "client_credentials",
            resource: `${config.endpoint}/api`,
            scope: "all",
        }), {
            auth: { username: config.appId, password: config.appSecret },
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
        });
        managementToken = res.data.access_token;
        tokenExpiry = Date.now() + (res.data.expires_in - 60) * 1000;
    }
    return axios.create({
        baseURL: `${config.endpoint}/api`,
        headers: { Authorization: `Bearer ${managementToken}` },
    });
}
export function getAccountsClient(config) {
    if (!config.accountsApiToken) {
        throw new Error("LOGTO_ACCOUNTS_TOKEN is required for Accounts API tools");
    }
    return axios.create({
        baseURL: `${config.endpoint}/api`,
        headers: { Authorization: `Bearer ${config.accountsApiToken}` },
    });
}
