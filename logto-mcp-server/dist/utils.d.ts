export declare function buildQuery(params: Record<string, unknown>): string;
export declare function ok(data: unknown): {
    content: {
        type: "text";
        text: string;
    }[];
};
export declare function err(e: unknown): {
    content: {
        type: "text";
        text: string;
    }[];
    isError: boolean;
};
