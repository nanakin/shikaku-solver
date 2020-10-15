# shikaku-solver

A shikaku (Japanese logic puzzle) solver using assumptions and cache.


The Shikaku game objective is to **divide a grid into rectangular (or square) pieces** such that each piece:
* contains exactly one number
* that number represents the area of the rectangle. 
![solver](https://user-images.githubusercontent.com/14202917/95357011-9cf8d780-08c7-11eb-900d-5957bb8e00f2.png)
## Usage
### Grid format
The grid should follow this format:
* the first line specify the size : width height (space separated) 
* following lines: space separated numbers to fill out the grid (0 for blank cells, otherwise the area value)

Example with a 5x5 grid with 5 areas:
```txt
5 5
0 0 8 0 0
0 0 0 0 0
6 0 4 0 4
0 0 0 0 0
0 0 3 0 0
```
### Execution
The grid is provided to the program by the **standart input**.

The solver will print:
- the number of solution
- a solution (if solvable)
```sh
$ python3 main.py < grid
1 solution
A A A A B
A A A A B
C C D D B
C C D D B
C C E E E
```

## The algorithm
### General idea
The program algorithm uses the same techniques you would probably use to solve **manually** a shikaku grid:
1. Find rectangles with only one possible way to be orientated and placed. 
2. Find cells that can only be reached by one area.

_Only if the first two techniques do not give results_: Place one of the rectangles possibilities and re-analyze the grid.

### More into details
The first phase before calling the solver is to **find all possible shapes** for each area number (that do not touch an other area number), this is done by `initial_possibilities_calculation`only once.

Then from that list of rectangles the `resolve` function checks if there is an area that has only **one shape that can fit**, if so we **add it** to the `grid_state`. This add will probably give rise to elimination of possibilities, indeed the areas next to the solved one may have possibilities that use cells of new added rectangle. So we verify the accuracy of the remaining areas possibilities (with `is_a_possibility`) and **eliminate** the ones that use now **occupied cells**. 

We can also find rectangles by analyzing the **empty cells**. If such cell is used by only one rectangle possibility, we add that shape to the grid. If a cell is covered by several possibilities but all from the same area number, we can eliminate the area's possibilities that do not use that cell.

We **repeat** this process until all rectangles are found! If this does **not converge to a result**, we need to fill the grid with **an assumption**, and re-run the `resolve` algorithm. This is managed by `resolve_with_assumptions` that can be called recursively.
To minimize the number of recursion due to assumptions we use a **cache** that keeps results so that in a **same empty cells situation** we can **re-use** the already calculated ones. 

### The algorithm by example
To illustrate the solver steps here a simple example.
Let's take this small grid: 
![empty-solver](https://user-images.githubusercontent.com/14202917/95756371-fedd8680-0ca5-11eb-8d96-2634a14b5be7.png)
Find all possible rectangles for all areas
![possibilities](https://user-images.githubusercontent.com/14202917/95356384-e39a0200-08c6-11eb-8bee-098a69df23a3.png)

As mentioned earlier, there are 2 main known techniques to solve a grid, we will analyze them independently for more clarity.

### With technique n°1 by analyzing rectangles
- There are too many rectangles possibilities for each area. We have to make an assumption to go further. The best area candidate is the one with the less possibilities and the biggest dimension, so one of the `8` rectangle.
- We re-run the solver with that assumption added to the grid. This actually eliminates all the rectangles possibilities that used the cells occupied by the `8` rectangle. If we look at the `6` rectangles only one is now correct, so we can add it to the grid. It's the same for the `central 4` now. And if we look now at the `right 4`, none of its initial possibilities are correct ! This mean that the previous assumption was incorrect.
![1assumption](https://user-images.githubusercontent.com/14202917/95356244-bea58f00-08c6-11eb-8b67-fd08dea4e76d.png)
- Let's retry with the second possibility of the `8` area. With the same process described before we can now see that everything fit. The grid is solved.
![2assumption](https://user-images.githubusercontent.com/14202917/95355130-7d60af80-08c5-11eb-970e-5c99da36abb4.png)

### With technique n°2 by analyzing cells
- If we look now how initial rectangles possibilities occupy **cells individually**, we can notice that some of them are only used by **one area**. 
    - The cell bellow `6` (4th line, 1st row) is for example accessible only the the area `6`. We know for sure that the solution for this area will use that cell because the other area cannot. We can eliminate the area possibilities that do not use it.
    - For the cell right next to `3` we can eliminate the rectangle possibility that is fully at left.
    - Same process for the cells under `right 4` and under `central 4`.
- After the previous elimination process we have now cells with only **one** solution. 
  - This is the case for the cell at the top-left corner of the grid, we can fill the grid with the only valid solution that use that cell.
  - Same for the cell underneath the `6` area.
- As the added two rectangles restricted the other areas possibilities, we have now new **one** solution cells and we can fill the grid with that process until the grid is full.
    
![technique-2](https://user-images.githubusercontent.com/14202917/96125642-30e42800-0ef4-11eb-87e6-f3296a15fa6b.png)


## Contribution
Feel free to suggest enhancement and report any error/non-sense or miss-understood code.

## Credit
Thanks to [codingame](https://www.codingame.com/ide/puzzle/shikaku-solver) for this puzzle idea.



