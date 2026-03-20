export function buildQuery(params) {
    const q = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
        if (v !== undefined && v !== null && v !== "") {
            q.append(k, String(v));
        }
    }
    const s = q.toString();
    return s ? `?${s}` : "";
}
export function ok(data) {
    return {
        content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
}
export function err(e) {
    let message = "Unknown error";
    if (axios_is_error(e)) {
        message = `HTTP ${e.response?.status}: ${JSON.stringify(e.response?.data ?? e.message)}`;
    }
    else if (e instanceof Error) {
        message = e.message;
    }
    return {
        content: [{ type: "text", text: `Error: ${message}` }],
        isError: true,
    };
}
function axios_is_error(e) {
    return typeof e === "object" && e !== null && "message" in e;
}
