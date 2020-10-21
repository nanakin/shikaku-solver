from solver import solve
from print import print_result
from helpers import Grid
import logging

logging.basicConfig(level=logging.INFO)


def read_input():
    width, height = [int(i) for i in input().split()]
    areas = {}
    for row in range(height):
        areas.update({(row, column): int(n) for column, n in enumerate(input().split()) if int(n) > 0})
    return (height, width), areas


if __name__ == "__main__":
    grid = Grid(*read_input())
    results = solve(grid)
    print_result(results, grid)
