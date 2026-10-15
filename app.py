from flask import Flask, render_template, request
import heapq
import json

app = Flask(__name__)

def heuristic(a, b):
    """Calculates Manhattan distance h(n)"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def solve_a_star(maze, start, goal):
    rows = len(maze)
    cols = len(maze[0])
    
    open_set = []
    heapq.heappush(open_set, (0, start))
    
    came_from = {}
    g_score = {(r, c): float('inf') for r in range(rows) for c in range(cols)}
    g_score[start] = 0
    
    f_score = {(r, c): float('inf') for r in range(rows) for c in range(cols)}
    f_score[start] = heuristic(start, goal)
    
    open_set_hash = {start}
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        open_set_hash.remove(current)
        
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]
            
        r, c = current
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (r + dr, c + dc)
            
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols:
                if maze[neighbor[0]][neighbor[1]] == 1:  # Wall
                    continue
                
                tentative_g_score = g_score[current] + 1
                
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    
                    if neighbor not in open_set_hash:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
                        open_set_hash.add(neighbor)
                        
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    # Defaults
    rows = 5
    cols = 5
    start = (0, 0)
    goal = (4, 4)
    maze = [[0 for _ in range(cols)] for _ in range(rows)]
    path = []
    error = None

    if request.method == "POST":
        try:
            rows = int(request.form.get("rows", 5))
            cols = int(request.form.get("cols", 5))
            
            start_row = int(request.form.get("start_row", 0))
            start_col = int(request.form.get("start_col", 0))
            start = (start_row, start_col)
            
            goal_row = int(request.form.get("goal_row", rows - 1))
            goal_col = int(request.form.get("goal_col", cols - 1))
            goal = (goal_row, goal_col)

            # Read maze data from hidden JSON field submitted by JS
            maze_data_str = request.form.get("maze_data")
            if maze_data_str:
                maze = json.loads(maze_data_str)
            else:
                maze = [[0 for _ in range(cols)] for _ in range(rows)]

            # Validation
            if not (0 <= start[0] < rows and 0 <= start[1] < cols):
                raise ValueError("Start coordinates are out of bounds.")
            if not (0 <= goal[0] < rows and 0 <= goal[1] < cols):
                raise ValueError("Goal coordinates are out of bounds.")
            if maze[start[0]][start[1]] == 1 or maze[goal[0]][goal[1]] == 1:
                raise ValueError("Start or Goal cannot be placed on a Wall (1).")

            # Solve A*
            path = solve_a_star(maze, start, goal)
            if path is None:
                error = "No path found from Start to Goal!"

        except Exception as e:
            error = f"Error: {str(e)}"

    return render_template(
        "index.html",
        rows=rows,
        cols=cols,
        maze=maze,
        start=start,
        goal=goal,
        path=path if path else [],
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)