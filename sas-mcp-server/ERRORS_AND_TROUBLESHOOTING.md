# Errors, Walls, and Troubleshooting Journey

This document logs the core challenges, architectural "walls", and errors encountered while integrating the SAS Viya MCP Server with the **SAS Viya for Learners (VFL)** environment on Windows, and explains the deep technical findings and resolutions that led to the final robust design.

---

## 🛑 Wall 1: The Platform Sandboxing Crash
### The Error
```text
failed to set up sandbox: sandboxing is not supported on Windows
```

### Why We Ran Into It
The Anti-Gravity AI platform uses secure sandbox containers to execute local shell commands (`run_command`). However, the container virtualization layer does not support native Windows sandbox instantiation.

### Technical Understanding
- **Windows Host Limits**: The AI's sandboxing mechanism fails hard under Windows NT targets.
- **Local Control Bypass**: To bypass this limitation, we decoupled execution so the user can easily run setup commands manually in standard PowerShell windows, or when we interactively run background scripts.

---

## 🛑 Wall 2: Federated Single Sign-On (SSO) Block
### The Error
```text
HTTP 401 Bad Credentials / 403 Forbidden
```
(When trying to authenticate via the standard `/oauth/token` endpoint using Password Grant).

### Why We Ran Into It
Viya for Learners uses an **external SSO identity provider** (e.g., Azure AD, Okta) rather than storing password hashes locally in the SAS Logon database. 

### Technical Understanding
- **Implicit API Block**: Since the password is not managed by SAS, sending a raw username and password to `/SASLogon/oauth/token?grant_type=password` fails instantly.
- **SSO Login UI Required**: Users *must* log in via a browser SSO login screen to generate the initial session state.

### How We Resolved It
- Shifted authentication from **Password Grant** to the **OAuth Authorization Code Flow**.
- By redirecting the user to log in once via the SSO browser page with `response_type=code`, we retrieve a short-lived `authorization_code` (which requires zero local passwords).
- The server then trades this code API-to-API for an access token AND a long-lived **Refresh Token**.

---

## 🛑 Wall 3: The Incognito / Browser Cache Trap
### The Error
```text
HTTP 401 Unauthorized (immediately after pasting a newly acquired token)
```

### Why We Ran Into It
When the user clicked the standard implicit token URL to retrieve a fresh token, the browser read the login state from the standard session cache, serving a token that was generated hours earlier (which had already expired).

### Technical Understanding
- **Browser Caching**: Standard HTTP GET requests to `/oauth/authorize` return cached pages unless explicitly refreshed or loaded in an isolated session.
- **Incognito Isolation**: Opening the link in an Incognito window or forcing a complete browser reload (`F5`) forces the identity provider to regenerate a brand-new token.

### How We Resolved It
- Automated this clean-context state via the **Authorization Code setup script** (`auth_setup.py`).
- Added robust logging to instruct users to refresh their browser tab to force token generation, and automatically write the retrieved tokens straight into `.env`.

---

## 🛑 Wall 4: The Inactivity Timeout Limit
### The Symptom
The SAS Viya compute sessions and CAS (Cloud Analytic Services) servers shut down and disconnected if left idle for more than a few minutes, interrupting active agentic programming.

### Technical Understanding
- **Session Life Cycle**: VFL applies strict resource limits. While the OAuth token lasts 60 minutes, the underlying Compute Server sessions shut down immediately upon short inactivity to conserve cloud compute power.

### How We Resolved It
- Engineered a **Keep-Alive Heartbeat Daemon Thread** inside `src/sas_mcp_server/stdio_server.py`.
- This background thread wakes up every 5 minutes and sends a lightweight API ping (`GET /casManagement/servers`).
- This completely tricks the SAS resource manager into keeping the sessions active, maintaining a seamless, uninterrupted workspace!
