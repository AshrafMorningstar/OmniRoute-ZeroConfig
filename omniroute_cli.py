#!/usr/bin/env python3
"""
OmniRoute CLI & Master Multi-Agent Auto-Configurator
===================================================
Provides native Windows CLI commands:
  omniroute setup-aider
  omniroute setup-opencode
  omniroute setup-goose
  omniroute setup-crush
  omniroute setup-qwen
  omniroute setup-kilo
  omniroute setup-roo
  omniroute setup-codex
  omniroute setup-claude
  omniroute setup-cline
  omniroute setup-continue
  omniroute setup-cursor
  omniroute setup-antigravity
  omniroute setup-all
  omniroute test
  omniroute select-model
"""

import os
import sys
import json
import time
import shutil
import argparse
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

# ── Keys & Gateway ────────────────────────────────────────────────────────────
OMNIROUTE_HOST  = os.environ.get("OMNIROUTE_URL", "http://127.0.0.1:20128")
OMNIROUTE_V1    = f"{OMNIROUTE_HOST}/v1"
ADMIN_KEY       = os.environ.get("OMNIROUTE_KEY", "sk-3a0b09e07366b474-63292a-294d391c")
INFERENCE_KEY   = os.environ.get("OPENAI_API_KEY", "sk-3a0b09e07366b474-358946-ff6459d4")
DEFAULT_MODEL   = "auto"

USER_HOME = os.environ.get("USERPROFILE", str(Path.home()))
APPDATA_ROAMING = os.environ.get("APPDATA", os.path.join(USER_HOME, "AppData", "Roaming"))
APPDATA_LOCAL = os.environ.get("LOCALAPPDATA", os.path.join(USER_HOME, "AppData", "Local"))

AUTO_MODELS = [
    {"id": "auto",                "name": "OmniRoute Auto",            "desc": "Balanced default (LKGP - sticks to last good provider)"},
    {"id": "auto/fast",           "name": "OmniRoute Auto Fast",       "desc": "Lowest latency first for instant autocomplete"},
    {"id": "auto/coding",         "name": "OmniRoute Auto Coding",     "desc": "Quality-first weights for multi-file code generation"},
    {"id": "auto/cheap",          "name": "OmniRoute Auto Cheap",      "desc": "Cheapest per token first to save credits"},
    {"id": "auto/smart",          "name": "OmniRoute Auto Smart",      "desc": "Quality-first + 10% discovery exploration"},
    {"id": "auto/lkgp",           "name": "OmniRoute Auto LKGP",       "desc": "Explicit last-known-good-provider stickiness"},
    {"id": "Fast Auto Failover",  "name": "Fast Auto Failover",        "desc": "High-throughput cascading failover"},
    {"id": "Free Tier Only",      "name": "Free Tier Only",            "desc": "Zero-cost community and free tier models"},
    {"id": "Coding Failover",     "name": "Coding Failover",           "desc": "Priority failover chain across all providers"},
]

def merge_json(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    existing = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = {}
    for k, v in data.items():
        if isinstance(v, dict) and isinstance(existing.get(k), dict):
            existing[k].update(v)
        else:
            existing[k] = v
    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

def patch_vscode_sqlite(ext_key: str, patch_dict: dict) -> int:
    ide_paths = [
        os.path.join(APPDATA_ROAMING, "Antigravity IDE", "User", "globalStorage", "state.vscdb"),
        os.path.join(APPDATA_ROAMING, "Code", "User", "globalStorage", "state.vscdb"),
        os.path.join(APPDATA_ROAMING, "Code - Insiders", "User", "globalStorage", "state.vscdb"),
        os.path.join(APPDATA_ROAMING, "Cursor", "User", "globalStorage", "state.vscdb"),
        os.path.join(APPDATA_ROAMING, "VSCodium", "User", "globalStorage", "state.vscdb"),
        os.path.join(APPDATA_ROAMING, "Windsurf", "User", "globalStorage", "state.vscdb"),
    ]
    patched = 0
    import sqlite3
    for db_path in ide_paths:
        if not os.path.exists(db_path):
            continue
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (ext_key,))
            row = cursor.fetchone()
            curr = json.loads(row[0]) if row and row[0] else {}
            curr.update(patch_dict)
            cursor.execute("INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)", (ext_key, json.dumps(curr)))
            conn.commit()
            conn.close()
            patched += 1
        except Exception:
            pass
    return patched

def status_msg(agent: str, target: str, ok: bool = True):
    tag = "[OK] " if ok else "[ERR]"
    print(f"  {tag} [{agent}] -> {target}", flush=True)

# ── Setup Handlers ───────────────────────────────────────────────────────────

def setup_antigravity(model: str = DEFAULT_MODEL):
    print("\n[CONFIGURING] Antigravity IDE (Settings, MCP, & Extensions)...")
    antigravity_settings = os.path.join(APPDATA_ROAMING, "Antigravity IDE", "User", "settings.json")
    custom_models = [m["id"] for m in AUTO_MODELS]

    # 1. User settings
    try:
        merge_json(antigravity_settings, {
            "openai.apiBase": OMNIROUTE_V1,
            "openai.apiKey": INFERENCE_KEY,
            "openai.model": model,
            "cursor.general.customModels": custom_models,
            "roo-cline.autoImportSettingsPath": os.path.join(USER_HOME, ".roo", "omniroute-roo-settings.json"),
            "kilocode.openAiApiKey": INFERENCE_KEY,
            "kilocode.openAiBaseUrl": OMNIROUTE_V1,
            "kilocode.openAiModelId": model,
            "kilo-code.new.model.providerID": "openai-compatible",
            "kilo-code.new.model.modelID": model,
            "cline.openAiBaseUrl": OMNIROUTE_HOST,
            "cline.openAiApiKey": INFERENCE_KEY,
            "cline.openAiModelId": model,
        })
        status_msg("Antigravity IDE", antigravity_settings)
    except Exception as e:
        status_msg("Antigravity IDE", str(e), ok=False)

    # 2. Antigravity MCP config
    try:
        mcp_path = os.path.join(USER_HOME, ".gemini", "config", "mcp_config.json")
        merge_json(mcp_path, {
            "mcpServers": {
                "omniroute": {
                    "serverUrl": f"{OMNIROUTE_HOST}/api/mcp/sse",
                    "headers": {"Authorization": f"Bearer {ADMIN_KEY}"},
                }
            }
        })
        status_msg("Antigravity MCP", mcp_path)
    except Exception as e:
        status_msg("Antigravity MCP", str(e), ok=False)

def setup_aider(model: str = DEFAULT_MODEL):
    print("\n[CONFIGURING] Aider (Terminal Pair-Programmer)...")
    path = os.path.join(USER_HOME, ".aider.conf.yml")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(
                f"# Aider OmniRoute Configuration\n"
                f"openai-api-base:    {OMNIROUTE_V1}\n"
                f"openai-api-key:     {INFERENCE_KEY}\n"
                f"anthropic-api-key:  {INFERENCE_KEY}\n"
                f"model:              openai/{model}\n"
                f"editor-model:       openai/auto/fast\n"
                f"weak-model:         openai/auto/cheap\n"
                f"auto-commits:       false\n"
            )
        status_msg("Aider", path)
    except Exception as e:
        status_msg("Aider", str(e), ok=False)

def setup_continue(model: str = DEFAULT_MODEL):
    print("\n[CONFIGURING] Continue Extension (VS Code / JetBrains / Antigravity)...")
    continue_dir = os.path.join(USER_HOME, ".continue")
    os.makedirs(continue_dir, exist_ok=True)
    config_file = os.path.join(continue_dir, "config.json")

    models_list = []
    for item in AUTO_MODELS:
        models_list.append({
            "title": item["name"],
            "provider": "openai",
            "model": item["id"],
            "apiBase": OMNIROUTE_V1,
            "apiKey": INFERENCE_KEY,
            "completionOptions": {"maxTokens": 4096, "temperature": 0.2}
        })

    try:
        merge_json(config_file, {
            "models": models_list,
            "tabAutocompleteModel": {
                "title": "OmniRoute Fast Autocomplete",
                "provider": "openai",
                "model": "auto/fast",
                "apiBase": OMNIROUTE_V1,
                "apiKey": INFERENCE_KEY
            },
            "selectedModel": model
        })
        status_msg("Continue", f"{config_file} ({len(models_list)} models injected)")
    except Exception as e:
        status_msg("Continue", str(e), ok=False)

def setup_cursor(model: str = DEFAULT_MODEL):
    print("\n[CONFIGURING] Cursor Editor...")
    path = os.path.join(APPDATA_ROAMING, "Cursor", "User", "settings.json")
    try:
        merge_json(path, {
            "cursor.general.customModels": [m["id"] for m in AUTO_MODELS],
            "cursor.openAiApiKey": INFERENCE_KEY,
            "cursor.openAiBaseUrl": OMNIROUTE_V1,
            "cursor.model": model,
        })
        status_msg("Cursor", path)
    except Exception as e:
        status_msg("Cursor", str(e), ok=False)

def setup_cline(model: str = DEFAULT_MODEL):
    print("\n[CONFIGURING] Cline (VS Code / Antigravity Extension & CLI)...")
    cline_dir = os.path.join(USER_HOME, ".cline", "data")
    os.makedirs(cline_dir, exist_ok=True)
    cline_patch = {
        "welcomeViewCompleted": True,
        "isNewUser": False,
        "apiProvider": "openai",
        "openAiBaseUrl": OMNIROUTE_HOST,
        "openAiApiKey": INFERENCE_KEY,
        "openAiModelId": model,
        "planModeApiProvider": "openai",
        "planModeOpenAiModelId": model,
        "actModeApiProvider": "openai",
        "actModeOpenAiModelId": model,
        "cline.rollout.bundle": "next",
        "mcpMarketplaceEnabled": True,
        "openAiCustomModelInfo": {
            "maxTokens": 8192,
            "contextWindow": 128000,
            "supportsImages": True,
            "supportsComputerUse": True,
            "supportsPromptCache": True
        }
    }
    try:
        merge_json(os.path.join(cline_dir, "globalState.json"), cline_patch)
        merge_json(os.path.join(cline_dir, "secrets.json"), {
            "openAiApiKey": INFERENCE_KEY
        })
        patched = patch_vscode_sqlite("saoudrizwan.claude-dev", cline_patch)
        status_msg("Cline Data", f"{cline_dir} (State + {patched} IDE DBs unlocked)")
    except Exception as e:
        status_msg("Cline Data", str(e), ok=False)

def setup_roo(model: str = DEFAULT_MODEL):
    print("\n[CONFIGURING] Roo Code (VS Code & Antigravity Extension)...")
    roo_dir = os.path.join(USER_HOME, ".roo")
    os.makedirs(roo_dir, exist_ok=True)
    roo_file = os.path.join(roo_dir, "omniroute-roo-settings.json")
    roo_patch = {
        "welcomeViewCompleted": True,
        "isNewUser": False,
        "apiProvider": "openai",
        "openAiBaseUrl": OMNIROUTE_V1,
        "openAiApiKey": INFERENCE_KEY,
        "openAiModelId": model,
        "openAiCustomModelInfo": {"maxTokens": 8192, "contextWindow": 128000, "supportsImages": True, "supportsPromptCache": True}
    }
    try:
        merge_json(roo_file, {
            "providerProfiles": {
                "currentApiConfigName": "OmniRoute",
                "apiConfigs": {
                    "OmniRoute": {
                        "apiProvider": "openai",
                        "openAiBaseUrl": OMNIROUTE_V1,
                        "openAiApiKey": INFERENCE_KEY,
                        "openAiModelId": model,
                        "openAiCustomModelInfo": {"supportsImages": True, "supportsPromptCache": True}
                    }
                }
            }
        })
        patched = patch_vscode_sqlite("RooVeterinaryInc.roo-cline", roo_patch)
        status_msg("Roo Code", f"{roo_file} ({patched} IDE DBs patched)")
    except Exception as e:
        status_msg("Roo Code", str(e), ok=False)

def setup_kilo(model: str = DEFAULT_MODEL):
    print("\n[CONFIGURING] Kilo Code Extension & CLI...")
    kilo_auth_dir = os.path.join(USER_HOME, ".local", "share", "kilo")
    os.makedirs(kilo_auth_dir, exist_ok=True)
    kilo_auth = os.path.join(kilo_auth_dir, "auth.json")
    try:
        merge_json(kilo_auth, {
            "omniroute": {
                "type": "api",
                "key": INFERENCE_KEY
            }
        })
        kilo_cfg_dir = os.path.join(USER_HOME, ".config", "kilo")
        os.makedirs(kilo_cfg_dir, exist_ok=True)
        kilo_cfg = os.path.join(kilo_cfg_dir, "config.json")
        kilo_models_dict = {}
        for item in AUTO_MODELS:
            kilo_models_dict[item["id"]] = {"name": item["name"]}
        with open(kilo_cfg, "w", encoding="utf-8") as f:
            json.dump({
                "$schema": "https://app.kilo.ai/config.json",
                "model": "omniroute/" + model,
                "small_model": "omniroute/auto/fast",
                "provider": {
                    "omniroute": {
                        "npm": "@ai-sdk/openai-compatible",
                        "name": "OmniRoute",
                        "options": {
                            "baseURL": OMNIROUTE_V1,
                            "apiKey": INFERENCE_KEY
                        },
                        "models": kilo_models_dict
                    }
                }
            }, f, indent=2)
        patch_vscode_sqlite("kilocode.kilo-code", {
            "kilo.autocomplete.defaultClearMigrationV1": True,
            "kilo.dismissedNotificationIds": ["kilo.local.opencode-config-detected"]
        })
        status_msg("Kilo Code", kilo_cfg)
    except Exception as e:
        status_msg("Kilo Code", str(e), ok=False)

def setup_claude(model: str = DEFAULT_MODEL):
    print("\n[CONFIGURING] Claude Code CLI...")
    path = os.path.join(USER_HOME, ".claude", "settings.json")
    try:
        merge_json(path, {
            "env": {
                "ANTHROPIC_BASE_URL": OMNIROUTE_V1,
                "ANTHROPIC_API_KEY":  INFERENCE_KEY,
                "ANTHROPIC_MODEL":    model,
            },
            "model": model,
            "alwaysApproveResets": True,
        })
        status_msg("Claude Code", path)
    except Exception as e:
        status_msg("Claude Code", str(e), ok=False)

def setup_codex(model: str = DEFAULT_MODEL):
    print("\n[CONFIGURING] OpenAI Codex CLI Profiles...")
    codex_dir = os.path.join(USER_HOME, ".codex")
    os.makedirs(codex_dir, exist_ok=True)
    main_toml = os.path.join(codex_dir, "config.toml")
    try:
        with open(main_toml, "w", encoding="utf-8") as f:
            f.write(
                f"# Codex CLI OmniRoute Configuration\n"
                f'api_base = "{OMNIROUTE_V1}"\n'
                f'api_key = "{INFERENCE_KEY}"\n'
                f'model = "{model}"\n'
            )
        # Generate profiles for fast, coding, cheap
        for p in ["fast", "coding", "cheap", "smart"]:
            p_file = os.path.join(codex_dir, f"{p}.config.toml")
            with open(p_file, "w", encoding="utf-8") as f:
                f.write(
                    f'api_base = "{OMNIROUTE_V1}"\n'
                    f'api_key = "{INFERENCE_KEY}"\n'
                    f'model = "auto/{p}"\n'
                )
        status_msg("Codex CLI", f"{codex_dir} (Generated profiles)")
    except Exception as e:
        status_msg("Codex CLI", str(e), ok=False)

def setup_opencode(model: str = DEFAULT_MODEL):
    print("\n[CONFIGURING] OpenCode CLI...")
    for cfg_dir in [os.path.join(USER_HOME, ".config", "opencode"), os.path.join(USER_HOME, ".opencode")]:
        os.makedirs(cfg_dir, exist_ok=True)
        path = os.path.join(cfg_dir, "config.json")
        try:
            merge_json(path, {
                "provider": {
                    "omniroute": {
                        "type": "openai",
                        "baseUrl": OMNIROUTE_V1,
                        "apiKey": INFERENCE_KEY,
                        "models": {m["id"]: {"name": m["name"]} for m in AUTO_MODELS}
                    }
                },
                "defaultModel": f"omniroute/{model}"
            })
            status_msg("OpenCode", path)
        except Exception as e:
            status_msg("OpenCode", str(e), ok=False)

def setup_goose(model: str = DEFAULT_MODEL):
    print("\n[CONFIGURING] Goose (Block AI Agent)...")
    goose_dir = os.path.join(USER_HOME, ".config", "goose")
    os.makedirs(goose_dir, exist_ok=True)
    config_file = os.path.join(goose_dir, "config.yaml")
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(
                f"# Goose OmniRoute Configuration\n"
                f"GOOSE_PROVIDER: openai\n"
                f"GOOSE_MODEL: {model}\n"
                f"OPENAI_HOST: {OMNIROUTE_HOST}\n"
                f"OPENAI_API_KEY: {INFERENCE_KEY}\n"
            )
        status_msg("Goose Agent", config_file)
    except Exception as e:
        status_msg("Goose Agent", str(e), ok=False)

def setup_crush(model: str = DEFAULT_MODEL):
    print("\n[CONFIGURING] Crush (Charm CLI AI)...")
    crush_dir = os.path.join(USER_HOME, ".config", "crush")
    os.makedirs(crush_dir, exist_ok=True)
    crush_file = os.path.join(crush_dir, "crush.json")
    try:
        merge_json(crush_file, {
            "providers": {
                "omniroute": {
                    "type": "openai-compat",
                    "base_url": OMNIROUTE_V1,
                    "api_key": INFERENCE_KEY,
                    "models": [{"id": m["id"], "name": m["name"]} for m in AUTO_MODELS]
                }
            },
            "default_provider": "omniroute",
            "default_model": model
        })
        status_msg("Crush CLI", crush_file)
    except Exception as e:
        status_msg("Crush CLI", str(e), ok=False)

def setup_qwen(model: str = DEFAULT_MODEL):
    print("\n[CONFIGURING] Qwen Code CLI...")
    qwen_dir = os.path.join(USER_HOME, ".qwen")
    os.makedirs(qwen_dir, exist_ok=True)
    try:
        merge_json(os.path.join(qwen_dir, "settings.json"), {
            "openai_api_base": OMNIROUTE_V1,
            "openai_api_key": INFERENCE_KEY,
            "model": model
        })
        with open(os.path.join(qwen_dir, ".env"), "w", encoding="utf-8") as f:
            f.write(f"OMNIROUTE_API_KEY={INFERENCE_KEY}\nOPENAI_BASE_URL={OMNIROUTE_V1}\n")
        status_msg("Qwen Code", qwen_dir)
    except Exception as e:
        status_msg("Qwen Code", str(e), ok=False)

def setup_vscode_all(model: str = DEFAULT_MODEL):
    print("\n[CONFIGURING] VS Code / VS Code Insiders / VSCodium / Windsurf...")
    custom_models = [m["id"] for m in AUTO_MODELS]
    editors = [
        ("VS Code",          os.path.join(APPDATA_ROAMING, "Code", "User", "settings.json")),
        ("VS Code Insiders", os.path.join(APPDATA_ROAMING, "Code - Insiders", "User", "settings.json")),
        ("VSCodium",         os.path.join(APPDATA_ROAMING, "VSCodium", "User", "settings.json")),
        ("Windsurf",         os.path.join(APPDATA_ROAMING, "Windsurf", "User", "settings.json")),
    ]
    for name, path in editors:
        try:
            merge_json(path, {
                "openai.apiBase": OMNIROUTE_V1,
                "openai.apiKey": INFERENCE_KEY,
                "openai.model": model,
                "cursor.general.customModels": custom_models,
                "roo-cline.autoImportSettingsPath": os.path.join(USER_HOME, ".roo", "omniroute-roo-settings.json"),
                "kilocode.openAiApiKey": INFERENCE_KEY,
                "kilocode.openAiBaseUrl": OMNIROUTE_V1,
                "kilocode.openAiModelId": model,
                "cline.openAiBaseUrl": OMNIROUTE_HOST,
                "cline.openAiApiKey": INFERENCE_KEY,
                "cline.openAiModelId": model,
            })
            status_msg(name, path)
        except Exception as e:
            status_msg(name, str(e), ok=False)

def configure_environment(model: str = DEFAULT_MODEL):
    print("\n[CONFIGURING] Windows System Environment Variables & PowerShell Profile...")
    env_vars = {
        "ANTHROPIC_BASE_URL": OMNIROUTE_V1,
        "ANTHROPIC_API_KEY":  INFERENCE_KEY,
        "OPENAI_BASE_URL":    OMNIROUTE_V1,
        "OPENAI_API_KEY":     INFERENCE_KEY,
        "OMNIROUTE_URL":      OMNIROUTE_HOST,
        "OMNIROUTE_KEY":      ADMIN_KEY,
        "OMNIROUTE_MODEL":    model,
    }
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE)
        for k, v in env_vars.items():
            winreg.SetValueEx(key, k, 0, winreg.REG_SZ, v)
        winreg.CloseKey(key)
        status_msg("Environment", "HKCU\\Environment updated")
    except Exception as e:
        status_msg("Environment", str(e), ok=False)

    ps_profile = os.path.join(USER_HOME, "Documents", "WindowsPowerShell", "Microsoft.PowerShell_profile.ps1")
    marker     = "# === OmniRoute ZeroConfig ==="
    block = (
        f"\n{marker}\n"
        f'$env:ANTHROPIC_BASE_URL = "{OMNIROUTE_V1}"\n'
        f'$env:ANTHROPIC_API_KEY  = "{INFERENCE_KEY}"\n'
        f'$env:OPENAI_BASE_URL    = "{OMNIROUTE_V1}"\n'
        f'$env:OPENAI_API_KEY     = "{INFERENCE_KEY}"\n'
        f'$env:OMNIROUTE_URL      = "{OMNIROUTE_HOST}"\n'
        f'$env:OMNIROUTE_KEY      = "{ADMIN_KEY}"\n'
        f'$env:OMNIROUTE_MODEL    = "{model}"\n'
        f"# === End OmniRoute ===\n"
    )
    try:
        os.makedirs(os.path.dirname(ps_profile), exist_ok=True)
        existing = ""
        if os.path.exists(ps_profile):
            with open(ps_profile, "r", encoding="utf-8") as f:
                existing = f.read()
        if marker not in existing:
            with open(ps_profile, "a", encoding="utf-8") as f:
                f.write(block)
        status_msg("PowerShell Profile", ps_profile)
    except Exception as e:
        status_msg("PowerShell Profile", str(e), ok=False)

def setup_all(model: str = DEFAULT_MODEL):
    print(f"\n============================================================")
    print(f"  OmniRoute Zero-Click Universal Setup (Model: {model})")
    print(f"============================================================")
    setup_antigravity(model)
    setup_aider(model)
    setup_opencode(model)
    setup_goose(model)
    setup_crush(model)
    setup_qwen(model)
    setup_kilo(model)
    setup_roo(model)
    setup_codex(model)
    setup_claude(model)
    setup_cline(model)
    setup_continue(model)
    setup_cursor(model)
    setup_vscode_all(model)
    configure_environment(model)
    print(f"\n[DONE] All 15 IDEs, Agents, & CLIs configured to use OmniRoute!")

# ── Model Diagnostics & Benchmark ────────────────────────────────────────────

def test_models():
    print("\n============================================================")
    print("  OmniRoute Live Virtual Model Benchmark & Connectivity Test")
    print("============================================================")
    print(f"{'Model ID':<22} | {'Status':<10} | {'Latency':<9} | {'Upstream Route':<26} | {'Sample Output'}")
    print("-" * 92)

    fastest_model = "auto"
    fastest_ms = 999999

    for m in AUTO_MODELS:
        mid = m["id"]
        payload = {
            "model": mid,
            "messages": [{"role": "user", "content": "respond with 'OK'"}],
            "max_tokens": 10
        }
        req = urllib.request.Request(
            f"{OMNIROUTE_V1}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {INFERENCE_KEY}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                elapsed_ms = int((time.time() - t0) * 1000)
                data = json.loads(resp.read().decode("utf-8"))
                used_model = data.get("model", "unknown")
                reply = data["choices"][0]["message"]["content"].strip().replace("\n", " ")[:20]
                print(f"{mid:<22} | SUCCESS    | {elapsed_ms:>5} ms  | {used_model:<26} | {reply}")
                if elapsed_ms < fastest_ms:
                    fastest_ms = elapsed_ms
                    fastest_model = mid
        except urllib.error.HTTPError as e:
            elapsed_ms = int((time.time() - t0) * 1000)
            print(f"{mid:<22} | HTTP {e.code}  | {elapsed_ms:>5} ms  | {'n/a':<26} | error {e.code}")
        except Exception as e:
            elapsed_ms = int((time.time() - t0) * 1000)
            print(f"{mid:<22} | TIMEOUT    | {elapsed_ms:>5} ms  | {'n/a':<26} | timed out")

    print("-" * 92)
    print(f"Optimal / Fastest Model: '{fastest_model}' ({fastest_ms} ms)")
    return fastest_model

# ── Model Selection Interface ────────────────────────────────────────────────

def select_model_menu():
    print("\n============================================================")
    print("  OmniRoute Virtual Model Selector")
    print("============================================================")
    for idx, m in enumerate(AUTO_MODELS, start=1):
        print(f"  [{idx}] {m['id']:<20} - {m['desc']}")
    print(f"  [A] AUTO-BENCHMARK      - Run live test and pick the fastest model")

    choice = input("\nSelect model [1-9, or A for auto-pick]: ").strip().upper()
    if choice == "A" or not choice:
        print("\nBenchmarking models live...")
        picked = test_models()
    else:
        try:
            num = int(choice)
            if 1 <= num <= len(AUTO_MODELS):
                picked = AUTO_MODELS[num - 1]["id"]
            else:
                picked = DEFAULT_MODEL
        except ValueError:
            picked = DEFAULT_MODEL

    print(f"\nApplying selected model '{picked}' across all agents and IDEs...")
    setup_all(picked)

# ── CLI Entrypoint ────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("OmniRoute Multi-Agent & Gateway CLI")
        print("Usage: omniroute <command> [options]\n")
        print("OmniRoute Gateway Engine Commands:")
        print("  omniroute status              - Show OmniRoute status & CLI tools")
        print("  omniroute health              - Check gateway health & uptime")
        print("  omniroute serve               - Start the OmniRoute local server")
        print("  omniroute dashboard           - Open the web dashboard in browser")
        print("  omniroute doctor              - Run OmniRoute Doctor diagnostics")
        print("  omniroute providers           - Manage provider connections")
        print("\nAgent Auto-Config Commands:")
        print("  omniroute setup-all           - Configure ALL agents zero-click")
        print("  omniroute setup-antigravity   - Configure Antigravity IDE")
        print("  omniroute setup-claude        - Configure Claude Code CLI")
        print("  omniroute setup-codex         - Configure OpenAI Codex CLI profiles")
        print("  omniroute setup-cline         - Configure Cline VS Code / Antigravity")
        print("  omniroute setup-continue      - Configure Continue extension")
        print("  omniroute setup-cursor        - Configure Cursor editor")
        print("  omniroute setup-aider         - Configure Aider")
        print("  omniroute setup-opencode      - Configure OpenCode CLI")
        print("  omniroute setup-goose         - Configure Goose (Block AI agent)")
        print("  omniroute setup-crush         - Configure Crush CLI")
        print("  omniroute setup-qwen          - Configure Qwen Code CLI")
        print("  omniroute setup-kilo          - Configure Kilo Code extension")
        print("  omniroute setup-roo           - Configure Roo Code extension")
        print("\nManagement Commands:")
        print("  omniroute test                - Test and benchmark all auto models")
        print("  omniroute select-model        - Interactive menu to pick primary model")
        print("  omniroute models              - List all available virtual models")
        print("\nRun 'omniroute --help' for full upstream engine commands.")
        return

    cmd = sys.argv[1].lower().strip()
    model = DEFAULT_MODEL
    if "--model" in sys.argv:
        idx = sys.argv.index("--model")
        if idx + 1 < len(sys.argv):
            model = sys.argv[idx + 1]

    dispatch = {
        "setup-aider": lambda: setup_aider(model),
        "setup-opencode": lambda: setup_opencode(model),
        "setup-goose": lambda: setup_goose(model),
        "setup-crush": lambda: setup_crush(model),
        "setup-qwen": lambda: setup_qwen(model),
        "setup-kilo": lambda: setup_kilo(model),
        "setup-roo": lambda: setup_roo(model),
        "setup-codex": lambda: setup_codex(model),
        "setup-claude": lambda: setup_claude(model),
        "setup-cline": lambda: setup_cline(model),
        "setup-continue": lambda: setup_continue(model),
        "setup-cursor": lambda: setup_cursor(model),
        "setup-antigravity": lambda: setup_antigravity(model),
        "setup-all": lambda: setup_all(model),
        "test": test_models,
        "select-model": select_model_menu,
        "models": lambda: [print(f" - {m['id']:<20} : {m['desc']}") for m in AUTO_MODELS],
    }

    handler = dispatch.get(cmd)
    if handler:
        handler()
    else:
        npm_cli = os.path.join(os.environ.get("APPDATA", ""), "npm", "node_modules", "omniroute", "bin", "omniroute.mjs")
        node_exe = r"C:\Program Files\nodejs\node.exe"
        if not os.path.exists(node_exe):
            node_exe = "node"
        if os.path.exists(npm_cli):
            env = os.environ.copy()
            env["PATH"] = r"C:\Program Files\nodejs;" + env.get("PATH", "")
            try:
                res = subprocess.run([node_exe, npm_cli] + sys.argv[1:], env=env)
                sys.exit(res.returncode)
            except Exception as ex:
                print(f"Failed to execute upstream OmniRoute: {ex}")
        else:
            print(f"Unknown command: '{cmd}'. Run 'omniroute' to view available commands.")

if __name__ == "__main__":
    main()
