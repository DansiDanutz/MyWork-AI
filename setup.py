#!/usr/bin/env python3
"""
MyWork-AI Framework Setup
=========================
Installation script for MyWork-AI framework tools.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

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
        "ruff>=0.1.0",
    ],
}

setup(
    name="mywork-ai",
    version="2.6.0",
    author="Dan Sidanutz",
    author_email="dan@mywork-ai.dev",
    description="AI-powered development framework — build, ship, and sell software products with CLI tools, workflows, and a marketplace",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dansidanutz/MyWork-AI",
    project_urls={
        "Bug Reports": "https://github.com/dansidanutz/MyWork-AI/issues",
        "Source": "https://github.com/dansidanutz/MyWork-AI",
        "Marketplace": "https://frontend-hazel-ten-17.vercel.app",
    },
    packages=["tools"],
    python_requires=">=3.9",
    install_requires=[
        "python-dotenv>=1.0.0",
    ],
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "mw=tools.mw:main",
            "mywork=tools.mw:main",
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
    keywords="ai, development, framework, automation, marketplace, cli, workflow",
)
