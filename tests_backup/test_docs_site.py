"""Tests for documentation site generator."""
import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.docs_site import (
    build_site, get_version, markdown_to_html, parse_commands, count_tests, count_tools
)


class TestMarkdownToHtml:
    def test_headers(self):
        assert '<h1>Title</h1>' in markdown_to_html('# Title')
        assert '<h2' in markdown_to_html('## Section')
        assert '<h3>' in markdown_to_html('### Sub')

    def test_code_blocks(self):
        md = "```python\nprint('hi')\n```"
        html = markdown_to_html(md)
        assert '<pre>' in html
        assert '<code' in html
        assert "print(&#x27;hi&#x27;)" in html or "print('hi')" in html

    def test_inline_code(self):
        html = markdown_to_html('Use `mw setup` to start')
        assert '<code>mw setup</code>' in html

    def test_bold(self):
        html = markdown_to_html('This is **bold** text')
        assert '<strong>bold</strong>' in html

    def test_list(self):
        md = "- item one\n- item two"
        html = markdown_to_html(md)
        assert '<ul>' in html
        assert '<li>item one</li>' in html

    def test_links(self):
        html = markdown_to_html('[Click](https://example.com)')
        assert 'href="https://example.com"' in html


class TestHelpers:
    def test_get_version(self):
        v = get_version()
        assert v  # Should return something
        assert '.' in v  # Should be semver-ish

    def test_count_tests(self):
        n = count_tests()
        assert n > 0

    def test_count_tools(self):
        n = count_tools()
        assert n > 0

    def test_parse_commands(self):
        sample = "Commands:\n    mw status          Quick health check\n    mw doctor          Full diagnostics"
        cmds = parse_commands(sample)
        assert len(cmds) == 2
        assert cmds[0]['usage'] == 'mw status'


class TestBuildSite:
    def test_build_creates_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "test_docs"
            build_site(str(out))
            assert (out / "index.html").exists()
            assert (out / "quickstart.html").exists()
            assert (out / "commands.html").exists()
            assert (out / "architecture.html").exists()
            assert (out / "changelog.html").exists()

    def test_build_html_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "test_docs"
            build_site(str(out))
            html = (out / "index.html").read_text()
            assert '<!DOCTYPE html>' in html
            assert 'MyWork-AI' in html
            assert '</html>' in html

    def test_build_has_css(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "test_docs"
            build_site(str(out))
            html = (out / "index.html").read_text()
            assert '--accent' in html  # CSS variables present
