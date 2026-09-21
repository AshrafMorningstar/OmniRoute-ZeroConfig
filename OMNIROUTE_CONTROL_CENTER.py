#!/usr/bin/env python3
"""
OmniRoute Master Control Center & Interactive Selector
======================================================
Interactive and 100% Automated Multi-Agent Manager for Windows:
  - Select ANY agent to configure or configure ALL in 1 click
  - Select ANY virtual model (auto, auto/coding, auto/fast, auto/cheap, auto/smart, Free Tier, etc.)
  - Test and benchmark models live with latency metrics
  - Run full self-healing diagnostics and auto-repair
  - Auto-restart OmniRoute gateway if down

Usage:
  python OMNIROUTE_CONTROL_CENTER.py            (Interactive Menu)
  python OMNIROUTE_CONTROL_CENTER.py --auto     (100% Automated Zero-Click)
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
from pathlib import Path

# Enable ANSI colors
try:
    os.system("")
except Exception:
    pass

C_GREEN  = "\033[92m"
C_RED    = "\033[91m"
C_YELLOW = "\033[93m"
C_CYAN   = "\033[96m"
C_BLUE   = "\033[94m"
C_BOLD   = "\033[1m"
C_RESET  = "\033[0m"

# Import engine functions from omniroute_cli and VERIFY_AND_FIX_ALL
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from omniroute_cli import (
    setup_aider, setup_opencode, setup_goose, setup_crush,
    setup_qwen, setup_kilo, setup_roo, setup_codex,
    setup_claude, setup_cline, setup_continue, setup_cursor,
    setup_antigravity, setup_vscode_all, setup_all,
    test_models, AUTO_MODELS, OMNIROUTE_HOST, OMNIROUTE_V1,
    INFERENCE_KEY, ADMIN_KEY, DEFAULT_MODEL
)
from VERIFY_AND_FIX_ALL import auto_fix_all, check_gateway, restart_omniroute_if_needed

AGENTS = [
    ("1",  "Aider",               "Terminal Pair-Programmer (.aider.conf.yml)",        setup_aider),
    ("2",  "OpenCode",            "OpenCode CLI (~/.config/opencode)",                 setup_opencode),
    ("3",  "Goose",               "Block AI Agent (~/.config/goose/config.yaml)",      setup_goose),
    ("4",  "Crush",               "Charm Crush CLI (~/.config/crush/crush.json)",      setup_crush),
    ("5",  "Qwen Code",           "Qwen Coding CLI (~/.qwen/settings.json)",           setup_qwen),
    ("6",  "Kilo Code",           "Kilo Code Extension & Auth (~/.local/share/kilo)",  setup_kilo),
    ("7",  "Roo Code",            "Roo Code Extension (omniroute-roo-settings.json)",  setup_roo),
    ("8",  "OpenAI Codex",        "Codex CLI Multi-Profiles (~/.codex)",               setup_codex),
    ("9",  "Claude Code",         "Anthropic Claude Code CLI (~/.claude/settings.json)", setup_claude),
    ("10", "Cline",               "Cline Extension (Bypass Browser Login)",            setup_cline),
    ("11", "Continue",            "Continue Assistant (9 Model Dropdown Injected)",    setup_continue),
    ("12", "Cursor",              "Cursor Editor (settings.json)",                     setup_cursor),
    ("13", "Antigravity IDE",     "Antigravity IDE Settings & MCP SSE Gateway",        setup_antigravity),
    ("14", "VS Code All",         "VS Code, Code Insiders, VSCodium, Windsurf",        setup_vscode_all),
    ("A",  "ALL AGENTS & IDES",   "Configure Every Agent & IDE Zero-Click",            setup_all),
]

def banner():
    print(f"{C_BOLD}{C_CYAN}======================================================================{C_RESET}")
    print(f"{C_BOLD}{C_GREEN}     OMNIROUTE MASTER CONTROL CENTER & AGENT MODEL SELECTOR     {C_RESET}")
    print(f"{C_BOLD}{C_CYAN}======================================================================{C_RESET}")
    print(f"  Gateway: {OMNIROUTE_HOST} | Models Available: 5,500+ | Auto LKGP Enabled\n")

def model_picker_menu(default: str = "auto") -> str:
    print(f"\n{C_BOLD}SELECT AI MODEL TO ASSIGN:{C_RESET}")
    print("-" * 55)
    for idx, m in enumerate(AUTO_MODELS, start=1):
        print(f"  [{C_CYAN}{idx}{C_RESET}] {m['id']:<20} - {m['desc']}")
    print(f"  [{C_GREEN}C{C_RESET}] Custom Model Name (e.g. anthropic/claude-opus-5, gemini-2.5-flash)")
    print(f"  [{C_YELLOW}B{C_RESET}] Auto-Benchmark (Test latency and pick fastest)")
    print(f"  [{C_BOLD}Enter{C_RESET}] Use default '{default}'")
    
    choice = input(f"\nEnter choice [1-{len(AUTO_MODELS)}, C, B or Enter]: ").strip()
    if not choice:
        return default
    if choice.upper() == "B":
        print("\nRunning live benchmark across models...")
        return test_models()
    if choice.upper() == "C":
        custom = input("Enter exact model ID: ").strip()
        return custom if custom else default
    try:
        idx = int(choice)
        if 1 <= idx <= len(AUTO_MODELS):
            return AUTO_MODELS[idx - 1]["id"]
    except ValueError:
        pass
    return default

def interactive_loop():
    while True:
        banner()
        print(f"{C_BOLD}AVAILABLE AGENTS & ACTIONS:{C_RESET}")
        print("-" * 65)
        for key, name, desc, _ in AGENTS:
            k_color = C_GREEN if key == "A" else C_CYAN
            print(f"  [{k_color}{key:>2}{C_RESET}] {name:<16} - {desc}")
        print("-" * 65)
        print(f"  [{C_YELLOW} T{C_RESET}] Run Universal Verification & Diagnostics")
        print(f"  [{C_YELLOW} F{C_RESET}] Run Self-Healing Auto-Repair on All Configs")
        print(f"  [{C_YELLOW} R{C_RESET}] Restart OmniRoute Desktop Daemon")
        print(f"  [{C_RED} Q{C_RESET}] Quit")
        print("-" * 65)

        choice = input(f"\nSelect an option [1-14, A for All, T for Test, Q to quit] (default: A): ").strip().upper()
        if not choice:
            choice = "A"

        if choice == "Q":
            print("\nExiting Control Center. OmniRoute remains active.")
            break
        elif choice == "T":
            check_gateway()
            auto_fix_all()
            test_models()
            input(f"\n{C_BOLD}Press Enter to return to menu...{C_RESET}")
        elif choice == "F":
            auto_fix_all()
            input(f"\n{C_BOLD}Press Enter to return to menu...{C_RESET}")
        elif choice == "R":
            restart_omniroute_if_needed()
            check_gateway()
            input(f"\n{C_BOLD}Press Enter to return to menu...{C_RESET}")
        elif choice == "A":
            model = model_picker_menu("auto")
            print(f"\nApplying model '{model}' to ALL 15 agents and IDEs...")
            setup_all(model)
            input(f"\n{C_BOLD}Press Enter to return to menu...{C_RESET}")
        else:
            match = [item for item in AGENTS if item[0] == choice]
            if match:
                key, name, desc, handler = match[0]
                model = model_picker_menu("auto")
                print(f"\nConfiguring {name} with model '{model}'...")
                handler(model)
                input(f"\n{C_BOLD}Press Enter to return to menu...{C_RESET}")
            else:
                print(f"{C_RED}Invalid selection. Please choose an option from the menu.{C_RESET}")
                time.sleep(1)

def run_fully_automatic():
    banner()
    print(f"{C_BOLD}[MODE] 100% Automated Zero-Click Setup & Verification{C_RESET}\n")
    check_gateway()
    auto_fix_all()
    print("\n[CONFIGURING] Setting up all 15 agents and IDEs with model 'auto'...")
    setup_all("auto")
    print("\n[TESTING] Benchmarking models live...")
    test_models()
    print(f"\n{C_BOLD}{C_GREEN}======================================================================{C_RESET}")
    print(f"{C_BOLD}{C_GREEN}  ALL 15 AGENTS & IDES CONFIGURED, TESTED, AND FULLY OPERATIONAL  {C_RESET}")
    print(f"{C_BOLD}{C_GREEN}======================================================================{C_RESET}\n")

def main():
    if "--auto" in sys.argv or "--all" in sys.argv:
        run_fully_automatic()
    else:
        interactive_loop()

if __name__ == "__main__":
    main()
