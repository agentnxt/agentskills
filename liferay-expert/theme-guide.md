# Liferay 7.4 CE — Theme Development & Deployment Guide

## Theme WAR Structure

```
my-theme/
└── src/main/webapp/
    ├── WEB-INF/
    │   ├── liferay-look-and-feel.xml    # Required: theme metadata
    │   └── liferay-plugin-package.properties  # Required: plugin metadata
    ├── css/
    │   ├── _custom.scss         # Main custom styles (loaded after Clay)
    │   ├── _clay_variables.scss # Clay/Bootstrap variable overrides (loaded before Clay)
    │   └── _layout.scss         # Layout-specific styles (import in _custom.scss)
    ├── templates/
    │   ├── portal_normal.ftl    # Main page template (overrides Classic theme)
    │   ├── navigation.ftl       # Navigation template
    │   └── init.ftl             # Variable initialization
    ├── images/                  # Theme images/logos
    └── js/                      # Custom JavaScript
```

**IMPORTANT:** Do NOT include `web.xml`. It causes `ClassNotFoundException: InvokerFilter` errors in 7.4.

## Required Files

### WEB-INF/liferay-look-and-feel.xml

```xml
<?xml version="1.0"?>
<!DOCTYPE look-and-feel PUBLIC "-//Liferay//DTD Look and Feel 7.4.0//EN"
  "http://www.liferay.com/dtd/liferay-look-and-feel_7_4_0.dtd">
<look-and-feel>
  <compatibility>
    <version>7.4.3.100+</version>
  </compatibility>
  <theme id="mytheme" name="My Theme">
    <template-extension>ftl</template-extension>
    <portlet-decorator id="barebone" name="Barebone">
      <portlet-decorator-css-class>portlet-barebone</portlet-decorator-css-class>
    </portlet-decorator>
    <portlet-decorator id="borderless" name="Borderless">
      <portlet-decorator-css-class>portlet-borderless</portlet-decorator-css-class>
    </portlet-decorator>
    <portlet-decorator id="decorate" name="Decorate">
      <default-portlet-decorator>true</default-portlet-decorator>
      <portlet-decorator-css-class>portlet-decorate</portlet-decorator-css-class>
    </portlet-decorator>
  </theme>
</look-and-feel>
```

The `id` attribute becomes part of the theme ID: `{id}_WAR_{id}theme` (lowercased, no hyphens).
Example: `id="unboxd-theme"` → theme ID = `unboxdtheme_WAR_unboxdtheme`

### WEB-INF/liferay-plugin-package.properties

```properties
name=My Theme
module-group-id=mytheme
module-incremental-version=1
tags=theme
short-description=Description here
author=Author Name
licenses=MIT
liferay-versions=7.4.3.100+
```

## CSS Architecture

### _clay_variables.scss (Loaded BEFORE Clay — variable overrides only)

```scss
$font-family-base: 'IBM Plex Sans', sans-serif;
$primary: #0072CE;
$body-bg: #F4F4F4;
$border-radius: 0;
$btn-border-radius: 0;
$card-border-radius: 0;
$navbar-dark-bg: #00395E;
```

### _custom.scss (Loaded AFTER Clay — all custom styles)

```scss
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');
@import 'layout';  // Import additional SCSS files

:root {
  --brand-primary: #00395E;
  --brand-accent: #0072CE;
}

body { font-family: var(--font-family-base) !important; }
#banner { background-color: var(--brand-primary) !important; }
// ... rest of styles
```

## FreeMarker Templates

### portal_normal.ftl — Key Variables Available

| Variable | Description |
|----------|-------------|
| `${site_name}` | Site name |
| `${site_default_url}` | Site home URL |
| `${company_name}` | Company/instance name |
| `${logo_css_class}` | CSS class for site logo |
| `${css_class}` | Body CSS class |
| `${w3c_language_id}` | Language code (e.g., en) |
| `${w3c_language_dir}` | Text direction (ltr/rtl) |
| `${root_css_class}` | Root HTML class |
| `${full_templates_path}` | Path to templates dir |
| `${has_navigation}` | Boolean: navigation exists |

### Required Includes (must be in portal_normal.ftl)

```ftl
<@liferay_util["include"] page=top_head_include />     <!-- In <head> -->
<@liferay_util["include"] page=body_top_include />      <!-- After <body> -->
<@liferay.control_menu />                                <!-- Admin toolbar -->
<@liferay_util["include"] page=content_include />        <!-- Page content -->
<@liferay_util["include"] page=body_bottom_include />    <!-- Before </body> -->
<@liferay.user_personal_bar />                           <!-- User menu -->
```

### Navigation Template Pattern

```ftl
<#if has_navigation && is_setup_complete>
  <ul class="nav">
    <#list nav_items as nav_item>
      <li class="${nav_item.isSelected()?then('active','')}">
        <a href="${nav_item.getURL()}" ${nav_item.getTarget()}>
          ${nav_item.getName()}
        </a>
        <#if nav_item.hasChildren()>
          <ul class="dropdown">
            <#list nav_item.getChildren() as child>
              <li><a href="${child.getURL()}">${child.getName()}</a></li>
            </#list>
          </ul>
        </#if>
      </li>
    </#list>
  </ul>
</#if>
```

## Building the WAR

No Java SDK needed on the host — build inside a container:

```bash
cd /path/to/theme/src/main/webapp

# Build WAR (exclude any previous WAR files)
docker run --rm -v "$(pwd)":/theme -w /theme eclipse-temurin:8-jdk \
  sh -c "jar cf /theme/mytheme.war WEB-INF css templates js images"

# Fix permissions for deployment
chmod 666 mytheme.war
```

## Deploying to Liferay

### Hot Deploy (Recommended)

```bash
# Copy WAR to deploy directory
docker cp mytheme.war LIFERAY_CONTAINER:/opt/liferay/deploy/mytheme.war

# Fix ownership (container runs as liferay:1000)
docker exec -u root LIFERAY_CONTAINER chown liferay:liferay /opt/liferay/deploy/mytheme.war
```

### Verify Deployment

```bash
# Watch logs for deployment
docker logs LIFERAY_CONTAINER 2>&1 | grep -i "mytheme"

# Expected success output:
# Processing mytheme.war
# Copying themes for .../mytheme.war
# Themes for .../mytheme.war copied successfully
# STARTED mytheme_7.4.3.120 [BUNDLE_ID]
```

### Common Deployment Errors

| Log Message | Cause | Fix |
|-------------|-------|-----|
| `Unable to write mytheme.war` | File owned by root | `docker exec -u root ... chown liferay:liferay` |
| `ClassNotFoundException: InvokerFilter` | web.xml in WAR | Remove WEB-INF/web.xml, rebuild |
| `STOPPED` then no `STARTED` | Invalid liferay-look-and-feel.xml | Check XML syntax and DTD version |

### Applying Theme After Deploy

```bash
# Via database (only reliable method in CE 7.4)
docker exec DB_CONTAINER psql -U USER -d DB \
  -c "UPDATE layoutset SET themeid = 'mythemeid_WAR_mythemeidtheme' WHERE groupid = GROUP_ID AND privatelayout = false;"
```

## Updating an Existing Theme

1. Edit SCSS/FTL files
2. Rebuild WAR: `docker run --rm -v "$(pwd)":/theme -w /theme eclipse-temurin:8-jdk sh -c "jar cf /theme/mytheme.war WEB-INF css templates js images"`
3. Redeploy: `docker cp` + `chown`
4. Liferay auto-detects the update (STOPPED → STARTED in logs)
5. Clear browser cache (Ctrl+Shift+R)
