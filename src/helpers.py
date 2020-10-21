from operator import mul
import string
import numpy as np
import math
from collections import namedtuple


class Grid:

    Size = namedtuple('Size', ['height', 'width'])

    def __init__(self, size, areas, values=None):
        self.size = self.Size(*size)
        self.areas = areas
        self.cells = values if values is not None else np.zeros(self.size, dtype=int)

    def __copy__(self):
        return Grid(self.size, self.areas, np.copy(self.cells))


def area_info(area_coord, grid):
    return f'area {area_coord} {grid.areas[area_coord]}'


def is_cell_in_rectangle(cell_coord, rectangle_info):
    """Verify if a cell is in a rectangle."""
    rect_coord, rect_size = rectangle_info
    return (rect_coord[0] <= cell_coord[0] < rect_coord[0] + rect_size[0]
            and rect_coord[1] <= cell_coord[1] < rect_coord[1] + rect_size[1])


def is_a_possibility(starts, size, area_coord, grid):
    """Verify if a given zone is free."""

    def is_area_info_in_rectangle():
        """Verify if there is another area number in the zone."""
        for coord in ((y_check, x_check) for y_check in range(start_y, end_y) for x_check in range(start_x, end_x)):
            if coord in grid.areas.keys() and coord != area_coord:
                return True
        return False

    (start_y, start_x), (r_height, r_width) = starts, size
    end_y, end_x = start_y + r_height, start_x + r_width

    if is_area_info_in_rectangle():  # cross another area number
        return False

    rectangle = grid.cells[start_y:end_y, start_x:end_x]
    free_space = rectangle[np.where(rectangle == 0)]
    return free_space.size == r_width * r_height  # OK if the given zone is not occupied


def initial_possibilities_calculation(grid):
    """For each area find all possible shape dimensions and their positions."""

    def get_divisors(n):
        """Yield all divisors of a number n."""
        for i in range(1, int(math.sqrt(n)) + 1):
            if n % i == 0:
                yield (i, n // i)

    def get_available_places(area_coord, size):
        """Find all places where the shape (length/width) could theoretically fit to match a given area, including its 90° rotation.""" 
        solutions = []
        for r_width, r_height in [size, reversed(size)]:
            for w in range(r_width):
                for h in range(r_height):
                    start_y, start_x = area_coord[0] - h, area_coord[1] - w
                    if (start_x >= 0 and start_y >= 0 and 0 < start_x + r_width <= grid.size.width
                            and 0 < start_y + r_height <= grid.size.height):
                        possibility = ((start_y, start_x), (r_height, r_width))
                        if is_a_possibility(*possibility, area_coord, grid):
                            solutions.append(possibility)
            if r_width == r_height:  # if the shape is a square, do not rotate
                break
        return solutions

    initial_possibilities = {coord: [] for coord in grid.areas.keys()}
    for coord, area in grid.areas.items():
        initial_possibilities[coord] = []
        for divisors in get_divisors(area):
            possibilities = get_available_places(coord, divisors)
            initial_possibilities[coord].extend(possibilities)
    return initial_possibilities


def get_empty_cells_possibilities(remaining_possibilities, grid):
    """Get the usage of each empty cell by the pre-calculated areas shapes possibilities."""
    empty_cells_usage = {(y, x): [] for y in range(grid.size.height) for x in range(grid.size.width) if grid.cells[y, x] == 0}
    for area_coord, possibilities in remaining_possibilities.items():
        for starts, size in possibilities:
            for cell_y in range(starts[0], starts[0] + size[0]):
                for cell_x in range(starts[1], starts[1] + size[1]):
                    if (cell_y, cell_x) in empty_cells_usage:
                        empty_cells_usage[(cell_y, cell_x)].append((starts, size, area_coord))
    return empty_cells_usage


def lexicographical_grid(grid):
    """Get a string representation of the 2D array grid."""
    letters = string.ascii_uppercase + string.ascii_lowercase
    ascii_solution = []
    i_letter = 0
    rectangles_letter = {}
    for rect_box in np.reshape(grid.cells, grid.size.height * grid.size.width):
        if rect_box not in rectangles_letter.keys():
            rectangles_letter[rect_box] = letters[i_letter]
            i_letter += 1
        ascii_solution.append(rectangles_letter[rect_box])
    return ''.join(ascii_solution)


def get_from_cache(grid, cached_results, rectangle_counter):
    """Find in the cache all solutions that can fill the given empty grid situation."""
    solutions = set()
    zeros_coords = np.where(grid.cells == 0)
    for cached_result in cached_results:
        cached_array = np.array([ord(letter) for letter in cached_result]).reshape(grid.size.height, grid.size.width) \
                       + next(rectangle_counter)
        grid.cells[zeros_coords] = cached_array[zeros_coords]
        solutions.add(lexicographical_grid(grid))
    return solutions


def get_assumed_possibilities_from_an_area(remaining_possibilities):
    """Select a area candidate and yield the remaining possibilities after making a guess"""

    def get_an_area_candidate(all_possibilities):
        """Find the area with the less possibilities and the biggest shape."""
        min_n_possibilities = len(min(all_possibilities.values(), key=lambda x: (len(x))))
        min_keys = [coord for coord, poss in all_possibilities.items() if len(poss) == min_n_possibilities]
        return max(min_keys, key=lambda k: max(map(lambda x: mul(*x[1]), all_possibilities[k])))

    candidate_coord = get_an_area_candidate(remaining_possibilities)  # select an area candidate
    # run over on the all candidate's possibilities (in case of multiple correct solutions)
    for rect_possibility in remaining_possibilities[candidate_coord]:
        assumed_possibilities = remaining_possibilities
        assumed_possibilities[candidate_coord] = [rect_possibility]  # select one candidate's possibility (one shape)
        yield assumed_possibilities




