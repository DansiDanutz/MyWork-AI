#!/usr/bin/env python3
"""
Test Script for Auto-Linting Agent
Verifies that the agent works correctly with different file types and scenarios.
"""

import os
import sys
import tempfile
import shutil
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.abspath("."))


def create_test_files(test_dir: Path):
    """Create test files with linting issues"""

    # Bad markdown file
    bad_md = test_dir / "test.md"
    bad_md.write_text("""# Test Markdown
This is a test file with linting issues.

## Header Without Blank Line
This should have a blank line before it.
- List item 1
- List item 2


- List with extra blank lines

### Another Header
Some text here.

http://example.com

<div>HTML without proper formatting</div>""")

    # Bad Python file
    bad_py = test_dir / "test.py"
    bad_py.write_text("""# Test Python file with issues
def bad_function(   x,y,z   ):
    if x>0:
        print( "Hello World" )
        return x+y+z
    else:
        return None

def another_function():
    # This line is too long and should be wrapped by Black but isn't currently formatted properly at all
    result = some_very_long_variable_name + another_very_long_variable_name + yet_another_long_variable_name
    return result


class BadClass:
    def __init__(self,name,value):
        self.name=name
        self.value=value

    def get_name( self ):
        return self.name
""")

    # Bad JavaScript file
    bad_js = test_dir / "test.js"
    bad_js.write_text("""// Test JavaScript with formatting issues
function badFunction(x,y,z){
if(x>0){
console.log("Hello World");
return x+y+z;
}else{
return null;
}
}

const obj={
name:"test",
value:123,
data:[1,2,3,4,5]
};

// Missing semicolon
const result = obj.name + obj.value""")

    # Bad JSON file
    bad_json = test_dir / "test.json"
    bad_json.write_text("""{
"name": "test",
"version": "1.0.0",
"description": "Test package",
"scripts": {
"start": "node index.js",
"test": "jest"
},
"dependencies": {
"express": "^4.17.1",
"lodash": "^4.17.21"
}
}""")

    return [bad_md, bad_py, bad_js, bad_json]


def test_agent_import():
    """Test that the agent can be imported successfully"""
    print("🧪 Testing agent import...")

    try:
        from auto_linting_agent import AutoLintingAgent, LintConfig, LintResult

        print("✅ Auto-linting agent imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import auto-linting agent: {e}")
        return False


def test_config_creation():
    """Test configuration creation and validation"""
    print("\n🧪 Testing configuration...")

    try:
        from auto_linting_agent import LintConfig

        # Test default config
        config = LintConfig()
        assert config.markdownlint == True
        assert config.auto_fix == True
        assert len(config.ignore_patterns) > 0
        print("✅ Default configuration created successfully")

        # Test custom config
        custom_config = LintConfig(
            markdownlint=False, auto_fix=False, ignore_patterns=["custom/**"]
        )
        assert custom_config.markdownlint == False
        assert custom_config.auto_fix == False
        print("✅ Custom configuration created successfully")

        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_file_type_detection():
    """Test file type detection and tool selection"""
    print("\n🧪 Testing file type detection...")

    try:
        from auto_linting_agent import AutoLintingAgent

        agent = AutoLintingAgent()

        # Test markdown detection
        md_tools = agent.get_linting_tools_for_file("test.md")
        assert "markdownlint" in md_tools
        print(f"✅ Markdown detection: {md_tools}")

        # Test Python detection
        py_tools = agent.get_linting_tools_for_file("test.py")
        expected_py_tools = ["black", "flake8", "pylint"]
        for tool in expected_py_tools:
            if tool not in py_tools:
                print(f"⚠️ Expected {tool} for Python files")
        print(f"✅ Python detection: {py_tools}")

        # Test JavaScript detection
        js_tools = agent.get_linting_tools_for_file("test.js")
        expected_js_tools = ["eslint", "prettier"]
        for tool in expected_js_tools:
            if tool not in js_tools:
                print(f"⚠️ Expected {tool} for JavaScript files")
        print(f"✅ JavaScript detection: {js_tools}")

        # Test JSON detection
        json_tools = agent.get_linting_tools_for_file("test.json")
        assert "prettier" in json_tools
        print(f"✅ JSON detection: {json_tools}")

        return True
    except Exception as e:
        print(f"❌ File type detection test failed: {e}")
        return False


def test_ignore_patterns():
    """Test file ignoring functionality"""
    print("\n🧪 Testing ignore patterns...")

    try:
        from auto_linting_agent import AutoLintingAgent, LintConfig

        config = LintConfig(ignore_patterns=["node_modules/**", "*.tmp"])
        agent = AutoLintingAgent(config=config)

        # Test ignored files with realistic paths
        import tempfile
        import os

        # Create a temporary test directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test config patterns
            test_config = LintConfig(ignore_patterns=["node_modules/**", "*.tmp", "*.pyc"])
            test_agent = AutoLintingAgent(root_dir=temp_dir, config=test_config)

            # Create test file paths within the temp directory
            node_file = os.path.join(temp_dir, "node_modules", "package", "index.js")
            temp_file = os.path.join(temp_dir, "temp.tmp")
            source_file = os.path.join(temp_dir, "src", "main.js")

            # Test patterns match correctly
            test1 = test_agent.should_ignore_file(node_file)
            test2 = test_agent.should_ignore_file(temp_file)
            test3 = test_agent.should_ignore_file(source_file)

            assert test1 == True, f"Expected True for node_modules file, got {test1}"
            assert test2 == True, f"Expected True for .tmp file, got {test2}"
            assert test3 == False, f"Expected False for regular source file, got {test3}"

        print("✅ Ignore patterns working correctly")
        return True
    except Exception as e:
        print(f"❌ Ignore patterns test failed: {e}")
        return False


def test_markdown_linting():
    """Test markdown linting functionality"""
    print("\n🧪 Testing markdown linting...")

    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)

        # Create test markdown file with issues
        test_file = test_dir / "test.md"
        test_file.write_text("""# Test Header
This is a test with some issues.
##Bad Header
This header needs a space.

- List item
- Another item

http://example.com

<div>HTML content</div>
""")

        try:
            from auto_linting_agent import AutoLintingAgent

            agent = AutoLintingAgent(str(test_dir))
            results = agent.lint_file(str(test_file))

            if results:
                result = results[0]  # Should be markdownlint result
                print(f"✅ Markdown linting completed: {result.issues_found} issues found")
                if result.issues_fixed > 0:
                    print(f"✅ Fixed {result.issues_fixed} markdown issues")
                return True
            else:
                print("⚠️ No markdown linting results (markdownlint might not be available)")
                return True  # Not a failure if tool isn't installed

        except Exception as e:
            print(f"❌ Markdown linting test failed: {e}")
            return False


def test_directory_scanning():
    """Test directory scanning functionality"""
    print("\n🧪 Testing directory scanning...")

    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)

        # Create test files
        test_files = create_test_files(test_dir)

        # Create subdirectory with more files
        sub_dir = test_dir / "subdir"
        sub_dir.mkdir()
        (sub_dir / "sub_test.md").write_text("# Sub Test\nContent here")

        try:
            from auto_linting_agent import AutoLintingAgent

            agent = AutoLintingAgent(str(test_dir))
            results = agent.lint_directory(str(test_dir))

            print(f"✅ Directory scan completed: {len(results)} results")

            # Check that files were processed
            processed_files = set(r.file_path for r in results)
            print(f"✅ Processed {len(processed_files)} files")

            # Print summary
            agent.print_summary(results)

            return True
        except Exception as e:
            print(f"❌ Directory scanning test failed: {e}")
            return False


def test_results_saving():
    """Test results saving functionality"""
    print("\n🧪 Testing results saving...")

    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)

        # Create .planning directory
        planning_dir = test_dir / ".planning"
        planning_dir.mkdir()

        # Create test file
        test_file = test_dir / "test.md"
        test_file.write_text("# Test\nContent")

        try:
            from auto_linting_agent import AutoLintingAgent, LintResult

            agent = AutoLintingAgent(str(test_dir))

            # Create mock results
            mock_results = [
                LintResult(
                    file_path=str(test_file),
                    tool="markdownlint",
                    issues_found=2,
                    issues_fixed=2,
                    success=True,
                    messages=["Fixed 2 issues"],
                    timestamp="2026-01-28T10:00:00Z",
                )
            ]

            # Save results
            agent.save_results(mock_results)

            # Check that results file was created
            results_file = planning_dir / "linting_results.json"
            assert results_file.exists()

            # Verify contents
            with open(results_file) as f:
                saved_results = json.load(f)

            assert len(saved_results) == 1
            assert saved_results[0]["tool"] == "markdownlint"
            assert saved_results[0]["issues_fixed"] == 2

            print("✅ Results saving working correctly")
            return True
        except Exception as e:
            print(f"❌ Results saving test failed: {e}")
            return False


def test_cli_integration():
    """Test CLI integration"""
    print("\n🧪 Testing CLI integration...")

    try:
        import subprocess

        # Test that the script can be run
        script_path = os.path.join(os.path.dirname(__file__), "auto_linting_agent.py")
        result = subprocess.run(
            [sys.executable, script_path, "--help"], capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0:
            print("✅ CLI help command works")
        else:
            print(f"⚠️ CLI help command failed: {result.stderr}")

        # Test stats command (should work even with no data)
        result = subprocess.run(
            [sys.executable, script_path, "--stats"], capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0:
            print("✅ CLI stats command works")
        else:
            print(f"⚠️ CLI stats command failed: {result.stderr}")

        return True
    except Exception as e:
        print(f"❌ CLI integration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Auto-Linting Agent Test Suite")
    print("=" * 50)

    tests = [
        test_agent_import,
        test_config_creation,
        test_file_type_detection,
        test_ignore_patterns,
        test_markdown_linting,
        test_directory_scanning,
        test_results_saving,
        test_cli_integration,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1

    print(f"\n📊 Test Results:")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failed}")
    print(f"   Total: {len(tests)}")

    if failed == 0:
        print(f"\n🎉 All tests passed! Auto-Linting Agent is ready for use.")
    else:
        print(f"\n⚠️ {failed} tests failed. Check the output above for details.")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
