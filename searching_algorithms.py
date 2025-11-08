from utils import *
from collections import deque
from queue import PriorityQueue
from grid import Grid
from spot import Spot
import math

def reconstruct_path(came_from: dict, current_spot: 'Spot', draw: callable) -> None:
    while current_spot in came_from:
        current_spot = came_from[current_spot]
        if not current_spot.is_start(): 
            current_spot.make_path()
        draw()

def h_manhattan_distance(p1: tuple[int, int], p2: tuple[int, int]) -> float:
    row1, col1 = p1
    row2, col2 = p2
    return abs(row1 - row2) + abs(col1 - col2)

def h_euclidian_distance(p1: tuple[int, int], p2: tuple[int, int]) -> float:
    row1, col1 = p1
    row2, col2 = p2
    return math.sqrt((row1 - row2)**2 + (col1 - col2)**2)

def _dls_recursive(current: 'Spot', end: 'Spot', came_from: dict, visited: set, limit: int, draw: callable) -> bool:
    if current == end:
        return True
    
    if limit == 0:
        return False
    
    if not current.is_start():
        current.make_closed()
        draw()

    for neighbor in current.neighbors:
        if neighbor not in visited and not neighbor.is_barrier():
            came_from[neighbor] = current
            visited.add(neighbor)
            
            if not neighbor.is_end() and not neighbor.is_start():
                neighbor.make_open()
            
            if _dls_recursive(neighbor, end, came_from, visited, limit - 1, draw):
                return True
            
            if not neighbor.is_end() and not neighbor.is_start():
                 neighbor.make_closed()

    return False

def _ida_star_search(current: 'Spot', end: 'Spot', came_from: dict, g_score: dict, limit: float, draw: callable) -> tuple[bool, float]:
    h = h_manhattan_distance
    f_score = g_score[current] + h(current.get_position(), end.get_position())

    if f_score > limit:
        return False, f_score

    if current == end:
        return True, f_score

    min_next_limit = float('inf')
    
    if not current.is_start():
        current.make_closed()
        draw()

    for neighbor in current.neighbors:
        temp_g_score = g_score[current] + 1 
        
        if temp_g_score < g_score[neighbor]:
            came_from[neighbor] = current
            g_score[neighbor] = temp_g_score
            
            if not neighbor.is_end() and not neighbor.is_start():
                neighbor.make_open()
                
            found, result_f = _ida_star_search(neighbor, end, came_from, g_score, limit, draw)
            
            if found:
                return True, result_f
            
            if not found:
                min_next_limit = min(min_next_limit, result_f)
            
            if not neighbor.is_end() and not neighbor.is_start():
                 neighbor.make_closed()

    return False, min_next_limit

def bfs(draw: callable, grid: Grid, start: Spot, end: Spot) -> bool:
    queue = deque([start])
    came_from = {}
    visited = {start} 
    
    while queue:
        current = queue.popleft()

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end() 
            return True
        
        for neighbor in current.neighbors:
            if neighbor not in visited:
                came_from[neighbor] = current
                visited.add(neighbor)
                queue.append(neighbor)
                
                if not neighbor.is_end() and not neighbor.is_start():
                    neighbor.make_open()

        draw()

        if not current.is_start():
            current.make_closed()
            
    return False

def dfs(draw: callable, grid: Grid, start: Spot, end: Spot) -> bool:
    stack = [start]
    came_from = {}
    visited = {start}
    
    while stack:
        current = stack.pop()

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end() 
            return True

        if not current.is_start():
            current.make_closed()
        
        for neighbor in current.neighbors:
            if neighbor not in visited:
                came_from[neighbor] = current
                visited.add(neighbor)
                stack.append(neighbor)
                
                if not neighbor.is_end() and not neighbor.is_start():
                    neighbor.make_open()

        draw()
            
    return False

def dls(draw: callable, grid: 'Grid', start: 'Spot', end: 'Spot', limit: int = 20) -> bool:
    came_from = {}
    visited = {start}
    
    if _dls_recursive(start, end, came_from, visited, limit, draw):
        reconstruct_path(came_from, end, draw)
        end.make_end()
        return True
    
    return False

def iddfs(draw: callable, grid: 'Grid', start: 'Spot', end: 'Spot', max_depth: int = 100) -> bool:
    for limit in range(max_depth + 1):
        came_from = {}
        visited = {start}
        
        if limit > 0:
            for row in grid.grid: 
                for spot in row:
                    if not spot.is_start() and not spot.is_end() and not spot.is_barrier():
                        spot.reset()
            
            start.make_start()
            end.make_end()
            draw()
        
        if _dls_recursive(start, end, came_from, visited, limit, draw):
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True
            
    return False

def ucs(draw: callable, grid: Grid, start: Spot, end: Spot) -> bool:
    count = 0 
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    
    came_from = {}
    g_score = {spot: float("inf") for row in grid.grid for spot in row}
    g_score[start] = 0
    open_set_hash = {start}

    while not open_set.empty():
        current = open_set.get()[2] 
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((g_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    
                    if not neighbor.is_end() and not neighbor.is_start():
                        neighbor.make_open()

        draw()

        if not current.is_start():
            current.make_closed()

    return False

def greedy_search(draw: callable, grid: Grid, start: Spot, end: Spot) -> bool:
    h = h_manhattan_distance
    count = 0
    open_set = PriorityQueue()
    open_set.put((h(start.get_position(), end.get_position()), count, start))
    
    came_from = {}
    visited = {start}

    while not open_set.empty():
        current = open_set.get()[2] 

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            if neighbor not in visited:
                came_from[neighbor] = current
                visited.add(neighbor)
                
                priority = h(neighbor.get_position(), end.get_position())
                
                count += 1
                open_set.put((priority, count, neighbor))
                
                if not neighbor.is_end() and not neighbor.is_start():
                    neighbor.make_open()

        draw()

        if not current.is_start():
            current.make_closed()

    return False

def astar(draw: callable, grid: Grid, start: Spot, end: Spot) -> bool:
    h = h_manhattan_distance
    count = 0 
    open_set = PriorityQueue()
    open_set.put((0 + h(start.get_position(), end.get_position()), count, start))
    
    came_from = {}
    g_score = {spot: float("inf") for row in grid.grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid.grid for spot in row}
    f_score[start] = h(start.get_position(), end.get_position())
    open_set_hash = {start}

    while not open_set.empty():
        current = open_set.get()[2] 
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_position(), end.get_position())
                
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    
                    if not neighbor.is_end() and not neighbor.is_start():
                        neighbor.make_open()

        draw()

        if not current.is_start():
            current.make_closed()

    return False

def ida_star(draw: callable, grid: 'Grid', start: 'Spot', end: 'Spot') -> bool:
    h = h_manhattan_distance
    limit = h(start.get_position(), end.get_position())
    
    num_rows = len(grid.grid)
    num_cols = len(grid.grid[0]) if num_rows > 0 else 0
    max_nodes = num_rows * num_cols

    while limit < float('inf') and max_nodes > 0:
        came_from = {}
        g_score = {spot: float("inf") for row in grid.grid for spot in row}
        g_score[start] = 0
        
        for row in grid.grid:
            for spot in row:
                if not spot.is_start() and not spot.is_end() and not spot.is_barrier():
                    spot.reset()
        start.make_start()
        end.make_end()
        draw()
        
        found, new_limit = _ida_star_search(start, end, came_from, g_score, limit, draw)

        if found:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True
        
        limit = new_limit
        max_nodes -= 1

    return False