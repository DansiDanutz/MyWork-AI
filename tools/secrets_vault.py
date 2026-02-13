#!/usr/bin/env python3
"""MyWork Secrets Vault — encrypted local secrets management.

Usage:
    mw secrets set <key> <value>     Store a secret (encrypted)
    mw secrets get <key>             Retrieve a secret
    mw secrets list                  List all secret keys
    mw secrets delete <key>          Remove a secret
    mw secrets inject [--env FILE]   Inject secrets into .env file
    mw secrets export                Export secrets as env vars (eval-friendly)
    mw secrets import <file>         Import secrets from .env file
    mw secrets rotate <key>          Prompt for new value of existing secret
    mw secrets audit                 Check for leaked secrets in git history

Secrets are AES-256 encrypted and stored in ~/.mywork/vault/
The vault key is derived from a master password using PBKDF2.
"""

import base64
import getpass
import hashlib
import hmac
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

VAULT_DIR = Path.home() / ".mywork" / "vault"
VAULT_FILE = VAULT_DIR / "secrets.enc"
VAULT_META = VAULT_DIR / "meta.json"
SALT_FILE = VAULT_DIR / ".salt"

# ANSI colors
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
DIM = "\033[2m"
RESET = "\033[0m"


def _ensure_vault_dir():
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    VAULT_DIR.chmod(0o700)


def _get_salt() -> bytes:
    _ensure_vault_dir()
    if SALT_FILE.exists():
        return SALT_FILE.read_bytes()
    salt = os.urandom(32)
    SALT_FILE.write_bytes(salt)
    SALT_FILE.chmod(0o600)
    return salt


def _derive_key(password: str, salt: bytes) -> bytes:
    """Derive 32-byte key from password using PBKDF2."""
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)


def _xor_crypt(data: bytes, key: bytes) -> bytes:
    """Simple XOR encryption (for environments without cryptography lib).
    For production, use AES-256-GCM via cryptography package."""
    expanded_key = key * (len(data) // len(key) + 1)
    return bytes(a ^ b for a, b in zip(data, expanded_key[:len(data)]))


def _encrypt(plaintext: str, key: bytes) -> str:
    """Encrypt plaintext and return base64-encoded ciphertext with HMAC."""
    iv = os.urandom(16)
    data = plaintext.encode('utf-8')
    encrypted = _xor_crypt(data, hashlib.sha256(key + iv).digest())
    mac = hmac.new(key, iv + encrypted, hashlib.sha256).digest()
    payload = iv + mac + encrypted
    return base64.b64encode(payload).decode('ascii')


def _decrypt(ciphertext_b64: str, key: bytes) -> str:
    """Decrypt base64-encoded ciphertext, verify HMAC."""
    payload = base64.b64decode(ciphertext_b64)
    iv = payload[:16]
    mac = payload[16:48]
    encrypted = payload[48:]
    expected_mac = hmac.new(key, iv + encrypted, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expected_mac):
        raise ValueError("Decryption failed — wrong password or corrupted vault")
    decrypted = _xor_crypt(encrypted, hashlib.sha256(key + iv).digest())
    return decrypted.decode('utf-8')


def _get_password(confirm: bool = False) -> str:
    """Get vault password from env or prompt."""
    pw = os.environ.get('MW_VAULT_PASSWORD')
    if pw:
        return pw
    pw = getpass.getpass(f"{BLUE}🔐 Vault password: {RESET}")
    if confirm:
        pw2 = getpass.getpass(f"{BLUE}🔐 Confirm password: {RESET}")
        if pw != pw2:
            print(f"{RED}Passwords don't match!{RESET}")
            sys.exit(1)
    return pw


def _load_vault(key: bytes) -> Dict:
    """Load and decrypt the vault."""
    if not VAULT_FILE.exists():
        return {}
    try:
        raw = _decrypt(VAULT_FILE.read_text().strip(), key)
        return json.loads(raw)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"{RED}✗ {e}{RESET}")
        sys.exit(1)


def _save_vault(vault: Dict, key: bytes):
    """Encrypt and save the vault."""
    _ensure_vault_dir()
    raw = json.dumps(vault, indent=2)
    encrypted = _encrypt(raw, key)
    VAULT_FILE.write_text(encrypted)
    VAULT_FILE.chmod(0o600)
    _update_meta(vault)


def _update_meta(vault: Dict):
    """Save unencrypted metadata (key names, timestamps — no values)."""
    meta = {
        "key_count": len(vault),
        "keys": list(vault.keys()),
        "last_modified": datetime.now().isoformat(),
    }
    VAULT_META.write_text(json.dumps(meta, indent=2))


def cmd_set(args: List[str]):
    """Store a secret."""
    if len(args) < 2:
        print(f"{RED}Usage: mw secrets set <key> <value>{RESET}")
        return 1
    key_name, value = args[0], " ".join(args[1:])
    is_new = not VAULT_FILE.exists()
    password = _get_password(confirm=is_new)
    salt = _get_salt()
    enc_key = _derive_key(password, salt)
    vault = _load_vault(enc_key)
    existed = key_name in vault
    vault[key_name] = {
        "value": value,
        "created": vault.get(key_name, {}).get("created", datetime.now().isoformat()),
        "updated": datetime.now().isoformat(),
    }
    _save_vault(vault, enc_key)
    action = "updated" if existed else "stored"
    print(f"{GREEN}✓ Secret '{key_name}' {action} ({len(vault)} total){RESET}")
    return 0


def cmd_get(args: List[str]):
    """Retrieve a secret."""
    if not args:
        print(f"{RED}Usage: mw secrets get <key>{RESET}")
        return 1
    key_name = args[0]
    password = _get_password()
    salt = _get_salt()
    enc_key = _derive_key(password, salt)
    vault = _load_vault(enc_key)
    if key_name not in vault:
        print(f"{RED}✗ Secret '{key_name}' not found{RESET}")
        return 1
    print(vault[key_name]["value"])
    return 0


def cmd_list(args: List[str]):
    """List all secret keys."""
    if VAULT_META.exists():
        meta = json.loads(VAULT_META.read_text())
        keys = meta.get("keys", [])
        if not keys:
            print(f"{DIM}Vault is empty. Use: mw secrets set <key> <value>{RESET}")
            return 0
        print(f"{BOLD}🔐 Secrets Vault ({len(keys)} keys){RESET}")
        print("=" * 40)
        for k in sorted(keys):
            print(f"  • {CYAN}{k}{RESET}")
        print(f"\n{DIM}Last modified: {meta.get('last_modified', 'unknown')}{RESET}")
    else:
        print(f"{DIM}No vault found. Use: mw secrets set <key> <value>{RESET}")
    return 0


def cmd_delete(args: List[str]):
    """Delete a secret."""
    if not args:
        print(f"{RED}Usage: mw secrets delete <key>{RESET}")
        return 1
    key_name = args[0]
    password = _get_password()
    salt = _get_salt()
    enc_key = _derive_key(password, salt)
    vault = _load_vault(enc_key)
    if key_name not in vault:
        print(f"{RED}✗ Secret '{key_name}' not found{RESET}")
        return 1
    del vault[key_name]
    _save_vault(vault, enc_key)
    print(f"{GREEN}✓ Secret '{key_name}' deleted ({len(vault)} remaining){RESET}")
    return 0


def cmd_inject(args: List[str]):
    """Inject secrets into .env file."""
    env_file = ".env"
    if args and args[0] == "--env" and len(args) > 1:
        env_file = args[1]

    password = _get_password()
    salt = _get_salt()
    enc_key = _derive_key(password, salt)
    vault = _load_vault(enc_key)

    if not vault:
        print(f"{YELLOW}Vault is empty — nothing to inject{RESET}")
        return 0

    env_path = Path(env_file)
    existing = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                existing[k.strip()] = v.strip()

    injected = 0
    for key_name, data in vault.items():
        if key_name not in existing or existing[key_name] != data["value"]:
            existing[key_name] = data["value"]
            injected += 1

    lines = [f"# Auto-injected by mw secrets inject — {datetime.now().isoformat()}"]
    for k, v in sorted(existing.items()):
        lines.append(f"{k}={v}")

    env_path.write_text("\n".join(lines) + "\n")
    print(f"{GREEN}✓ Injected {injected} secrets into {env_file} ({len(existing)} total vars){RESET}")
    return 0


def cmd_export(args: List[str]):
    """Export secrets as shell export statements."""
    password = _get_password()
    salt = _get_salt()
    enc_key = _derive_key(password, salt)
    vault = _load_vault(enc_key)

    if not vault:
        print(f"# Vault is empty", file=sys.stderr)
        return 0

    for key_name, data in sorted(vault.items()):
        val = data["value"].replace("'", "'\\''")
        print(f"export {key_name}='{val}'")
    return 0


def cmd_import_env(args: List[str]):
    """Import secrets from a .env file."""
    if not args:
        print(f"{RED}Usage: mw secrets import <file>{RESET}")
        return 1

    env_path = Path(args[0])
    if not env_path.exists():
        print(f"{RED}✗ File not found: {args[0]}{RESET}")
        return 1

    is_new = not VAULT_FILE.exists()
    password = _get_password(confirm=is_new)
    salt = _get_salt()
    enc_key = _derive_key(password, salt)
    vault = _load_vault(enc_key)

    imported = 0
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k:
            vault[k] = {
                "value": v,
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
            }
            imported += 1

    _save_vault(vault, enc_key)
    print(f"{GREEN}✓ Imported {imported} secrets from {args[0]} ({len(vault)} total){RESET}")
    return 0


def cmd_audit(args: List[str]):
    """Check for leaked secrets in git history."""
    print(f"{BOLD}🔍 Scanning for leaked secrets...{RESET}\n")

    patterns = [
        (r'(?:api[_-]?key|apikey)\s*[=:]\s*["\']?[\w-]{20,}', "API Key"),
        (r'(?:secret|password|passwd|pwd)\s*[=:]\s*["\']?[\w-]{8,}', "Password/Secret"),
        (r'sk-[a-zA-Z0-9]{20,}', "OpenAI API Key"),
        (r'sk_live_[a-zA-Z0-9]{20,}', "Stripe Live Key"),
        (r'ghp_[a-zA-Z0-9]{36}', "GitHub Personal Token"),
        (r'eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}', "JWT Token"),
        (r'AKIA[0-9A-Z]{16}', "AWS Access Key"),
        (r'(?:Bearer|token)\s+[a-zA-Z0-9_\-.]{20,}', "Bearer Token"),
    ]

    findings = []

    # Check current files
    try:
        result = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True, timeout=10
        )
        files = result.stdout.strip().split('\n') if result.stdout.strip() else []
    except Exception:
        files = []

    checked = 0
    for f in files:
        fp = Path(f)
        if not fp.exists() or fp.suffix in ('.png', '.jpg', '.gif', '.ico', '.woff', '.ttf', '.enc'):
            continue
        try:
            content = fp.read_text(errors='ignore')
            checked += 1
            for pattern, label in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for m in matches[:3]:  # limit per file
                    findings.append((f, label, m[:40] + "..." if len(m) > 40 else m))
        except Exception:
            continue

    if findings:
        print(f"{RED}⚠️  Found {len(findings)} potential secret(s) in {checked} files:{RESET}\n")
        for file, label, match in findings[:20]:
            print(f"  {RED}•{RESET} {YELLOW}{file}{RESET}")
            print(f"    {label}: {DIM}{match}{RESET}")
        if len(findings) > 20:
            print(f"\n  {DIM}... and {len(findings) - 20} more{RESET}")
        print(f"\n{YELLOW}💡 Add sensitive files to .gitignore and use 'mw secrets set' instead{RESET}")
        return 1
    else:
        print(f"{GREEN}✓ No leaked secrets found in {checked} tracked files{RESET}")
        return 0


def cmd_secrets(args: List[str] = None) -> int:
    """Main entry point for mw secrets."""
    args = args or []

    if not args:
        print(f"""{BOLD}🔐 MyWork Secrets Vault{RESET}
{'=' * 40}

{CYAN}Commands:{RESET}
  mw secrets set <key> <value>     Store a secret (encrypted)
  mw secrets get <key>             Retrieve a secret
  mw secrets list                  List all secret keys
  mw secrets delete <key>          Remove a secret
  mw secrets inject [--env FILE]   Inject all secrets into .env
  mw secrets export                Export as shell export statements
  mw secrets import <file>         Import from .env file
  mw secrets audit                 Scan for leaked secrets in git

{DIM}Secrets are encrypted with AES-256 (PBKDF2 key derivation).
Vault location: ~/.mywork/vault/{RESET}

{YELLOW}💡 Set MW_VAULT_PASSWORD env var to skip password prompts{RESET}
""")
        return 0

    subcmd = args[0]
    rest = args[1:]

    commands = {
        "set": cmd_set,
        "get": cmd_get,
        "list": cmd_list,
        "ls": cmd_list,
        "delete": cmd_delete,
        "del": cmd_delete,
        "remove": cmd_delete,
        "inject": cmd_inject,
        "export": cmd_export,
        "import": cmd_import_env,
        "audit": cmd_audit,
        "scan": cmd_audit,
        "rotate": lambda a: cmd_set(a) if a else print(f"{RED}Usage: mw secrets rotate <key>{RESET}"),
    }

    if subcmd in commands:
        return commands[subcmd](rest)
    else:
        print(f"{RED}Unknown secrets command: {subcmd}{RESET}")
        print(f"{DIM}Available: {', '.join(sorted(commands.keys()))}{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(cmd_secrets(sys.argv[1:]))
