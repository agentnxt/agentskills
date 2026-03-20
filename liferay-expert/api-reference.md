# Liferay 7.4 CE — API Reference

## Authentication

Basic Auth works for all endpoints:
```bash
AUTH="admin@example.com:password"
curl -s -u $AUTH "http://localhost:8080/api/jsonws/..."
```

**Critical:** `auth.token.check.enabled=true` in portal-ext.properties blocks ALL JSON-WS POST calls (returns empty `{}`). To automate via API:

```bash
# 1. Disable temporarily
sed -i 's/auth.token.check.enabled=true/auth.token.check.enabled=false/' /opt/liferay/portal-ext.properties
docker restart liferay_portal

# 2. Run your API calls...

# 3. Re-enable immediately
sed -i 's/auth.token.check.enabled=false/auth.token.check.enabled=true/' /opt/liferay/portal-ext.properties
docker restart liferay_portal
```

## API Discovery

Always discover endpoints from the running instance:

```bash
# Browse all JSON-WS services
curl -s -u $AUTH "http://localhost:8080/api/jsonws" | grep -oP 'href="/api/jsonws[^"]*"' | grep "SERVICE_NAME"

# OpenAPI spec for headless APIs
curl -s -u $AUTH "http://localhost:8080/o/headless-delivery/v1.0/openapi.json"

# List all headless API paths
curl -s -u $AUTH "http://localhost:8080/o/headless-delivery/v1.0/openapi.json" | python3 -c "
import sys,json
for path in sorted(json.load(sys.stdin).get('paths',{})): print(path)"
```

---

## Page Creation

### Working Method: JSON-WS 10-Parameter Signature

```
POST /api/jsonws/layout/add-layout
Signature: /layout/add-layout-10-long-boolean-long-java.lang.String-java.lang.String-java.lang.String-java.lang.String-boolean-java.lang.String-com.liferay.portal.kernel.service.ServiceContext
```

```bash
curl -s -u $AUTH -X POST "http://localhost:8080/api/jsonws/layout/add-layout" \
  -d "groupId=GROUP_ID" \
  -d "privateLayout=false" \
  -d "parentLayoutId=0" \
  -d "name=Page Name" \
  -d "title=Page Title" \
  -d "description=" \
  -d "type=portlet" \
  -d "hidden=false" \
  -d "friendlyURL=/page-url" \
  -d "serviceContext.scopeGroupId=GROUP_ID" \
  -d "serviceContext.addGroupPermissions=true" \
  -d "serviceContext.addGuestPermissions=true"
```

**Valid `type` values:**
| Type | Description |
|------|-------------|
| `portlet` | Widget page — can add portlets via typeSettings |
| `content` | Content page — managed via Liferay UI page editor |
| `panel` | Panel page |
| `embedded` | Embedded page |
| `link_to_layout` | Link to another page |
| `url` | URL redirect page |

**Parameters:**
- `groupId` — Site's group ID (discover via `/o/headless-admin-user/v1.0/my-user-account`)
- `privateLayout` — `false` for public pages, `true` for private
- `parentLayoutId` — `0` for top-level, or parent's layoutId for child pages
- `friendlyURL` — Must start with `/`, must be unique within the site

### Batch Page Creation

```bash
for PAGE in "Home,/home" "Blog,/blog" "Products,/products"; do
  IFS=',' read -r NAME URL <<< "$PAGE"
  curl -s -u $AUTH -X POST "http://localhost:8080/api/jsonws/layout/add-layout" \
    -d "groupId=GROUP_ID" -d "privateLayout=false" -d "parentLayoutId=0" \
    -d "name=$NAME" -d "title=$NAME" -d "description=" \
    -d "type=portlet" -d "hidden=false" -d "friendlyURL=$URL" \
    -d "serviceContext.scopeGroupId=GROUP_ID"
done
```

### NOT Working in CE 7.4

```
POST /o/headless-delivery/v1.0/sites/{siteId}/site-pages
→ Returns "BAD_REQUEST UnsupportedOperationException"
→ Requires DXP feature flag: feature.flag.LPS-178052=true (DXP only, experimental)
```

---

## Widget Management

### Add Widget to Page

Update the page's `typeSettings` to include portlet IDs:

```bash
curl -s -u $AUTH -X POST "http://localhost:8080/api/jsonws/layout/update-layout" \
  -d "groupId=GROUP_ID" \
  -d "privateLayout=false" \
  -d "layoutId=LAYOUT_ID" \
  -d "typeSettings=layout-template-id=1_column
column-1=PORTLET_ID,"
```

### Layout Templates

| Template ID | Description |
|-------------|-------------|
| `1_column` | Single full-width column |
| `2_columns_i` | 30/70 split |
| `2_columns_ii` | 70/30 split |
| `2_columns_iii` | 50/50 split |
| `1_2_columns_i` | Full width + 30/70 below |
| `1_2_columns_ii` | Full width + 70/30 below |
| `1_2_1_columns` | Full + 50/50 + Full |
| `3_columns` | 33/33/33 split |

### Multiple Widgets in One Column

```
typeSettings=layout-template-id=2_columns_iii
column-1=PORTLET_ID_1,PORTLET_ID_2,
column-2=PORTLET_ID_3,
```

### Common Portlet IDs

| Widget | Portlet ID |
|--------|-----------|
| Blogs | `com_liferay_blogs_web_portlet_BlogsPortlet` |
| Blogs Aggregator | `com_liferay_blogs_web_portlet_BlogsAgreggatorPortlet` |
| Document Library | `com_liferay_document_library_web_portlet_DLPortlet` |
| Web Content Display | `com_liferay_journal_content_web_portlet_JournalContentPortlet` |
| Web Content List | `com_liferay_journal_content_search_web_portlet_JournalContentSearchPortlet` |
| Asset Publisher | `com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet` |
| Navigation Menu | `com_liferay_site_navigation_menu_web_portlet_SiteNavigationMenuPortlet` |
| Breadcrumb | `com_liferay_site_navigation_breadcrumb_web_portlet_SiteNavigationBreadcrumbPortlet` |
| Categories Navigation | `com_liferay_asset_categories_navigation_web_portlet_AssetCategoriesNavigationPortlet` |
| Tags Navigation | `com_liferay_asset_tags_navigation_web_portlet_AssetTagsNavigationPortlet` |
| Search Bar | `com_liferay_portal_search_web_portlet_SearchBarPortlet` |
| Search Results | `com_liferay_portal_search_web_portlet_SearchResultsPortlet` |
| Wiki | `com_liferay_wiki_web_portlet_WikiPortlet` |
| Message Boards | `com_liferay_message_boards_web_portlet_MBPortlet` |
| User Profile | `com_liferay_my_account_web_portlet_MyAccountPortlet` |
| Login | `com_liferay_login_web_portlet_LoginPortlet` |
| IFrame | `com_liferay_iframe_web_portlet_IFramePortlet` |

---

## Theme Application

### JSON-WS Method Does NOT Exist in CE 7.4

`/api/jsonws/layout-set/update-look-and-feel` → 404

### Working Method: Direct Database Update

```bash
# Apply theme to public pages of a site
docker exec DB_CONTAINER psql -U DB_USER -d DB_NAME \
  -c "UPDATE layoutset SET themeid = 'THEME_ID' WHERE groupid = GROUP_ID AND privatelayout = false;"

# Verify
docker exec DB_CONTAINER psql -U DB_USER -d DB_NAME \
  -c "SELECT groupid, themeid FROM layoutset WHERE groupid = GROUP_ID;"
```

Theme IDs follow the pattern: `themename_WAR_themenameTheme` (e.g., `unboxdtheme_WAR_unboxdtheme`)

Discover installed themes:
```bash
curl -s -u $AUTH "http://localhost:8080/api/jsonws/theme/get-war-themes"
```

---

## Content Management

### Structured Content (Web Content Articles)

```bash
# List content structures
curl -s -u $AUTH "http://localhost:8080/o/headless-delivery/v1.0/sites/GROUP_ID/content-structures"

# Create web content
curl -s -u $AUTH -X POST "http://localhost:8080/o/headless-delivery/v1.0/sites/GROUP_ID/structured-contents" \
  -H "Content-Type: application/json" \
  -d '{
    "contentStructureId": STRUCTURE_ID,
    "title": "Article Title",
    "contentFields": [
      {"name": "content", "contentFieldValue": {"data": "<p>HTML content here</p>"}}
    ]
  }'
```

### Blog Posts

```bash
# List blogs
curl -s -u $AUTH "http://localhost:8080/o/headless-delivery/v1.0/sites/GROUP_ID/blog-postings"

# Create blog post
curl -s -u $AUTH -X POST "http://localhost:8080/o/headless-delivery/v1.0/sites/GROUP_ID/blog-postings" \
  -H "Content-Type: application/json" \
  -d '{
    "headline": "Blog Title",
    "articleBody": "<p>Blog content</p>",
    "alternativeHeadline": "Subtitle"
  }'
```

### Documents

```bash
# Upload document
curl -s -u $AUTH -X POST "http://localhost:8080/o/headless-delivery/v1.0/sites/GROUP_ID/documents" \
  -F "file=@/path/to/file.pdf" \
  -F "document={\"title\":\"My Document\"};type=application/json"
```

### Navigation Menus

```bash
# List navigation menus
curl -s -u $AUTH "http://localhost:8080/o/headless-delivery/v1.0/sites/GROUP_ID/navigation-menus"

# Create navigation menu
curl -s -u $AUTH -X POST "http://localhost:8080/o/headless-delivery/v1.0/sites/GROUP_ID/navigation-menus" \
  -H "Content-Type: application/json" \
  -d '{"name": "Main Nav"}'
```

---

## Database Reference

Table names in PostgreSQL (no underscore suffix unlike MySQL):

| Table | Purpose |
|-------|---------|
| `layout` | Pages/layouts |
| `layoutset` | Site-level settings (theme, logo) |
| `layoutfriendlyurl` | Friendly URLs for pages |
| `user_` | Note: user_ has underscore in both PG and MySQL |
| `group_` | Sites/groups |
| `company` | Portal instances |
| `journalarticle` | Web content articles |
| `blogsentry` | Blog posts |
| `dlfileentry` | Documents |
| `kbarticle` | Knowledge base articles |

### Useful Queries

```sql
-- All pages for a site
SELECT layoutid, plid, friendlyurl, type_ FROM layout WHERE groupid = 'GROUP_ID' AND privatelayout = false;

-- Current theme
SELECT groupid, themeid FROM layoutset WHERE groupid = 'GROUP_ID';

-- Admin users
SELECT screenname, emailaddress FROM user_;

-- Company info
SELECT companyid, webid, mx FROM company;
```
