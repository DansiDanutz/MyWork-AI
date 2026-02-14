#!/usr/bin/env python3
"""
mw bench — Code benchmarking tool.

Benchmark Python functions, scripts, or shell commands with statistical analysis.
Measures execution time, memory usage, and provides comparison reports.

Usage:
    mw bench <file>::<function>         Benchmark a Python function
    mw bench --cmd "<command>"          Benchmark a shell command
    mw bench --compare <a> <b>          Compare two benchmarks
    mw bench --runs <N>                 Number of iterations (default: 10)
    mw bench --warmup <N>              Warmup runs (default: 2)
    mw bench --output json|md|table    Output format (default: table)
    mw bench history                    Show past benchmark results
    mw bench baseline <name>            Save current run as baseline
    mw bench vs-baseline <name>         Compare against saved baseline
"""

import sys
import os
import time
import json
import statistics
import subprocess
import importlib.util
import traceback
import resource

BENCH_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.bench')


def ensure_dir():
    os.makedirs(BENCH_DIR, exist_ok=True)


def get_memory_mb():
    """Get current memory usage in MB."""
    try:
        ru = resource.getrusage(resource.RUSAGE_CHILDREN)
        return ru.ru_maxrss / 1024  # Convert KB to MB on Linux
    except Exception:
        return 0.0


def bench_function(file_path, func_name, runs=10, warmup=2):
    """Benchmark a Python function."""
    spec = importlib.util.spec_from_file_location("bench_module", file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    func = getattr(mod, func_name)
    
    # Warmup
    for _ in range(warmup):
        func()
    
    times = []
    for _ in range(runs):
        start = time.perf_counter_ns()
        func()
        elapsed = (time.perf_counter_ns() - start) / 1_000_000  # ms
        times.append(elapsed)
    
    return analyze(times, f"{os.path.basename(file_path)}::{func_name}")


def bench_command(cmd, runs=10, warmup=2):
    """Benchmark a shell command."""
    # Warmup
    for _ in range(warmup):
        subprocess.run(cmd, shell=True, capture_output=True)
    
    times = []
    for _ in range(runs):
        start = time.perf_counter_ns()
        result = subprocess.run(cmd, shell=True, capture_output=True)
        elapsed = (time.perf_counter_ns() - start) / 1_000_000  # ms
        times.append(elapsed)
    
    return analyze(times, cmd[:60])


def analyze(times, label):
    """Statistical analysis of timing results."""
    return {
        'label': label,
        'runs': len(times),
        'mean_ms': round(statistics.mean(times), 3),
        'median_ms': round(statistics.median(times), 3),
        'min_ms': round(min(times), 3),
        'max_ms': round(max(times), 3),
        'stdev_ms': round(statistics.stdev(times), 3) if len(times) > 1 else 0,
        'p95_ms': round(sorted(times)[int(len(times) * 0.95)], 3) if len(times) >= 5 else round(max(times), 3),
        'times': [round(t, 3) for t in times],
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
    }


def format_table(result):
    """Format as pretty table."""
    lines = []
    lines.append(f"\n\033[1m⏱  Benchmark: {result['label']}\033[0m")
    lines.append("=" * 50)
    lines.append(f"  Runs:       {result['runs']}")
    lines.append(f"  Mean:       {result['mean_ms']:.3f} ms")
    lines.append(f"  Median:     {result['median_ms']:.3f} ms")
    lines.append(f"  Min:        {result['min_ms']:.3f} ms")
    lines.append(f"  Max:        {result['max_ms']:.3f} ms")
    lines.append(f"  Stdev:      {result['stdev_ms']:.3f} ms")
    lines.append(f"  P95:        {result['p95_ms']:.3f} ms")
    
    # Visual bar chart of runs
    if len(result['times']) <= 20:
        lines.append(f"\n  Distribution:")
        max_t = max(result['times'])
        for i, t in enumerate(result['times']):
            bar_len = int((t / max_t) * 30) if max_t > 0 else 0
            bar = '█' * bar_len
            lines.append(f"    Run {i+1:2d}: {bar} {t:.3f}ms")
    
    lines.append("")
    return '\n'.join(lines)


def format_md(result):
    """Format as markdown."""
    lines = [
        f"## Benchmark: {result['label']}",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Runs | {result['runs']} |",
        f"| Mean | {result['mean_ms']:.3f} ms |",
        f"| Median | {result['median_ms']:.3f} ms |",
        f"| Min | {result['min_ms']:.3f} ms |",
        f"| Max | {result['max_ms']:.3f} ms |",
        f"| Stdev | {result['stdev_ms']:.3f} ms |",
        f"| P95 | {result['p95_ms']:.3f} ms |",
    ]
    return '\n'.join(lines)


def compare_results(a, b):
    """Compare two benchmark results."""
    diff = ((b['mean_ms'] - a['mean_ms']) / a['mean_ms']) * 100
    faster = "faster" if diff < 0 else "slower"
    lines = []
    lines.append(f"\n\033[1m📊 Comparison\033[0m")
    lines.append("=" * 50)
    lines.append(f"  A: {a['label']} — {a['mean_ms']:.3f}ms avg")
    lines.append(f"  B: {b['label']} — {b['mean_ms']:.3f}ms avg")
    lines.append(f"  Δ: {abs(diff):.1f}% {faster}")
    if diff < -10:
        lines.append(f"  \033[92m✅ B is significantly faster!\033[0m")
    elif diff > 10:
        lines.append(f"  \033[91m⚠️  B is significantly slower!\033[0m")
    else:
        lines.append(f"  \033[93m≈ Results are comparable\033[0m")
    return '\n'.join(lines)


def save_baseline(name, result):
    """Save benchmark result as a named baseline."""
    ensure_dir()
    path = os.path.join(BENCH_DIR, f"baseline_{name}.json")
    with open(path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"✅ Baseline '{name}' saved to {path}")


def load_baseline(name):
    """Load a saved baseline."""
    path = os.path.join(BENCH_DIR, f"baseline_{name}.json")
    if not os.path.exists(path):
        print(f"❌ No baseline '{name}' found")
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def show_history():
    """Show all saved baselines."""
    ensure_dir()
    baselines = [f for f in os.listdir(BENCH_DIR) if f.startswith('baseline_')]
    if not baselines:
        print("No saved baselines. Use: mw bench baseline <name>")
        return
    print(f"\n\033[1m📋 Saved Baselines\033[0m")
    print("=" * 50)
    for f in sorted(baselines):
        with open(os.path.join(BENCH_DIR, f)) as fh:
            data = json.load(fh)
        name = f.replace('baseline_', '').replace('.json', '')
        print(f"  {name:20s} — {data['mean_ms']:.3f}ms avg ({data['runs']} runs, {data.get('timestamp', '?')})")


def show_help():
    print(__doc__)


def main():
    args = sys.argv[1:]
    
    if not args or args[0] in ('-h', '--help', 'help'):
        show_help()
        return
    
    if args[0] == 'history':
        show_history()
        return
    
    if args[0] == 'self':
        # Benchmark the mw CLI itself
        from tools.benchmark import cmd_benchmark
        sys.exit(cmd_benchmark(args[1:]))
        return
    
    runs = 10
    warmup = 2
    fmt = 'table'
    cmd = None
    target = None
    baseline_name = None
    vs_baseline = None
    
    i = 0
    while i < len(args):
        if args[i] == '--runs' and i + 1 < len(args):
            runs = int(args[i + 1]); i += 2
        elif args[i] == '--warmup' and i + 1 < len(args):
            warmup = int(args[i + 1]); i += 2
        elif args[i] == '--output' and i + 1 < len(args):
            fmt = args[i + 1]; i += 2
        elif args[i] == '--cmd' and i + 1 < len(args):
            cmd = args[i + 1]; i += 2
        elif args[i] == 'baseline' and i + 1 < len(args):
            baseline_name = args[i + 1]; i += 2
        elif args[i] == 'vs-baseline' and i + 1 < len(args):
            vs_baseline = args[i + 1]; i += 2
        elif '::' in args[i]:
            target = args[i]; i += 1
        else:
            i += 1
    
    # Run benchmark
    if cmd:
        result = bench_command(cmd, runs, warmup)
    elif target and '::' in target:
        file_path, func_name = target.split('::', 1)
        result = bench_function(file_path, func_name, runs, warmup)
    else:
        print("❌ Specify a target: mw bench <file>::<func> or mw bench --cmd '<command>'")
        sys.exit(1)
    
    # Output
    if fmt == 'json':
        print(json.dumps(result, indent=2))
    elif fmt == 'md':
        print(format_md(result))
    else:
        print(format_table(result))
    
    # Save baseline if requested
    if baseline_name:
        save_baseline(baseline_name, result)
    
    # Compare against baseline if requested
    if vs_baseline:
        baseline = load_baseline(vs_baseline)
        print(compare_results(baseline, result))


if __name__ == '__main__':
    main()
