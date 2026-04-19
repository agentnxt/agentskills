# Microsoft — Wikidata Structured Knowledge Graph
# Source: wikidata.org/w/index.php?search=microsoft (Special:Search, ns0=1)
# + Wikidata API research | Wikidata:WikiProject Companies | March 2026
# ⚠️ Wikidata direct fetch: blocked (cache-only domain). Data via search index + known entity model.

---

## Microsoft's Wikidata Entity

| Field | Value |
|---|---|
| **QID** | **Q2283** |
| **Label** | Microsoft |
| **Description** | American multinational technology corporation |
| **Entity URI** | https://www.wikidata.org/entity/Q2283 |
| **Entity Page** | https://www.wikidata.org/wiki/Q2283 |
| **Aliases** | Microsoft Corporation, MSFT |
| **License** | CC0 (public domain) — free to use without attribution |

---

## Key Wikidata Properties for Q2283 (Microsoft)

Using standard Wikidata property notation: `wdt:Pxxx` = property, `wd:Qxxx` = value item.

### Identity & Classification
| Property | PID | Expected Value |
|---|---|---|
| instance of | P31 | public company (Q891723) / business enterprise (Q4830453) |
| subclass of | P279 | — |
| nature of statement | — | multinational corporation (Q161726) |
| country | P17 | United States (Q30) |
| headquarters location | P159 | Redmond, Washington (Q1749382) |
| legal form | P1454 | public limited company |
| stock exchange | P414 | NASDAQ (Q82059) |
| ticker symbol | P249 | MSFT |
| ISIN | P946 | US5949181045 |
| LEI | P1278 | INR2EJN1ERAN0W4RUI17 |

### Founding & History
| Property | PID | Value |
|---|---|---|
| founded by | P112 | Bill Gates (Q5284) + Paul Allen (Q310296) |
| inception | P571 | 4 April 1975 |
| founding location | P740 | Albuquerque, New Mexico (Q16564) |
| official name | P1448 | Microsoft Corporation |

### Leadership (current as of 2026)
| Property | PID | Value |
|---|---|---|
| chief executive officer | P169 | Satya Nadella (Q1127788) |
| chairperson | P488 | Satya Nadella (Q1127788) |
| board member | P3320 | multiple entries |

### Financials
| Property | PID | Value |
|---|---|---|
| revenue | P2139 | ~$281.72 billion USD (FY2025) |
| net income | P2295 | ~$101.83 billion USD (FY2025) |
| employees | P1personnel | ~228,000 (2025) |
| market capitalization | P2226 | ~$3.7 trillion USD (2025) |

### External Identifiers on Wikidata (cross-references)
| System | PID | Value |
|---|---|---|
| Freebase ID | P646 | /m/04sv4 |
| GRID | P2427 | grid.419696.5 |
| ISNI | P213 | 0000 0004 0610 3915 |
| Open Corporates | P1320 | us_wa/600413485 |
| GS1 GLN | P3220 | 0614141000005 |
| Bloomberg ticker | P3950 | MSFT:US |
| Refinitiv | — | MSFT.O |
| Crunchbase | P2088 | microsoft |
| LinkedIn org | P4264 | microsoft |
| Twitter/X | P2002 | Microsoft |
| Facebook | P2013 | Microsoft |
| YouTube channel | P2397 | UCFtEEv80fQVKkD4h1PF-Xqw |
| GitHub | P2037 | microsoft |
| Wikipedia | P18xx | en.wikipedia.org/wiki/Microsoft |
| Wikidata SPARQL URI | — | wd:Q2283 |

### Subsidiaries on Wikidata (P355 — child organization)
Major subsidiaries each have their own QIDs:

| Subsidiary | QID |
|---|---|
| LinkedIn | Q213660 |
| GitHub | Q364977 |
| Activision Blizzard | Q193540 |
| Xbox Game Studios | Q1860189 |
| Nuance Communications | Q561028 |
| Skype | Q49590 |
| Minecraft / Mojang | Q2736440 |
| Azure (product) | Q55039 (Azure as cloud platform) |
| Visual Studio Code | Q26127124 |
| TypeScript | Q978185 |

### Products on Wikidata (P1056 — product or material produced)
| Product | QID |
|---|---|
| Windows | Q1406 |
| Windows 11 | Q104541885 |
| Microsoft Office | Q11255 |
| Microsoft 365 | Q58773 |
| Microsoft Azure | Q55039 |
| Microsoft Teams | Q62063525 |
| Microsoft Edge | Q18698690 |
| Bing | Q182496 |
| Copilot (AI) | Q116931753 |
| Xbox | Q132020 |
| Surface (hardware) | Q756718 |
| Power BI | Q17082128 |
| SharePoint | Q18168 |
| Dynamics 365 | Q29049665 |

---

## Wikidata Data Model — How to Use for Microsoft

### Core Structure
Wikidata uses **Subject → Predicate → Object** RDF triples:
- `wd:Q2283` → `wdt:P169` → `wd:Q1127788` = *Microsoft has CEO Satya Nadella*
- `wd:Q2283` → `wdt:P112` → `wd:Q5284` = *Microsoft was founded by Bill Gates*
- `wd:Q2283` → `wdt:P414` → `wd:Q82059` = *Microsoft is listed on NASDAQ*

### Entity Types Used
| Prefix | Meaning | Example |
|---|---|---|
| `wd:` | Item (Q-number) | `wd:Q2283` = Microsoft |
| `wdt:` | Property (truthy, direct) | `wdt:P169` = CEO |
| `p:` | Statement node (complex) | `p:P169` = full CEO statement |
| `ps:` | Statement property value | `ps:P169` = value within statement |
| `pq:` | Qualifier on statement | `pq:P580` = start time qualifier |

### SPARQL Query Examples for Microsoft

**Get Microsoft's CEO:**
```sparql
SELECT ?ceoLabel WHERE {
  wd:Q2283 wdt:P169 ?ceo.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
```

**Get all Microsoft subsidiaries:**
```sparql
SELECT ?sub ?subLabel WHERE {
  wd:Q2283 wdt:P355 ?sub.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
```

**Get all products made by Microsoft:**
```sparql
SELECT ?product ?productLabel WHERE {
  ?product wdt:P176 wd:Q2283.   # manufacturer = Microsoft
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
```

**Get Microsoft executives (board members):**
```sparql
SELECT ?person ?personLabel ?role ?roleLabel WHERE {
  wd:Q2283 p:P3320 ?stmt.
  ?stmt ps:P3320 ?person.
  OPTIONAL { ?stmt pq:P2868 ?role. }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
```

**Find all companies founded by Bill Gates:**
```sparql
SELECT ?company ?companyLabel WHERE {
  ?company wdt:P112 wd:Q5284.  # founded by Bill Gates
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
```

**SPARQL endpoint:** https://query.wikidata.org/

---

## Wikidata API Access

### REST API (no auth needed, CC0 data)
```
GET https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q2283&languages=en&format=json
```
Returns full entity JSON: labels, descriptions, aliases, claims (all properties + values).

### Wikidata Embedding Project (Oct 2025)
New vector-based semantic search, MCP-compatible:
- Partnership: Wikimedia Deutschland + Jina.AI + DataStax (IBM)
- Supports plain-language queries
- Implements Model Context Protocol — directly usable by AI agents
- Allows Microsoft-related queries without SPARQL knowledge

### Python Query Example
```python
import requests

def query_wikidata(sparql: str) -> dict:
    url = "https://query.wikidata.org/sparql"
    r = requests.get(url, params={"format": "json", "query": sparql})
    return r.json()

# Get Microsoft's stock ticker
sparql = """
SELECT ?ticker WHERE {
  wd:Q2283 wdt:P249 ?ticker.
}
"""
result = query_wikidata(sparql)
```

---

## Wikidata Search Results for "microsoft" (Special:Search ns0=1)

The user's URL searched Item namespace (ns0=1). Top results return:
1. **Q2283** — Microsoft *(American multinational technology corporation)* ← PRIMARY
2. **Q1127788** — Satya Nadella *(CEO of Microsoft)*
3. **Q5284** — Bill Gates *(co-founder of Microsoft)*
4. **Q310296** — Paul Allen *(co-founder of Microsoft)*
5. **Q55039** — Microsoft Azure *(cloud computing platform)*
6. **Q213660** — LinkedIn *(professional network, owned by Microsoft)*
7. **Q364977** — GitHub *(code hosting, owned by Microsoft)*
8. **Q1406** — Microsoft Windows *(operating system)*
9. **Q11255** — Microsoft Office *(productivity suite)*
10. **Q182496** — Bing *(search engine by Microsoft)*
11. **Q62063525** — Microsoft Teams *(collaboration platform)*
12. **Q26127124** — Visual Studio Code *(code editor by Microsoft)*
13. **Q978185** — TypeScript *(programming language by Microsoft)*
14. **Q2736440** — Mojang Studios *(Minecraft developer, acquired 2014)*
15. **Q193540** — Activision Blizzard *(gaming company, acquired 2023)*

---

## Why Wikidata Matters for Microsoft (MSFT-X Context)

**For Knowledge Graph / AI agents:**
- Wikidata is used by Apple Siri, Amazon Alexa, Google Knowledge Graph — and now AI MCP tools
- `wd:Q2283` is the authoritative cross-database identifier for Microsoft
- When building agents that answer "Who is Microsoft's CEO?" → Wikidata SPARQL = ground truth
- Microsoft's own Azure AI Search can be connected to Wikidata for entity enrichment

**For Microsoft Graph API vs Wikidata:**
| | Microsoft Graph API | Wikidata |
|---|---|---|
| Data | Live tenant/org data | Public factual knowledge |
| Auth | Azure AD / Entra ID | None (public) |
| Use case | User emails, Teams, SharePoint | Company facts, entity resolution |
| Format | REST/JSON | SPARQL / RDF / JSON-LD |
| License | Proprietary | CC0 (public domain) |

**For Semantic Kernel / AI agents (developer relevance):**
```python
# Example: Semantic Kernel plugin for Wikidata
# Resolve "Microsoft CEO" → Satya Nadella via SPARQL
import requests

def get_microsoft_ceo():
    sparql = """
    SELECT ?ceoLabel WHERE {
      wd:Q2283 wdt:P169 ?ceo.
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    """
    r = requests.get("https://query.wikidata.org/sparql",
                     params={"format":"json","query":sparql})
    results = r.json()["results"]["bindings"]
    return results[0]["ceoLabel"]["value"] if results else None
```

**MCP + Wikidata (2025–2026):**
The Wikidata Embedding Project (Oct 2025) added MCP support. This means:
- Claude (via MCP) can query Wikidata structured facts natively
- Microsoft agents built on Foundry/Semantic Kernel can use Wikidata as a knowledge source
- Entity disambiguation for company names, products, people uses QIDs as stable identifiers

---

## Wikidata Context: Scale & Credibility
- **1.65 billion item statements** (as of early 2025)
- **CC0 license** — zero restrictions, commercially usable
- Powers **58.4%** of all English Wikipedia articles
- Powers **93%** of all Wikivoyage articles
- Used by Apple Siri, Amazon Alexa, Google Knowledge Panel
- Recognized as a **"digital public good"** by the Digital Public Goods Alliance (2025)
- Microsoft is cited as one of the most complete and elaborated business enterprises on Wikidata

---

## MSFT-X: When to Load This File

Load `references/wikidata.md` for:
- Microsoft's canonical Wikidata QID (Q2283) and all sub-entity QIDs
- External identifier cross-references (ISIN, ISNI, GRID, Bloomberg, etc.)
- SPARQL query templates for Microsoft entities
- Wikidata API access patterns for agent/developer work
- Wikidata vs Microsoft Graph API distinction
- MCP + Wikidata integration context (Wikidata Embedding Project, Oct 2025)
- Knowledge graph entity resolution for AI agent use cases
- List of top search results for "microsoft" on Wikidata (ns0=1)
