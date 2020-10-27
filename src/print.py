import colorama as c
import sys


def print_result(solutions, grid):
    if solutions is None:
        print('0', 'Unsolvable grid')
    else:
        print(len(solutions), 'solutions', '\n')
        solution = min(solutions)
        c.init()
        colors = (c.Fore.RED, c.Fore.GREEN, c.Fore.YELLOW, c.Fore.BLUE, c.Fore.MAGENTA, c.Fore.CYAN)
        print(c.Fore.WHITE, '   ', *[f'{x:02d}' for x in range(grid.size.width)], file=sys.stderr)
        for y in range(grid.size.height):
            line = f'{c.Fore.WHITE}{y:02d} '
            for x in range(grid.size.width):
                if (y, x) in grid.areas.keys():
                    line += f'{c.Fore.WHITE}{grid.areas[(y, x)]:02d} '
                else:
                    line += f' {colors[ord(solution[y * grid.size.width + x]) % 6]}{solution[y * grid.size.width + x]} '
            print(line, file=sys.stderr)
        print(c.Style.RESET_ALL)
