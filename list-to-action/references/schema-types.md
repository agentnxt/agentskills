# Schema.org Type Map

For each supported type: the canonical schema.org class, required metadata fields, optional enrichment fields, and the best content angle for each action family.

---

## Product
**schema.org/Product**

| Field | Required | Notes |
|---|---|---|
| name | ✅ | Product name |
| description | ✅ | 1–3 sentence summary |
| brand | ○ | Brand/manufacturer name |
| sku | ○ | Stock-keeping unit |
| category | ○ | Product category |
| image | ○ | Image URL or prompt description |
| url | ○ | Product page URL |
| offers.price | ○ | Price with currency |
| keywords | ○ | Tags for content generation |
| targetAudience | ○ | Who it's for |
| aggregateRating | ○ | Average rating + count |

**Content angle:** Features → benefits → use cases → who it's for → CTA

---

## Service
**schema.org/Service**

| Field | Required | Notes |
|---|---|---|
| name | ✅ | Service name |
| description | ✅ | What the service does |
| provider | ○ | Company/person offering it |
| areaServed | ○ | Geographic scope |
| category | ○ | Service category |
| offers | ○ | Pricing info |
| url | ○ | Service page |
| keywords | ○ | Tags |

**Content angle:** Problem solved → how it works → who it's for → differentiator → CTA

---

## SoftwareApplication
**schema.org/SoftwareApplication**

| Field | Required | Notes |
|---|---|---|
| name | ✅ | App/tool name |
| description | ✅ | What it does |
| applicationCategory | ○ | e.g. BusinessApplication |
| operatingSystem | ○ | Web, iOS, Android, etc. |
| url | ○ | Website or app store link |
| offers | ○ | Pricing / free tier |
| featureList | ○ | Key features |
| keywords | ○ | Tags |

**Content angle:** Use case → key features → integrations → pricing → CTA

---

## Article / BlogPosting / CreativeWork
**schema.org/Article, BlogPosting, CreativeWork**

| Field | Required | Notes |
|---|---|---|
| name / headline | ✅ | Title |
| abstract / description | ✅ | 1–2 sentence summary |
| keywords | ✅ | Topics to cover |
| author | ○ | Attribution |
| targetAudience | ○ | Reader profile |
| about | ○ | Core subject |
| datePublished | ○ | Target publish date |
| wordCount | ○ | Target length |

**Content angle:** Hook → problem/context → main argument → evidence → takeaway → CTA

---

## Person
**schema.org/Person**

| Field | Required | Notes |
|---|---|---|
| name | ✅ | Full name |
| jobTitle | ○ | Role |
| description | ○ | Bio or context |
| worksFor | ○ | Organization |
| url | ○ | Website or LinkedIn |
| sameAs | ○ | Social profiles (array) |
| email | ○ | Contact email |
| knowsAbout | ○ | Expertise areas |

**Content angle:** Who they are → what they do → why it matters → quote/insight → CTA

---

## Organization
**schema.org/Organization**

| Field | Required | Notes |
|---|---|---|
| name | ✅ | Company/org name |
| description | ✅ | What they do |
| url | ○ | Website |
| industry | ○ | Sector |
| foundingDate | ○ | When founded |
| numberOfEmployees | ○ | Size |
| sameAs | ○ | Social profiles |
| keywords | ○ | Tags |

**Content angle:** Mission → what they do → who they serve → differentiator → CTA

---

## Event
**schema.org/Event**

| Field | Required | Notes |
|---|---|---|
| name | ✅ | Event name |
| startDate | ✅ | ISO 8601 datetime |
| endDate | ○ | ISO 8601 datetime |
| location | ○ | Place or virtual URL |
| organizer | ○ | Name/org |
| description | ✅ | What happens |
| url | ○ | Registration/info page |
| keywords | ○ | Tags |
| eventStatus | ○ | Scheduled/Cancelled/Postponed |

**Content angle:** What → when → where → why attend → how to register → CTA

---

## Place
**schema.org/Place**

| Field | Required | Notes |
|---|---|---|
| name | ✅ | Place name |
| description | ✅ | What it is |
| address | ○ | PostalAddress object |
| geo | ○ | Lat/long |
| url | ○ | Website |
| image | ○ | Photo URL or prompt |
| keywords | ○ | Tags |

**Content angle:** What it is → where it is → why it matters → visitor tips → CTA

---

## ImageObject
**schema.org/ImageObject**

| Field | Required | Notes |
|---|---|---|
| name | ✅ | Image title |
| contentUrl | ✅ | URL or file path |
| caption | ○ | Alt text / caption |
| creator | ○ | Photographer/designer |
| dateCreated | ○ | Date |
| keywords | ○ | Tags |
| license | ○ | Usage rights |
| about | ○ | Subject of image |

**Content angle:** Visual description → context → story behind it → usage → CTA

---

## VideoObject
**schema.org/VideoObject**

| Field | Required | Notes |
|---|---|---|
| name | ✅ | Video title |
| description | ✅ | What it covers |
| contentUrl | ○ | URL |
| thumbnailUrl | ○ | Thumbnail |
| duration | ○ | ISO 8601 duration (PT5M) |
| uploadDate | ○ | Date |
| keywords | ○ | Tags |

**Content angle:** Hook → what you'll learn → key moments → watch now CTA

---

## Recipe
**schema.org/Recipe**

| Field | Required | Notes |
|---|---|---|
| name | ✅ | Recipe name |
| description | ✅ | Brief description |
| recipeIngredient | ✅ | Array of ingredients |
| recipeInstructions | ✅ | Steps |
| cookTime | ○ | ISO 8601 duration |
| recipeYield | ○ | Servings |
| recipeCuisine | ○ | Cuisine type |
| keywords | ○ | Tags |
| image | ○ | Photo |

**Content angle:** Story/origin → what makes it special → key technique → result → CTA

---

## JobPosting
**schema.org/JobPosting**

| Field | Required | Notes |
|---|---|---|
| title | ✅ | Job title |
| description | ✅ | Role description |
| hiringOrganization | ✅ | Company name |
| datePosted | ○ | Date |
| jobLocation | ○ | Location or remote |
| baseSalary | ○ | Salary range |
| skills | ○ | Required skills |
| url | ○ | Apply link |

**Content angle:** Role summary → key responsibilities → ideal candidate → why join → apply CTA

---

## Course
**schema.org/Course**

| Field | Required | Notes |
|---|---|---|
| name | ✅ | Course name |
| description | ✅ | What it teaches |
| provider | ○ | Platform/institution |
| skills | ○ | What learners gain |
| timeRequired | ○ | Duration |
| url | ○ | Enroll link |
| keywords | ○ | Tags |

**Content angle:** What you'll learn → who it's for → format → outcome → enroll CTA

---

## Offer / Deal
**schema.org/Offer**

| Field | Required | Notes |
|---|---|---|
| name | ✅ | Offer name |
| description | ✅ | What's included |
| price | ✅ | Numeric price |
| priceCurrency | ✅ | ISO 4217 (USD, EUR, INR…) |
| validFrom | ○ | Start date |
| validThrough | ○ | Expiry date |
| url | ○ | Offer page |
| keywords | ○ | Tags |

**Content angle:** What's on offer → value → urgency → terms → CTA

---

## Fallback: Generic Item

If type cannot be determined, use these universal fields:

```json
{
  "name": "",
  "description": "",
  "url": "",
  "keywords": [],
  "targetAudience": "",
  "notes": ""
}
```

Treat content angle as: **What it is → why it matters → who cares → CTA**
