import time
from MazeSolver import generateMaze, generateTeleporterLinks, bfs
import matplotlib.pyplot as plt


def runExperiments(N=10, t=1, mazes=100):
    # Lists to store metrics
    bfsTimes = []
    bfsLengths = []
    bfsExploredCellsList = []
    bfsExploredCellsAmount = 0
    bfsUnsolvable = 0
    bfsTotalTeleportersUsed = 0

    for maze in range(mazes):
        # Generate maze
        maze = generateMaze(N)

        # Generate teleportation links
        teleporterLinks = generateTeleporterLinks(maze.grid, t)

        # BFS
        bfsTime, bfsPath, bfsExploredCells, bfsTeleportersUsed = timeAlgorithm(bfs, maze, teleporterLinks)

        if bfsPath is None:
            bfsUnsolvable += 1
            continue

        bfsTimes.append(bfsTime)
        bfsLengths.append(len(bfsPath) - 2)  # Subtract 2 to exclude start and end
        bfsExploredCellsList.append(bfsExploredCells)
        bfsExploredCellsAmount += len(bfsExploredCells)
        bfsTotalTeleportersUsed += bfsTeleportersUsed

    # Calculate averages
    avgBfsTime = sum(bfsTimes) / len(bfsTimes)
    avgBfsLength = sum(bfsLengths) / len(bfsTimes)
    avgBfsExploredCells = bfsExploredCellsAmount / len(bfsTimes)
    avgBfsTeleportersUsed = bfsTotalTeleportersUsed / len(bfsTimes)

    print(f"BFS over {mazes} mazes:")
    print(f"Average Time: {avgBfsTime:.6f} seconds")
    print(f"Average Path Length: {avgBfsLength:.2f} steps")
    print(f"Average Cells Explored: {avgBfsExploredCells:.2f} steps")
    print(f"Average Teleporters Used: {avgBfsTeleportersUsed:.2f}")
    print(f"Unsolvable Mazes: {bfsUnsolvable:.2f}")


def runUnsolvableTrendExperiment(N=30, maxTeleporters=100, mazes=10000):
    unsolvableRates = []

    # Vary the number of teleporters from 0 to maxTeleporters
    for t in range(maxTeleporters + 1):
        unsolvableCount = 0

        for maze in range(mazes):
            # Generate maze
            maze = generateMaze(N)

            # Generate teleportation links
            teleporterLinks = generateTeleporterLinks(maze.grid, t)

            # Solve the maze using BFS
            bfsTime, bfsPath, bfsExploredCells, bfsTeleportersUsed = timeAlgorithm(bfs, maze, teleporterLinks)

            # Check if the maze is unsolvable
            if bfsPath is None:
                unsolvableCount += 1

        # Calculate the percentage of unsolvable mazes
        unsolvableRate = (unsolvableCount / mazes) * 100
        unsolvableRates.append(unsolvableRate)

        print(f"Teleporters: {t}, Unsolvable: {unsolvableRate:.2f}%")

    # Plot the results
    plt.figure(figsize=(10, 6))
    plt.plot(range(maxTeleporters + 1), unsolvableRates, marker='o', linestyle='-', label=f"Maze Size {N}x{N}")
    plt.title(f"Impact of Teleporters on Maze Solvability (Size: {N}x{N})")
    plt.xlabel("Number of Teleporters")
    plt.ylabel("Percentage of Unsolvable Mazes")
    plt.grid(True)
    plt.legend()
    plt.show()


def analyseStepsToGoal(N=30, maxTeleporters=200, mazes=100):
    avgSteps = []  # Store average steps for each amount of teleporters

    # Vary the number of teleporters from 0 to maxTeleporters
    for t in range(maxTeleporters + 1):
        totalSteps = 0
        solvableMazes = 0

        for maze in range(mazes):
            # Generate maze
            maze = generateMaze(N)

            # Generate teleportation links
            teleporterLinks = generateTeleporterLinks(maze.grid, t)

            # Solve the maze using BFS
            bfsTime, bfsPath, bfsExploredCells, bfsTeleportersUsed = timeAlgorithm(bfs, maze, teleporterLinks)

            if bfsPath is not None:  # Only include solvable mazes
                totalSteps += len(bfsPath) - 2  # Subtract 2 to exclude start and end
                solvableMazes += 1

        # Calculate the average number of steps for this amount of teleporters
        if solvableMazes > 0:
            avgSteps.append(totalSteps / solvableMazes)
        else:
            avgSteps.append(None)  # Handle cases with no solvable mazes

        print(f"Teleporters: {t}, Average Steps: {avgSteps[-1]:.2f} (over {solvableMazes} solvable mazes)")

    # Plot the results
    plt.figure(figsize=(10, 6))
    plt.plot(range(maxTeleporters + 1), avgSteps, marker='o', linestyle='-', label=f"Maze Size {N}x{N}")
    plt.title(f"Effect of Teleporters on Steps to Goal (Size: {N}x{N}, {mazes:,} Mazes)", fontsize=14)
    plt.xlabel("Number of Teleporters")
    plt.ylabel("Average Steps to Goal")
    plt.grid(True)
    plt.legend()
    plt.show()


def analyseEffectOfMazeSize(mazeSizes, t=2, mazes=100):
    avgSteps = []

    for n in mazeSizes:
        totalSteps = 0
        solvableMazes = 0

        for maze in range(mazes):
            # Generate maze of size n x n
            maze = generateMaze(n)

            # Generate fixed number of teleporters (t = 2)
            teleporterLinks = generateTeleporterLinks(maze.grid, t)

            # Solve the maze using BFS
            bfsTime, bfsPath, bfsExploredCells, bfsTeleportersUsed = timeAlgorithm(bfs, maze, teleporterLinks)

            if bfsPath is not None:  # Only count solvable mazes
                totalSteps += len(bfsPath) - 2  # Subtract 2 to exclude start and end
                solvableMazes += 1

        # Calculate average steps for this maze size
        avgSteps.append(totalSteps / solvableMazes if solvableMazes > 0 else None)

        print(f"Maze Size: {n}x{n}, Average Steps: {avgSteps[-1]:.2f} (over {solvableMazes} solvable mazes)")

    # Plot the results
    plt.figure(figsize=(10, 6))
    plt.plot(mazeSizes, avgSteps, marker='o', linestyle='-', label="2 Teleporters")
    plt.title("Effect of Maze Size on Steps to Goal")
    plt.xlabel("Maze Size (n x n)")
    plt.ylabel("Average Steps to Goal")
    plt.xticks(mazeSizes)
    plt.grid(True)
    plt.legend()
    plt.show()


def timeAlgorithm(algorithm, maze, teleporterLinks):
    startTime = time.perf_counter()
    path, exploredCells, teleportersUsed = algorithm(maze, teleporterLinks)
    endTime = time.perf_counter()
    elapsedTime = endTime - startTime
    return elapsedTime, path, exploredCells, teleportersUsed
