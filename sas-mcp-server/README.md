# SAS Viya MCP Server for Google Antigravity

This repository houses the production-ready **SAS Viya Model Context Protocol (MCP) Server**, engineered specifically to bridge the **Google Antigravity AI Agent** with the **SAS Viya for Learners (VFL)** environment.

By running this MCP server locally, Google Antigravity gains the power to dynamically execute SAS code, run high-performance Cloud Analytic Services (CAS) actions, register/score models, and query Visual Analytics reports directly from the chat interface.

---

## 🌟 The Antigravity + SAS Viya for Learners Integration

SAS Viya for Learners applies strict security policies, including federated Single Sign-On (SSO / `external_oauth`) and short inactivity timeouts. Standard API password logins are completely blocked in this environment.

To make this seamless for **Google Antigravity**, we implemented three core architectural features:

1. **OAuth Authorization Code Flow (`auth_setup.py`)**: A one-time setup that launches your browser, performs the SSO login, and generates a long-lived **Refresh Token** (lasts up to 90 days). This avoids having to share passwords or handle complex authentication manually.
2. **Transparent Auto-Refresh (`viya_utils.py`)**: If the current token expires (which happens after 60 minutes), the server catches the 401 error, automatically trades the refresh token for a new access token, and retries the AI's requested action.
3. **Continuous Keep-Alive Heartbeat (`stdio_server.py`)**: Spawns a lightweight background thread that pings the Viya API every 5 minutes to keep active compute and CAS sessions alive, ensuring Antigravity is always connected.

---

## 🛠️ Codebase Structure

This repository is kept completely clean, generic, and free of any personal session or project metadata, making it ready to be pushed to your private or public Git repository:

- **`src/sas_mcp_server/stdio_server.py`**: Main MCP server entrance. Houses the **Keep-Alive Heartbeat** daemon.
- **`src/sas_mcp_server/viya_utils.py`**: Core API utility layer containing the **Auto-Refresh Interceptor**.
- **`auth_setup.py`**: Safe setup utility to perform the one-time authentication.

---

## 📖 Setup Guide (For Google Antigravity Integration)

### Step 1: Prepare Environment
1. Ensure you have **Python 3.10+** installed.
2. Open your terminal in this directory and set up a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Step 2: Configure `.env` File
Create a `.env` file in the project root (this file is automatically ignored by Git so your credentials will never be leaked). Add the following:
```ini
VIYA_ENDPOINT=https://vfl-028.engage.sas.com
SSL_VERIFY=false
KEEP_ALIVE_HEARTBEAT=true
```

### Step 3: Run Setup
Run the one-time authentication setup:
```powershell
.\.venv\Scripts\python.exe auth_setup.py
```
- Click the generated URL.
- Log into your SAS Viya for Learners SSO.
- Copy the code from the address bar of the broken `localhost` page.
- Paste it into the script to automatically save your tokens.

### Step 4: Configure Antigravity / Claude Desktop
To let Google Antigravity or your local Claude Desktop connect to this server, configure the MCP settings in your client's config file (e.g. `mcp_config.json`):
```json
{
  "mcpServers": {
    "sas-viya": {
      "command": "python",
      "args": ["-m", "src.sas_mcp_server.main"],
      "cwd": "C:/Users/nivesh.bagavatham/OneDrive - OTSI/Desktop/Anti G/sas-mcp-server",
      "env": {
        "VIYA_ENDPOINT": "https://vfl-028.engage.sas.com"
      }
    }
  }
}
```

---

## ⚙️ Heartbeat Control & Toggles
To preserve SAS Viya server resources when you are done working, open `.env` and toggle the heartbeat:
```ini
KEEP_ALIVE_HEARTBEAT=false
```
When `false`, the server runs completely silently without background threads.
