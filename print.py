import colorama as c
from grid_info import width, height, areas
import sys


def print_result(solutions):
    if solutions is None:
        print('Unsolvable grid')
    else:
        print('\n', len(solutions), 'solutions', '\n')
        solution = min(solutions)
        c.init()
        colors = (c.Fore.RED, c.Fore.GREEN, c.Fore.YELLOW, c.Fore.BLUE, c.Fore.MAGENTA, c.Fore.CYAN)
        print(c.Fore.WHITE, '   ', *[f'{x:02d}' for x in range(width)], file=sys.stderr)
        for y in range(height):
            line = f'{c.Fore.WHITE}{y:02d} '
            for x in range(width):
                if (y, x) in areas.keys():
                    line += f'{c.Fore.WHITE}{areas[(y, x)]:02d} '
                else:
                    line += f' {colors[ord(solution[y * width + x]) % 6]}{solution[y * width + x]} '
            print(line, file=sys.stderr)
        print(c.Style.RESET_ALL)
