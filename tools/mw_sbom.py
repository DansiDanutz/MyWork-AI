#!/usr/bin/env python3
"""
SBOM (Software Bill of Materials) Generation Tool for MyWork-AI

This tool generates comprehensive software bills of materials in multiple formats:
- CycloneDX JSON (industry standard for security)
- SPDX JSON (software package data exchange)
- Human-readable summary

Usage:
    mw sbom
    mw sbom --format json
    mw sbom --format spdx
    mw sbom --output /path/to/sbom.json
"""

import os
import sys
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import importlib.metadata as metadata

try:
    import click
except ImportError:
    print("Error: click is required. Install with: pip install click")
    sys.exit(1)


def get_git_info() -> Dict[str, str]:
    """Get git repository information."""
    try:
        commit = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        tag = subprocess.check_output(
            ['git', 'describe', '--tags', '--abbrev=0'],
            stderr=subprocess.DEVNULL
        ).decode().strip() or "unknown"

        return {
            'commit': commit,
            'branch': branch,
            'tag': tag,
        }
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {
            'commit': 'unknown',
            'branch': 'unknown',
            'tag': 'unknown',
        }


def get_package_metadata(package_name: str) -> Dict[str, Any]:
    """Get detailed metadata for a package."""
    try:
        dist = metadata.metadata(package_name)

        return {
            'name': package_name,
            'version': dist.get('Version', 'unknown'),
            'author': dist.get('Author', 'unknown'),
            'license': dist.get('License', 'unknown'),
            'home_page': dist.get('Home-page', 'unknown'),
            'summary': dist.get('Summary', ''),
        }
    except metadata.PackageNotFoundError:
        return {
            'name': package_name,
            'version': 'unknown',
            'author': 'unknown',
            'license': 'unknown',
            'home_page': 'unknown',
            'summary': '',
        }


def get_installed_packages() -> List[Dict[str, Any]]:
    """Get all installed packages with metadata."""
    packages = []
    for dist in metadata.distributions():
        name = dist.metadata['Name']
        version = dist.version

        packages.append(get_package_metadata(name))

    return sorted(packages, key=lambda x: x['name'].lower())


def generate_cyclonedx_sbom(packages: List[Dict[str, Any]], git_info: Dict[str, str]) -> Dict[str, Any]:
    """Generate CycloneDX v1.4 format SBOM."""
    components = []

    for pkg in packages:
        component = {
            'type': 'library',
            'bom-ref': f'pkg:pypi/{pkg["name"].lower()}@{pkg["version"]}',
            'name': pkg['name'],
            'version': pkg['version'],
            'description': pkg['summary'] or f"{pkg['name']} library",
            'licenses': [],
            'purl': f'pkg:pypi/{pkg["name"].lower()}@{pkg["version"]}',
            'externalReferences': [],
            'properties': [],
        }

        # Add license if known
        if pkg['license'] and pkg['license'].lower() not in ['unknown', '']:
            component['licenses'].append({
                'license': {'id': pkg['license']}
            })

        # Add homepage URL
        if pkg['home_page'] and pkg['home_page'].lower() not in ['unknown', '']:
            component['externalReferences'].append({
                'type': 'website',
                'url': pkg['home_page']
            })

        # Add author as property
        if pkg['author'] and pkg['author'].lower() not in ['unknown', '']:
            component['properties'].append({
                'name': 'author',
                'value': pkg['author']
            })

        components.append(component)

    # Build full CycloneDX document
    sbom = {
        '$schema': 'http://cyclonedx.org/schema/bom-1.4.schema.json',
        'bomFormat': 'CycloneDX',
        'specVersion': '1.4',
        'version': 1,
        'metadata': {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'tools': [
                {
                    'vendor': 'MyWork-AI',
                    'name': 'mw sbom',
                    'version': '1.0.0',
                }
            ],
            'component': {
                'type': 'application',
                'name': 'MyWork-AI',
                'version': metadata.version('mywork-ai'),
                'description': 'Complete AI-powered development framework',
                'author': 'Dan Sidanutz',
                'licenses': [
                    {
                        'license': {'id': 'MIT'}
                    }
                ],
                'purl': f'pkg:pypi/mywork-ai@{metadata.version("mywork-ai")}',
            },
            'properties': [
                {
                    'name': 'git:commit',
                    'value': git_info['commit']
                },
                {
                    'name': 'git:branch',
                    'value': git_info['branch']
                },
                {
                    'name': 'git:tag',
                    'value': git_info['tag']
                },
            ]
        },
        'components': components,
    }

    return sbom


def generate_spdx_sbom(packages: List[Dict[str, Any]], git_info: Dict[str, str]) -> Dict[str, Any]:
    """Generate SPDX v2.3 format SBOM."""
    spdx_id = "SPDXRef-DOCUMENT"

    # Build packages list
    packages_list = []
    for i, pkg in enumerate(packages):
        spdx_id_pkg = f"SPDXRef-Package-{i}"

        package_entry = {
            'SPDXID': spdx_id_pkg,
            'name': pkg['name'],
            'versionInfo': pkg['version'],
            'downloadLocation': f'https://pypi.org/project/{pkg["name"]}/',
            'filesAnalyzed': False,
            'licenseConcluded': pkg['license'] if pkg['license'] != 'unknown' else 'NOASSERTION',
            'licenseDeclared': pkg['license'] if pkg['license'] != 'unknown' else 'NOASSERTION',
            'copyrightText': 'NOASSERTION',
            'externalRefs': [
                {
                    'referenceCategory': 'PACKAGE-MANAGER',
                    'referenceLocator': f'pkg:pypi/{pkg["name"].lower()}@{pkg["version"]}',
                    'referenceType': 'purl',
                }
            ],
        }

        # Add homepage
        if pkg['home_page'] and pkg['home_page'].lower() not in ['unknown', '']:
            package_entry['externalRefs'].append({
                'referenceCategory': 'OTHER',
                'referenceLocator': pkg['home_page'],
                'referenceType': 'website',
            })

        packages_list.append(package_entry)

    # Build relationships
    relationships = []
    for i, pkg in enumerate(packages):
        relationships.append({
            'spdxElementId': f"SPDXRef-Package-{i}",
            'relationshipType': 'DEPENDS_ON',
            'relatedSpdxElement': f"SPDXRef-Document",
        })

    # Build full SPDX document
    sbom = {
        'spdxVersion': 'SPDX-2.3',
        'dataLicense': 'CC0-1.0',
        'SPDXID': spdx_id,
        'name': 'MyWork-AI SBOM',
        'documentNamespace': f'https://github.com/dansidanutz/MyWork-AI/sbom-{git_info["commit"]}',
        'creationInfo': {
            'created': datetime.utcnow().isoformat() + 'Z',
            'creators': [
                'Tool: mw-sbom-1.0.0',
            ],
        },
        'packages': packages_list,
        'relationships': relationships,
    }

    return sbom


def generate_human_readable_sbom(packages: List[Dict[str, Any]], git_info: Dict[str, str]) -> str:
    """Generate a human-readable summary of the SBOM."""
    lines = [
        "=" * 80,
        "MyWork-AI Software Bill of Materials",
        "=" * 80,
        f"Generated: {datetime.utcnow().isoformat()}",
        f"Version: {metadata.version('mywork-ai')}",
        f"Git Commit: {git_info['commit']}",
        f"Git Branch: {git_info['branch']}",
        f"Git Tag: {git_info['tag']}",
        "=" * 80,
        f"Total Dependencies: {len(packages)}",
        "=" * 80,
        "",
    ]

    # Group by license
    license_groups: Dict[str, List[Dict[str, Any]]] = {}
    for pkg in packages:
        lic = pkg['license'] if pkg['license'] != 'unknown' else 'Unknown'
        if lic not in license_groups:
            license_groups[lic] = []
        license_groups[lic].append(pkg)

    # Print by license
    lines.append("Dependencies by License:")
    lines.append("-" * 80)
    for lic, pkgs in sorted(license_groups.items()):
        lines.append(f"\n{lic} ({len(pkgs)} packages):")
        for pkg in sorted(pkgs, key=lambda x: x['name'].lower()):
            lines.append(f"  - {pkg['name']} {pkg['version']}")

    # Count licenses
    lines.append("")
    lines.append("=" * 80)
    lines.append("License Summary:")
    lines.append("-" * 80)
    for lic, pkgs in sorted(license_groups.items(), key=lambda x: len(x[1]), reverse=True):
        lines.append(f"  {lic}: {len(pkgs)}")

    lines.append("")
    lines.append("=" * 80)

    return '\n'.join(lines)


@click.command()
@click.option('--format', 'output_format', type=click.Choice(['json', 'spdx', 'txt', 'all']), default='txt', help='Output format')
@click.option('--output', '-o', type=click.Path(), help='Output file path (default: stdout)')
@click.option('--include-dev', is_flag=True, help='Include dev dependencies')
def main(output_format: str, output: Optional[str], include_dev: bool):
    """Generate a Software Bill of Materials for MyWork-AI."""
    click.echo("📦 Generating MyWork-AI SBOM...")

    # Get git information
    git_info = get_git_info()

    # Get installed packages
    packages = get_installed_packages()

    # Filter out dev dependencies if requested
    if not include_dev:
        # Keep only packages that are in core dependencies
        # This is a simplified approach - in production you'd parse requirements
        packages = [p for p in packages if p['name'].lower() not in ['pytest', 'black', 'flake8', 'mypy', 'ruff', 'pre-commit']]

    # Generate appropriate format
    if output_format == 'json' or output_format == 'all':
        sbom = generate_cyclonedx_sbom(packages, git_info)

        if output and output_format != 'all':
            with open(output, 'w') as f:
                json.dump(sbom, f, indent=2)
            click.echo(f"✅ CycloneDX SBOM written to {output}")
        else:
            click.echo("\n📄 CycloneDX SBOM (JSON):")
            click.echo(json.dumps(sbom, indent=2))

    if output_format == 'spdx' or output_format == 'all':
        sbom = generate_spdx_sbom(packages, git_info)

        if output_format == 'all':
            spdx_file = output.replace('.json', '-spdx.json') if output else 'sbom-spdx.json'
        else:
            spdx_file = output or 'sbom-spdx.json'

        with open(spdx_file, 'w') as f:
            json.dump(sbom, f, indent=2)
        click.echo(f"✅ SPDX SBOM written to {spdx_file}")

    if output_format == 'txt' or output_format == 'all':
        sbom = generate_human_readable_sbom(packages, git_info)

        if output_format == 'all':
            txt_file = output.replace('.json', '.txt') if output else 'sbom.txt'
        else:
            txt_file = output or 'sbom.txt'

        with open(txt_file, 'w') as f:
            f.write(sbom)
        click.echo(f"✅ Human-readable SBOM written to {txt_file}")

    click.echo(f"\n📊 Total dependencies: {len(packages)}")
    click.echo(f"🔗 Git commit: {git_info['commit'][:8]}")


if __name__ == '__main__':
    main()
