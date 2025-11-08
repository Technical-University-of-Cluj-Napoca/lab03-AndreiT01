import pygame
from utils import *
from grid import Grid
from searching_algorithms import *

pygame.font.init()
FONT = pygame.font.SysFont('Arial', 18)
GREEN_BG = (0, 200, 0)

ALGORITHMS = {
    pygame.K_1: (bfs, "Breadth-First Search (BFS)"),
    pygame.K_2: (dfs, "Depth-First Search (DFS)"),
    pygame.K_3: (ucs, "Uniform Cost Search (UCS/Dijkstra)"),
    pygame.K_4: (greedy_search, "Greedy Search"),
    pygame.K_5: (astar, "A* Search"),
    pygame.K_6: (dls, "Depth-Limited Search (DLS, Limit=20)"),
    pygame.K_7: (iddfs, "Iterative Deepening DFS (IDDFS)"),
    pygame.K_8: (ida_star, "Iterative Deepening A* (IDA*)"),
}

if __name__ == "__main__":
    pygame.init()
    
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))

    pygame.display.set_caption("Path Visualizing Algorithm")

    ROWS = 50 
    COLS = 50 
    
    grid = Grid(WIN, ROWS, COLS, WIDTH, HEIGHT)

    start = None
    end = None
    
    selected_algorithm_func = ALGORITHMS[pygame.K_1][0] 
    selected_algorithm_name = ALGORITHMS[pygame.K_1][1]
    print(f"Algorithm selected: {selected_algorithm_name} (Press 1-8 to change)")

    run = True
    started = False

    while run:
        WIN.fill(GREEN_BG) 
        
        pygame.display.set_caption(f"Path Visualizing Algorithm | Current: {selected_algorithm_name} | SPACE to Run, C to Clear")
        
        grid.draw() 
        
        text_surface = FONT.render('Press 1-8 to choose algorithm', True, COLORS['BLACK'])
        WIN.blit(text_surface, (10, 10))
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if started:
                continue

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                
                if hasattr(grid, 'get_clicked_pos'):
                    row, col = grid.get_clicked_pos(pos)
                else:
                    cell_size = WIDTH // ROWS
                    row, col = pos[1] // cell_size, pos[0] // cell_size

                if row >= ROWS or row < 0 or col >= COLS or col < 0:
                    continue

                spot = grid.grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()
                elif not end and spot != start:
                    end = spot
                    end.make_end()
                elif spot != end and spot != start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                
                if hasattr(grid, 'get_clicked_pos'):
                    row, col = grid.get_clicked_pos(pos)
                else:
                    cell_size = WIDTH // ROWS
                    row, col = pos[1] // cell_size, pos[0] // cell_size
                    
                spot = grid.grid[row][col]
                spot.reset()

                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key in ALGORITHMS:
                    selected_algorithm_func, selected_algorithm_name = ALGORITHMS[event.key]
                    
                    if start and end and hasattr(grid, 'reset_grid_state'):
                        grid.reset_grid_state()
                    
                    print(f"Algorithm selected: {selected_algorithm_name}")
                    
                elif event.key == pygame.K_SPACE and not started:
                    if not start or not end:
                        print("Error: Please set both Start and End points.")
                        continue
                        
                    started = True
                    print(f"Running {selected_algorithm_name}...")
                    
                    for row in grid.grid:
                        for spot in row:
                            spot.update_neighbors(grid.grid)
                            
                    selected_algorithm_func(lambda: grid.draw(), grid, start, end)
                    
                    started = False

                elif event.key == pygame.K_c:
                    print("Clearing the grid...")
                    start = None
                    end = None
                    grid.reset()
                    
    pygame.quit()