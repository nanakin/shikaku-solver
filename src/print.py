import colorama as c


class Coloration:
    """Used as CM to restore default color when exit (normally or not)."""

    def __init__(self, activated):
        self.activated = activated
        self.colors = (c.Fore.RED, c.Fore.GREEN, c.Fore.YELLOW, c.Fore.BLUE, c.Fore.MAGENTA, c.Fore.CYAN)

    def __enter__(self):
        if self.activated:
            c.init()
        return self

    def __exit__(self, type, value, traceback):
        if self.activated:
            print(c.Style.RESET_ALL)

    def __call__(self, selected_color):
        if not self.activated:
            return ''
        if type(selected_color) == int:
            return self.colors[selected_color]
        return selected_color


def print_result(solutions, grid, to_color, list_all):
    """Print the puzzle result(s) if any."""

    def print_grid(solution):
        """Print a puzzle solution to stdout."""
        print('\n', color(c.Fore.WHITE), ' ', *[f'{x:02d}' for x in range(grid.size.width)])

        for y in range(grid.size.height):
            line = f'{color(c.Fore.WHITE)}{y:02d} '

            for x in range(grid.size.width):
                if (y, x) in grid.areas.keys():
                    line += f'{color(c.Fore.WHITE)}{grid.areas[(y, x)]:02d} '
                else:
                    line += f' {color(ord(solution[y * grid.size.width + x]) % 6)}' \
                        f'{solution[y * grid.size.width + x]} '
            print(line)

    if solutions is None:
        print('0', 'Unsolvable grid')
    else:
        print(len(solutions), 'Solutions')

        with Coloration(to_color) as color:
            if list_all:
                for solution in solutions:
                    print_grid(solution)
            else:
                print_grid(min(solutions))
