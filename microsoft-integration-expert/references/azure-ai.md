# Azure AI Services — Reference

Source: https://learn.microsoft.com/en-us/azure/ai-services/

## Azure OpenAI Service

### Key Models Available
| Model | Best For |
|---|---|
| GPT-4o | Multimodal reasoning, general purpose |
| GPT-4 Turbo | Long context (128K), complex tasks |
| GPT-3.5 Turbo | Fast, cost-efficient completions |
| text-embedding-ada-002 | Semantic search, RAG |
| text-embedding-3-large | Higher quality embeddings |
| DALL-E 3 | Image generation |
| Whisper | Speech to text |

### Access
- Apply for access: https://aka.ms/oai/access
- Deploy via Azure portal → Azure OpenAI resource → Model deployments

### API Call
```python
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_KEY"],
    api_version="2024-02-01"
)

response = client.chat.completions.create(
    model="gpt-4",  # deployment name
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)
```

### Responsible AI — Content Filters
Always configure content filters in Azure AI Foundry:
- Violence, Hate, Sexual, Self-harm categories
- Severity thresholds: Low/Medium/High
- Prompt shields (protect against jailbreak + indirect injection)
- Groundedness detection (for RAG)

---

## Azure AI Foundry

The unified platform for building AI apps: https://ai.azure.com

### Key Features
- **Model catalog** — 1600+ models (OpenAI, Meta Llama, Mistral, etc.)
- **Prompt flow** — Visual LLM pipeline builder
- **Fine-tuning** — Customize models with your data
- **Evaluations** — Measure groundedness, coherence, relevance
- **AI Search integration** — Built-in vector indexing for RAG

### RAG Pattern (Retrieval-Augmented Generation)
```
User query → Azure AI Search (vector + keyword) → Top K chunks
                                                         ↓
                              GPT-4 + context → Grounded answer
```

Azure AI Search setup:
```python
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import *

# Create vector index
index = SearchIndex(
    name="knowledge-base",
    fields=[
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchField(name="content_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                   searchable=True, vector_search_dimensions=1536,
                   vector_search_profile_name="myHnswProfile")
    ],
    vector_search=VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="myHnsw")],
        profiles=[VectorSearchProfile(name="myHnswProfile", algorithm_configuration_name="myHnsw")]
    )
)
```

---

## Key Azure AI Services (Cognitive Services)

| Service | Use Case |
|---|---|
| Azure AI Speech | STT, TTS, speaker recognition |
| Azure AI Vision | OCR, image analysis, face detection |
| Azure AI Language | NER, sentiment, summarization, translation |
| Azure AI Translator | 100+ language translation |
| Azure AI Document Intelligence | Extract structured data from PDFs/forms |
| Azure AI Content Safety | Moderate text and images |
| Azure AI Search | Enterprise-grade vector + hybrid search |

---

## Azure AI Security Best Practices

1. Use **Managed Identity** to connect to Azure OpenAI — no keys in code
2. Store API keys in **Azure Key Vault**
3. Enable **Private Endpoints** — keep traffic off public internet
4. Enable **Diagnostic Logs** → send to Log Analytics / Sentinel
5. Set **Content Filters** — don't deploy unfiltered models
6. Enable **Prompt Shields** — protect against prompt injection attacks
7. Use **Groundedness detection** for RAG apps to prevent hallucination
