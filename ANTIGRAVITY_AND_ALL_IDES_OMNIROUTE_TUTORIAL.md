# Complete Guide: OmniRoute in Antigravity IDE & All Coding Agents

This guide explains how **OmniRoute** works inside **Antigravity IDE**, how to verify the **MCP (Model Context Protocol)** connection, and how model selection works across all your IDEs and CLI agents.

---

## 1. How OmniRoute Works in Antigravity IDE

### Why the Bottom Dropdown Shows Gemini Models
In **Antigravity IDE**, the main chat engine is powered by Google DeepMind's native models (e.g., Gemini 2.5 Pro / Flash).
**OmniRoute connects to Antigravity as an active Model Context Protocol (MCP) Server**, not as a raw chat dropdown replacement.

This gives Antigravity direct access to over **30+ OmniRoute MCP Tools** to inspect, route, switch combos, benchmark latency, and execute tasks across your connected AI models.

### How to Check that the MCP Server is Working

#### Method A: Ask Antigravity Directly in Chat
You can test the connection anytime simply by typing any of these commands into the Antigravity chat:
* *"Check OmniRoute health using MCP"*
* *"List my active OmniRoute combos"*
* *"Pick the fastest model from OmniRoute for coding"*
* *"Explain the current route for OmniRoute"*

Antigravity will execute the MCP tool and reply with live data directly from the gateway!

#### Method B: Live Verification Evidence
The MCP server is connected via **SSE (Server-Sent Events)** configured in [`C:\Users\Admin\.gemini\config\mcp_config.json`](file:///C:/Users/Admin/.gemini/config/mcp_config.json):
```json
{
  "mcpServers": {
    "omniroute": {
      "serverUrl": "http://127.0.0.1:20128/api/mcp/sse",
      "headers": {
        "Authorization": "Bearer sk-3a0b09e07366b474-63292a-294d391c"
      }
    }
  }
}
```

* **Health Tool (`omniroute_get_health`)**:
  ```json
  {
    "status": "healthy",
    "version": "3.8.50",
    "uptime": "817s",
    "cryptography": "healthy (aes-256-gcm)"
  }
  ```
* **Combos Tool (`omniroute_list_combos`)**:
  Returns all configured virtual chains:
  - `Fast Auto Failover`
  - `Coding Failover`
  - `Kimi Coding`
  - `Antigravity Resilient`
  - `Free Tier Only`
  - `Research and Analysis`
  - `Vision Tasks`

---

## 2. Where Can You Change / Select OmniRoute Models Directly?

In extensions and CLI agents designed for custom OpenAI-compatible endpoints, **OmniRoute provides full model selection**:

| IDE / Agent | Where Model is Selected | Available Models |
|---|---|---|
| **Continue Extension** | Bottom chat dropdown in VS Code / VSCodium | `OmniRoute Auto`, `Auto Coding`, `Auto Fast`, `Auto Smart`, `Auto Cheap`, `Auto Offline`, `Fast Auto Failover`, `Free Tier Only`, `Coding Failover` |
| **Kilo Code Extension** | Bottom model picker or Provider Settings | `omniroute/auto`, `omniroute/auto/fast`, `omniroute/auto/coding`, `omniroute/auto/smart`, `omniroute/auto/cheap`, `omniroute/auto/offline` |
| **Roo Code / Cline** | Extension Settings -> Provider: OpenAI Compatible | Model ID: `auto` (or `auto/coding`, `auto/fast`) |
| **Cursor** | Cursor Settings -> Models | `auto`, `auto/coding`, `auto/fast` |
| **Claude Code CLI** | Configured in `~/.claude/settings.json` | `auto` |
| **OpenAI Codex CLI** | Terminal command flags | `codex --profile fast`, `codex --profile coding`, `codex --profile cheap` |
| **Aider** | Command line startup | `aider --model openai/auto` |
| **OpenCode CLI** | Configured in `opencode.json` | `omniroute/auto` |

---

## 3. OmniRoute Virtual Model Directory

OmniRoute dynamically routes requests according to what each virtual model optimizes for:

| Virtual Model ID | Target Optimization | Strategy |
|---|---|---|
| **`auto`** | 🎯 Balanced default | Last-Known-Good-Provider (LKGP) failover |
| **`auto/coding`** | 🧑‍💻 Code generation quality | High reasoning, coding benchmark weights |
| **`auto/fast`** | ⚡ Ultra-low latency | Routes to fastest available responding provider |
| **`auto/smart`** | 🔭 Quality + Exploration | Quality-first with 10% model discovery |
| **`auto/cheap`** | 💰 Cost optimization | Selects cheapest provider per token |
| **`auto/offline`** | 🔋 Quota protection | Selects provider with most remaining quota headroom |

---

## 4. One-Click Management & Recovery Tools

All automation scripts are located in [`e:\AS Projects\OmniRoute-ZeroConfig`](file:///e:/AS%20Projects/OmniRoute-ZeroConfig):

1. **[RESTART_OMNIROUTE_CLEAN.bat](file:///e:/AS%20Projects/OmniRoute-ZeroConfig/RESTART_OMNIROUTE_CLEAN.bat)**:
   - Closes any stuck background instances.
   - Clears corrupted Chromium GPU cache to prevent black screens.
   - Launches OmniRoute cleanly with software rendering (`--disable-gpu`).
   - Opens the browser dashboard at [http://127.0.0.1:20128/](http://127.0.0.1:20128/).

2. **[RUN_VERIFY.bat](file:///e:/AS%20Projects/OmniRoute-ZeroConfig/RUN_VERIFY.bat)**:
   - Performs a complete self-healing health check on all 15 agents and IDEs.
   - Benchmarks live inference across all virtual models.

3. **[OMNIROUTE_CONTROL_CENTER.bat](file:///e:/AS%20Projects/OmniRoute-ZeroConfig/OMNIROUTE_CONTROL_CENTER.bat)**:
   - Interactive terminal console for model switching, testing, and agent configuration.
