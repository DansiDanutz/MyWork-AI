# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in MyWork Framework, please report it
responsibly.

### How to Report

1. **Do NOT** open a public issue
2. Email details to the maintainer privately
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Resolution**: Depends on severity

### What Qualifies

- Exposed credentials or API keys
- Authentication bypass
- Code injection vulnerabilities
- Sensitive data exposure
- Access control issues

### What Doesn't Qualify

- Issues requiring physical access
- Social engineering
- Denial of service (unless trivially exploitable)
- Missing security headers (unless exploitable)

## Security Best Practices

### For Users

1. **Never commit `.env`**
   - Contains API keys and secrets
   - Always in `.gitignore`

2. **Never commit `.mcp.json`**
   - Contains MCP server credentials
   - Use `.mcp.json.example` as template

3. **Use environment variables**
   - All sensitive data in `.env`
   - Reference with `os.getenv()`

4. **Run security checks**

   ```bash
   python tools/mw.py doctor

```markdown

   - Checks for exposed secrets
   - Validates `.gitignore`

5. **Keep dependencies updated**

   ```bash
   python tools/mw.py update check

   ```

### For Contributors

1. **No hardcoded secrets**
   - Use environment variables
   - Document in `.env.example`

2. **Review `.gitignore`**
   - Add new sensitive file patterns
   - Test with `git status`

3. **Validate inputs**
   - Sanitize user input
   - Use parameterized queries

4. **Security in PRs**
   - Use the security checklist
   - Flag security-relevant changes

## Security Features

### Built-in Protections

- **`.gitignore`**: Comprehensive exclusions for:
  - Environment files (`.env`, `.env.*`)
  - MCP configs (`.mcp.json`)
  - Brain data (`brain_data.json`)
  - Registry data (`module_registry.json`)
  - Credentials and keys

- **Health Check**: `mw doctor` checks:
  - Exposed secrets in code
  - Missing `.gitignore` entries
  - Insecure configurations

- **Example Files**: Safe templates:
  - `.env.example` - No real keys
  - `.mcp.json.example` - No real credentials

### API Key Management

```bash

# Correct: Environment variable

ANTHROPIC_API_KEY=sk-ant-xxxxx  # In .env only

# Wrong: Hardcoded

api_key = "sk-ant-real-key"  # Never do this!

```markdown

## Disclosure Policy

We follow responsible disclosure:

1. Report received and acknowledged
2. Issue verified and assessed
3. Fix developed and tested
4. Advisory published with credit (if desired)
5. Public disclosure after fix is available

Thank you for helping keep MyWork secure!
