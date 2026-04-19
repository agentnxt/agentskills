# Langflow 1.x Flow JSON Schema Reference

## Top-level structure

```json
{
  "id": "uuid-v4",
  "name": "Flow Name",
  "description": "What this flow does",
  "data": {
    "nodes": [...],
    "edges": [...],
    "viewport": { "x": 0, "y": 0, "zoom": 1 }
  },
  "is_component": false,
  "updated_at": "ISO8601",
  "folder_id": null,
  "endpoint_name": "optional-slug"
}
```

## Node types (built-in, Langflow 1.x)

### Input / Output
| Component type | Description |
|---|---|
| `ChatInput` | Chat message entry point. Fields: `input_value`, `session_id`, `sender`, `sender_name` |
| `ChatOutput` | Chat message exit. Fields: `input_value`, `session_id`, `data_template` |
| `TextInput` | Plain text input. Field: `input_value` |
| `TextOutput` | Plain text output. Field: `input_value` |

### LLMs (Language Models)
| Component type | Key fields |
|---|---|
| `OpenAIModel` | `model_name`, `openai_api_key`, `temperature`, `max_tokens`, `stream` |
| `AnthropicModel` | `model`, `anthropic_api_key`, `temperature`, `max_tokens` |
| `OllamaModel` | `base_url`, `model_name`, `temperature` |
| `VertexAIModel` | `project`, `location`, `model_name` |
| `AzureOpenAIModel` | `azure_endpoint`, `azure_deployment`, `api_version`, `api_key` |

### Prompts
| Component type | Key fields |
|---|---|
| `PromptTemplate` | `template` (string with `{variable}` or Mustache `{{variable}}` placeholders) |
| `SystemMessagePromptTemplate` | `template` |

### Agents & Tools
| Component type | Description |
|---|---|
| `Agent` | ReAct agent. Fields: `llm`, `tools`, `system_prompt`, `max_iterations` |
| `ToolCallingAgent` | OpenAI function-calling agent |
| `CrewAIAgent` | CrewAI agent wrapper |
| `PythonREPLTool` | Executes Python code |
| `SearchAPITool` | Web search |
| `WikipediaAPITool` | Wikipedia lookup |
| `CustomComponent` | Your custom Python component |

### Memory / State
| Component type | Key fields |
|---|---|
| `ConversationBufferMemory` | `memory_key`, `return_messages` |
| `ConversationSummaryMemory` | `llm`, `memory_key` |
| `ZepMemory` | `zep_url`, `session_id`, `api_key` |

### Vector Stores
| Component type | Key fields |
|---|---|
| `Chroma` | `collection_name`, `persist_directory`, `embedding` |
| `PineconeVectorStore` | `index_name`, `pinecone_api_key`, `embedding` |
| `QdrantVectorStore` | `url`, `collection_name`, `api_key`, `embedding` |
| `WeaviateVectorStore` | `url`, `index_name`, `api_key`, `embedding` |
| `PGVector` | `pg_server_url`, `collection_name`, `embedding` |
| `AstraDBVectorStore` | `token`, `api_endpoint`, `collection_name`, `embedding` |

### Embeddings
| Component type | Key fields |
|---|---|
| `OpenAIEmbeddings` | `openai_api_key`, `model` |
| `OllamaEmbeddings` | `base_url`, `model_name` |
| `HuggingFaceEmbeddings` | `model_name` |
| `CohereEmbeddings` | `cohere_api_key`, `model` |

### Document Loaders
| Component type | Key fields |
|---|---|
| `FileLoader` | `path` |
| `WebBaseLoader` | `web_path` |
| `NotionDirectoryLoader` | `path` |
| `GitLoader` | `repo_path`, `branch` |

### Text Splitters
| Component type | Key fields |
|---|---|
| `RecursiveCharacterTextSplitter` | `chunk_size`, `chunk_overlap`, `separators` |
| `CharacterTextSplitter` | `chunk_size`, `chunk_overlap`, `separator` |

### Retrievers
| Component type | Key fields |
|---|---|
| `VectorStoreRetriever` | `vectorstore`, `search_type`, `k` |
| `MultiQueryRetriever` | `llm`, `retriever` |

### Control Flow (1.8+)
| Component type | Description |
|---|---|
| `Loop` | Isolated subgraph loop. Fields: `max_iterations`, `exit_condition` |
| `Conditional` | Branch on condition |
| `Pass` | No-op passthrough |

---

## Edge handle format

```
{sourceId}|{outputName}|{sourceId}
```

Example:
```
OpenAIModel-abc12|text|OpenAIModel-abc12
```

Target handle:
```
{targetId}|{inputFieldName}|{targetId}
```

---

## Minimal working flow (Text → LLM → Text)

```json
{
  "name": "Simple LLM Flow",
  "description": "Takes text input, runs through OpenAI, outputs text",
  "data": {
    "nodes": [
      {
        "id": "TextInput-aaa",
        "type": "genericNode",
        "position": { "x": 100, "y": 200 },
        "data": {
          "type": "TextInput",
          "id": "TextInput-aaa",
          "node": {
            "display_name": "Text Input",
            "description": "User prompt",
            "template": {
              "input_value": { "value": "", "type": "str", "show": true }
            },
            "outputs": [{ "name": "text", "types": ["Message"] }]
          }
        }
      },
      {
        "id": "OpenAIModel-bbb",
        "type": "genericNode",
        "position": { "x": 400, "y": 200 },
        "data": {
          "type": "OpenAIModel",
          "id": "OpenAIModel-bbb",
          "node": {
            "display_name": "OpenAI",
            "template": {
              "model_name": { "value": "gpt-4o-mini", "type": "str" },
              "openai_api_key": { "value": "", "type": "str", "password": true },
              "temperature": { "value": 0.7, "type": "float" },
              "input_value": { "value": "", "type": "str" }
            },
            "outputs": [{ "name": "text", "types": ["Message"] }]
          }
        }
      },
      {
        "id": "TextOutput-ccc",
        "type": "genericNode",
        "position": { "x": 700, "y": 200 },
        "data": {
          "type": "TextOutput",
          "id": "TextOutput-ccc",
          "node": {
            "display_name": "Text Output",
            "template": {
              "input_value": { "value": "", "type": "str" }
            },
            "outputs": []
          }
        }
      }
    ],
    "edges": [
      {
        "source": "TextInput-aaa",
        "sourceHandle": "TextInput-aaa|text|TextInput-aaa",
        "target": "OpenAIModel-bbb",
        "targetHandle": "OpenAIModel-bbb|input_value|OpenAIModel-bbb",
        "id": "edge-1"
      },
      {
        "source": "OpenAIModel-bbb",
        "sourceHandle": "OpenAIModel-bbb|text|OpenAIModel-bbb",
        "target": "TextOutput-ccc",
        "targetHandle": "TextOutput-ccc|input_value|TextOutput-ccc",
        "id": "edge-2"
      }
    ],
    "viewport": { "x": 0, "y": 0, "zoom": 1 }
  },
  "is_component": false
}
```
