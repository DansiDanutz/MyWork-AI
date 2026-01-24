#!/usr/bin/env python3
"""
LLM Provider Switcher for Autocoder
Switches between configured LLM providers in Autocoder's .env file.

Usage:
    python switch_llm_provider.py [provider]

Providers:
    zai       - Z.ai GLM-4.7 (cost-effective, default)
    claude    - Native Claude (highest quality)
    openrouter - OpenRouter (100+ models, built-in fallback)
    groq      - Groq (ultra-fast)

Example:
    python switch_llm_provider.py openrouter
"""

import os
import sys
import re
from pathlib import Path

# Load environment variables from master .env (without requiring dotenv)
MYWORK_ROOT = Path("/Users/dansidanutz/Desktop/MyWork")

def load_env_file(env_path: Path):
    """Load environment variables from a .env file."""
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and value:
                    os.environ.setdefault(key, value)

load_env_file(MYWORK_ROOT / ".env")

AUTOCODER_ENV = Path.home() / "Desktop/GamesAI/autocoder/.env"

# Get API keys from environment (SECURE - no hardcoded secrets)
def get_env_key(key: str, default: str = "") -> str:
    """Get API key from environment."""
    return os.getenv(key, default)

# Provider configurations - API keys read from environment
PROVIDERS = {
    "zai": {
        "name": "Z.ai (GLM-4.7)",
        "vars": {
            "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
            "ANTHROPIC_AUTH_TOKEN": "${ZAI_API_KEY}",  # Read from env
            "API_TIMEOUT_MS": "3000000",
            "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-4.7",
            "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-4.7",
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-4.5-air",
        },
        "env_key": "ZAI_API_KEY",
    },
    "claude": {
        "name": "Claude Native",
        "vars": {},  # Empty = use Claude subscription
        "env_key": "ANTHROPIC_API_KEY",
    },
    "openrouter": {
        "name": "OpenRouter",
        "vars": {
            "ANTHROPIC_BASE_URL": "https://openrouter.ai/api/v1",
            "ANTHROPIC_AUTH_TOKEN": "${OPENROUTER_API_KEY}",  # Read from env
            "API_TIMEOUT_MS": "3000000",
            "ANTHROPIC_DEFAULT_OPUS_MODEL": "anthropic/claude-3-opus",
            "ANTHROPIC_DEFAULT_SONNET_MODEL": "anthropic/claude-3.5-sonnet",
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": "anthropic/claude-3-haiku",
        },
        "env_key": "OPENROUTER_API_KEY",
    },
    "groq": {
        "name": "Groq",
        "vars": {
            "ANTHROPIC_BASE_URL": "https://api.groq.com/openai/v1",
            "ANTHROPIC_AUTH_TOKEN": "${GROQ_API_KEY}",  # Read from env
            "API_TIMEOUT_MS": "300000",
            "ANTHROPIC_DEFAULT_OPUS_MODEL": "llama-3.1-70b-versatile",
            "ANTHROPIC_DEFAULT_SONNET_MODEL": "llama-3.1-70b-versatile",
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": "llama-3.1-8b-instant",
        },
        "env_key": "GROQ_API_KEY",
    },
}

# Variables to manage (comment/uncomment)
MANAGED_VARS = [
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_AUTH_TOKEN",
    "API_TIMEOUT_MS",
    "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL",
]


def read_env() -> str:
    """Read the current .env file."""
    return AUTOCODER_ENV.read_text()


def write_env(content: str):
    """Write the .env file."""
    AUTOCODER_ENV.write_text(content)


def get_current_provider(content: str) -> str:
    """Detect current active provider."""
    base_url_match = re.search(r'^ANTHROPIC_BASE_URL=(.+)$', content, re.MULTILINE)
    if not base_url_match:
        return "claude"

    url = base_url_match.group(1)
    if "z.ai" in url:
        return "zai"
    elif "openrouter" in url:
        return "openrouter"
    elif "groq" in url:
        return "groq"
    elif "deepseek" in url:
        return "deepseek"
    return "unknown"


def resolve_env_vars(vars_dict: dict) -> dict:
    """Resolve ${VAR_NAME} placeholders with actual environment values."""
    resolved = {}
    for key, value in vars_dict.items():
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_key = value[2:-1]
            env_value = os.getenv(env_key)
            if not env_value:
                print(f"⚠️  Warning: {env_key} not found in environment")
                print(f"   Add it to {MYWORK_ROOT}/.env")
                return None
            resolved[key] = env_value
        else:
            resolved[key] = value
    return resolved


def switch_provider(target: str):
    """Switch to the target provider."""
    if target not in PROVIDERS:
        print(f"Unknown provider: {target}")
        print(f"Available: {', '.join(PROVIDERS.keys())}")
        sys.exit(1)

    content = read_env()
    current = get_current_provider(content)

    if current == target:
        print(f"Already using {PROVIDERS[target]['name']}")
        return

    # Resolve environment variables for the target provider
    provider_config = PROVIDERS[target]
    if provider_config["vars"]:
        resolved_vars = resolve_env_vars(provider_config["vars"])
        if resolved_vars is None:
            print(f"❌ Cannot switch - missing API key")
            sys.exit(1)
    else:
        resolved_vars = {}

    print(f"Switching from {PROVIDERS.get(current, {}).get('name', current)} to {PROVIDERS[target]['name']}...")

    # Comment out all managed variables first
    for var in MANAGED_VARS:
        # Comment out active lines
        content = re.sub(
            rf'^({var}=.*)$',
            r'# \1',
            content,
            flags=re.MULTILINE
        )

    # If target has vars, add/uncomment them
    if resolved_vars:
        # Find the Z.ai section and add new active vars after the header
        lines = content.split('\n')
        new_lines = []
        in_zai_section = False
        vars_added = False

        for line in lines:
            new_lines.append(line)

            # After Z.ai header, insert new active vars
            if "PROVIDER: Z.ai" in line and not vars_added:
                in_zai_section = True
            elif in_zai_section and line.startswith("# ---") and not vars_added:
                # Insert active vars before this line
                new_lines.pop()  # Remove the separator we just added
                for var, value in resolved_vars.items():
                    new_lines.append(f"{var}={value}")
                new_lines.append("")
                new_lines.append(line)  # Re-add the separator
                vars_added = True
                in_zai_section = False

        content = '\n'.join(new_lines)

    write_env(content)
    print(f"✅ Switched to {PROVIDERS[target]['name']}")
    print(f"   Restart Autocoder to apply changes.")


def list_providers():
    """List all available providers and current status."""
    content = read_env()
    current = get_current_provider(content)

    print("LLM Providers for Autocoder:")
    print("-" * 40)
    for key, info in PROVIDERS.items():
        status = "✅ ACTIVE" if key == current else "  "
        print(f"  {status} {key:12} - {info['name']}")
    print("-" * 40)
    print(f"\nUsage: python {sys.argv[0]} <provider>")


def main():
    if len(sys.argv) < 2:
        list_providers()
        return

    target = sys.argv[1].lower()
    if target in ("list", "-l", "--list"):
        list_providers()
    elif target in ("help", "-h", "--help"):
        print(__doc__)
    else:
        switch_provider(target)


if __name__ == "__main__":
    main()
