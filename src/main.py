from solver import shikaku_solve
from print import print_result
from helpers import Grid, Coord
import logging
import argparse


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
    parser.add_argument("-f", "--file",
                        help="provide a path to a puzzle grid")
    parser.add_argument("--color",
                        help="print solution(s) grid with colors", action="store_true")
    parser.add_argument("--all",
                        help="print all possible solutions", action="store_true")
    parser.add_argument("-v", "--verbose",
                        help="log informative message", action='count', default=0)
    args = parser.parse_args()

    if args.file:
        with open(args.file) as f:
            grid = read_grid(f.readline)
    else:
        grid = read_grid()

    if args.verbose > 0:
        logging.basicConfig(level=logging.INFO if args.verbose == 1 else logging.DEBUG)

    results = shikaku_solve(grid)
    print_result(results, grid, args.color, args.all)
