import pygame


SCREEEN_HEIGHT = 500
SCREEN_WIDTH = 800
MARGIN = 50
COLOR_MAP = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
}

class display:
    def __init__(self, graph):
        self.graph = graph
        self.max_x = max(zone.x for zone in self.graph.zones_dict.values())
        self.max_y = max(zone.y for zone in self.graph.zones_dict.values())

    def draw_zones(self, screen):
        font = pygame.font.Font(None, 30)
        
        for name, zone in self.graph.zones_dict.items():
            color = COLOR_MAP.get(zone.color, (128, 128, 128))
            screen_x = int(MARGIN + zone.x * (SCREEN_WIDTH - 2 * MARGIN) / self.max_x)
            screen_y = int(MARGIN + zone.y * (SCREEEN_HEIGHT - 2 * MARGIN) / self.max_y)
            text = font.render(zone.name, True, (255, 0, 0))
            screen.blit(text, (screen_x - 28, screen_y - 37))
            # print(zone)
            pygame.draw.circle(screen, color, (screen_x, screen_y), 20)


    def draw_conn(self, screen):
        for zone in self.graph.zones_dict.values():
            zone_screen_x = int(MARGIN + zone.x * (SCREEN_WIDTH - 2 * MARGIN) / self.max_x)                
            zone_screen_y = int(MARGIN + zone.y * (SCREEEN_HEIGHT - 2 * MARGIN) / self.max_y)
            for neighbor, conn in zone.neighbors:

                neighbor_screen_x = int(MARGIN + neighbor.x * (SCREEN_WIDTH - 2 * MARGIN) / self.max_x)
                neighbor_screen_y = int(MARGIN + neighbor.y * (SCREEEN_HEIGHT - 2 * MARGIN) / self.max_y)
                pygame.draw.line(screen, (0, 0, 0), (zone_screen_x, zone_screen_y), (neighbor_screen_x, neighbor_screen_y), 2)

    def run(self, path):
        pygame.init()
        run = True
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEEN_HEIGHT))
        pygame.display.set_caption("FLY_IN")
        clock = pygame.time.Clock()
        while run:
            screen.fill((255, 255, 255))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            self.draw_conn(screen)
            self.draw_zones(screen)
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()