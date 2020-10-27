import sys
import subprocess


def run_solver(file):
    script = [sys.executable, 'src/main.py', '--file', file]
    return subprocess.run(script, capture_output=True, text=True, check=True).stdout


def test_30x30_16():
    out = run_solver('puzzle-grids/30x30-16')
    assert '16' in out[0:2]


def test_25x20_48():
    out = run_solver('puzzle-grids/25x20-48')
    assert '48' in out[0:2]


def test_20x20_32():
    out = run_solver('puzzle-grids/20x20-32')
    assert '32' in out[0:2]


def test_15x20_20():
    out = run_solver('puzzle-grids/15x20-20')
    assert '20' in out[0:2]


def test_unsolvable():
    out = run_solver('puzzle-grids/15x20-0')
    assert '0' in out[0]
