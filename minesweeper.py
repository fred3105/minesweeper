#!/usr/bin/env python3
import time
import random
import numpy as np

# Constants for clarity
MINE = 1
SAFE = 0
REVEALED = 1
FLAGGED = 9
UNKNOWN = 0
UNKNOWN_CHAR = "X"
FLAG_CHAR = "f"


def gather_solver_statistics(size, num_mines, sample_size):
    """Gather statistics on the solver's performance over multiple games."""
    turns_distribution = [0] * (size * size)
    loss_turns_distribution = [0] * (size * size)
    start_time = time.time()
    successes = 0
    failures = 0
    bombs_hit = 0

    for _ in range(sample_size):
        result, turns = solve_with_max_strategy(
            play_computer, check_elementary_logic, size, num_mines
        )
        if result == "grille resolue":
            successes += 1
        elif result == "Partie perdu":
            failures += 1
        elif result == "Bombe":
            bombs_hit += 1
        turns_distribution[turns - 1] += 1
        if result == "Partie perdu":
            loss_turns_distribution[turns - 1] += 1

    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = round(elapsed_time % 60, 2)
    success_rate = (
        successes / (successes + failures) if (successes + failures) > 0 else 0
    )
    success_percentage = round(success_rate * 100, 2)

    # Simple confidence interval approximation
    std_error = 1 / (sample_size**0.5)
    conf_min = max(0, success_rate - std_error)
    conf_max = min(1, success_rate + std_error)

    print(
        f"{success_percentage}% success rate achieved in {minutes} minutes {seconds} seconds"
    )
    print(
        f"Confidence interval: {round(conf_min * 100, 2)}% to {round(conf_max * 100, 2)}%"
    )
    return "Completed"


def precompute_neighbors(size):
    """Precompute valid neighbors for each cell."""
    neighbors = {}
    for i in range(size):
        for j in range(size):
            neigh = []
            for di, dj in [
                (-1, -1),
                (-1, 0),
                (-1, 1),
                (0, -1),
                (0, 1),
                (1, -1),
                (1, 0),
                (1, 1),
            ]:
                ni, nj = i + di, j + dj
                if 0 <= ni < size and 0 <= nj < size:
                    neigh.append((ni, nj))
            neighbors[(i, j)] = neigh
    return neighbors


def solve_with_max_strategy(play_function, logic_function, size, num_mines):
    turns = 0
    flags_placed = 0
    is_dead = False
    is_finished = False
    stuck_counter = 0
    neighbors = precompute_neighbors(size)
    processed_cells = set()
    changed_cells = set()

    mine_grid, neighbor_mines, known_cells = setup_grid(
        size, num_mines, size // 2, size // 2
    )
    player_info = np.full((size, size), UNKNOWN_CHAR, dtype=object)
    update_player_info(player_info, known_cells, neighbor_mines, size)
    changed_cells.add((size // 2, size // 2))

    mine_cells = set(logic_function(player_info))
    safe_cells = set(find_safe_cells(set(), player_info, size))

    while not is_finished:
        if stuck_counter >= 4:
            weights = calculate_weights(player_info, changed_cells, neighbors)
            x, y = find_max_weight_cell(weights, player_info)
            is_dead, known_cells, player_info, is_finished = play_function(
                mine_grid, neighbor_mines, known_cells, player_info, size, "oui", x, y
            )
            turns += 1
            if is_dead:
                return "Partie perdu", turns
            stuck_counter = 0
            changed_cells = {(x, y)}

        # Single-pass processing
        actions = set()  # (x, y, is_mine) tuples
        for x, y in mine_cells:
            for nx, ny in neighbors[(x, y)]:
                if (nx, ny) not in processed_cells and player_info[
                    nx, ny
                ] == UNKNOWN_CHAR:
                    actions.add((nx, ny, True))
        for x, y in safe_cells:
            for nx, ny in neighbors[(x, y)]:
                if (nx, ny) not in processed_cells and player_info[
                    nx, ny
                ] == UNKNOWN_CHAR:
                    actions.add((nx, ny, False))

        for x, y, is_mine in actions:
            is_dead, known_cells, player_info, is_finished = play_function(
                mine_grid,
                neighbor_mines,
                known_cells,
                player_info,
                size,
                "oui" if is_mine else "non",
                x,
                y,
            )
            turns += 1
            if is_dead:
                return "Partie perdu", turns
            processed_cells.add((x, y))
            changed_cells.add((x, y))
            if is_mine:
                flags_placed += 1

        if flags_placed == num_mines:
            for i in range(size):
                for j in range(size):
                    if player_info[i, j] == UNKNOWN_CHAR:
                        is_dead, known_cells, player_info, is_finished = play_function(
                            mine_grid,
                            neighbor_mines,
                            known_cells,
                            player_info,
                            size,
                            "non",
                            i,
                            j,
                        )
                        turns += 1

        prev_safe_cells = safe_cells
        safe_cells = set(find_safe_cells(set(), player_info, size))
        mine_cells = set(logic_function(player_info))
        stuck_counter = stuck_counter + 1 if safe_cells == prev_safe_cells else 0

        if is_finished and not is_dead:
            return "grille resolue", turns
        elif is_finished and is_dead:
            return "Bombe", turns

    return "non aboutie", turns


def is_valid(grid, x, y):
    """Check if coordinates are within grid bounds."""
    return 0 <= x < len(grid) and 0 <= y < len(grid)


def find_interesting_cells(player_info):
    """Identify cells with numbers that have at least one unknown neighbor."""
    cells = []
    for i in range(player_info.shape[0]):
        for j in range(player_info.shape[1]):
            val = player_info[i, j]
            if val not in (UNKNOWN_CHAR, FLAG_CHAR, "0") and has_unknown_neighbor(
                player_info, i, j
            ):
                cells.append((i, j))
    return cells


def find_safe_cells(safe_cells, player_info, size):
    """Find cells where all adjacent mines are flagged, making remaining unknowns safe."""
    interesting_cells = find_interesting_cells(player_info)
    safe_cells_list = []
    for x, y in interesting_cells:
        unknown_count = 0
        flag_count = 0
        for dx, dy in [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]:
            nx, ny = x + dx, y + dy
            if is_valid(player_info, nx, ny):
                if player_info[nx, ny] == UNKNOWN_CHAR:
                    unknown_count += 1
                elif player_info[nx, ny] == FLAG_CHAR:
                    flag_count += 1
        if flag_count == int(player_info[x, y]):
            safe_cells_list.append((x, y))
    return safe_cells_list


def has_unknown_neighbor(player_info, x, y):
    """Check if the cell at (x, y) has at least one unknown neighbor."""
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < player_info.shape[0] and 0 <= ny < player_info.shape[1]:
                if player_info[nx, ny] == UNKNOWN_CHAR:
                    return True
    return False


def check_elementary_logic(player_info):
    """Identify cells where the number of unknown neighbors equals the number of mines."""
    interesting_cells = find_interesting_cells(player_info)
    mine_cells = []
    for x, y in interesting_cells:
        neighbor_count = 0
        for dx, dy in [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]:
            nx, ny = x + dx, y + dy
            if is_valid(player_info, nx, ny) and player_info[nx, ny] in (
                UNKNOWN_CHAR,
                FLAG_CHAR,
            ):
                neighbor_count += 1
        if neighbor_count == int(player_info[x, y]):
            mine_cells.append((x, y))
    return mine_cells


def play_computer(
    mine_grid, neighbor_mines, known_cells, player_info, size, flag, x, y
):
    """Execute a computer move (flag or reveal)."""
    is_dead = False
    is_finished = False
    (
        player_info,
        mine_grid,
        neighbor_mines,
        known_cells,
        x,
        y,
        flag,
        is_finished,
        is_dead,
    ) = make_move(
        player_info,
        mine_grid,
        neighbor_mines,
        known_cells,
        x,
        y,
        flag,
        is_finished,
        is_dead,
    )
    reveal(neighbor_mines, x, y, known_cells)
    update_player_info(player_info, known_cells, neighbor_mines, size)

    mine_count = np.sum(mine_grid == MINE)
    flagged_mines = np.sum((player_info == FLAG_CHAR) & (mine_grid == MINE))
    has_unknown = UNKNOWN_CHAR in player_info
    if flagged_mines == mine_count and not has_unknown:
        is_finished = True
    return is_dead, known_cells, player_info, is_finished


def count_neighbor_mines(mine_grid):
    """Calculate the number of mines adjacent to each cell."""
    size = mine_grid.shape[0]
    neighbor_mines = np.zeros((size, size), dtype=int)
    for i in range(size):
        for j in range(size):
            if mine_grid[i, j] == MINE:
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        ni, nj = i + di, j + dj
                        if is_valid(mine_grid, ni, nj) and (di != 0 or dj != 0):
                            neighbor_mines[ni, nj] += 1
    return neighbor_mines


def setup_grid(size, num_mines, start_x, start_y):
    """Initialize the game grid with mines and revealed starting area."""
    known_cells = np.zeros(shape=(size, size), dtype=int)
    mine_grid = np.zeros(shape=(size, size), dtype=int)

    # Mark starting area as safe (2 temporarily)
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            nx, ny = start_x + dx, start_y + dy
            if is_valid(mine_grid, nx, ny):
                mine_grid[nx, ny] = 2

    # Place mines randomly, avoiding the starting area
    mines_placed = 0
    while mines_placed < num_mines:
        x, y = random.randint(0, size - 1), random.randint(0, size - 1)
        if mine_grid[x, y] == SAFE:
            mine_grid[x, y] = MINE
            mines_placed += 1

    # Reveal starting area
    for i in range(size):
        for j in range(size):
            if mine_grid[i, j] == 2:
                mine_grid[i, j] = SAFE
                known_cells[i, j] = REVEALED

    neighbor_mines = count_neighbor_mines(mine_grid)
    reveal(neighbor_mines, start_x, start_y, known_cells)
    return mine_grid, neighbor_mines, known_cells


def reveal(neighbor_mines, x, y, known_cells):
    """Reveal a cell and its neighbors recursively if no mines are adjacent."""
    if not is_valid(neighbor_mines, x, y) or known_cells[x, y] != UNKNOWN:
        return
    known_cells[x, y] = REVEALED
    if neighbor_mines[x, y] == 0:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    reveal(neighbor_mines, x + dx, y + dy, known_cells)


def make_move(
    player_info,
    mine_grid,
    neighbor_mines,
    known_cells,
    x,
    y,
    flag,
    is_finished,
    is_dead,
):
    """Process a single move (flag or reveal)."""
    if not is_valid(mine_grid, x, y) or known_cells[x, y] in (REVEALED, 2):
        return (
            player_info,
            mine_grid,
            neighbor_mines,
            known_cells,
            x,
            y,
            flag,
            is_finished,
            is_dead,
        )

    if known_cells[x, y] == FLAGGED and flag in ("non", "n"):
        known_cells[x, y] = UNKNOWN
    elif mine_grid[x, y] == MINE and flag in ("non", "n"):
        is_finished = True
        is_dead = True
    elif flag in ("oui", "o"):
        known_cells[x, y] = FLAGGED
    elif mine_grid[x, y] == SAFE and flag in ("non", "n"):
        known_cells[x, y] = REVEALED
    return (
        player_info,
        mine_grid,
        neighbor_mines,
        known_cells,
        x,
        y,
        flag,
        is_finished,
        is_dead,
    )


def update_player_info(player_info, known_cells, neighbor_mines, size):
    """Update the player's view using vectorized NumPy operations."""
    revealed_mask = known_cells == REVEALED
    flagged_mask = known_cells == FLAGGED
    player_info[revealed_mask] = neighbor_mines[revealed_mask].astype(str)
    player_info[flagged_mask] = FLAG_CHAR
    player_info[~revealed_mask & ~flagged_mask] = UNKNOWN_CHAR


def play_manually(size, num_mines):
    """Play Minesweeper manually via console input."""
    x = int(input("Row: "))
    y = int(input("Column: "))
    mine_grid, neighbor_mines, known_cells = setup_grid(size, num_mines, x, y)
    player_info = np.full((size, size), UNKNOWN_CHAR, dtype=object)
    update_player_info(player_info, known_cells, neighbor_mines, size)
    print(player_info)

    is_finished = False
    while not is_finished:
        x = int(input("Row: "))
        y = int(input("Column: "))
        flag = input("Flag (yes/no): ").lower()
        (
            player_info,
            mine_grid,
            neighbor_mines,
            known_cells,
            x,
            y,
            flag,
            is_finished,
            is_dead,
        ) = make_move(
            player_info,
            mine_grid,
            neighbor_mines,
            known_cells,
            x,
            y,
            flag,
            False,
            False,
        )
        reveal(neighbor_mines, x, y, known_cells)
        update_player_info(player_info, known_cells, neighbor_mines, size)

        mine_count = np.sum(mine_grid == MINE)
        correct_flags = np.sum((known_cells == FLAGGED) & (mine_grid == MINE))
        has_unknown = UNKNOWN in known_cells
        if correct_flags == mine_count and not has_unknown:
            is_finished = True
            print(player_info)
            print("Bravo, vous avez gagné")
        elif is_dead:
            is_finished = True
            print(player_info)
            print("Raté, vous avez perdu")
        else:
            print(player_info)


def calculate_weights(player_info, changed_cells, neighbors):
    """Incrementally update weights based on changed cells."""
    size = player_info.shape[0]
    weights = np.zeros((size, size), dtype=float)
    interesting_cells = set()
    for x, y in changed_cells:
        interesting_cells.update(
            (nx, ny)
            for nx, ny in neighbors[(x, y)]
            if player_info[nx, ny] not in (UNKNOWN_CHAR, FLAG_CHAR, "0")
        )
    for i, j in interesting_cells:
        if not has_unknown_neighbor(player_info, i, j):
            continue
        unknowns = [
            n for n in neighbors[(i, j)] if player_info[n[0], n[1]] == UNKNOWN_CHAR
        ]
        unknown_count = len(unknowns)
        if unknown_count > 0:
            flag_count = sum(
                1 for n in neighbors[(i, j)] if player_info[n[0], n[1]] == FLAG_CHAR
            )
            weight = (int(player_info[i, j]) - flag_count) / unknown_count
            for ux, uy in unknowns:
                weights[ux, uy] += weight
    return weights


def get_unknown_neighbors(player_info, x, y):
    """Get coordinates and count of unknown neighbors."""
    unknowns_x, unknowns_y = [], []
    count = 0
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if is_valid(player_info, nx, ny) and player_info[nx, ny] == UNKNOWN_CHAR:
                unknowns_x.append(nx)
                unknowns_y.append(ny)
                count += 1
    return unknowns_x, unknowns_y, count


def count_flags(player_info, x, y):
    """Count flagged neighbors."""
    count = 0
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if is_valid(player_info, nx, ny) and player_info[nx, ny] == FLAG_CHAR:
                count += 1
    return count


def find_max_weight_cell(weights, player_info):
    """Find the unknown cell with the highest weight."""
    max_weight = -np.inf
    max_x, max_y = 0, 0
    for i in range(weights.shape[0]):
        for j in range(weights.shape[1]):
            if player_info[i, j] == UNKNOWN_CHAR and weights[i, j] > max_weight:
                max_weight = weights[i, j]
                max_x, max_y = i, j
    if max_weight == -np.inf:  # No weighted cell found, pick random unknown
        unknowns_x, unknowns_y = np.where(player_info == UNKNOWN_CHAR)
        idx = random.randint(0, len(unknowns_x) - 1)
        return unknowns_x[idx], unknowns_y[idx]
    return max_x, max_y


if __name__ == "__main__":
    gather_solver_statistics(20, 10, 1000)
