-- ============================================
-- Agent Skill Benchmark Platform — Full Schema
-- 151 input variables, 9 output metrics
-- ============================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";  -- pgvector for semantic search

-- ============================================
-- CORE ENTITIES
-- ============================================

-- Apps: the client that runs everything
CREATE TABLE apps (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT UNIQUE NOT NULL,
  type TEXT,  -- cli-agent, ide-extension, cloud-agent, chatbot
  categories TEXT[],
  source_code_url TEXT,
  ui_type TEXT,  -- cli, web, desktop, mobile, api
  supported_models TEXT[],
  total_tokens BIGINT DEFAULT 0,
  total_requests BIGINT DEFAULT 0,
  growth_percent FLOAT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Frameworks: orchestration layer
CREATE TABLE frameworks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT UNIQUE NOT NULL,
  version TEXT,
  type TEXT,  -- skill-based, agent-chain, workflow
  supports_subagents BOOLEAN DEFAULT false,
  supports_mcp BOOLEAN DEFAULT false,
  supports_hooks BOOLEAN DEFAULT false,
  supports_memory BOOLEAN DEFAULT false,
  supports_planning BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Skills: reusable instruction sets
CREATE TABLE skills (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT UNIQUE NOT NULL,
  display_name TEXT NOT NULL,
  version TEXT,
  description TEXT,
  long_description TEXT,
  categories TEXT[],
  icon TEXT,
  skill_md TEXT,  -- full SKILL.md content
  line_count INT,
  has_scripts BOOLEAN DEFAULT false,
  has_references BOOLEAN DEFAULT false,
  aggregate_score FLOAT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Semantic search on skill descriptions
ALTER TABLE skills ADD COLUMN IF NOT EXISTS embedding vector(1536);
CREATE INDEX idx_skills_embedding ON skills USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);

-- Tools: scripts, APIs, MCP servers
CREATE TABLE tools (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  type TEXT,  -- script, api, mcp
  language TEXT,
  description TEXT,
  inputs JSONB,
  outputs JSONB,
  api_endpoint TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Prompts: optimized inputs per skill
CREATE TABLE prompts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  category TEXT,
  complexity TEXT,  -- low, medium, high
  expected_tools TEXT[],
  tested BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================
-- LLM MODELS & PROVIDERS
-- ============================================

CREATE TABLE llm_models (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT UNIQUE NOT NULL,  -- claude-opus-4.6, gemma4:31b
  provider TEXT,  -- anthropic, google, openai, ollama, openrouter
  variant TEXT,  -- standard, fast, mini

  -- Pricing (per million tokens)
  input_price_per_m FLOAT DEFAULT 0,
  output_price_per_m FLOAT DEFAULT 0,
  cache_read_price_per_m FLOAT DEFAULT 0,
  cache_write_price_per_m FLOAT DEFAULT 0,
  pricing_tier TEXT,  -- free, pay-per-token, batch

  -- Capabilities (Category 22)
  modality TEXT[],  -- text, image, audio, video
  tool_calling TEXT,  -- none, sequential, parallel
  structured_output BOOLEAN DEFAULT false,
  streaming BOOLEAN DEFAULT true,
  code_execution BOOLEAN DEFAULT false,
  web_search TEXT,  -- none, built-in, tool-based
  file_handling TEXT[],  -- pdf, images, audio

  -- Technical specs (Category 2)
  context_window INT,
  max_output_tokens INT,
  training_cutoff DATE,

  -- Benchmarks (Category 23)
  mmlu FLOAT,
  humaneval FLOAT,
  swe_bench FLOAT,
  gpqa FLOAT,
  math_score FLOAT,
  arena_elo INT,
  ttft_ms INT,  -- time to first token
  tokens_per_second FLOAT,

  -- Usage analytics (Category 24)
  market_share FLOAT,
  weekly_token_volume BIGINT,
  failure_rate FLOAT,

  -- Meta
  is_self_hosted BOOLEAN DEFAULT false,
  is_free BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================
-- TASK-MODEL ROUTING (Category 26)
-- ============================================

CREATE TABLE task_types (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT UNIQUE NOT NULL,  -- text-gen, image-gen, stt, tts, etc.
  category TEXT,  -- ai-generation, ai-understanding, editing, processing, visualization
  description TEXT
);

CREATE TABLE task_model_mappings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  task_type_id UUID REFERENCES task_types(id),
  llm_model_id UUID REFERENCES llm_models(id),
  priority INT DEFAULT 0,  -- lower = preferred
  is_default BOOLEAN DEFAULT false,
  is_free BOOLEAN DEFAULT false,
  is_self_hosted BOOLEAN DEFAULT false,
  docker_image TEXT,  -- thefractionalpm/whisper-stt:latest
  endpoint TEXT,  -- http://localhost:9000
  notes TEXT
);

-- ============================================
-- BENCHMARK RESULTS (the big table)
-- ============================================

CREATE TABLE benchmark_runs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Core refs (Category 1)
  skill_id UUID REFERENCES skills(id),
  prompt_id UUID REFERENCES prompts(id),
  app_id UUID REFERENCES apps(id),
  framework_id UUID REFERENCES frameworks(id),
  llm_model_id UUID REFERENCES llm_models(id),

  -- Skill config (Category 4)
  skill_version TEXT,
  reference_docs_loaded TEXT[],
  bundled_scripts TEXT[],
  mcp_servers_connected TEXT[],

  -- LLM config (Category 2)
  temperature FLOAT,
  max_tokens INT,
  context_window_used INT,
  system_prompt_hash TEXT,
  thinking_mode TEXT,  -- off, extended, budget-N

  -- Execution environment (Category 3)
  runtime TEXT,  -- local, docker, cloud-vm, serverless
  os TEXT,  -- macos, linux, windows
  network_access TEXT,  -- full, vpn, airgapped, internal
  auth_context TEXT,  -- sa-key, oauth, api-key, ambient
  permissions TEXT,  -- full, read-only, sandboxed
  installed_tools JSONB,  -- {"python": "3.12", "docker": true}

  -- Target infrastructure (Category 5)
  cloud_provider TEXT,  -- gcp, aws, azure, self-hosted
  region TEXT,
  existing_state TEXT,  -- greenfield, existing
  iam_permissions TEXT[],
  quotas_limits JSONB,

  -- Input context (Category 6)
  codebase_language TEXT,
  repo_structure TEXT,  -- monorepo, single-service
  existing_cicd TEXT,  -- none, github-actions, jenkins
  secrets_count INT,

  -- Data (Category 7)
  training_data_cutoff DATE,
  rag_data_sources TEXT[],
  data_schema JSONB,
  data_volume TEXT,
  data_freshness TEXT,  -- realtime, cached, historical

  -- Context & Memory (Category 8)
  conversation_history_length INT,
  system_instructions_hash TEXT,
  has_persistent_memory BOOLEAN DEFAULT false,
  has_project_memory BOOLEAN DEFAULT false,
  has_feedback_memory BOOLEAN DEFAULT false,
  session_state JSONB,
  multi_agent_context JSONB,
  context_window_usage_pct FLOAT,

  -- User / Human-in-the-loop (Category 9)
  user_expertise TEXT,  -- junior, senior, non-technical
  approval_speed TEXT,  -- instant, deliberate
  approval_pattern TEXT,  -- approve-all, selective
  language_locale TEXT,
  intent_clarity TEXT,  -- vague, moderate, detailed

  -- Agent architecture (Category 10)
  agent_type TEXT,  -- single, multi-agent
  delegation_depth INT,
  retry_strategy TEXT,  -- fail-fast, retry-3x
  fallback_chain TEXT[],
  planning_mode TEXT,  -- plan-then-execute, streaming
  tool_selection TEXT,  -- greedy, deliberate

  -- Safety & Compliance (Category 11)
  content_filters TEXT,  -- strict, moderate, off
  sandbox_mode TEXT,  -- full, read-only, dry-run
  audit_requirements TEXT[],
  secret_handling TEXT,  -- hardcoded, secret-manager, vault
  pii_sensitivity TEXT,  -- visible, redacted

  -- Temporal (Category 12)
  execution_time TIMESTAMPTZ,
  api_availability TEXT,  -- up, degraded, maintenance
  concurrent_usage INT,
  timeout_seconds INT,
  freshness_requirement TEXT,  -- realtime, eventual

  -- Output expectations (Category 13)
  output_format TEXT,  -- json, yaml, code, prose
  verbosity TEXT,  -- terse, detailed
  audience TEXT,  -- machine, human
  determinism_required BOOLEAN DEFAULT false,

  -- Versioning (Category 14)
  llm_version TEXT,
  framework_version TEXT,
  api_versions JSONB,
  sdk_versions JSONB,

  -- Evaluation criteria (Category 15)
  grader TEXT,  -- human, script, llm-as-judge
  rubric TEXT,  -- binary, 1-5, qualitative
  subjectivity TEXT,  -- objective, subjective
  baseline TEXT,  -- no-skill, previous-version, competitor

  -- Data processing pipeline (Category 16)
  chunking_algorithm TEXT,  -- fixed, semantic, sentence, recursive
  chunk_size INT,
  chunk_overlap INT,
  splitting_strategy TEXT,  -- paragraph, heading, code-block

  -- Embeddings (Category 17)
  embedding_model TEXT,
  embedding_dimensions INT,
  embedding_normalization TEXT,  -- l2, cosine, none
  embedding_fine_tuned BOOLEAN DEFAULT false,
  embedding_multimodal BOOLEAN DEFAULT false,

  -- Vector DB / Retrieval (Category 18)
  vector_db TEXT,  -- pinecone, qdrant, pgvector, chroma
  index_type TEXT,  -- hnsw, ivf, flat
  distance_metric TEXT,  -- cosine, dot-product, euclidean
  top_k INT,
  similarity_threshold FLOAT,
  hybrid_search BOOLEAN DEFAULT false,
  reranker TEXT,  -- none, cohere, cross-encoder
  metadata_filtering BOOLEAN DEFAULT false,

  -- Data transformation (Category 19)
  preprocessing TEXT[],
  enrichment TEXT[],
  deduplication TEXT,  -- exact, fuzzy, semantic
  update_strategy TEXT,  -- full-reindex, incremental
  ttl_seconds INT,

  -- Knowledge graph (Category 20)
  graph_db TEXT,  -- neo4j, surrealdb, neptune
  ontology TEXT,
  traversal_depth INT,
  hybrid_retrieval BOOLEAN DEFAULT false,

  -- Model provider / routing (Category 21)
  provider TEXT,  -- direct, openrouter, bedrock, vertex
  model_variant TEXT,
  rate_limits JSONB,

  -- Task-model routing (Category 26)
  routing_strategy TEXT,  -- task-based, cost-based, latency-based
  free_tier_priority BOOLEAN DEFAULT true,
  self_hosted_priority BOOLEAN DEFAULT true,
  cost_budget FLOAT,
  quality_threshold FLOAT,

  -- ============================================
  -- OUTPUT METRICS (9 metrics)
  -- ============================================
  eval_score FLOAT,
  assertions_passed INT,
  assertions_total INT,
  tokens_input INT,
  tokens_output INT,
  tokens_cached INT DEFAULT 0,
  duration_seconds FLOAT,
  cost_llm FLOAT,
  cost_infra FLOAT,
  steps_taken INT,
  user_confirmations INT,
  errors_encountered INT,
  completeness FLOAT,

  -- Meta
  raw_output TEXT,
  grading_details JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================
-- EVAL ASSERTIONS
-- ============================================

CREATE TABLE assertions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
  prompt_id UUID REFERENCES prompts(id),
  text TEXT NOT NULL,  -- "No gcloud CLI commands used"
  type TEXT,  -- grep_present, grep_absent, semantic
  pattern TEXT,  -- regex pattern for grep checks
  description TEXT
);

CREATE TABLE assertion_results (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  benchmark_run_id UUID REFERENCES benchmark_runs(id) ON DELETE CASCADE,
  assertion_id UUID REFERENCES assertions(id),
  passed BOOLEAN,
  evidence TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================
-- LEADERBOARD (materialized view)
-- ============================================

CREATE MATERIALIZED VIEW leaderboard AS
SELECT
  s.id AS skill_id,
  s.name AS skill_name,
  s.display_name,
  s.categories,
  m.name AS llm_name,
  f.name AS framework_name,
  COUNT(br.id) AS run_count,
  AVG(br.eval_score) AS avg_eval_score,
  AVG(br.cost_llm) AS avg_cost_llm,
  AVG(br.duration_seconds) AS avg_duration,
  AVG(br.completeness) AS avg_completeness,
  AVG(br.tokens_input + br.tokens_output) AS avg_tokens
FROM benchmark_runs br
JOIN skills s ON br.skill_id = s.id
LEFT JOIN llm_models m ON br.llm_model_id = m.id
LEFT JOIN frameworks f ON br.framework_id = f.id
GROUP BY s.id, s.name, s.display_name, s.categories, m.name, f.name;

CREATE UNIQUE INDEX idx_leaderboard_pk ON leaderboard(skill_id, llm_name, framework_name);

-- Refresh: REFRESH MATERIALIZED VIEW CONCURRENTLY leaderboard;

-- ============================================
-- INDEXES
-- ============================================

-- Skills
CREATE INDEX idx_skills_categories ON skills USING GIN(categories);
CREATE INDEX idx_skills_name ON skills(name);
CREATE INDEX idx_skills_score ON skills(aggregate_score DESC);

-- Tools & Prompts
CREATE INDEX idx_tools_skill ON tools(skill_id);
CREATE INDEX idx_prompts_skill ON prompts(skill_id);

-- Benchmark runs
CREATE INDEX idx_bench_skill ON benchmark_runs(skill_id);
CREATE INDEX idx_bench_llm ON benchmark_runs(llm_model_id);
CREATE INDEX idx_bench_framework ON benchmark_runs(framework_id);
CREATE INDEX idx_bench_score ON benchmark_runs(eval_score DESC);
CREATE INDEX idx_bench_cost ON benchmark_runs(cost_llm);
CREATE INDEX idx_bench_created ON benchmark_runs(created_at DESC);
CREATE INDEX idx_bench_provider ON benchmark_runs(provider);
CREATE INDEX idx_bench_cloud ON benchmark_runs(cloud_provider);

-- Assertion results
CREATE INDEX idx_assert_run ON assertion_results(benchmark_run_id);

-- Task model mappings
CREATE INDEX idx_task_mapping_task ON task_model_mappings(task_type_id);
CREATE INDEX idx_task_mapping_model ON task_model_mappings(llm_model_id);

-- ============================================
-- ROW LEVEL SECURITY (for multi-user)
-- ============================================

ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE benchmark_runs ENABLE ROW LEVEL SECURITY;

-- Public read for all skills
CREATE POLICY "Skills are viewable by everyone" ON skills
  FOR SELECT USING (true);

-- Public read for benchmark results
CREATE POLICY "Benchmark results are viewable by everyone" ON benchmark_runs
  FOR SELECT USING (true);

-- ============================================
-- SEED DATA: Task Types
-- ============================================

INSERT INTO task_types (name, category, description) VALUES
  ('text-gen', 'ai-generation', 'Text generation and completion'),
  ('image-gen', 'ai-generation', 'Text to image generation'),
  ('video-gen', 'ai-generation', 'Text to video generation'),
  ('audio-gen', 'ai-generation', 'Text to audio/speech generation'),
  ('music-gen', 'ai-generation', 'Text to music generation'),
  ('tts', 'ai-generation', 'Text to speech synthesis'),
  ('code-gen', 'ai-generation', 'Code generation and completion'),
  ('math-reasoning', 'ai-generation', 'Mathematical problem solving'),
  ('stt', 'ai-understanding', 'Speech to text transcription'),
  ('ocr', 'ai-understanding', 'Optical character recognition'),
  ('image-understanding', 'ai-understanding', 'Image analysis and description'),
  ('video-understanding', 'ai-understanding', 'Video analysis and description'),
  ('embedding', 'ai-understanding', 'Text/multimodal embedding generation'),
  ('reranking', 'ai-understanding', 'Search result reranking'),
  ('translation', 'ai-understanding', 'Language translation'),
  ('image-edit', 'editing', 'Image editing and manipulation'),
  ('video-edit', 'editing', 'Video editing and processing'),
  ('audio-edit', 'editing', 'Audio editing and processing'),
  ('file-convert', 'processing', 'File format conversion'),
  ('pdf-process', 'processing', 'PDF extraction, merge, split'),
  ('spreadsheet-process', 'processing', 'Spreadsheet reading and transformation'),
  ('diagram-gen', 'visualization', 'Diagram and chart generation'),
  ('3d-gen', 'visualization', '3D model generation from images'),
  ('graph-viz', 'visualization', 'Graph and network visualization');

-- ============================================
-- SEED DATA: LLM Models
-- ============================================

INSERT INTO llm_models (name, provider, input_price_per_m, output_price_per_m, context_window, modality, tool_calling, is_self_hosted, is_free) VALUES
  ('claude-opus-4.6', 'anthropic', 15.0, 75.0, 1000000, ARRAY['text','image'], 'parallel', false, false),
  ('claude-sonnet-4.6', 'anthropic', 3.0, 15.0, 200000, ARRAY['text','image'], 'parallel', false, false),
  ('claude-haiku-4.5', 'anthropic', 0.25, 1.25, 200000, ARRAY['text','image'], 'parallel', false, false),
  ('gpt-4o', 'openai', 2.5, 10.0, 128000, ARRAY['text','image','audio'], 'parallel', false, false),
  ('gpt-4o-mini', 'openai', 0.15, 0.60, 128000, ARRAY['text','image'], 'parallel', false, false),
  ('gemini-2.5-pro', 'google', 1.25, 10.0, 1000000, ARRAY['text','image','audio','video'], 'parallel', false, false),
  ('gemini-2.5-flash', 'google', 0.15, 0.60, 1000000, ARRAY['text','image','audio','video'], 'parallel', false, false),
  ('gemma4:31b', 'ollama', 0, 0, 131072, ARRAY['text','image'], 'none', true, true),
  ('deepseek-r1', 'ollama', 0, 0, 131072, ARRAY['text'], 'none', true, true),
  ('llama-3.3-70b', 'ollama', 0, 0, 131072, ARRAY['text'], 'parallel', true, true);

-- ============================================
-- SEED DATA: Frameworks
-- ============================================

INSERT INTO frameworks (name, version, type, supports_subagents, supports_mcp, supports_hooks, supports_memory, supports_planning) VALUES
  ('Claude Code', '2.1', 'skill-based', true, true, true, true, true),
  ('CrewAI', '0.80', 'agent-chain', true, false, false, true, true),
  ('LangChain', '0.3', 'agent-chain', true, false, false, true, true),
  ('n8n', '2.14', 'workflow', false, true, false, false, false),
  ('AutoGen', '0.4', 'agent-chain', true, false, false, true, true),
  ('Raw API', '1.0', 'direct', false, false, false, false, false);
