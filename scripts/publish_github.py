#!/usr/bin/env python3
"""
OmniRoute ZeroConfig :: Automated GitHub Publisher
==================================================
Initializes git repo, creates remote on GitHub (AshrafMorningstar),
and pushes all files automatically.
"""

import sys
import os
import json
import subprocess
import urllib.request
import urllib.error
import argparse

DEFAULT_TOKEN    = os.environ.get("GITHUB_TOKEN", "")
REPO_NAME        = "OmniRoute-ZeroConfig"
REPO_DESCRIPTION = "Universal Zero-Config AI Gateway & Model Selector for all IDEs & coding agents with auto-failover across 20+ LLM providers."
REPO_TOPICS      = [
    "omniroute", "ai-gateway", "failover", "zero-config",
    "vscode", "cursor", "windsurf", "continue-dev", "cline",
    "claude-code", "aider", "llm-routing", "antigravity"
]
GITHUB_API       = "https://api.github.com"

def api_call(token: str, method: str, path: str, data: dict = None):
    url = f"{GITHUB_API}{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "OmniRoute-ZeroConfig/1.0",
    }
    body = json.dumps(data).encode() if data else None
    req  = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body
    except Exception as e:
        return 500, str(e)

def main():
    parser = argparse.ArgumentParser(description="Publish OmniRoute ZeroConfig to GitHub")
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="GitHub Personal Access Token")
    parser.add_argument("--username", default="AshrafMorningstar", help="GitHub username")
    args = parser.parse_args()

    token = args.token
    print("[1/5] Authenticating with GitHub...")
    code, user = api_call(token, "GET", "/user")
    if code != 200:
        print(f"[ERROR] GitHub auth failed (HTTP {code}): {user}")
        sys.exit(1)
    username = args.username or user.get("login", "")
    print(f"  Logged in as: {username}")

    print(f"\n[2/5] Creating GitHub repository '{REPO_NAME}'...")
    code, resp = api_call(token, "POST", "/user/repos", {
        "name":        REPO_NAME,
        "description": REPO_DESCRIPTION,
        "private":     False,
        "auto_init":   False,
        "has_issues":  True,
        "has_wiki":    False,
    })
    if code == 201:
        print(f"  Repository created: https://github.com/{username}/{REPO_NAME}")
    elif code == 422:
        print(f"  Repository already exists, syncing to existing repo.")
    else:
        print(f"  Repo status: HTTP {code}")

    print(f"\n[3/5] Setting SEO topics...")
    api_call(token, "PUT", f"/repos/{username}/{REPO_NAME}/topics", {"names": REPO_TOPICS})

    print(f"\n[4/5] Initializing Git & Pushing...")
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def run_git(cmd):
        res = subprocess.run(["git"] + cmd, cwd=repo_root, capture_output=True, text=True, shell=True)
        return res

    run_git(["init"])
    run_git(["config", "user.name", "Ashraf Morningstar"])
    run_git(["config", "user.email", "ashrafmorningstar@gmail.com"])
    run_git(["add", "."])
    run_git(["commit", "-m", "Initial commit: Universal Zero-Config OmniRoute IDE Integrator"])
    run_git(["branch", "-M", "main"])

    remote_url = f"https://{token}@github.com/{username}/{REPO_NAME}.git"
    run_git(["remote", "remove", "origin"])
    run_git(["remote", "add", "origin", remote_url])

    push_res = run_git(["push", "-u", "origin", "main", "--force"])
    if push_res.returncode == 0:
        print("  Pushed successfully to GitHub!")
    else:
        print(f"  Push output: {push_res.stderr.strip()}")

    print("\n[5/5] Done!")
    print(f"Live GitHub Repository: https://github.com/{username}/{REPO_NAME}")

if __name__ == "__main__":
    main()
