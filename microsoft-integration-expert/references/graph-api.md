# Microsoft Graph API — Deep Reference

Source: https://learn.microsoft.com/en-us/graph/

## Base URLs
- v1.0 (production): `https://graph.microsoft.com/v1.0/`
- beta: `https://graph.microsoft.com/beta/` ⚠️ Not for production

## Authentication Header
Every Graph call needs:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

## Key Resource Endpoints

### Users & Identity
```
GET /users                          # List all users (requires User.Read.All)
GET /me                             # Current signed-in user
GET /users/{id}                     # Specific user
GET /me/memberOf                    # Groups user belongs to
POST /users                         # Create user
PATCH /users/{id}                   # Update user properties
```

### Mail (Exchange Online)
```
GET /me/messages                    # Inbox messages
GET /me/mailFolders                 # Mail folders
POST /me/sendMail                   # Send email
POST /me/messages/{id}/reply        # Reply to message
GET /me/messages?$filter=isRead eq false   # Unread messages
```

### Calendar
```
GET /me/events                      # Calendar events
POST /me/events                     # Create event
GET /me/calendarView?startDateTime=...&endDateTime=...  # Date range
GET /me/calendar/calendarView       # Calendar view
```

### Teams
```
GET /me/joinedTeams                 # Teams user belongs to
GET /teams/{id}/channels            # Channels in a team
POST /teams/{id}/channels/{cid}/messages  # Post a message
GET /chats                          # 1:1 and group chats
POST /chats/{id}/messages           # Send chat message
GET /teams/{id}/members             # Team members
```

### SharePoint & OneDrive
```
GET /me/drive                       # User's OneDrive
GET /me/drive/root/children         # Root folder contents
GET /sites?search=*                 # Search all sites
GET /sites/{id}/lists               # Lists in a site
GET /sites/{id}/lists/{lid}/items   # List items
POST /me/drive/root/children        # Upload file
```

### Groups & Directory
```
GET /groups                         # All groups
GET /groups/{id}/members            # Group members
POST /groups                        # Create group
GET /directoryRoles                 # Directory roles
```

## Advanced Patterns

### $filter, $select, $expand, $orderby
```
# Only get name and email
GET /users?$select=displayName,mail

# Filter active users
GET /users?$filter=accountEnabled eq true

# Expand manager
GET /me?$expand=manager

# Sort by name
GET /users?$orderby=displayName asc

# Combined
GET /me/messages?$filter=isRead eq false&$select=subject,from&$top=10
```

### Batching (up to 20 requests in one HTTP call)
```json
POST https://graph.microsoft.com/v1.0/$batch
{
  "requests": [
    { "id": "1", "method": "GET", "url": "/me" },
    { "id": "2", "method": "GET", "url": "/me/messages?$top=5" }
  ]
}
```

### Delta Queries (track changes efficiently)
```
GET /me/messages/delta              # Initial sync
GET /me/messages/delta?$deltatoken=xxx   # Subsequent syncs
```

### Webhooks / Change Notifications
```json
POST /subscriptions
{
  "changeType": "created,updated",
  "notificationUrl": "https://your-endpoint.com/notify",
  "resource": "me/messages",
  "expirationDateTime": "2026-03-30T00:00:00Z",
  "clientState": "secretClientState"
}
```
Subscriptions expire — renew with PATCH /subscriptions/{id}

## Permissions Reference (Most Common)

| Permission | Type | What It Allows |
|---|---|---|
| User.Read | Delegated | Sign in and read user profile |
| User.ReadWrite.All | Application | Read/write all users |
| Mail.Read | Delegated | Read user's email |
| Mail.Send | Delegated | Send email as user |
| Calendars.ReadWrite | Delegated | Full calendar access |
| Files.ReadWrite | Delegated | User's OneDrive files |
| Sites.Read.All | Application | All SharePoint sites |
| Group.ReadWrite.All | Delegated | All groups |
| TeamSettings.ReadWrite.All | Application | All Teams settings |
| ChannelMessage.Read.All | Application | Read all Teams messages |

## SDKs
- **JavaScript/TypeScript**: `@microsoft/microsoft-graph-client`
- **Python**: `msgraph-sdk-python`
- **C#/.NET**: `Microsoft.Graph` NuGet package
- **PowerShell**: `Microsoft.Graph` module (`Connect-MgGraph`)

## Graph Explorer
Test queries interactively: https://developer.microsoft.com/en-us/graph/graph-explorer
