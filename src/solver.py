from helpers import lexicographical_grid, get_from_cache, get_assumed_possibilities_from_an_area, is_a_possibility, \
    get_empty_cells_possibilities, is_cell_in_rectangle, area_info, initial_possibilities_calculation
import numpy as np
import logging
from itertools import count
from copy import copy
rectangle_counter = count(start=1)
cache = {}


def resolve(remaining_possibilities, grid):
    """Filter inaccurate possibilities and fill the grid with rectangles. Run until it converges (no new results)."""

    def add_rectangle(starts, size):
        nonlocal new_rectangle_found_during_iteration
        (y, x), (h, w) = starts, size
        grid.cells[y:y + h, x:x + w] = next(rectangle_counter)
        new_rectangle_found_during_iteration = True
        logging.debug(grid.cells)

    new_rectangle_found_during_iteration = True
    while new_rectangle_found_during_iteration:  # Main solver loop
        new_rectangle_found_during_iteration = False

        # Part 1: Filter inaccurate rectangles possibilities from the pre-calculated list
        # For each area number verify the accuracy of all its possibilities

        reduced_possibilities = {}
        for area_coord, possibilities in remaining_possibilities.items():
            reduced_possibilities[area_coord] = [possibility for possibility in possibilities
                                                 if is_a_possibility(possibility, area_coord, grid)]
            if len(reduced_possibilities[area_coord]) == 0:  # not shape fit in the area, the grid cannot be solved
                logging.info(f'x grid not solvable - impossible for {area_info(area_coord, grid)}')
                return None, None
            elif len(reduced_possibilities[area_coord]) == 1:  # found an area solution
                logging.info(f' + rectangle added for {area_info(area_coord, grid)} - from rectangles')
                add_rectangle(*reduced_possibilities[area_coord][0])
                del reduced_possibilities[area_coord]
            else:
                eliminated_possibilities = set(remaining_possibilities[area_coord]) - set(reduced_possibilities[area_coord])
                if len(eliminated_possibilities) > 0:
                    logging.info(f' - eliminate {len(eliminated_possibilities)} inaccurate rectangles for {area_info(area_coord, grid)}')
        remaining_possibilities = reduced_possibilities

        # Part 2: Filter by cell (optional part that accelerates the convergence)
        # if a box grid can be used by:
        # - only one rectangle: add it
        # - only one area, eliminate the area possibilities that don't use this cell.
        # if a cell cannot be reached: end the resolver
        for box_coord, areas_possibilities in get_empty_cells_possibilities(remaining_possibilities, grid).items():
            if grid.cells[box_coord] == 0:  # re-check as new rectangles may be added to the grid during the iteration
                if len(areas_possibilities) == 1:  # cell used by only one area
                    area_coord, cell_possibilities = next(iter(areas_possibilities.items()))
                    if len(cell_possibilities) == 1:  # cell used by only one rectangle area
                        cell_possibility = cell_possibilities[0]
                        if is_a_possibility(cell_possibility, area_coord, grid):
                            logging.info(f' + rectangle added for {area_info(area_coord, grid)} - from cells')
                            add_rectangle(*cell_possibility)  # only one shape can use the cell
                            del remaining_possibilities[area_coord]
                        else:  # not accurate possibility
                            logging.info(f'x grid not solvable - impossible to fit the cell {box_coord}')
                            return None, None  # an empty box cannot be filled: the grid cannot be solved
                    else:  # eliminate the area possibilities that do not use this cell
                        previous = len(cell_possibilities)
                        remaining_possibilities[area_coord] = [
                            rect_possibility for rect_possibility in remaining_possibilities[area_coord]
                            if is_cell_in_rectangle(box_coord, rect_possibility)]
                        if len(remaining_possibilities[area_coord]) < previous:
                            new_rectangle_found_during_iteration = True
                            logging.info(f' - eliminate poss. for {area_info(area_coord, grid)} not using {box_coord}')
                elif len(areas_possibilities) == 0:  # if no possibility
                    logging.info(f'x grid not solvable - impossible to fit the cell {box_coord}')
                    return None, None  # an empty box cannot be filled: the grid cannot be solved

    return grid, remaining_possibilities


def resolve_with_assumptions(remaining_possibilities, grid, rec_lvl=0):
    """Call the 'resolve' algorithm with assumption(s) if necessary."""

    logging.info(f'{rec_lvl*"-"}* resolve')
    grid, remaining_possibilities = resolve(remaining_possibilities, grid)

    if remaining_possibilities is None or not remaining_possibilities:  # 'resolve' algorithm converged to an end result
        if remaining_possibilities is not None:  # the grid solution is correct
            logging.info(f'{rec_lvl*"-"} solved')
            return [lexicographical_grid(grid)]
        else:  # cannot solve the grid
            logging.info(f'{rec_lvl * "-"} not solvable')
            return None

    else:  # the resolver cannot finish without an assumption
        logging.info(f'{rec_lvl*"-"}start new assumption:')
        zeros_hash = tuple(tuple(zero_coord) for zero_coord in np.argwhere(grid.cells == 0))  # hash for cache analysis
        if zeros_hash in cache:  # a same zeros-grid situation was already analyzed, re-use result
            logging.info(f'{rec_lvl*"-"} results in cache !')
            if len(cache[zeros_hash]) > 0:
                return get_from_cache(grid, cache[zeros_hash], rectangle_counter)
            else:
                return None

        else:  # re-run the resolver with all different possibilities of one chosen area (to keep all correct solutions)
            correct_solutions = set()
            for assumed_possibilities in get_assumed_possibilities_from_an_area(remaining_possibilities):
                # solve again (recursion) but with a new assumption
                solutions = resolve_with_assumptions(remaining_possibilities=assumed_possibilities,
                                                     grid=copy(grid), rec_lvl=rec_lvl + 1)
                if solutions is not None:
                    correct_solutions.update(solutions)
            cache[zeros_hash] = correct_solutions
            if len(correct_solutions) > 0:
                return correct_solutions
            else:
                return None


def solve(grid):
    return resolve_with_assumptions(remaining_possibilities=initial_possibilities_calculation(grid),
                                    grid=grid)
