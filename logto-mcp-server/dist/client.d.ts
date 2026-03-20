import { AxiosInstance } from "axios";
export interface LogtoConfig {
    endpoint: string;
    appId: string;
    appSecret: string;
    accountsApiToken?: string;
}
export declare function getManagementClient(config: LogtoConfig): Promise<AxiosInstance>;
export declare function getAccountsClient(config: LogtoConfig): AxiosInstance;
