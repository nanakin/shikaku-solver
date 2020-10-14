from helpers import lexicographical_grid, get_from_cache, get_assumed_possibilities_from_an_area, is_a_possibility, \
    get_empty_cells_possibilities
import numpy as np
from itertools import count

rectangle_counter = count(start=1)
cache = {}


def resolve(remaining_possibilities, grid_state):
    """Filter inaccurate possibilities and fill the grid with rectangles. Run until it converges (no new results)."""

    def add_rectangle(starts, size):
        nonlocal new_rectangle_found_during_iteration
        (y, x), (h, w) = starts, size
        grid_state[y:y + h, x:x + w] = next(rectangle_counter)
        new_rectangle_found_during_iteration = True

    new_rectangle_found_during_iteration = True
    while new_rectangle_found_during_iteration:  # Main solver loop
        new_rectangle_found_during_iteration = False

        # Part 1: Filter inaccurate rectangles possibilities from the pre-calculated list
        # For each area number verify the accuracy of all its possibilities
        reduced_possibilities = {}
        for area_coord, possibilities in remaining_possibilities.items():
            reduced_possibilities[area_coord] = [possibility for possibility in possibilities
                                                 if is_a_possibility(*possibility, area_coord, grid_state)]
            if len(reduced_possibilities[area_coord]) == 0:  # not shape fit in the area, the grid cannot be solved
                print('not OK rect')
                return None, None
            elif len(reduced_possibilities[area_coord]) == 1:  # found an area solution
                print('found 1 rectangle')
                add_rectangle(*reduced_possibilities[area_coord][0])
                del reduced_possibilities[area_coord]
        remaining_possibilities = reduced_possibilities

        # Part 2: Filter by cell (optional part that accelerates the convergence)
        # if a box grid can be used by only one rectangle: add it
        # if a cell cannot be reached: end the resolver
        for box_coord, box_possibilities in get_empty_cells_possibilities(remaining_possibilities, grid_state).items():
            if grid_state[box_coord] == 0:  # re-check as new rectangles may be added to the grid during the iteration
                if len(box_possibilities) == 1 and is_a_possibility(*box_possibilities[0], grid_state):
                    print('found 1 rectangle by cells')
                    add_rectangle(*box_possibilities[0][0:2])  # only one shape can use the cell
                    del remaining_possibilities[box_possibilities[0][2]]
                elif len(box_possibilities) <= 1:
                    print('not OK cells', box_coord, grid_state[box_coord])
                    return None, None  # an empty box cannot be filled: the grid cannot be solved
    return grid_state, remaining_possibilities


def resolve_with_assumptions(remaining_possibilities, grid_state):
    """Call the 'resolve' algorithm with assumption(s) if necessary."""

    grid_state, remaining_possibilities = resolve(remaining_possibilities, grid_state)

    if remaining_possibilities is None or not remaining_possibilities:  # 'resolve' algorithm converged to an end result
        if remaining_possibilities is not None:  # the grid solution is correct
            return [lexicographical_grid(grid_state)]
        else:  # cannot solve the grid
            return None

    else:  # the resolver cannot finish without an assumption

        zeros_hash = tuple(tuple(zero_coord) for zero_coord in np.argwhere(grid_state == 0))  # hash for cache analysis
        if zeros_hash in cache:  # a same zeros-grid situation was already analyzed, re-use result
            if len(cache[zeros_hash]) > 0:
                return get_from_cache(grid_state, cache[zeros_hash], rectangle_counter)
            else:
                return None

        else:  # re-run the resolver with all different possibilities of one chosen area (to keep all correct solutions)
            correct_solutions = set()
            for assumed_possibilities in get_assumed_possibilities_from_an_area(remaining_possibilities):
                # solve again (recursion) but with a new assumption
                solutions = resolve_with_assumptions(remaining_possibilities=assumed_possibilities,
                                                     grid_state=np.copy(grid_state))
                if solutions is not None:
                    correct_solutions.update(solutions)
            cache[zeros_hash] = correct_solutions
            return correct_solutions
