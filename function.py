import pygame
import math
import time
import random

HEIGHT = 750 #480
WIDTH = 1100 #630
ROWS = 80 #60
COLS = 100 #90

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
PURPLE = (128,0,128)
ORANGE = (255,165,0)
GREY = (128,128,128)
TURQUOISE = (64,224, 208)

class Node:
    def __init__(self, row, col, width_square, height_square, total_rows, total_cols):
        self.row = row
        self.col = col
        self.width_square = width_square
        self.height_square = height_square
        self.total_rows = total_rows
        self.total_cols = total_cols
        self.x = width_square * col
        self.y = height_square * row
        self.color = BLUE
        self.comes_from = None
        self.is_central_node = (self.col % 4 == 2) and (self.row % 4 == 2)
    
    def set_comes_from(self, grid, comes_from):
        self.comes_from = comes_from
        for i in [-1, 0, 1]:
            if comes_from.col > self.col:
                grid[self.row + i][self.col + 2].remove_barrier()
            elif comes_from.col < self.col:
                grid[self.row + i][self.col - 2].remove_barrier()
            elif comes_from.row > self.row:
                grid[self.row + 2][self.col + i].remove_barrier()
            elif comes_from.row < self.row:
                grid[self.row - 2][self.col + i].remove_barrier()

    def is_visited(self):
        return self.color == WHITE
    
    #to remove later
    def make_test_color(self):
        self.color = ORANGE
    
    def make_barrier(self):
        self.color = BLACK
    
    def is_barrier(self):
        return self.color == BLACK
    
    def make_empty(self, grid):
        self.color = WHITE
        for node in self.inner_neighbors:
            node.color = WHITE
    
    def reset(self,grid):
        self.color = BLUE
        for node in self.inner_neighbors:
            node.color = BLUE

    def is_start(self):
        return self.color == GREEN
    
    def is_end(self):
        return self.color == PURPLE

    def remove_barrier(self):
        self.color = WHITE
    
    def get_comes_from(self):
        return self.comes_from

    def make_start(self, grid):
        self.color = GREEN
        for node in self.inner_neighbors:
            node.color = GREEN
    
    def make_end(self, grid):
        self.color = PURPLE
        for node in self.inner_neighbors:
            node.color = PURPLE
    
    def make_visited(self, grid):
        self.color = WHITE
        for node in self.inner_neighbors:
            node.color = WHITE
    
    def is_empty(self):
        self.color == BLUE
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width_square, self.height_square))
    
    def update_inner_neighbors(self, grid):
        self.inner_neighbors = []
        if self.is_central_node:
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    if not (i == 0 and j == 0):
                        self.inner_neighbors.append(grid[self.row + i][self.col + j])
        return self.inner_neighbors

    def update_outer_neighbors(self, centrals_grid, tot_centr_rows, tot_centr_cols):
        self.outer_neighbors = []
        self.col_centr = self.col // 4
        self.row_centr = self.row // 4
        if self.col_centr != 0:
            self.outer_neighbors.append(centrals_grid[self.row_centr][self.col_centr - 1])
        if self.row_centr != 0:
            self.outer_neighbors.append(centrals_grid[self.row_centr - 1][self.col_centr])
        if self.row_centr < tot_centr_rows - 1:
            self.outer_neighbors.append(centrals_grid[self.row_centr + 1][self.col_centr]) 
        if self.col_centr < tot_centr_cols - 1:
            self.outer_neighbors.append(centrals_grid[self.row_centr][self.col_centr + 1])
        return self.outer_neighbors
    
    def available_neighbors(self, viewed):
        available_neighbors = []
        for neighbor in self.outer_neighbors:
            if not neighbor in viewed:
                available_neighbors.append(neighbor)
        return available_neighbors

def get_clicked_pos(pos, rows, cols, width, height):
    x, y  = pos
    gapx = width // cols
    gapy = height // rows

    row = y // gapy
    col = x // gapx

    return row, col

def draw_grid(win, rows, cols, width, height):
    gapx = width // cols
    gapy = height // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gapy), (width, i*gapy))
    for j in range(cols):
        pygame.draw.line(win, GREY, (j * gapx, 0), (j * gapx, height))

def draw(win, grid):
    for row_lst in grid:
        for node in row_lst:
            node.draw(win)        
    
    #draw_grid(win, rows, cols, width, height)
    pygame.display.update()

def make_grid(rows, cols, width, height):
    grid = []
    gapx = width // cols
    gapy = height // rows
    for row in range(rows):
        grid.append([])
        for col in range(cols):
            node = Node(row, col, gapx, gapy, rows, cols)
            grid[row].append(node)
            if (row % 4 == 0) or (row == rows - 1) or (col % 4 == 0) or (col == cols - 1):
                node.make_barrier()
    return grid

def make_central_grid(grid):
    centrals_grid = []
    for row_count, rows in enumerate(grid):
        if (row_count % 4 == 2):
            centrals_grid.append([])
            for col_count,node in enumerate(rows):
                if (col_count % 4 == 2):
                    centrals_grid[row_count//4].append(node)
    for i in range(len(centrals_grid)):
        for j in range(len(centrals_grid[-1])):
            centrals_grid[i][j].update_outer_neighbors(centrals_grid, len(centrals_grid), len(centrals_grid[-1]))
            centrals_grid[i][j].update_inner_neighbors(grid)
    return centrals_grid

def fix_globals(width, height, rows, cols):
    if rows % 4 != 1:
        for i in range(4):
            rows += 1
            if rows % 4 == 1:
                break
    
    if cols % 4 != 1:
        for i in range(4):
            cols += 1
            if cols % 4 == 1:
                break
    
    gapx = width // cols
    gapy = height // rows

    height = (gapy * rows) 
    width = (gapx * cols) 

    return width, height, rows, cols

def algorithm(draw, grid, start, end):
    
    stack = [end]
    viewed = []

    while not ((stack[-1] == end) and (0 == len(start.available_neighbors(viewed)))):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current_cell = stack[-1]
        viewed.append(current_cell)

        if any(current_cell.available_neighbors(viewed)):
            new_cell = random.choice(current_cell.available_neighbors(viewed))
            new_cell.set_comes_from(grid, current_cell)
            new_cell.make_empty(grid)
            stack.append(new_cell)
        else:
            stack.pop()
        
        start.make_start(grid)
        end.make_end(grid)
        draw()



def main(width, height, rows, cols):
    
    width, height, rows, cols = fix_globals(width, height, rows, cols)
    
    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Maze visualization")
    
    grid = make_grid(rows, cols, width, height)
    
    centrals_grid = make_central_grid(grid)

    start = None
    end = None
        
    Creating_maze = True

    while Creating_maze:
        draw(win, grid)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Creating_maze = False
            
            if pygame.mouse.get_pressed()[0]: #LEFT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, cols, width, height)
                cell_row, cell_col = row//4, col//4
                node = centrals_grid[cell_row][cell_col]
                
                if not start and node != end:
                    start = node
                    node.make_start(grid)

                elif not end and node != start:
                    end = node
                    node.make_end(grid)

            if pygame.mouse.get_pressed()[2]: #RIGHT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, cols, width, height)
                cell_row, cell_col = row//4, col//4
                node = centrals_grid[cell_row][cell_col]
                
                if node.is_start():
                    start = None
                    end = None
                
                elif node.is_end():
                    end = None
                
                node.reset(grid)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    algorithm(lambda: draw(win, grid), grid, start, end)
                
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(rows, cols, width, height)
                    centrals_grid = make_central_grid(grid)
    
    pygame.quit()
    return grid

#main(WIDTH, HEIGHT, ROWS, COLS)
