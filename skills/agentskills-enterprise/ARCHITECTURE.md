# Agent Skill Benchmark Platform — Architecture Spec

## Vision

A platform that benchmarks, showcases, and compares **Agent Skills** across every variable that affects their output — LLM, framework, tools, data pipeline, infrastructure, and more. Think OpenRouter Rankings meets Vertex AI Prompt Gallery, but for **agent skills** instead of raw models.

**Goal:** Answer the question — *"Given my skill, prompt, tools, LLM, and infrastructure, what result will I get, and how does it compare to alternatives?"*

---

## Data Model

### Entity Hierarchy

```
App (the client that runs everything)
└── Framework (orchestration layer)
    └── Skill (reusable instruction set)
        ├── Tools[] (scripts, APIs, MCP servers)
        ├── Prompts[] (optimized inputs)
        └── Results[] (benchmark runs)
            ├── LLM + Config
            ├── Data Pipeline
            ├── Context & Memory
            ├── Environment
            └── Output Metrics
```

### Core Entities

#### App
The outermost wrapper — the application that end-users interact with.

```json
{
  "id": "app_001",
  "name": "AgentNXT CLI",
  "type": "cli-agent",
  "category": ["coding", "devops", "automation"],
  "source_code_url": "https://github.com/agentnxt/cli",
  "ui_type": "cli",
  "supported_models": ["claude-opus-4.6", "claude-sonnet-4.6", "gpt-4o"],
  "total_tokens": 0,
  "total_requests": 0,
  "growth_percent": 0,
  "created_at": "2026-04-10"
}
```

#### Framework
The orchestration layer that runs the agent.

```json
{
  "id": "framework_001",
  "name": "Claude Code",
  "version": "2.1.92",
  "type": "skill-based",
  "supports_subagents": true,
  "supports_mcp": true,
  "supports_hooks": true,
  "supports_memory": true,
  "supports_planning": true
}
```

#### Skill
A reusable instruction set with bundled resources.

```json
{
  "id": "skill_001",
  "name": "gcp-cloud-run-deploy",
  "version": "1.1",
  "description": "Full-lifecycle Cloud Run deployment via REST APIs",
  "category": ["deployment", "ci-cd", "monitoring", "alerting"],
  "tools": ["tool_001", "tool_002", "tool_003", "tool_004"],
  "prompts": ["prompt_001", "prompt_002", "prompt_003"],
  "eval_score_aggregate": 0.786,
  "line_count": 450,
  "has_scripts": true,
  "has_references": true,
  "created_at": "2026-04-10"
}
```

#### Tool
A script, API, or MCP server that a skill uses.

```json
{
  "id": "tool_001",
  "name": "auth.py",
  "type": "script",
  "language": "python",
  "description": "OAuth2 token exchange for GCP service accounts",
  "inputs": ["service_account_key_json"],
  "outputs": ["bearer_token"],
  "dependencies": [],
  "api_endpoint": "https://oauth2.googleapis.com/token"
}
```

#### Prompt
An optimized input for a skill.

```json
{
  "id": "prompt_001",
  "skill_id": "skill_001",
  "text": "I have a FastAPI app at github.com/myorg/inventory-api. Deploy it to Cloud Run in us-central1, set up GitHub Actions CI/CD, create a Metabase dashboard for monitoring, and add alerts for error rate and latency.",
  "category": "full-deploy",
  "complexity": "high",
  "expected_tools_used": ["auth.py", "deploy.py", "monitoring.py", "alerts.py"],
  "tested": true
}
```

#### Result (Benchmark Run)
A single execution of Skill + Prompt + all variables.

```json
{
  "id": "result_001",
  "skill_id": "skill_001",
  "prompt_id": "prompt_001",
  "timestamp": "2026-04-10T21:30:00Z",

  "input_variables": {
    "app": { ... },
    "framework": { ... },
    "llm": { ... },
    "llm_config": { ... },
    "environment": { ... },
    "skill_config": { ... },
    "target_infra": { ... },
    "input_context": { ... },
    "data": { ... },
    "context_memory": { ... },
    "user": { ... },
    "agent_architecture": { ... },
    "safety": { ... },
    "temporal": { ... },
    "output_expectations": { ... },
    "versioning": { ... },
    "data_pipeline": { ... },
    "embeddings": { ... },
    "vector_db": { ... },
    "data_transform": { ... },
    "knowledge_graph": { ... },
    "model_provider": { ... },
    "model_capabilities": { ... },
    "benchmarks": { ... },
    "usage_analytics": { ... }
  },

  "output_metrics": {
    "eval_score": 1.0,
    "assertions_passed": 11,
    "assertions_total": 11,
    "tokens_input": 25000,
    "tokens_output": 12000,
    "duration_seconds": 255,
    "cost_llm": 1.28,
    "cost_infra": 0.00,
    "steps_taken": 27,
    "user_confirmations": 6,
    "errors_encountered": 0,
    "completeness": 1.0
  }
}
```

---

## Variable Taxonomy (151 variables, 9 output metrics)

### 1. Core (5)
| Variable | Type | Description |
|----------|------|-------------|
| skill | ref | Which skill is being used |
| skill_version | string | Version of the skill |
| prompt | ref | Which prompt is being used |
| tools | ref[] | Tools available to the skill |
| mcp_servers | ref[] | MCP servers connected |

### 2. LLM Configuration (5)
| Variable | Type | Description |
|----------|------|-------------|
| temperature | float | 0.0-2.0, creativity vs determinism |
| max_tokens | int | Output length limit |
| context_window | int | Total context capacity |
| system_prompt | text | Behavioral instructions |
| thinking_mode | enum | Extended thinking on/off, budget |

### 3. Execution Environment (6)
| Variable | Type | Description |
|----------|------|-------------|
| runtime | enum | Local, Docker, Cloud VM, serverless |
| os | enum | macOS, Linux, Windows |
| network_access | enum | Full, VPN, air-gapped, internal |
| auth_context | enum | SA key, OAuth, API key, ambient |
| permissions | enum | Full, read-only, sandboxed |
| installed_tools | string[] | Python version, Docker, etc. |

### 4. Skill Configuration (4)
| Variable | Type | Description |
|----------|------|-------------|
| skill_version | string | v1.0, v1.1, etc. |
| reference_docs_loaded | string[] | Which refs were loaded |
| bundled_scripts | string[] | Available helper scripts |
| mcp_servers_connected | string[] | Active MCP connections |

### 5. Target Infrastructure (5)
| Variable | Type | Description |
|----------|------|-------------|
| cloud_provider | enum | GCP, AWS, Azure, self-hosted |
| region | string | us-central1, eu-west1, etc. |
| existing_state | enum | Greenfield, existing services |
| iam_permissions | string[] | Roles assigned |
| quotas_limits | object | Free tier, rate limits |

### 6. Input Context (4)
| Variable | Type | Description |
|----------|------|-------------|
| codebase_language | string | Python, Node, Go, etc. |
| repo_structure | enum | Monorepo, single service |
| existing_cicd | enum | None, GitHub Actions, Jenkins |
| secrets_count | int | Number of env vars/secrets |

### 7. Data (6)
| Variable | Type | Description |
|----------|------|-------------|
| training_data_cutoff | date | LLM knowledge boundary |
| rag_data_sources | string[] | Docs, vector DB, etc. |
| user_data | object | Files, DBs, spreadsheets |
| schema | object | JSON/DB/API schemas |
| data_volume | string | 10 rows vs 10M rows |
| data_freshness | enum | Real-time, cached, historical |

### 8. Context & Memory (8)
| Variable | Type | Description |
|----------|------|-------------|
| conversation_history_length | int | Messages in session |
| system_instructions | text | CLAUDE.md content |
| persistent_memory | object | User prefs, past decisions |
| project_memory | object | Deadlines, initiatives |
| feedback_memory | object | Learned corrections |
| session_state | object | Current progress |
| multi_agent_context | object | Shared state |
| context_window_usage | float | % of window consumed |

### 9. User / Human-in-the-Loop (5)
| Variable | Type | Description |
|----------|------|-------------|
| user_expertise | enum | Junior, senior, non-technical |
| approval_speed | enum | Instant, deliberate |
| approval_pattern | enum | Approve-all, selective |
| language_locale | string | en, hi, es, etc. |
| intent_clarity | enum | Vague, moderate, detailed |

### 10. Agent Architecture (6)
| Variable | Type | Description |
|----------|------|-------------|
| agent_type | enum | Single, multi-agent |
| delegation_depth | int | Levels of subagents |
| retry_strategy | enum | Fail-fast, retry-3x |
| fallback_chain | string[] | Opus→Sonnet→Haiku |
| planning_mode | enum | Plan-then-execute, streaming |
| tool_selection | enum | Greedy, deliberate |

### 11. Safety & Compliance (5)
| Variable | Type | Description |
|----------|------|-------------|
| content_filters | enum | Strict, moderate, off |
| sandbox_mode | enum | Full, read-only, dry-run |
| audit_requirements | string[] | SOC2, GDPR, HIPAA |
| secret_handling | enum | Hardcoded, Secret Manager, vault |
| pii_sensitivity | enum | Can see, redacted |

### 12. Temporal / Timing (5)
| Variable | Type | Description |
|----------|------|-------------|
| time_of_execution | datetime | Peak vs off-peak |
| api_availability | enum | Up, degraded, maintenance |
| concurrent_usage | int | Solo vs 100 agents |
| timeout_settings | int | Seconds allowed |
| freshness_requirement | enum | Real-time, eventual |

### 13. Output Expectations (4)
| Variable | Type | Description |
|----------|------|-------------|
| format | enum | JSON, YAML, code, prose |
| verbosity | enum | Terse, detailed |
| audience | enum | Machine, human |
| determinism_required | bool | Same output every time? |

### 14. Versioning (5)
| Variable | Type | Description |
|----------|------|-------------|
| llm_version | string | opus-4.6, sonnet-4.6 |
| framework_version | string | Claude Code 2.1 |
| api_versions | object | Cloud Run v2, n8n 2.14 |
| sdk_versions | object | Python 3.9, Node 22 |
| skill_version | string | v1.0, v1.1 |

### 15. Evaluation Criteria (4)
| Variable | Type | Description |
|----------|------|-------------|
| grader | enum | Human, script, LLM-as-judge |
| rubric | enum | Binary, 1-5 scale, qualitative |
| subjectivity | enum | Objective, subjective |
| baseline | enum | No-skill, previous version, competitor |

### 16. Data Processing Pipeline (4)
| Variable | Type | Description |
|----------|------|-------------|
| chunking_algorithm | enum | Fixed, semantic, sentence, recursive |
| chunk_size | int | Tokens per chunk |
| chunk_overlap | int | Overlap tokens |
| splitting_strategy | enum | Paragraph, heading, code block |

### 17. Embeddings (5)
| Variable | Type | Description |
|----------|------|-------------|
| embedding_model | string | text-embedding-3-large, etc. |
| embedding_dimensions | int | 256, 768, 1536, 3072 |
| normalization | enum | L2, cosine, none |
| fine_tuned | bool | Domain-specific or generic |
| multimodal | bool | Text-only vs text+image+code |

### 18. Vector Database / Retrieval (8)
| Variable | Type | Description |
|----------|------|-------------|
| vector_db | string | Pinecone, Qdrant, pgvector |
| index_type | enum | HNSW, IVF, flat |
| distance_metric | enum | Cosine, dot product, Euclidean |
| top_k | int | Results returned |
| similarity_threshold | float | Cutoff score |
| hybrid_search | bool | Vector + keyword |
| reranker | string | Cohere, cross-encoder, none |
| metadata_filtering | bool | Pre-filter by attributes |

### 19. Data Transformation (5)
| Variable | Type | Description |
|----------|------|-------------|
| preprocessing | string[] | Strip HTML, OCR, PDF parse |
| enrichment | string[] | Entity extraction, summarization |
| deduplication | enum | Exact, fuzzy, semantic |
| update_strategy | enum | Full reindex, incremental |
| ttl_seconds | int | Cache expiry |

### 20. Knowledge Graph (4)
| Variable | Type | Description |
|----------|------|-------------|
| graph_db | string | Neo4j, SurrealDB, Neptune |
| ontology | string | Schema.org, custom |
| traversal_depth | int | Hops in graph |
| hybrid_retrieval | bool | Graph + vector combined |

### 21. Model Provider / Routing (7)
| Variable | Type | Description |
|----------|------|-------------|
| provider | string | Direct API, OpenRouter, Bedrock |
| model_variant | string | claude-opus-4.6-fast vs standard |
| pricing_tier | enum | Pay-per-token, free, batch |
| input_price_per_m | float | $/M input tokens |
| output_price_per_m | float | $/M output tokens |
| cache_pricing | object | Read/write cache discounts |
| rate_limits | object | RPM, TPM, concurrent |

### 22. Model Capabilities (7)
| Variable | Type | Description |
|----------|------|-------------|
| modality | string[] | Text, image, audio, video |
| tool_calling | enum | None, sequential, parallel |
| structured_output | bool | JSON mode support |
| streaming | bool | Streaming support |
| code_execution | bool | Built-in sandbox |
| web_search | enum | Built-in, tool-based, none |
| file_handling | string[] | PDF, images, audio |

### 23. Performance Benchmarks (8)
| Variable | Type | Description |
|----------|------|-------------|
| mmlu | float | General knowledge |
| humaneval | float | Coding ability |
| swe_bench | float | Real-world software engineering |
| gpqa | float | Graduate-level reasoning |
| math_score | float | Mathematical reasoning |
| arena_elo | int | Human preference ranking |
| ttft_ms | int | Time to first token |
| tokens_per_second | float | Generation speed |

### 24. Usage Analytics (5)
| Variable | Type | Description |
|----------|------|-------------|
| market_share | float | % of total tokens |
| weekly_token_volume | int | Tokens processed |
| use_case_distribution | object | % by category |
| language_distribution | object | % by language |
| failure_rate | float | % of errored requests |

### 25. Application / Client (8)
| Variable | Type | Description |
|----------|------|-------------|
| app_type | enum | CLI, IDE extension, cloud agent |
| app_category | string[] | Coding, roleplay, research |
| total_tokens | int | Lifetime token consumption |
| total_requests | int | Lifetime API calls |
| growth_rate | float | Weekly growth % |
| source_code | string | Repo URL or "closed" |
| supported_models | string[] | Compatible LLMs |
| ui_type | enum | CLI, web, desktop, mobile, API |

### 26. Task-Model Routing (10)

Not every subtask should go to the same model. The orchestrator (general LLM) decides **what** to do, then routes each subtask to the **best specialized model** for that task type.

| Variable | Type | Description |
|----------|------|-------------|
| task_type | enum | text-gen, image-gen, video-gen, audio-gen, tts, stt, embedding, ocr, translation, code-completion, math-reasoning |
| routed_model | string | Which model actually handles this subtask |
| model_specialization | enum | general, specialized | 
| routing_strategy | enum | task-based, cost-based, latency-based, quality-based |
| fallback_chain | string[] | Ordered list of models to try (e.g., Ollama → Gemini free → OpenAI free → paid) |
| free_tier_priority | bool | Always try free tiers before paid |
| self_hosted | bool | Prefer self-hosted (Ollama) over cloud APIs |
| cost_budget | float | Max $ per task, route to cheapest model that meets quality threshold |
| quality_threshold | float | Minimum acceptable quality (0.0-1.0) before escalating to better model |
| nothing_hardcoded | bool | All model names, URLs, endpoints via env vars / config |

#### Task-Model Mapping (Default)

The orchestrator LLM (e.g., Claude in conversation, or Gemma for evals) plans the workflow. For each subtask, it routes to the best model:

| Task Type | Best Model Category | Open Source Options | Paid Options |
|-----------|-------------------|---------------------|-------------|
| **Orchestration / Planning** | General LLM | Gemma 4 31B, Llama 3.3 | Claude, GPT-4o |
| **Text Generation** | General LLM | Gemma 4 31B | Claude, GPT-4o |
| **Text → Image** | Image Gen | Flux, SDXL, Stable Diffusion 3 | DALL-E 3, Midjourney, Imagen 3 |
| **Text → Video** | Video Gen | CogVideoX, Open-Sora | Runway Gen-3, Kling, Veo 2 |
| **Text → Audio/Music** | Audio Gen | Bark, MusicGen | Suno, Udio, ElevenLabs |
| **Text → Speech (TTS)** | TTS | Piper, Coqui, F5-TTS | ElevenLabs, Google TTS |
| **Speech → Text (STT)** | STT | Whisper (local) | Whisper API, Deepgram |
| **Embeddings** | Embedding model | BGE-M3, Nomic, Jina | text-embedding-3-large |
| **OCR** | OCR engine | Surya, PaddleOCR, Tesseract | Google Vision, Azure OCR |
| **Translation** | Translation model | NLLB, SeamlessM4T | DeepL, Google Translate |
| **Code Completion** | Code LLM | DeepSeek Coder, Codestral | Copilot, Claude |
| **Math / Reasoning** | Reasoning LLM | DeepSeek R1, Qwen-Math | Claude (extended thinking), o3 |
| **Image Understanding** | Vision LLM | LLaVA, InternVL | Claude Vision, GPT-4o |
| **Reranking** | Reranker | Cross-encoder, ColBERT | Cohere Rerank |
| **Image Editing** | Image Editor | GIMP Script-Fu, ImageMagick, InstructPix2Pix | Adobe Firefly, Canva API |
| **Video Editing** | Video Editor | FFmpeg, MoviePy, DaVinci Resolve (scripted) | Runway, Descript API |
| **Video Understanding** | Video LLM | Video-LLaVA, InternVideo | Gemini 2.5 Pro, GPT-4o |
| **File Conversion** | Converter | Pandoc, LibreOffice CLI, ImageMagick, FFmpeg | CloudConvert, Zamzar API |
| **PDF Processing** | PDF tools | PyMuPDF, pdfplumber, Ghostscript | Adobe PDF Services |
| **Spreadsheet Processing** | Data tools | openpyxl, pandas, csvkit | Google Sheets API |
| **Audio Editing** | Audio Editor | FFmpeg, Audacity (CLI), SoX | Descript, Adobe Podcast |
| **3D / CAD** | 3D Gen | TripoSR, InstantMesh, OpenSCAD | Meshy, Spline AI |
| **Diagram / Chart** | Visualization | Mermaid, D3.js, Matplotlib, Graphviz | Excalidraw, Figma API |

#### Routing Logic

```
User request arrives
    │
    ▼
Orchestrator LLM decomposes into subtasks
    │
    ▼
For each subtask:
    ├── Identify task_type
    ├── Check config for task → model mapping
    ├── Try free_tier / self_hosted first
    ├── If fails or below quality_threshold → try next in fallback_chain
    ├── If cost_budget exceeded → stop and report
    └── Return result to orchestrator
    │
    ▼
Orchestrator combines results → final output
```

#### Config Example (env vars, never hardcoded)

```env
# Orchestrator
LLM_PROVIDER=ollama
LLM_MODEL=gemma4:31b
LLM_ENDPOINT=http://localllm:11434

# Task routing
IMAGE_GEN_MODEL=flux
IMAGE_GEN_ENDPOINT=http://localhost:7860
TTS_MODEL=piper
TTS_ENDPOINT=http://localhost:5500
STT_MODEL=whisper
STT_ENDPOINT=http://localhost:9000
EMBEDDING_MODEL=bge-m3
EMBEDDING_ENDPOINT=http://localhost:8080
OCR_ENGINE=surya

# Fallback chain (comma-separated)
FALLBACK_CHAIN=ollama,gemini-free,groq-free,openai-free,claude

# Budget
COST_BUDGET_PER_TASK=0.00
QUALITY_THRESHOLD=0.8
```

---

## Output Metrics (9)

| Metric | Type | Description |
|--------|------|-------------|
| eval_score | float | Assertion pass rate (0.0-1.0) |
| tokens_input | int | Input tokens consumed |
| tokens_output | int | Output tokens consumed |
| duration_seconds | float | Wall clock time |
| cost_llm | float | LLM provider cost ($) |
| cost_infra | float | Infrastructure cost ($) |
| steps_taken | int | Tool calls / API calls made |
| user_confirmations | int | Times paused for approval |
| errors_encountered | int | Retries and failures |
| completeness | float | Did it finish? (0.0-1.0) |

---

## Gallery UI Design

### Pages

#### 1. Skill Gallery (Home)
- Grid of skill cards with category filters
- Each card shows: name, description, category tags, eval score badge, tool count
- Search bar with natural language query
- Filter by: category, LLM, framework, eval score range

#### 2. Skill Detail Page
- Skill description and architecture diagram
- **Tools tab** — list of tools with descriptions, inputs/outputs
- **Prompts tab** — optimized prompts with copy button, complexity badge
- **Benchmarks tab** — comparison table across LLMs, frameworks
  - Sortable by eval score, cost, latency, completeness
  - Filter by LLM, framework, provider
- **Eval Results tab** — detailed assertion pass/fail per test case

#### 3. Compare Page
- Side-by-side comparison of 2-4 skills or configurations
- Radar chart: eval score, cost, speed, completeness, tool usage
- Table: all 151 variables with diff highlighting

#### 4. Leaderboard
- Rankings by: overall score, cost efficiency, speed, completeness
- Filter by category, LLM, framework
- Trending skills (growth rate)

#### 5. Submit Skill
- Upload SKILL.md + tools + prompts
- Auto-run evals against multiple LLMs
- Generate benchmark results
- Publish to gallery

### Card Component

```
┌─────────────────────────────────────────┐
│  [icon]  gcp-cloud-run-deploy     v1.1  │
│                                         │
│  Full-lifecycle Cloud Run deployment    │
│  via REST APIs with CI/CD, monitoring,  │
│  and alerting                           │
│                                         │
│  Tools: 4  │  Prompts: 3  │  Evals: 3  │
│                                         │
│  ┌──────┐ ┌──────┐ ┌──────────┐        │
│  │Deploy│ │CI/CD │ │Monitoring│        │
│  └──────┘ └──────┘ └──────────┘        │
│                                         │
│  Score: 100% (Opus 4.6)  Cost: $1.28   │
│         86% (Sonnet 4.6)  Cost: $0.30  │
│                                         │
│  [Try It]  [View Details]  [Compare]    │
└─────────────────────────────────────────┘
```

---

## Tech Stack (Recommendation)

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Next.js + Tailwind | Fast, SSR for SEO, great DX |
| UI Components | shadcn/ui | Clean, accessible, customizable |
| Database | Supabase (PostgreSQL) | Free tier, real-time, auth built-in |
| Vector search | pgvector (via Supabase) | Semantic skill search |
| File storage | Supabase Storage or GitHub | Skill files, eval outputs |
| Auth | Supabase Auth | GitHub OAuth for skill submissions |
| Hosting | Vercel or Cloud Run | Auto-deploy from GitHub |
| Eval runner | Claude Code CLI (`claude -p`) | Automated benchmark runs |
| Charts | Recharts or Chart.js | Benchmark visualizations |

---

## API Design

### Endpoints

```
GET    /api/skills                    # List skills (with filters)
GET    /api/skills/:id                # Skill detail
GET    /api/skills/:id/tools          # Tools for a skill
GET    /api/skills/:id/prompts        # Prompts for a skill
GET    /api/skills/:id/results        # Benchmark results
POST   /api/skills                    # Submit new skill
POST   /api/skills/:id/run            # Run eval

GET    /api/compare?skills=a,b,c      # Compare skills
GET    /api/leaderboard               # Rankings

GET    /api/frameworks                # List frameworks
GET    /api/llms                      # List LLMs with pricing
GET    /api/categories                # List categories
```

### Query Parameters

```
GET /api/skills?
  category=deployment,monitoring&
  llm=claude-opus-4.6&
  framework=claude-code&
  min_score=0.8&
  sort=eval_score&
  order=desc&
  limit=20&
  offset=0
```

---

## Database Schema

```sql
-- Core entities
CREATE TABLE skills (
  id UUID PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  version TEXT,
  description TEXT,
  categories TEXT[],
  skill_md TEXT,
  line_count INT,
  has_scripts BOOLEAN,
  has_references BOOLEAN,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE tools (
  id UUID PRIMARY KEY,
  skill_id UUID REFERENCES skills(id),
  name TEXT NOT NULL,
  type TEXT, -- script, api, mcp
  language TEXT,
  description TEXT,
  inputs JSONB,
  outputs JSONB,
  api_endpoint TEXT
);

CREATE TABLE prompts (
  id UUID PRIMARY KEY,
  skill_id UUID REFERENCES skills(id),
  text TEXT NOT NULL,
  category TEXT,
  complexity TEXT, -- low, medium, high
  expected_tools TEXT[],
  tested BOOLEAN DEFAULT false
);

-- Benchmark results
CREATE TABLE results (
  id UUID PRIMARY KEY,
  skill_id UUID REFERENCES skills(id),
  prompt_id UUID REFERENCES prompts(id),
  timestamp TIMESTAMPTZ DEFAULT now(),

  -- Input variables (JSONB for flexibility)
  input_variables JSONB NOT NULL,

  -- Output metrics (typed columns for queries)
  eval_score FLOAT,
  assertions_passed INT,
  assertions_total INT,
  tokens_input INT,
  tokens_output INT,
  duration_seconds FLOAT,
  cost_llm FLOAT,
  cost_infra FLOAT,
  steps_taken INT,
  user_confirmations INT,
  errors_encountered INT,
  completeness FLOAT
);

-- Denormalized for fast leaderboard queries
CREATE TABLE leaderboard (
  skill_id UUID REFERENCES skills(id),
  llm TEXT,
  framework TEXT,
  avg_eval_score FLOAT,
  avg_cost FLOAT,
  avg_duration FLOAT,
  run_count INT,
  last_updated TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_results_skill ON results(skill_id);
CREATE INDEX idx_results_score ON results(eval_score DESC);
CREATE INDEX idx_skills_categories ON skills USING GIN(categories);
CREATE INDEX idx_leaderboard_score ON leaderboard(avg_eval_score DESC);
```

---

## Eval Runner Architecture

```
User submits skill
    │
    ▼
Parse SKILL.md → extract tools, prompts
    │
    ▼
For each prompt × LLM combination:
    │
    ├── Spawn eval agent (claude -p)
    │   ├── With skill (test)
    │   └── Without skill (baseline)
    │
    ├── Capture: tokens, duration, output
    │
    ├── Grade: run assertions against output
    │
    └── Store: result in database
    │
    ▼
Aggregate → update leaderboard
    │
    ▼
Publish to gallery
```

---

## MVP Scope

### Phase 1: Static Gallery (1-2 days)
- Static Next.js site with hardcoded skill data
- 2 skills: gcp-cloud-run-deploy, n8n-orchestrator
- Skill cards with tools, prompts, eval scores
- Search and category filters
- Deploy to Vercel

### Phase 2: Dynamic + Database (1 week)
- Supabase backend
- Skill submission form
- Benchmark comparison page
- Leaderboard

### Phase 3: Automated Eval Runner (2 weeks)
- GitHub Action that runs evals on skill submission
- Multi-LLM benchmarking (Opus, Sonnet, Haiku, GPT-4o)
- Auto-publish results to gallery

### Phase 4: Marketplace (1 month)
- User accounts, skill publishing
- Install skill to Claude Code with one click
- Rating and reviews
- Usage analytics

---

## Repository Structure

```
agentskills-platform/
├── apps/
│   └── web/                    # Next.js frontend
│       ├── app/
│       │   ├── page.tsx        # Gallery home
│       │   ├── skills/[id]/    # Skill detail
│       │   ├── compare/        # Comparison page
│       │   └── leaderboard/    # Rankings
│       ├── components/
│       │   ├── SkillCard.tsx
│       │   ├── BenchmarkTable.tsx
│       │   ├── CompareChart.tsx
│       │   └── PromptList.tsx
│       └── lib/
│           ├── supabase.ts
│           └── types.ts
├── packages/
│   └── eval-runner/            # Benchmark automation
│       ├── run.py
│       ├── grade.py
│       └── aggregate.py
├── supabase/
│   └── migrations/             # Database schema
└── README.md
```
