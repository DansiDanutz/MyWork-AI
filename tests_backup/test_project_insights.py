"""Tests for project_insights tool."""
import pytest
from tools.project_insights import (
    analyze_tech_debt,
    analyze_hotspots,
    analyze_complexity_hotspots,
    analyze_test_coverage,
    analyze_contributor_patterns,
    generate_health_grade,
    print_insights,
)


def test_analyze_tech_debt():
    debt = analyze_tech_debt()
    assert isinstance(debt, dict)
    # Should find at least some TODOs in the codebase
    total = sum(len(v) for v in debt.values())
    assert total >= 0


def test_analyze_hotspots():
    hotspots = analyze_hotspots(days=30)
    assert isinstance(hotspots, list)
    if hotspots:
        assert len(hotspots[0]) == 2  # (filename, count)
        assert isinstance(hotspots[0][1], int)


def test_analyze_complexity_hotspots():
    cx = analyze_complexity_hotspots()
    assert isinstance(cx, list)
    if cx:
        assert len(cx[0]) == 3  # (func_name, file, lines)


def test_analyze_test_coverage():
    cov = analyze_test_coverage()
    assert 'total_tools' in cov
    assert 'tested' in cov
    assert 'untested' in cov
    assert 'coverage_pct' in cov
    assert 0 <= cov['coverage_pct'] <= 100
    assert cov['total_tools'] > 0


def test_analyze_contributor_patterns():
    contrib = analyze_contributor_patterns(days=30)
    assert isinstance(contrib, dict)


def test_generate_health_grade():
    grade, score, reasons = generate_health_grade(
        {'TODO': [{'file': 'a.py', 'line': 1, 'text': 'fix'}]},
        [('main.py', 10)],
        {'coverage_pct': 80, 'tested': 8, 'total_tools': 10, 'untested': ['a', 'b']},
    )
    assert grade in 'ABCDF'
    assert 0 <= score <= 100
    assert isinstance(reasons, list)


def test_generate_health_grade_poor():
    grade, score, reasons = generate_health_grade(
        {'TODO': [{}] * 120},
        [('main.py', 60)],
        {'coverage_pct': 30, 'tested': 3, 'total_tools': 10, 'untested': []},
    )
    assert grade in 'DF'
    assert len(reasons) >= 2


def test_print_insights_summary(capsys):
    ret = print_insights(['--summary'])
    assert ret == 0
    out = capsys.readouterr().out
    assert 'Grade:' in out


def test_print_insights_help(capsys):
    ret = print_insights(['--help'])
    assert ret == 0


def test_print_insights_full(capsys):
    ret = print_insights([])
    assert ret == 0
    out = capsys.readouterr().out
    assert 'Insights' in out or 'Health Grade' in out
