import sys
import subprocess


def run_solver(file, options=[], capture_output=True, text=True):
    script = [sys.executable, 'src/main.py', '--file', file]
    script.extend(options)
    return subprocess.run(
        script, capture_output=capture_output, text=text, check=True)


def test_30x30_16():
    out = run_solver('puzzle-grids/30x30-16').stdout
    assert '16' in out[0:2]


def test_25x20_48():
    out = run_solver('puzzle-grids/25x20-48').stdout
    assert '48' in out[0:2]


def test_20x20_32():
    out = run_solver('puzzle-grids/20x20-32').stdout
    assert '32' in out[0:2]


def test_15x20_20():
    out = run_solver('puzzle-grids/15x20-20').stdout
    assert '20' in out[0:2]


def test_5x5_1():
    out = run_solver('puzzle-grids/5x5-1').stdout
    assert '1' in out[0]


def test_5x5_1_output():
    options = ['-vv']
    err = run_solver('puzzle-grids/5x5-1', options).stderr
    assert 12 == len(err.split('\n'))


def test_unsolvable():
    out = run_solver('puzzle-grids/15x20-0').stdout
    assert '0' in out[0]
