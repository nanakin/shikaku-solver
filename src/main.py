from solver import shikaku_solve
from print import print_result
from helpers import Grid, Coord
import logging
import argparse

logging.basicConfig(level=logging.INFO)


def read_grid(read_line=input):
    """Read the grid from an input (file or stdin)."""
    width, height = [int(i) for i in read_line().split()]
    areas = {}
    for row in range(height):
        areas.update(
            {Coord(row, column): int(n)
             for column, n in enumerate(read_line().split())
             if int(n) > 0})
    return Grid((height, width), areas)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="provide a path to a puzzle grid")
    parser.add_argument("--color", help="print solution(s) grid with colors", action="store_true")
    args = parser.parse_args()

    if args.file:
        with open(args.file) as f:
            grid = read_grid(f.readline)
    else:
        grid = read_grid()

    results = shikaku_solve(grid)
    print_result(results, grid, args.color)
