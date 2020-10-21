from helpers import lexicographical_grid, get_from_cache, get_assumed_possibilities_from_an_area, is_a_possibility, \
    empty_cells_possibilities, is_cell_in_rectangle, area_info, initial_possibilities_calculation
import numpy as np
import logging
from itertools import count
from copy import copy
rectangle_counter = count(start=1)
cache = {}


def resolve(remaining_possibilities, grid):
    """Filter inaccurate possibilities and fill the grid with rectangles. Run until it converges (no new results)."""

    def add_rectangle(starts, size):
        nonlocal new_change_during_iteration
        (y, x), (h, w) = starts, size
        grid.cells[y:y + h, x:x + w] = next(rectangle_counter)
        new_change_during_iteration = True
        logging.debug(grid.cells)

    new_change_during_iteration = True
    while new_change_during_iteration:  # Main solver loop
        new_change_during_iteration = False

        # Part 1: Filter inaccurate rectangles possibilities from the pre-calculated list
        # For each area number verify the accuracy of all its possibilities
        reduced_possibilities = {}
        for area_coord, area_possibilities in remaining_possibilities.items():
            accurate_area_possibilities = [possibility for possibility in area_possibilities
                                           if is_a_possibility(possibility, area_coord, grid)]
            if len(accurate_area_possibilities) == 0:  # not shape fit in the area, the grid cannot be solved
                logging.info(f'x grid not solvable - impossible for {area_info(area_coord, grid)}')
                return None
            elif len(accurate_area_possibilities) == 1:  # found an area solution
                logging.info(f' + rectangle added for {area_info(area_coord, grid)} - from rectangles')
                add_rectangle(*accurate_area_possibilities[0])
            else:
                reduced_possibilities[area_coord] = accurate_area_possibilities
                # logging purpose only
                eliminated_possibilities = set(area_possibilities) - set(accurate_area_possibilities)
                if len(eliminated_possibilities) > 0:
                    logging.info(f' - eliminate {len(eliminated_possibilities)} inaccurate rectangles'
                                 ' for {area_info(area_coord, grid)}')
        remaining_possibilities = reduced_possibilities

        # Part 2: Filter by cell (optional part that accelerates the convergence)
        # if a cell can be used by:
        # - only one rectangle: add it
        # - only one area, eliminate the area possibilities that don't use this cell.
        # if a cell cannot be reached: end the resolver
        for cell_coord, areas_possibilities in empty_cells_possibilities(remaining_possibilities, grid).items():
            if grid.cells[cell_coord] == 0:  # re-check as new rectangles may be added to the grid during the iteration
                if len(areas_possibilities) == 1:  # cell used by only one area
                    area_coord, cell_possibilities = next(iter(areas_possibilities.items()))
                    if len(cell_possibilities) == 1:  # cell used by only one rectangle area
                        cell_possibility = cell_possibilities[0]
                        if is_a_possibility(cell_possibility, area_coord, grid):
                            logging.info(f' + rectangle added for {area_info(area_coord, grid)} - from cells')
                            add_rectangle(*cell_possibility)  # only one shape can use the cell
                            del remaining_possibilities[area_coord]
                        else:  # not accurate possibility
                            logging.info(f'x grid not solvable - impossible to fit the cell {cell_coord}')
                            return None  # an empty box cannot be filled: the grid cannot be solved
                    else:  # eliminate the area possibilities that do not use this cell
                        previous = len(cell_possibilities)
                        remaining_possibilities[area_coord] = [
                            rect_possibility for rect_possibility in remaining_possibilities[area_coord]
                            if is_cell_in_rectangle(cell_coord, rect_possibility)]
                        if len(remaining_possibilities[area_coord]) < previous:
                            new_change_during_iteration = True
                            logging.info(f' - eliminate poss. for {area_info(area_coord, grid)} not using {cell_coord}')
                elif len(areas_possibilities) == 0:  # if no possibility
                    logging.info(f'x grid not solvable - impossible to fit the cell {cell_coord}')
                    return None  # an empty box cannot be filled: the grid cannot be solved

    return remaining_possibilities


def resolve_with_assumptions(remaining_possibilities, grid, rec_lvl=0):
    """Call the 'resolve' algorithm with assumption(s) if necessary."""

    logging.info(f'{rec_lvl*"-"}* resolve')
    remaining_possibilities = resolve(remaining_possibilities, grid)

    if remaining_possibilities is None or not remaining_possibilities:  # 'resolve' algorithm converged to an end result
        logging.info(f'{rec_lvl * "-"} stop')
        return [lexicographical_grid(grid)] if remaining_possibilities is not None else None

    else:  # the resolver cannot finish without an assumption
        logging.info(f'{rec_lvl*"-"} start new assumption:')

        # hash for cache analysis
        zeros_hash = tuple(tuple(zero_coord) for zero_coord in np.argwhere(grid.cells == 0))
        if zeros_hash in cache:  # a same zeros-grid situation was already analyzed, re-use result
            logging.info(f'{rec_lvl*"-"} results in cache !')
            return get_from_cache(grid, cache[zeros_hash], rectangle_counter) if len(cache[zeros_hash]) > 0 else None

        else:  # re-run the resolver with all different possibilities of one chosen area (to keep all correct solutions)
            correct_solutions = set()
            for assumed_possibilities in get_assumed_possibilities_from_an_area(remaining_possibilities):
                # solve again (recursion) but with a new assumption
                solutions = resolve_with_assumptions(remaining_possibilities=assumed_possibilities,
                                                     grid=copy(grid), rec_lvl=rec_lvl + 1)
                if solutions is not None:
                    correct_solutions.update(solutions)
            cache[zeros_hash] = correct_solutions
            return correct_solutions if len(correct_solutions) > 0 else None


def shikaku_solve(grid):
    """Calculate all possibilities then resolve the grid."""
    return resolve_with_assumptions(remaining_possibilities=initial_possibilities_calculation(grid),
                                    grid=grid)
