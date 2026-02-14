# PyPI Publishing Setup

## Required GitHub Secrets

To enable automatic publishing to PyPI when version tags are pushed, add the following secret to this repository:

### PYPI_TOKEN
1. Go to https://pypi.org/manage/account/token/
2. Create a new API token with "Entire account" scope
3. Copy the token (starts with `pypi-`)
4. Add it to GitHub repository secrets:
   - Go to: Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_TOKEN`
   - Value: [paste the token here]

## Publishing Process

Once the secret is configured:

1. Push a version tag: `git tag v1.2.3 && git push origin v1.2.3`
2. GitHub Actions will automatically:
   - Run tests
   - Build the package
   - Publish to PyPI

## Workflows

- `.github/workflows/ci.yml` - Runs on every push/PR (tests, linting, security)
- `.github/workflows/publish.yml` - Runs on version tags (PyPI publishing)
- `.github/workflows/release.yml` - Creates GitHub releases with changelog