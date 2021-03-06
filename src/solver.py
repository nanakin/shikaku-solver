from helpers import lexicographical_grid, get_from_cache, get_assumed_possibilities_from_an_area, is_zone_free, \
    empty_cells_possibilities, is_cell_in_rectangle, area_info, initial_possibilities_calculation, Log
import numpy as np
from itertools import count
from copy import copy
rectangle_counter = count(start=1)
cache = {}


def add_rectangle(possibility, grid):
    (y, x), (h, w) = possibility.start, possibility.size
    grid.cells[y:y + h, x:x + w] = next(rectangle_counter)


def resolve(remaining_possibilities, grid):
    """Filter inaccurate possibilities and fill the grid with rectangles. Run until it converges (no new results)."""

    def filter_by_rect_and_find():
        """Filter inaccurate rectangles possibilities and find solutions.

        If an area has only one possibility, add it to the grid. If an area has no solution: end the resolver.
        If a possibility is no longer accurate, eliminate it."""

        reduced_possibilities = {}
        for area_coord, area_possibilities in remaining_possibilities.items():
            accurate_area_possibilities = [possibility for possibility in area_possibilities
                                           if is_zone_free(possibility, grid)]
            if len(accurate_area_possibilities) == 0:  # not shape fit in the area, the grid cannot be solved
                Log.info(f'<<< unsolvable - impossible for {area_info(area_coord, grid)}')
                return None
            elif len(accurate_area_possibilities) == 1:  # found an area solution
                Log.info(f'rectangle added for {area_info(area_coord, grid)} - from rectangles')
                add_rectangle(accurate_area_possibilities[0], grid)
            else:
                reduced_possibilities[area_coord] = accurate_area_possibilities
                # logging purpose only
                eliminated_possibilities = set(area_possibilities) - set(accurate_area_possibilities)
                if len(eliminated_possibilities) > 0:
                    Log.debug(f'eliminate {len(eliminated_possibilities)} inaccurate rectangles'
                              f' for {area_info(area_coord, grid)}')
        return reduced_possibilities

    def filter_by_cell_and_find():
        """Filter and find by analyzing the cells usage by remaining possibilities.

        If a cell can be used by only one rectangle: add it, only by one area: eliminate the area possibilities that 
        don't use this cell. If a cell cannot be reached: end the resolver."""

        for cell_coord, areas_possibilities in empty_cells_possibilities(remaining_possibilities, grid).items():
            if grid.cells[cell_coord] == 0:  # re-check as new rectangles may be added to the grid during the iteration
                if len(areas_possibilities) == 1:  # cell used by only one area
                    area_coord, cell_possibilities = next(iter(areas_possibilities.items()))
                    if grid.cells[area_coord] == 0:  # re-check that the area was not already filled by a previous iter.
                        if len(cell_possibilities) == 1:  # cell used by only one rectangle area
                            cell_possibility = cell_possibilities[0]
                            if is_zone_free(cell_possibility, grid):
                                Log.info(f'rectangle added for {area_info(area_coord, grid)} - from cells')
                                add_rectangle(cell_possibility, grid)  # only one shape can use the cell
                                del remaining_possibilities[area_coord]
                            else:  # not accurate possibility
                                Log.info(f'<<< unsolvable - impossible to fit the cell {cell_coord}')
                                return None  # an empty box cannot be filled: the grid cannot be solved
                        else:  # eliminate the area possibilities that do not use this cell
                            if len(remaining_possibilities[area_coord]) > len(cell_possibilities):
                                remaining_possibilities[area_coord] = cell_possibilities
                                Log.debug(f'eliminate poss. for {area_info(area_coord, grid)} not using {cell_coord}')
                elif len(areas_possibilities) == 0:  # if no possibility
                    Log.info(f'<<< unsolvable - impossible to fit the cell {cell_coord}')
                    return None  # an empty box cannot be filled: the grid cannot be solved
        return remaining_possibilities

    previous_state = None
    while remaining_possibilities != previous_state:
        previous_state = remaining_possibilities

        # Part 1: Filter inaccurate rectangles possibilities from the pre-calculated list
        remaining_possibilities = filter_by_rect_and_find()
        if remaining_possibilities is None:
            return None

        # Part 2: Filter by cell (optional part that accelerates the convergence)
        remaining_possibilities = filter_by_cell_and_find()
        if remaining_possibilities is None:
            return None

    if len(remaining_possibilities) == 0:
        Log.info('<<< solved')
    return remaining_possibilities


@Log.store_recursion_level  # (logging purpose only)
def resolve_with_assumptions(remaining_possibilities, grid):
    """Call the 'resolve' algorithm with assumption(s) if necessary."""

    remaining_possibilities = resolve(remaining_possibilities, grid)

    if remaining_possibilities is None or not remaining_possibilities:  # 'resolve' algorithm converged to an end result
        return [lexicographical_grid(grid)] if remaining_possibilities is not None else None

    else:  # the resolver cannot finish without an assumption
        # hash for cache analysis
        zeros_hash = tuple(tuple(zero_coord) for zero_coord in np.argwhere(grid.cells == 0))
        if zeros_hash in cache:  # a same zeros-grid situation was already analyzed, re-use result
            Log.info('<<< configuration of the grid in the cache !')
            return get_from_cache(grid, cache[zeros_hash], rectangle_counter) if len(cache[zeros_hash]) > 0 else None

        else:  # re-run the resolver with all different possibilities of one chosen area (to keep all correct solutions)
            Log.info('need new assumption to continue...')
            correct_solutions = set()
            for assumed_possibilities, possibility in get_assumed_possibilities_from_an_area(remaining_possibilities):
                # solve again (recursion) but with a new assumption
                Log.info(f'>>> try with {possibility}')
                solutions = resolve_with_assumptions(remaining_possibilities=assumed_possibilities,
                                                     grid=copy(grid))
                if solutions is not None:
                    correct_solutions.update(solutions)
            cache[zeros_hash] = correct_solutions
            return correct_solutions if len(correct_solutions) > 0 else None


def shikaku_solve(grid):
    """Calculate all possibilities then find the good ones to resolve the grid."""
    return resolve_with_assumptions(remaining_possibilities=initial_possibilities_calculation(grid),
                                    grid=grid)
