export interface Tool {
  name: string;
  type: "script" | "api" | "mcp";
  language?: string;
  description: string;
}

export interface Prompt {
  text: string;
  category: string;
  complexity: "low" | "medium" | "high";
}

export interface EvalResult {
  name: string;
  with_skill_score: number;
  with_skill_total: number;
  baseline_score: number;
  baseline_total: number;
  note?: string;
}

export interface BenchmarkResult {
  llm: string;
  framework: string;
  eval_score: number;
  tokens: number;
  duration_seconds: number;
  cost_llm: number;
  cost_infra: number;
}

export interface Skill {
  id: string;
  name: string;
  display_name: string;
  version: string;
  description: string;
  long_description: string;
  categories: string[];
  icon: string;
  tools: Tool[];
  prompts: Prompt[];
  evals: EvalResult[];
  benchmarks: BenchmarkResult[];
  aggregate_score: number;
  line_count: number;
  created_at: string;
}

export const categories = [
  "All",
  "Deployment",
  "CI/CD",
  "Monitoring",
  "Alerting",
  "Orchestration",
  "Integration",
  "Automation",
];

export const skills: Skill[] = [
  {
    id: "gcp-cloud-run-deploy",
    name: "gcp-cloud-run-deploy",
    display_name: "GCP Cloud Run Deploy",
    version: "1.1",
    description:
      "Full-lifecycle deployment of GitHub repos to Google Cloud Run via REST APIs — build, deploy, CI/CD, monitoring, and alerting.",
    long_description:
      "A comprehensive skill for deploying GitHub repositories to Google Cloud Run with full CI/CD, monitoring, and alerting — all via direct REST API calls (never CLI). Follows an API-first philosophy where every action leaves audit trails in Cloud Audit Logs. Supports both creating new services and updating existing ones, with user confirmation at every major step.",
    categories: ["Deployment", "CI/CD", "Monitoring", "Alerting"],
    icon: "cloud",
    tools: [
      {
        name: "auth.py",
        type: "script",
        language: "Python",
        description: "OAuth2 token exchange for GCP service accounts",
      },
      {
        name: "deploy.py",
        type: "script",
        language: "Python",
        description:
          "Build image via Cloud Build + deploy to Cloud Run via Admin API v2",
      },
      {
        name: "monitoring.py",
        type: "script",
        language: "Python",
        description: "Set up Metabase dashboards for Cloud Run monitoring",
      },
      {
        name: "alerts.py",
        type: "script",
        language: "Python",
        description:
          "Create GCP Cloud Monitoring alert policies and notification channels",
      },
    ],
    prompts: [
      {
        text: "I have a FastAPI app at github.com/myorg/inventory-api. Deploy it to Cloud Run in us-central1, set up GitHub Actions CI/CD, create a Metabase dashboard for monitoring, and add alerts for error rate and latency. My service account key is at ~/sa-key.json, project ID is acme-prod-2024, and Metabase is at https://metabase.acme.internal.",
        category: "Full Deploy",
        complexity: "high",
      },
      {
        text: "My Cloud Run service payment-gateway in eu-west1 needs updating — push the new image from the latest commit on main branch. Also add a webhook alert to https://hooks.slack.com/services/xxx when error rate goes above 3%. Project: fintech-staging, SA key: ~/keys/staging.json",
        category: "Update + Alerts",
        complexity: "medium",
      },
      {
        text: "I already have user-service running on Cloud Run in us-east1, project saas-platform. Set up both GitHub Actions and Cloud Build triggers for the repo mycompany/user-service. Then connect my Metabase at https://analytics.mycompany.com to show request rate, latency p95, and instance scaling. Suggest what other metrics I should track based on the codebase.",
        category: "CI/CD + Monitoring",
        complexity: "high",
      },
    ],
    evals: [
      {
        name: "Full Deploy (FastAPI)",
        with_skill_score: 11,
        with_skill_total: 11,
        baseline_score: 3,
        baseline_total: 11,
      },
      {
        name: "Update + Webhook Alert",
        with_skill_score: 3,
        with_skill_total: 6,
        baseline_score: 4,
        baseline_total: 6,
        note: "Agent truncated by permission issues",
      },
      {
        name: "CI/CD + Monitoring",
        with_skill_score: 6,
        with_skill_total: 7,
        baseline_score: 4,
        baseline_total: 7,
      },
    ],
    benchmarks: [
      {
        llm: "Claude Opus 4.6",
        framework: "Claude Code",
        eval_score: 0.786,
        tokens: 56074,
        duration_seconds: 255,
        cost_llm: 1.28,
        cost_infra: 0.0,
      },
    ],
    aggregate_score: 0.786,
    line_count: 450,
    created_at: "2026-04-10",
  },
  {
    id: "n8n-orchestrator",
    name: "n8n-orchestrator",
    display_name: "n8n Orchestrator",
    version: "1.0",
    description:
      "Build and manage n8n workflows on the AutonomyX platform — create, debug, and integrate with internal services.",
    long_description:
      "Build and manage n8n workflows with full knowledge of the AutonomyX platform architecture. Knows the correct internal service URLs, Docker network topology, n8n API endpoints, authentication patterns, and version-specific gotchas (like executeCommand being unavailable in v2.14.2). Connects Firecrawl, Ollama, Liferay, and Langflow through proper HTTP Request nodes.",
    categories: ["Orchestration", "Integration", "Automation"],
    icon: "workflow",
    tools: [
      {
        name: "n8n REST API",
        type: "api",
        description:
          "Workflows, executions, credentials CRUD at localhost:5678",
      },
      {
        name: "MCP Server (mcp-n8n)",
        type: "mcp",
        description: "JSON-RPC workflow management via MCP protocol",
      },
    ],
    prompts: [
      {
        text: "Create an n8n workflow that triggers on a webhook, fetches data from a Google Sheet, filters rows where status is 'pending', and sends each one to a Slack channel.",
        category: "Create Workflow",
        complexity: "medium",
      },
      {
        text: "My n8n workflow ID 42 keeps failing on execution. List recent executions, find the errors, and fix the workflow.",
        category: "Debug Workflow",
        complexity: "medium",
      },
      {
        text: "Build an n8n workflow that uses Firecrawl to scrape a URL, processes the content with Ollama (qwen2.5:7b), and posts the summary to Liferay as a web content article.",
        category: "Multi-Service Integration",
        complexity: "high",
      },
    ],
    evals: [
      {
        name: "Create Webhook Workflow",
        with_skill_score: 1,
        with_skill_total: 8,
        baseline_score: 0,
        baseline_total: 8,
        note: "Both outputs truncated by permission issues",
      },
      {
        name: "Debug Failing Workflow",
        with_skill_score: 7,
        with_skill_total: 7,
        baseline_score: 4,
        baseline_total: 7,
      },
      {
        name: "Multi-Service Integration",
        with_skill_score: 8,
        with_skill_total: 8,
        baseline_score: 0,
        baseline_total: 8,
      },
    ],
    benchmarks: [
      {
        llm: "Claude Opus 4.6",
        framework: "Claude Code",
        eval_score: 1.0,
        tokens: 41049,
        duration_seconds: 131,
        cost_llm: 0.98,
        cost_infra: 0.0,
      },
    ],
    aggregate_score: 1.0,
    line_count: 106,
    created_at: "2026-04-10",
  },
];
