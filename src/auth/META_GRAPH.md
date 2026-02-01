# META GRAPH API SETUP
## Facebook + Instagram Reels Upload Bot

---

This guide explains how to configure **Meta Graph API** for automated uploads to:

- Facebook Reels
- Instagram Reels

This is the official, supported method using Meta APIs. No unofficial SDKs. No browser automation.

---

## ⚠️ Important Requirements

Instagram uploads **will not work** unless all conditions below are met:

- ✅ Facebook Page
- ✅ Instagram **Business** account (not personal)
- ✅ Instagram linked to the Facebook Page
- ✅ Page owned by the same Facebook account

---

## Overview

```
Instagram Business Account
        ↓
Linked to Facebook Page
        ↓
Page connected to Meta App
        ↓
Graph API Access Token
        ↓
Reels Upload
```

---

# 1. Create Meta Developer Account

Open:

```
https://developers.facebook.com/
```

Login using the **Facebook account that owns the Page**.

---

# 2. Create Meta App

Go to:

```
My Apps → Create App
```

Choose:

```
Other → Business
```

Fill in:

- **App name:** `short-maker`
- **Email:** your email

Create the app.

---

# 3. Add Required Products

Inside the app dashboard, add:

- ✅ Facebook Login
- ✅ Instagram Graph API

---

# 4. Basic App Configuration

Go to:

```
Settings → Basic
```

Add platform:

```
Website
```

Website URL:

```
https://localhost/
```

Save changes.

---

# 5. Link Instagram to Facebook Page

Open:

```
https://www.facebook.com/pages/
```

Navigate to:

```
Your Page → Settings → Linked Accounts
```

Link your **Instagram Business account**.

---

# 6. Get Facebook Page ID

Open Graph API Explorer:

```
https://developers.facebook.com/tools/explorer/
```

Select:

- Your app
- User access token

Run:

```
GET /me/accounts
```

Response example:

```json
{
  "id": "123456789",
  "name": "My Page",
  "access_token": "EAAG..."
}
```

Save:

- `PAGE_ID`
- `PAGE_ACCESS_TOKEN`

---

# 7. Get Instagram Business Account ID

Run:

```
GET /PAGE_ID?fields=instagram_business_account
```

Response:

```json
{
  "instagram_business_account": {
    "id": "1784140xxxxxxxx"
  }
}
```

Save:

```
IG_USER_ID
```

---

# 8. Required Permissions

Request and approve the following permissions:

```
pages_show_list
pages_read_engagement
pages_manage_metadata
pages_manage_engagement
instagram_basic
instagram_content_publish
```

Without these permissions, uploads will fail.

---

# 9. Convert Token to Long-Lived Token

Short-lived tokens expire in 1 hour.

Convert to a 60-day token:

```
https://graph.facebook.com/v19.0/oauth/access_token
?grant_type=fb_exchange_token
&client_id=app_id
&client_secret=secret_id
&fb_exchange_token=EAA...
```


- client_id = App ID (short-maker → 12345...)
- client_secret = App secret from App Dashboard → Settings → Basic
- fb_exchange_token = the short-lived user token you just generated

if expired 
- Generate a short-lived token with pages_show_list from Graph API Explorer
- Copy it exactly (starts with EAA…)
- Paste it into the fb_exchange_token parameter in the URL above
- Use your App ID and App Secret from the same app
- Open the URL in a browser or curl → you should get a JSON with access_token and expires_in

Save the returned token.

---

# 10. Account File Structure

Recommended layout:

```
accounts/
└── dopamine_drop555/
    ├── meta.env
    └── client_secret.json
```

---

## meta.env

```env
PAGE_ID=
IG_USER_ID=
PAGE_ACCESS_TOKEN=EAA...
```

---

# 11. Instagram Reels Upload Flow

### Step 1 — Create Media Container

```
POST /{ig_user_id}/media
```

Parameters:

- `video_url`
- `caption`
- `media_type=REELS`

---

### Step 2 — Publish Reel

```
POST /{ig_user_id}/media_publish
```

Using the returned:

```
creation_id
```

---

# 12. Facebook Reels Upload Flow

```
POST /{page_id}/video_reels
```

Parameters:

- `video_url`
- `description`

---

# 13. Common Errors

### ❌ Instagram account is not business

Fix:

```
Instagram → Settings → Account → Switch to Business
```

---

### ❌ Media not ready

Cause:
Meta processing delay.

Fix:

Wait **10–30 seconds** before calling `media_publish`.

---

### ❌ Missing permissions

Fix:

```
App Dashboard → Permissions → Request Advanced Access
```

---

### ❌ (#10) Applicati
