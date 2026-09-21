# OmniRoute ZeroConfig 🚀

> **Zero-Config AI Gateway & Universal Auto-Model Selector for all IDEs & Coding Agents.**  
> Automatically configures VS Code, Cursor, Windsurf, Continue Extension, Claude Code CLI, Aider, and Antigravity IDE to route through your local OmniRoute instance with dynamic failover.

---

## ⚡ Zero-Config: Just Use `auto`

No combos to manually manage. Setting your model to `auto` (or a specialized suffix) tells OmniRoute to build a scored virtual combo on the fly across all your active providers:

| Model ID | What It Optimizes For | Typical Upstream Route |
| :--- | :--- | :--- |
| **`auto`** | 🎯 **Balanced Default** (LKGP — sticks to your last good provider) | `openrouter/auto`, `gemini-2.5-flash` |
| **`auto/fast`** | ⚡ **Lowest Latency First** (Instant completion & typing speed) | `claude-sonnet-5`, `gemini-2.5-flash` |
| **`auto/coding`** | 🧑‍💻 **Quality-First Weights** for deep multi-file code generation | `claude-sonnet-4-5`, `gemini-2.5-pro` |
| **`auto/cheap`** | 💰 **Cheapest Per Token First** (Maximizes credit life) | `claude-sonnet-5`, `groq/llama-3.3` |
| **`auto/smart`** | 🔭 **Quality-First + 10% Exploration** to discover top models | `claude-sonnet-5` |
| **`auto/lkgp`** | 📌 **Explicit Last-Known-Good-Provider Stickiness** | Sticks to previously verified host |
| **`auto/offline`** | 🔋 **Most Quota / Rate-Limit Headroom First** | Prioritizes highest quota pools |
| **`auto/chaos`** | 🧪 **Fault-Injection Weights** for resilience & failover testing | Dynamic chaos simulation |
| **`Free Tier Only`** | 🆓 **Zero Cost Fallback Chain** | `gemini-2.5-flash`, `groq` |
| **`Coding Failover`**| 🛡️ **Priority Cascading Failover** | `gemini-2.5-flash` &rarr; `gpt-4o-mini` |

---

## ❓ Why Were Models Not Showing Up in IDEs?

Most AI extensions and IDEs (like Continue, Cursor, and VS Code extensions) have one of two limitations:
1. **Dropdown Truncation**: OmniRoute exposes over 5,500 models from 20+ providers. Many IDE dropdown pickers fail or truncate after the first 50–100 items.
2. **Explicit Whitelisting**: Extensions like **Continue (`~/.continue/config.json`)** and **Cursor** require custom models to be explicitly declared in their local configuration JSON before they will appear in the UI selector dropdown.

### How OmniRoute ZeroConfig Fixes It:
Running `SETUP_ALL_IDES.bat` automatically injects the exact `auto` model catalog into:
* **Continue (`~/.continue/config.json`)**: Injects all `auto` variants directly into the dropdown list.
* **Cursor (`settings.json`)**: Configures `cursor.general.customModels` and sets the active OpenAI base URL.
* **Windsurf (`settings.json`)**: Configures custom model base URL and API keys.
* **Claude Code CLI (`~/.claude/settings.json`)**: Sets `ANTHROPIC_BASE_URL` and `ANTHROPIC_MODEL`.
* **Aider (`~/.aider.conf.yml`)**: Configures primary model (`openai/auto/fast`) and editor/weak model chains.
* **Antigravity IDE**: Connects the MCP SSE endpoint at `http://127.0.0.1:20128/api/mcp/sse`.
* **Windows System Environment**: Sets `OPENAI_BASE_URL`, `ANTHROPIC_BASE_URL`, and keys globally.

---

### 1. One-Click Master Diagnostics & Self-Healing Fix
Double-click:
```bat
RUN_VERIFY.bat
```
Or run via terminal:
```powershell
python VERIFY_AND_FIX_ALL.py
```
*This performs end-to-end testing of the OmniRoute gateway daemon, tests live completions, patches SQLite extension state (bypassing Cline's browser login lock and setting up Roo/Kilo), and repairs all 15 IDE and agent configurations in seconds.*

### 2. Universal Setup
Double-click:
```bat
SETUP_ALL_IDES.bat
```
Or run via terminal:
```powershell
python omniroute_zeroconfig.py --auto
```
*This benchmarks all available models, selects the fastest working route, and configures all IDEs instantly.*

### 3. Live Benchmark Testing
Double-click:
```bat
TEST_AUTO_MODELS.bat
```
Or run:
```powershell
python omniroute_zeroconfig.py --test
```

### 4. Global Windows CLI Commands
Run any of the following directly from PowerShell, CMD, or VS Code / Antigravity terminal:

```powershell
# Universal Diagnostics & Self-Healing Fix
python VERIFY_AND_FIX_ALL.py

# Universal Zero-Click Setup (Configures all 14 agents instantly)
omniroute setup-all

# Specific Agent Setup Commands
omniroute setup-antigravity    # Antigravity IDE & Extensions (Cline, Roo, Kilo)
omniroute setup-aider          # Aider terminal pair-programmer
omniroute setup-opencode       # OpenCode CLI
omniroute setup-goose          # Block Goose agent
omniroute setup-crush          # Charm Crush CLI
omniroute setup-qwen           # Qwen coding CLI
omniroute setup-kilo           # Kilo Code extension & CLI
omniroute setup-roo            # Roo Code extension
omniroute setup-codex          # OpenAI Codex CLI profiles (~/.codex)
omniroute setup-claude         # Anthropic Claude Code launch profiles
omniroute setup-cline          # Cline agent extension
omniroute setup-continue       # Continue VS Code / JetBrains extension
omniroute setup-cursor         # Cursor editor

# Model Benchmark & Selection
omniroute test                 # Test and benchmark all auto models live
omniroute select-model         # Interactive menu to pick primary model
omniroute models               # List all available virtual models
```

### 4. Push to GitHub
```bat
PUSH_TO_GITHUB.bat
```

---

## 🔑 Default Connection Details

* **Gateway Base URL**: `http://127.0.0.1:20128/v1`
* **Web Dashboard**: [http://127.0.0.1:20128/dashboard](http://127.0.0.1:20128/dashboard)
* **Client Inference Key**: `sk-3a0b09e07366b474-358946-ff6459d4`
* **Management Admin Key**: `sk-3a0b09e07366b474-63292a-294d391c`
