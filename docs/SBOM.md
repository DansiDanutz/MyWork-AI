# Software Bill of Materials (SBOM)

MyWork-AI includes comprehensive SBOM (Software Bill of Materials) generation capabilities for supply chain security and compliance.

## What is an SBOM?

A Software Bill of Materials (SBOM) is a formal, machine-readable inventory of all components, libraries, and dependencies in your software. It provides:

- **Transparency**: Full visibility into all dependencies and their versions
- **Security**: Enables vulnerability scanning and dependency management
- **Compliance**: Helps meet regulatory requirements (NIST, FDA, etc.)
- **License Management**: Track all software licenses in use

## Supported Formats

MyWork-AI supports industry-standard SBOM formats:

### CycloneDX JSON (v1.4)
- Industry standard for software supply chain security
- Supported by major security tools and platforms
- Includes comprehensive component metadata

### SPDX JSON (v2.3)
- Software Package Data Exchange standard
- Widely used for license compliance
- Provides detailed license information

### Human-Readable Summary
- Easy-to-read text format
- Groups dependencies by license
- Includes git commit and version information

## Usage

### Generate a Human-Readable SBOM
```bash
mw sbom
```

Output includes:
- MyWork-AI version
- Git commit, branch, and tag
- Total dependency count
- Dependencies grouped by license
- License summary

### Generate CycloneDX JSON
```bash
mw sbom --format json
mw sbom --format json --output sbom.json
```

### Generate SPDX JSON
```bash
mw sbom --format spdx
mw sbom --format spdx --output sbom-spdx.json
```

### Generate All Formats
```bash
mw sbom --format all
mw sbom --format all --output sbom.json  # Produces sbom.json, sbom-spdx.json, sbom.txt
```

## GitHub Actions Integration

MyWork-AI automatically generates SBOMs on:

- **Every push to main**: Ensures SBOM is always current
- **Pull requests**: Validates SBOM changes
- **Releases**: Attaches SBOM artifacts to releases

Generated SBOMs are:
1. Uploaded as workflow artifacts (retained for 90 days)
2. Attached to GitHub releases
3. Available for download from the Actions tab

## SBOM Contents

The SBOM includes:

- **MyWork-AI metadata**: Version, git commit, branch, tag
- **All dependencies**: Every Python package in the environment
- **License information**: For each dependency
- **Package URLs (purl)**: Standardized dependency identifiers
- **External references**: Homepage URLs, documentation links

## Security Benefits

### Vulnerability Management
- Export SBOM to vulnerability scanners (e.g., OWASP Dependency-Check)
- Track vulnerable dependencies across all versions
- Automated security scanning in CI/CD pipelines

### License Compliance
- Identify all licenses in use
- Flag copyleft licenses (GPL, AGPL)
- Ensure license policy compliance

### Supply Chain Transparency
- Know exactly what code is in your software
- Trace dependency origins
- Audit supply chain changes

## Production Use Cases

### 1. Regulatory Compliance
Many industries require SBOMs:
- **NIST**: SSDF and Executive Order 14028
- **FDA**: Medical device software
- **EU**: Cyber Resilience Act
- **Automotive**: UN R155/UN R156

### 2. CI/CD Integration
```yaml
# Example GitHub workflow
- name: Generate SBOM
  run: mw sbom --format json --output sbom.json

- name: Scan for vulnerabilities
  run: |
    pip install trivy
    trivy sbom --format json --output vuln.json sbom.json

- name: Upload SBOM
  uses: actions/upload-artifact@v4
  with:
    name: sbom
    path: sbom.json
```

### 3. Dependency Audits
```bash
# Generate SBOM
mw sbom --format all

# Review license summary
cat sbom.txt | grep -A 20 "License Summary"

# Check for specific licenses
cat sbom-spdx.json | jq '.packages[] | select(.licenseConcluded | contains("GPL"))'
```

### 4. Release Documentation
Attach SBOM to every release:
```bash
# Pre-release checklist
mw sbom --format all --output release-sbom.json
git add release-sbom.json
git commit -m "Add SBOM for v${VERSION}"
git tag v${VERSION}
```

## Best Practices

1. **Generate on every release**: Keep SBOMs synchronized with releases
2. **Automate in CI/CD**: No manual steps required
3. **Store artifacts**: Keep SBOMs alongside code
4. **Scan regularly**: Check for new vulnerabilities
5. **Document policies**: Establish SBOM retention and distribution policies

## Export Formats Comparison

| Format | Best For | Tool Support | Human Readable |
|--------|----------|--------------|----------------|
| CycloneDX JSON | Security scanning | Excellent | No |
| SPDX JSON | License compliance | Good | No |
| Text Summary | Quick review | N/A | Yes |

## Example SBOM Entry (CycloneDX)

```json
{
  "type": "library",
  "bom-ref": "pkg:pypi/click@8.1.7",
  "name": "click",
  "version": "8.1.7",
  "description": "Composable command line interface toolkit",
  "licenses": [
    {
      "license": {
        "id": "BSD-3-Clause"
      }
    }
  ],
  "purl": "pkg:pypi/click@8.1.7",
  "externalReferences": [
    {
      "type": "website",
      "url": "https://palletsprojects.com/p/click/"
    }
  ]
}
```

## Troubleshooting

### Missing Dependencies
If some dependencies don't appear in the SBOM:
```bash
# Ensure all dependencies are installed
pip install -e ".[all]"

# Regenerate SBOM
mw sbom --format all
```

### Large SBOM Files
For projects with many dependencies:
```bash
# Use JSON format (smaller than text)
mw sbom --format json --output sbom.json

# Compress the output
gzip sbom.json
```

### Git Information Missing
If git commit shows "unknown":
```bash
# Ensure in a git repository
git init
git add .
git commit -m "Initial commit"

# Regenerate SBOM
mw sbom
```

## Resources

- [CycloneDX Specification](https://cyclonedx.org/)
- [SPDX Specification](https://spdx.dev/)
- [NIST SBOM Guidance](https://www.nist.gov/publications/software-bill-materials-sbom)
- [OWASP Dependency-Track](https://dependencytrack.org/)

## Related Commands

- `mw deps`: Dependency management and security auditing
- `mw health`: Project health scoring
- `mw audit`: Security scanning
- `mw scan`: Project and module registry scanning

---

**Last Updated**: 2026-04-17
**Version**: 3.0.1
