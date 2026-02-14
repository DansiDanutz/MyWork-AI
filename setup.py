#!/usr/bin/env python3
"""
MyWork-AI Framework Setup
=========================
Installation script for MyWork-AI framework tools.
"""

from setuptools import setup
from pathlib import Path

# Read the README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

# Read requirements
requirements = [
    "click>=8.1.0",
    "rich>=13.0.0",
    "python-dotenv>=1.0.0",
    "httpx>=0.25.0",
    "pyyaml>=6.0.0",
]

# Optional requirements for different features
extras_require = {
    "api": [
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
    ],
    "dev": [
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
        "pytest-timeout>=2.2.0",
        "flake8>=6.0.0",
        "black>=23.0.0",
        "ruff>=0.1.0",
        "mypy>=1.7.0",
    ],
    "all": [],  # Will be populated below
}
extras_require["all"] = list(set(req for reqs in extras_require.values() for req in reqs))

setup(
    name="mywork-ai",
    version="2.0.0",
    author="Dan Sidanutz",
    author_email="dan@mywork.ai",
    description="AI-powered development framework with tools, workflows, and brain (knowledge vault)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dansidanutz/MyWork-AI",
    project_urls={
        "Bug Reports": "https://github.com/dansidanutz/MyWork-AI/issues",
        "Source": "https://github.com/dansidanutz/MyWork-AI",
    },
    packages=[],
    package_dir={"": "tools"},
    py_modules=[
        "mw",
        "config",
        "brain",
        "brain_learner",
        "module_registry",
        "health_check",
        "auto_update",
        "autocoder_api",
        "autocoder_service",
        "scaffold",
        "switch_llm_provider",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "mw=mw:main",
            "mywork=mw:main",
            "mywork-brain=brain:main",
            "mywork-health=health_check:main",
            "mywork-registry=module_registry:main",
            "mywork-scaffold=scaffold:main",
            "mywork-update=auto_update:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Build Tools",
    ],
    keywords="ai, development, framework, automation, claude, gsd",
)
