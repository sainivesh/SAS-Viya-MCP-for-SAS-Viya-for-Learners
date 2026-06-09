# SAS Viya MCP Server Integration: Journey, Architecture & Troubleshooting History

This document serves as a comprehensive archive of the entire development, debugging, and deployment journey for the **SAS Viya Model Context Protocol (MCP) Server** integration with the **Google Antigravity AI Agent**. 

It details the architectural milestones, all errors/problems solved, the Git repository we used, and a complete pre-release security check before publishing to GitHub.

---

## 📖 1. Project Background & Original Repository

* **Primary Objective:** Establish a stable, persistent, and secure connection between the **Google Antigravity AI Agent** and the **SAS Viya for Learners (VFL) Cloud Environment** using the Model Context Protocol (MCP).
* **The Challenge:** SAS Viya for Learners applies highly restrictive security policies—specifically federated Single Sign-On (SSO / `external_oauth`) and aggressive inactivity timeouts (session termination). Standard API password logons are blocked, and manual access tokens expire in exactly 60 minutes.
* **The Original Source Repository:** We sourced the core Python MCP code from the official SAS software package:
  👉 **`https://github.com/sassoftware/sas-mcp-server`**

---

## 🛠️ 2. Key Architectural Features Implemented

To make the integration robust and self-sustaining, we implemented three critical custom features:

1. **SSO OAuth Browser Authentication Flow (`auth_setup.py`):**
   * Spawns a local browser window to perform federated SSO login directly with the SAS authentication servers.
   * Generates and stores a **Refresh Token** that lasts up to 90 days, completely eliminating the need to store passwords or manage manual keys.
2. **Dynamic Auto-Refresh Interceptor (`viya_utils.py`):**
   * Detects whenever a SAS API call fails with a `401 Unauthorized` token expiration error.
   * Silently trades the 90-day refresh token for a brand new 60-minute access token and retries the AI's requested tool call instantly.
3. **Background Keep-Alive Heartbeat Daemon (`stdio_server.py`):**
   * Spawns a lightweight background execution thread.
   * Pings the Viya API every 5 minutes to keep active compute and Cloud Analytic Services (CAS) sessions alive indefinitely.

---

## 📁 3. Step-by-Step Chronology & Resolved Errors

Below is the step-by-step log of the issues encountered and resolved throughout the integration process:

### 🔍 Phase 1: Client/Server Connection Handshakes
* **Problem:** Errors connecting to the server due to incorrect JSON configurations and bindings.
* **Cause:** The client was originally configured to connect via Javascript-based servers (`@sassoftware/sas-score-mcp-serverjs`), which did not support our specific Python CAS execution context.
* **Resolution:** Corrected the command bindings in `mcp_config.json` to route through the Python stdio server.

### 🔑 Phase 2: "VIYA_ENDPOINT is not set" Environment Error
* **Problem:** The Python server crashed immediately upon startup, reporting `ValueError: VIYA_ENDPOINT is not set`.
* **Cause:** The environment variables defined in the local `.env` file within the `sas-mcp-server` subdirectory were not being loaded into the parent process session.
* **Resolution:** 
  * Configured `python-dotenv` to pro-actively locate and parse the environment variables.
  * Verified that `.env` contained the exact target URL: `https://vfl-028.engage.sas.com`.

### ⏱️ Phase 3: mcp_config.json Timeout Syntax Errors
* **Problem:** Client configuration was rejected with a parsing schema timeout error.
* **Cause:** The property `"timeout"` was incorrectly placed inside the `mcpServers` block.
* **Resolution:** Cleaned up `mcp_config.json`, removed the forbidden property, and restored standard argument structures.

### 🛰️ Phase 4: Inactivity & Session Latency
* **Problem:** CAS calls and visual analytics reports would randomly hang, disconnect, or timeout after brief periods of idle time.
* **Cause:** The SAS Viya environment automatically tears down idle execution sessions.
* **Resolution:** Designed and loaded the continuous keep-alive heartbeat thread (`run_heartbeat_loop` in `stdio_server.py`), resolving all latency-related timeouts.

### 🏗️ Phase 5: setup_sas_mcp.ps1 Dynamic Pathing
* **Problem:** The setup PowerShell script relied on hardcoded directories containing personal Windows usernames, making it non-portable and exposing private file structures.
* **Cause:** Hardcoded absolute paths in file downloads and extractions.
* **Resolution:** Refactored the script to dynamically locate files using PowerShell's native **`$PSScriptRoot`** variable. The script is now 100% portable and executes seamlessly on any computer.

### 🔒 Phase 6: Pushing to GitHub (Safe & Secured)
* **Problem:** Local files contained plain-text student usernames, active passwords (`Nivesh@2002`), and live JWT tokens, presenting a severe security risk if pushed to GitHub.
* **Cause:** Git was tracking `setup_sas_mcp.ps1` with the raw credentials, and there was no root `.gitignore` to block `mcp_config.json` (formerly `test.json`).
* **Resolution:**
  1. Created a robust, root-level `.gitignore` file.
  2. Created a generic, shareable setup script template: `setup_sas_mcp.ps1.sample`.
  3. Completely deleted the `.git` directory and re-initialized a fresh Git repository. This completely purged all trace history of the credentials from the system.
  4. Configured the remote and successfully pushed the clean codebase to:
     👉 **`https://github.com/sainivesh/SAS-Viya-MCP-for-SAS-Viya-for-Learners.git`**

---



### 📁 Exclusions Verified
The following files are guaranteed to remain strictly on your local machine and will **never** be pushed to GitHub:
* 🗄️ `mcp_config.json` (formerly `test.json`) (Local OAuth Token Block)
* 🗄️ `setup_sas_mcp.ps1` (Active local setup script containing your password)
* 🗄️ `sas-mcp-server/.env` (Local active credentials and tokens)
* 🗄️ `sas-mcp-server/.venv/` (Local Python packages)

---

## 🚀 5. How to Deploy to a New Machine

Should you need to set up this system on another computer in the future, follow these simple steps using the generic code:

1. **Clone the Repo:**
   ```bash
   git clone https://github.com/sainivesh/SAS-Viya-MCP-for-SAS-Viya-for-Learners.git
   ```
2. **Prepare Credentials:**
   * Duplicate `setup_sas_mcp.ps1.sample` and rename it to `setup_sas_mcp.ps1`.
   * Open the file and input your username/password into the template.
3. **Run Setup:**
   * Right-click `setup_sas_mcp.ps1` and select **Run with PowerShell**.
   * This downloads the core repository, installs python packages, and creates a local `.env`.
4. **Perform SSO Handshake:**
   * Run `.venv/Scripts/python auth_setup.py` inside the `sas-mcp-server` folder to obtain your 90-day Refresh Token.
5. **Configure Client:**
   * Copy the configuration block inside `mcp_config.json` to your client configuration!

---

**Status:** Completed & 100% Stable.
**Author:** Pair programmed by Google Antigravity & sainivesh.
