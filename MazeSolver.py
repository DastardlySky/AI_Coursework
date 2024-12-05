import random
from mazelib import Maze
from mazelib.generate.Prims import Prims
import matplotlib.pyplot as plt
from collections import deque
import matplotlib.colors as mcolors


def bfs(maze, teleporterLinks):
    start = maze.start
    end = maze.end

    openPositions = 0
    height = len(maze.grid)
    width = len(maze.grid[0])

    # Count open positions (cells with value 0)
    for row in range(height):
        for col in range(width):
            if maze.grid[row][col] == 0:
                openPositions += 1

    exploredCells = []

    teleportersUsed = 0

    # Initialize the main queue with the start node
    normalQueue = deque([start])

    # Initialize the queue for "backup" teleporters with the start node
    teleporterQueue = deque()

    # Dictionary to keep track of visited nodes and their predecessors
    cameFrom = {start: None}

    # Create a dictionary for quick teleporter lookup (one-way teleporters)
    teleporterDict = {start: end for start, end in teleporterLinks}

    while normalQueue or teleporterQueue:

        # always prioritise "normal" cells unless none are available.
        if normalQueue:
            current = normalQueue.popleft()
        else:
            current = teleporterQueue.popleft()

        exploredCells.append(current)

        # Calculate progress (between 0 and 1)
        progress = len(exploredCells) / openPositions

        # If we have reached the goal, reconstruct the path
        if current == end:
            return reconstructPath(cameFrom, current), exploredCells, teleportersUsed

        # If the current space is a teleporter start, teleport to the teleporter end
        if current in teleporterDict.keys():
            teleportEnd = teleporterDict[current]
            if teleportEnd not in cameFrom:
                cameFrom[teleportEnd] = current
                normalQueue.insert(0, teleportEnd)
                teleportersUsed += 1

            # go to the next item in queue, don't look at the teleporter start's neighbours
            continue

        # Explore neighbours
        for neighbour in getNeighbours(current, maze):
            # if the neighbour is a normal cell, just add to the back of the queue and track the predecessor
            if neighbour not in cameFrom and neighbour not in teleporterDict:
                cameFrom[neighbour] = current
                normalQueue.append(neighbour)
            # If the neighbor is a teleporter, decide based on progress whether to use it
            else:
                if neighbour not in cameFrom:
                    # remember the predecessor
                    cameFrom[neighbour] = current
                    # Use exploration progress to probabilistically decide the exploration path:
                    if progress < random.random():
                        normalQueue.append(neighbour)
                    else:
                        teleporterQueue.append(neighbour)

    # If the end is not reachable
    return None, exploredCells, teleportersUsed


def manhattanDistance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstructPath(cameFrom, current):
    path = [current]
    while current in cameFrom and cameFrom[current] is not None:
        current = cameFrom[current]
        path.append(current)
    path.reverse()
    return path


def generateMaze(N):
    m = Maze()
    m.generator = Prims(int(N / 2), int(N / 2))
    m.generate()
    m.generate_entrances(True, True)
    return m


def getNeighbours(location, maze):
    x, y = location
    neighbours = []

    # Possible movements: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    size = len(maze.grid)

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        # Check if the new position is within bounds
        if 0 <= nx < size and 0 <= ny < size:
            # Check if the cell is an open path (0) / it's at the end of the maze
            if maze.grid[nx][ny] == 0 or (nx, ny) == maze.end:
                neighbours.append((nx, ny))

    return neighbours


def generateTeleporterLinks(grid, amountOfTeleporters):
    # Collect all open path positions (cells with value 0)
    openPositions = []
    height = len(grid)
    width = len(grid[0])

    for row in range(height):
        for col in range(width):
            if grid[row][col] == 0:
                openPositions.append((row, col))

    # Shuffle the list to randomize the positions
    random.shuffle(openPositions)

    # Calculate the maximum possible number of teleporters
    maxPossibleTeleporters = len(openPositions) // 2
    if amountOfTeleporters > maxPossibleTeleporters:
        print(
            f"Warning: Requested {amountOfTeleporters} teleporters, but only {maxPossibleTeleporters} can be created.")
        amountOfTeleporters = maxPossibleTeleporters

    # Pair up the open positions to create teleporters
    teleporterLinks = []
    for teleporter in range(amountOfTeleporters):
        # Pop two positions from the list to ensure they are not reused
        teleporterStart = openPositions.pop()
        teleporterEnd = openPositions.pop()
        teleporterLinks.append((teleporterStart, teleporterEnd))

    return teleporterLinks


# Displays the maze with teleportation links and a legend to the right of the maze
def showPNG(maze, teleporterLinks, path=None, exploredCells=None):
    plt.figure(figsize=(10, 5))
    plt.imshow(maze.grid, cmap=plt.cm.binary, interpolation='nearest')
    plt.xticks([]), plt.yticks([])

    # Plot the entrance (start) as green and add a label to the legend
    plt.plot(maze.start[1], maze.start[0], 'o', markersize=10, color='green', label="Start")

    # Plot the exit (end) as red and add a label to the legend
    plt.plot(maze.end[1], maze.end[0], 'o', markersize=10, color='red', label="End")

    # Plot the teleporter links and add a label to the legend
    for i, ((x1, y1), (x2, y2)) in enumerate(teleporterLinks):
        plt.plot(y1, x1, 'o', markersize=10, color='blue', label="Teleporter Start" if i == 0 else "")
        plt.plot(y2, x2, 'o', markersize=10, color='orange', label="Teleporter End" if i == 0 else "")
        plt.annotate('', xy=(y2, x2), xytext=(y1, x1), arrowprops=dict(arrowstyle="->", color='purple', lw=2))

    # Plot the path if provided
    if path:
        px, py = zip(*path)
        plt.plot(py, px, 'x-', color='black', label="Path", lw=1)

    # plotting to use a gradient color based on discovery order
    if exploredCells:
        px, py = zip(*exploredCells)
        indices = range(len(exploredCells))  # Discovery order indices

        # Normalize the indices to range between 0 and 1
        norm = mcolors.Normalize(vmin=0, vmax=len(exploredCells))

        # scatter plot with colors based on discovery order
        scatter = plt.scatter(py, px, marker="D", c=indices, cmap=plt.cm.magma, s=100, label="Explored Cells", alpha=0.6, edgecolors='none')

        # colorbar to indicate discovery order
        cbar = plt.colorbar(scatter, ax=plt.gca(), fraction=0.046, pad=0.04)
        cbar.set_label('Discovery Order')

    plt.legend(loc='upper left', bbox_to_anchor=(-0.5, 1), borderaxespad=0)
    plt.show()


# Main execution
def main():

    # Generate maze
    N = 30
    maze = generateMaze(N)

    # Generate teleportation links
    t = 500
    teleporterLinks = generateTeleporterLinks(maze.grid, t)

    # Find the path
    path, exploredCells, teleportersUsed = bfs(maze, teleporterLinks)

    print("Path:")
    print(path)

    # Display the maze with teleportation links and path
    showPNG(maze, teleporterLinks, path, exploredCells)
