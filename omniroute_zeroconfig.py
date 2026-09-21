#!/usr/bin/env python3
"""
OmniRoute-ZeroConfig :: Universal Auto-Model Selector & IDE Integrator
======================================================================
Zero-click automatic configuration of all IDEs and AI coding agents to route
through local OmniRoute gateway (http://127.0.0.1:20128/v1).

Supported Models (Zero-Config Virtual Scoring):
  * auto            - Balanced default (LKGP - sticks to last good provider)
  * auto/fast       - Lowest latency first (Anthropic / Groq / Flash)
  * auto/cheap      - Cheapest per token first
  * auto/smart      - Quality-first + 10% exploration
  * auto/coding     - Quality-first code generation
  * auto/lkgp       - Explicit last-known-good-provider stickiness
  * Coding Failover - Priority failover chain
  * Free Tier Only  - Zero-cost community & free tiers
"""

import os
import sys
import json
import shutil
import urllib.request
import urllib.error
import subprocess
import argparse
from typing import Dict, List, Any, Optional

# ── Configuration Constants ──────────────────────────────────────────────────
OMNIROUTE_HOST  = os.environ.get("OMNIROUTE_URL", "http://127.0.0.1:20128")
OMNIROUTE_V1    = f"{OMNIROUTE_HOST}/v1"
ADMIN_KEY       = os.environ.get("OMNIROUTE_KEY", "sk-3a0b09e07366b474-63292a-294d391c")
INFERENCE_KEY   = os.environ.get("OPENAI_API_KEY", "sk-3a0b09e07366b474-358946-ff6459d4")
DEFAULT_MODEL   = "auto"

ROAMING   = os.environ.get("APPDATA", r"C:\Users\Admin\AppData\Roaming")
USER_HOME = os.environ.get("USERPROFILE", r"C:\Users\Admin")

AUTO_MODELS_CATALOG = [
    {"id": "auto",            "name": "OmniRoute Auto (Balanced LKGP)",     "desc": "Balanced default; sticks to last good provider"},
    {"id": "auto/fast",       "name": "OmniRoute Auto Fast",               "desc": "Lowest latency first for instant code completion"},
    {"id": "auto/coding",     "name": "OmniRoute Auto Coding",             "desc": "Quality-first weights for deep code generation"},
    {"id": "auto/cheap",      "name": "OmniRoute Auto Cheap",              "desc": "Cheapest per token first"},
    {"id": "auto/smart",      "name": "OmniRoute Auto Smart",              "desc": "Quality-first + 10% model exploration"},
    {"id": "auto/lkgp",       "name": "OmniRoute Auto LKGP",               "desc": "Explicit last-known-good-provider stickiness"},
    {"id": "Free Tier Only",  "name": "OmniRoute Free Tier Only",          "desc": "High-speed free tier failover"},
    {"id": "Coding Failover", "name": "OmniRoute Coding Failover",         "desc": "Full cascading failover across all keys"},
]

RESULTS = []

def log(tag: str, label: str, message: str, ok: bool = True):
    symbol = "[OK] " if ok else "[ERR]"
    print(f"  {symbol} [{label}] {message}", flush=True)
    RESULTS.append({"tag": tag, "label": label, "message": message, "ok": ok})

def merge_json(file_path: str, new_data: dict):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    data = {}
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    for k, v in new_data.items():
        if isinstance(v, dict) and isinstance(data.get(k), dict):
            data[k].update(v)
        else:
            data[k] = v
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ── 1. Configure VS Code Variants & Cursor & Windsurf ───────────────────────
def configure_editors(selected_model: str = DEFAULT_MODEL):
    print(f"\n[1/7] Configuring Code Editors with model '{selected_model}'...")
    editors = [
        ("VS Code",          os.path.join(ROAMING, "Code",             "User", "settings.json")),
        ("VS Code Insiders", os.path.join(ROAMING, "Code - Insiders",  "User", "settings.json")),
        ("VSCodium",         os.path.join(ROAMING, "VSCodium",         "User", "settings.json")),
        ("Cursor",           os.path.join(ROAMING, "Cursor",           "User", "settings.json")),
        ("Windsurf",         os.path.join(ROAMING, "Windsurf",         "User", "settings.json")),
    ]

    custom_models_list = [m["id"] for m in AUTO_MODELS_CATALOG]

    settings_payload = {
        "openai.apiBase":                     OMNIROUTE_V1,
        "openai.apiKey":                      INFERENCE_KEY,
        "openai.model":                       selected_model,
        "cursor.general.customModels":        custom_models_list,
        "cursor.openAiApiKey":                INFERENCE_KEY,
        "cursor.openAiBaseUrl":               OMNIROUTE_V1,
        "cursor.model":                       selected_model,
        "windsurf.openAiApiKey":              INFERENCE_KEY,
        "windsurf.openAiBaseUrl":             OMNIROUTE_V1,
        "github.copilot.advanced": {
            "debug.overrideEngine":           selected_model,
            "debug.overrideProxyUrl":         OMNIROUTE_V1,
        }
    }

    for name, path in editors:
        try:
            merge_json(path, settings_payload)
            log("EDITOR", name, path, ok=True)
        except Exception as e:
            log("EDITOR", name, f"{path} ({e})", ok=False)

# ── 2. Configure Continue Extension (Shows models in UI dropdown!) ──────────
def configure_continue(selected_model: str = DEFAULT_MODEL):
    print("\n[2/7] Configuring Continue Extension (Injected Model Dropdowns)...")
    continue_dir = os.path.join(USER_HOME, ".continue")
    config_file  = os.path.join(continue_dir, "config.json")
    os.makedirs(continue_dir, exist_ok=True)

    continue_models = []
    for item in AUTO_MODELS_CATALOG:
        continue_models.append({
            "title": item["name"],
            "provider": "openai",
            "model": item["id"],
            "apiBase": OMNIROUTE_V1,
            "apiKey": INFERENCE_KEY,
            "completionOptions": {
                "maxTokens": 4096,
                "temperature": 0.2
            }
        })

    config_data = {
        "models": continue_models,
        "tabAutocompleteModel": {
            "title": "OmniRoute Fast Autocomplete",
            "provider": "openai",
            "model": "auto/fast",
            "apiBase": OMNIROUTE_V1,
            "apiKey": INFERENCE_KEY
        },
        "selectedModel": selected_model
    }

    try:
        merge_json(config_file, config_data)
        log("CONTINUE", "Continue Extension", f"{config_file} (Registered {len(continue_models)} UI models)", ok=True)
    except Exception as e:
        log("CONTINUE", "Continue Extension", f"{config_file} ({e})", ok=False)

# ── 3. Configure Claude Code CLI ────────────────────────────────────────────
def configure_claude_code(selected_model: str = DEFAULT_MODEL):
    print(f"\n[3/7] Configuring Claude Code CLI (Model: {selected_model})...")
    path = os.path.join(USER_HOME, ".claude", "settings.json")
    try:
        merge_json(path, {
            "env": {
                "ANTHROPIC_BASE_URL": OMNIROUTE_V1,
                "ANTHROPIC_API_KEY":  INFERENCE_KEY,
                "ANTHROPIC_MODEL":    selected_model,
            },
            "model":              selected_model,
            "alwaysApproveResets": True,
        })
        log("AGENT", "Claude Code", path, ok=True)
    except Exception as e:
        log("AGENT", "Claude Code", f"{path} ({e})", ok=False)

# ── 4. Configure Aider ───────────────────────────────────────────────────────
def configure_aider(selected_model: str = DEFAULT_MODEL):
    print("\n[4/7] Configuring Aider...")
    path = os.path.join(USER_HOME, ".aider.conf.yml")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(
                f"# Aider Configuration - OmniRoute ZeroConfig\n"
                f"openai-api-base:    {OMNIROUTE_V1}\n"
                f"openai-api-key:     {INFERENCE_KEY}\n"
                f"anthropic-api-key:  {INFERENCE_KEY}\n"
                f"model:              openai/{selected_model}\n"
                f"editor-model:       openai/auto/fast\n"
                f"weak-model:         openai/auto/cheap\n"
                f"auto-commits:       false\n"
            )
        log("AGENT", "Aider", path, ok=True)
    except Exception as e:
        log("AGENT", "Aider", f"{path} ({e})", ok=False)

# ── 5. Configure Antigravity IDE MCP ────────────────────────────────────────
def configure_antigravity():
    print("\n[5/7] Configuring Antigravity IDE MCP Connection...")
    path = os.path.join(USER_HOME, ".gemini", "config", "mcp_config.json")
    try:
        merge_json(path, {
            "mcpServers": {
                "omniroute": {
                    "serverUrl": f"{OMNIROUTE_HOST}/api/mcp/sse",
                    "headers": {"Authorization": f"Bearer {ADMIN_KEY}"},
                }
            }
        })
        log("AGENT", "Antigravity IDE (MCP)", path, ok=True)
    except Exception as e:
        log("AGENT", "Antigravity IDE", f"{path} ({e})", ok=False)

# ── 6. Configure Windows Environment & PowerShell Profile ───────────────────
def configure_environment(selected_model: str = DEFAULT_MODEL):
    print("\n[6/7] Setting Persistent System Environment Variables...")
    env_vars = {
        "ANTHROPIC_BASE_URL": OMNIROUTE_V1,
        "ANTHROPIC_API_KEY":  INFERENCE_KEY,
        "OPENAI_BASE_URL":    OMNIROUTE_V1,
        "OPENAI_API_KEY":     INFERENCE_KEY,
        "OMNIROUTE_URL":      OMNIROUTE_HOST,
        "OMNIROUTE_KEY":      ADMIN_KEY,
        "OMNIROUTE_MODEL":    selected_model,
    }
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE)
        for k, v in env_vars.items():
            winreg.SetValueEx(key, k, 0, winreg.REG_SZ, v)
            log("ENV", k, v[:40] + ("..." if len(v) > 40 else ""), ok=True)
        winreg.CloseKey(key)
    except Exception as e:
        for k, v in env_vars.items():
            try:
                subprocess.run(["setx", k, v], capture_output=True, text=True, timeout=10)
                log("ENV", k, v[:40] + ("..." if len(v) > 40 else ""), ok=True)
            except Exception as ex:
                log("ENV", k, str(ex), ok=False)

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
        f'$env:OMNIROUTE_MODEL    = "{selected_model}"\n'
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
        log("PROFILE", "PowerShell Profile", ps_profile, ok=True)
    except Exception as e:
        log("PROFILE", "PowerShell Profile", str(e), ok=False)

# ── 7. Diagnostic Testing Suite ──────────────────────────────────────────────
def run_diagnostic_tests():
    print("\n[7/7] Executing Live OmniRoute Virtual Model Benchmark...")
    print(f"{'Model / Variant':<22} | {'Status':<10} | {'Latency':<9} | {'Upstream Route':<28} | {'Reply Sample'}")
    print("-" * 95)

    test_models = [
        "auto",
        "auto/fast",
        "auto/cheap",
        "auto/smart",
        "auto/lkgp",
        "Coding Failover",
        "Fast Auto Failover",
        "Free Tier Only"
    ]

    import time

    best_model = "auto"
    best_latency = 999999

    for model_id in test_models:
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": "Return 'OK'"}],
            "max_tokens": 15
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
            with urllib.request.urlopen(req, timeout=15) as resp:
                elapsed_ms = int((time.time() - t0) * 1000)
                data = json.loads(resp.read().decode("utf-8"))
                used_model = data.get("model", "unknown")
                reply = data["choices"][0]["message"]["content"].strip().replace("\n", " ")[:25]
                print(f"{model_id:<22} | SUCCESS    | {elapsed_ms:>5} ms  | {used_model:<28} | {reply}")
                if elapsed_ms < best_latency:
                    best_latency = elapsed_ms
                    best_model = model_id
        except urllib.error.HTTPError as e:
            elapsed_ms = int((time.time() - t0) * 1000)
            err_text = e.read().decode("utf-8", errors="ignore")
            print(f"{model_id:<22} | HTTP {e.code}  | {elapsed_ms:>5} ms  | {'n/a':<28} | {err_text[:25]}")
        except Exception as e:
            elapsed_ms = int((time.time() - t0) * 1000)
            print(f"{model_id:<22} | TIMEOUT/ERR| {elapsed_ms:>5} ms  | {'n/a':<28} | {str(e)[:25]}")

    print("-" * 95)
    print(f"  Fastest Responsive Model: '{best_model}' ({best_latency} ms)")
    return best_model

# ── Main Entrypoint ──────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="OmniRoute ZeroConfig Universal Integrator")
    parser.add_argument("--auto", action="store_true", help="Run full automated zero-click setup with fastest model")
    parser.add_argument("--test", action="store_true", help="Run diagnostic benchmark tests only")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Specify preferred model (default: auto)")
    args = parser.parse_args()

    print("=" * 65)
    print("   OmniRoute ZeroConfig :: Universal Agent & IDE Integrator")
    print("   Zero-Click Model Routing · Dropdown Ingestion · All IDEs")
    print("=" * 65)

    if args.test:
        run_diagnostic_tests()
        return

    selected_model = args.model
    if args.auto:
        print("\n[AUTO-DISCOVERY] Running pre-flight benchmark to pick optimal model...")
        fastest = run_diagnostic_tests()
        if fastest:
            selected_model = fastest
        print(f"\n[AUTO-DISCOVERY] Selected optimal model: '{selected_model}'")

    configure_editors(selected_model)
    configure_continue(selected_model)
    configure_claude_code(selected_model)
    configure_aider(selected_model)
    configure_antigravity()
    configure_environment(selected_model)

    print("\n" + "=" * 65)
    ok_count = sum(1 for r in RESULTS if r["ok"])
    print(f"[DONE] {ok_count} components configured successfully!")
    print(f"Active Primary Model: {selected_model}")
    print("All models are now selectable in Continue, Cursor, Windsurf, & VS Code.")
    print("=" * 65)

if __name__ == "__main__":
    main()
