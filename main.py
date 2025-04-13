import random
from heapq import heappush, heappop

from constant import *

class Game:
    def __init__(self):
        pygame.init()

        self.display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_caption(DISPLAY_TITLE)

        self.clock = pygame.time.Clock()
        self.delta = 0

        self.running = True

        #   Player
        self.player_pos = [0, 0]
        self.player_rect = self.update_rect()

        #   Movement
        self.path = []
        self.step_timer = 0
        self.step_delay = 0.1

        #   Obstacles
        self.obstacles = set()
        self.generate_obstacles()

        self.blink_obstacle = None
        self.blink_timer = 0

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.running:
                    self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = mouse_x // TILE_SIZE
                grid_y = mouse_y // TILE_SIZE

                if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                    start = tuple(self.player_pos)
                    goal = (grid_x, grid_y)

                    if goal in self.obstacles:
                        print("Position is blocked.")

                        #   Visual feedback
                        self.blink_obstacle = goal
                        self.blink_timer = OBSTACLE_BLINK_DURATION
                        return

                    self.path = self.a_star(start, goal)

                    #   Jump to position (no pathfinding)
                    # self.player_pos = [grid_x, grid_y]

    def a_star(self, start, goal):

        #   Manhattan distance (from tile to goal)
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        #   Priority queue (holding next node)
        open_set = []

        #   Push start node into priority queue
        heappush(open_set, (0, start))

        #   Stores the best previous step to reach a node
        origin = {}

        #   Cost from start to the current node
        g_score = {start: 0}

        #   Estimated cost from start to goal through a node
        f_score = {start: heuristic(start, goal)}

        while open_set:

            #   Go to next node with lowest f_score
            _, current = heappop(open_set)

            #   Follow path through origin if the goal is reached
            if current == goal:
                path = []
                while current in origin:
                    path.append(current)
                    current = origin[current]
                path.reverse()
                return path

            #   Nearby paths (left, right, up, down)
            neighbors = [
                (current[0] + dx, current[1] + dy)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
            ]

            for neighbor in neighbors:

                #   Skip any paths outside the grid
                if not (0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT):
                    continue

                #   Skip (avoid) obstacles
                if neighbor in self.obstacles:
                    continue

                #   Check path cost (update g_score, f_score and add neighbor to open_set)
                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(neighbor, float("inf")):
                    origin[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                    heappush(open_set, (f_score[neighbor], neighbor))

        #   No path found
        return []

    def generate_obstacles(self):
        tile_amount = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)]

        #   Remove player start position
        tile_amount.remove(tuple(self.player_pos))

        random.shuffle(tile_amount)
        obstacle_amount = int(len(tile_amount) * OBSTACLE_PERCENT)
        self.obstacles = set(tile_amount[:obstacle_amount])

    def update_rect(self):
        return pygame.Rect(self.player_pos[0] * TILE_SIZE, self.player_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def update(self):

        #   Movement
        self.step_timer += self.delta

        if self.path and self.step_timer >= self.step_delay:
            self.step_timer = 0
            next_step = self.path.pop(0)
            self.player_pos = list(next_step)

        #   Obstacle blink
        if self.blink_timer > 0:
            self.blink_timer -= self.delta
            if self.blink_timer <= 0:
                self.blink_obstacle = None

    def render(self):
        self.display.fill(WHITE)

        for x in range(0, DISPLAY_WIDTH, TILE_SIZE):
            pygame.draw.line(self.display, BLACK, (x, 0), (x, DISPLAY_HEIGHT))
        for y in range(0, DISPLAY_HEIGHT, TILE_SIZE):
            pygame.draw.line(self.display, BLACK, (0, y), (DISPLAY_WIDTH, y))

        for obstacle in self.obstacles:
            rect = pygame.Rect(obstacle[0] * TILE_SIZE, obstacle[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if obstacle == self.blink_obstacle:
                pygame.draw.rect(self.display, OBSTACLE_BLINK_COLOR, rect)
            else:
                pygame.draw.rect(self.display, OBSTACLE_COLOR, rect)

        self.player_rect = self.update_rect()
        pygame.draw.rect(self.display, PLAYER_COLOR, self.player_rect)

        pygame.display.update()

    def run(self):
        while self.running:
            self.delta = self.clock.tick(60) * 0.001

            self.events()
            self.update()
            self.render()

if __name__ == "__main__":
    game = Game()
    game.run()