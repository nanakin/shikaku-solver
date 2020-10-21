def read_input():
    width, height = [int(i) for i in input().split()]
    areas = {}
    for row in range(height):
        areas.update({(row, column): int(n) for column, n in enumerate(input().split()) if int(n) > 0})
    return width, height, areas


width, height, areas = read_input()
