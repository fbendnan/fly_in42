import math
from collections import defaultdict
from typing import Dict, Optional, List, Tuple, DefaultDict

import pygame

from helpers.sim import Simulation
from helpers.dron import Drone


SCREEN_WIDTH = 1900
SCREEN_HEIGHT = 950
MARGIN = 80
ZONE_RADIUS = 32
DRONE_SIZE = 20

COLOR_MAP: Dict[str, Tuple[int, int, int]] = {
    "red": (200, 50, 50),
    "green": (50, 200, 50),
    "blue": (50, 50, 200),
    "yellow": (220, 220, 0),
    "black": (30, 30, 30),
    "white": (240, 240, 240),
    "gray": (120, 120, 120),
    "purple": (160, 50, 160),
    "orange": (240, 140, 0),
    "cyan": (0, 200, 200),
    "brown": (150, 75, 0),
    "lime": (100, 200, 0),
    "magenta": (200, 0, 200),
    "gold": (200, 170, 0),
}
DEFAULT_ZONE_COLOR: Tuple[int, int, int] = (100, 100, 100)


class Display:
    def __init__(self, simulation: Simulation) -> None:
        self.sim: Simulation = simulation
        self.graph = simulation.graph
        self.zones = self.graph.zones_dict
        self.min_x = min(z["x"] for z in self.zones.values())
        self.max_x = max(z["x"] for z in self.zones.values())
        self.min_y = min(z["y"] for z in self.zones.values())
        self.max_y = max(z["y"] for z in self.zones.values())

        if self.max_x == self.min_x:
            self.max_x += 1
        if self.max_y == self.min_y:
            self.max_y += 1

        self.drone_img: Optional[pygame.Surface] = None
        self.font_zone: Optional[pygame.font.Font] = None
        self.font_small: Optional[pygame.font.Font] = None

    def _to_screen(self, x: float, y: float) -> Tuple[int, int]:
        sx = (
            MARGIN
            + (x - self.min_x)
            * (SCREEN_WIDTH - 2 * MARGIN)
            / (self.max_x - self.min_x)
        )
        sy = (
            MARGIN
            + (y - self.min_y)
            * (SCREEN_HEIGHT - 2 * MARGIN)
            / (self.max_y - self.min_y)
        )
        return int(sx), int(sy)

    def draw_connections(self, screen: pygame.Surface) -> None:
        if self.font_small is None:
            return
        drawn: set[Tuple[str, str]] = set()
        for zone in self.zones.values():
            start = self._to_screen(zone["x"], zone["y"])

            for neighbor, conn in zone["neighbors"]:
                edge = tuple(
                    sorted((zone["name"], neighbor["name"]))
                )
                if edge in drawn:
                    continue

                drawn.add(edge)
                end = self._to_screen(
                    neighbor["x"], neighbor["y"]
                )
                cap = conn["max_link_capacity"]

                pygame.draw.line(
                    screen,
                    (100, 100, 100),
                    start,
                    end,
                )

                mx = (start[0] + end[0]) // 2
                my = (start[1] + end[1]) // 2 - 10

                cap_text = self.font_small.render(
                    str(cap),
                    True,
                    (90, 90, 180),
                )
                screen.blit(cap_text, (mx, my))

    def draw_zones(self, screen: pygame.Surface) -> None:
        if self.font_zone is None or self.font_small is None:
            return
        for name, zone in self.zones.items():
            color = COLOR_MAP.get(
                zone["color"],
                DEFAULT_ZONE_COLOR,
            )
            cx, cy = self._to_screen(
                zone["x"], zone["y"]
            )

            pygame.draw.circle(
                screen,
                (0, 0, 0),
                (cx + 2, cy + 2),
                ZONE_RADIUS,
                0,
            )
            pygame.draw.circle(
                screen,
                color,
                (cx, cy),
                ZONE_RADIUS,
            )
            pygame.draw.circle(
                screen,
                (0, 0, 0),
                (cx, cy),
                ZONE_RADIUS,
                1,
            )

            name_text = self.font_zone.render(
                name,
                True,
                (0, 0, 0),
            )

            if name_text.get_width() > ZONE_RADIUS * (2 - 0.2):
                smaller_font = pygame.font.Font(
                    None,
                    self.font_zone.get_height() + 4,
                )
                name_text = smaller_font.render(
                    name,
                    True,
                    (0, 0, 0),
                )

            name_rect = name_text.get_rect(
                center=(cx, cy - 5)
            )
            screen.blit(name_text, name_rect)

            cap_text = self.font_small.render(
                f"max:{zone['max_drones']}",
                True,
                (255, 255, 255),
            )
            cap_rect = cap_text.get_rect(
                center=(cx, cy + ZONE_RADIUS - 12)
            )
            screen.blit(cap_text, cap_rect)

    def draw_drones(self, screen: pygame.Surface) -> None:
        if self.drone_img is None or self.font_small is None:
            return

        zone_drones: DefaultDict[str, List[Drone]] = defaultdict(list)
        in_transit_drones: List[Drone] = []

        for drone in self.sim.drones:
            if drone.state == "delivered":
                zone_drones[self.sim.end].append(drone)
            elif drone.state == "in_zone":
                zone_drones[drone.current_zone].append(drone)
            elif drone.state == "in_transit":
                in_transit_drones.append(drone)

        for zone_name, drones in zone_drones.items():
            if not drones:
                continue

            zone = self.zones[zone_name]
            cx, cy = self._to_screen(
                zone["x"], zone["y"]
            )
            total = len(drones)

            for idx, drone in enumerate(drones):
                angle = 2 * math.pi * idx / total
                off_x = int(15 * math.cos(angle))
                off_y = int(15 * math.sin(angle))

                pos = (
                    cx + off_x - DRONE_SIZE // 2,
                    cy + off_y - DRONE_SIZE // 2,
                )
                screen.blit(self.drone_img, pos)

                dron_id_text = self.font_small.render(
                    str(drone.id),
                    True,
                    (120, 80, 90),
                )
                dron_id_rect = dron_id_text.get_rect(
                    center=(cx + off_x, cy + off_y)
                )
                screen.blit(dron_id_text, dron_id_rect)

        # Draw drones in transit
        for drone in in_transit_drones:
            from_zone = self.zones[drone.current_zone]
            to_zone = self.zones[drone.target_zone]

            start = self._to_screen(
                from_zone["x"],
                from_zone["y"],
            )
            end = self._to_screen(
                to_zone["x"],
                to_zone["y"],
            )

            t = 0.5
            mx = start[0] + t * (end[0] - start[0])
            my = start[1] + t * (end[1] - start[1])

            pos = (
                int(mx) - DRONE_SIZE // 2,
                int(my) - DRONE_SIZE // 2,
            )
            screen.blit(self.drone_img, pos)

            dron_id_text = self.font_small.render(
                str(drone.id),
                True,
                (255, 255, 255),
            )
            dron_id_rect = dron_id_text.get_rect(
                center=(int(mx), int(my))
            )
            screen.blit(dron_id_text, dron_id_rect)

    def goo(self, delay_ms: int = 4000) -> None:
        pygame.init()

        self.font_zone = pygame.font.Font(None, 15)
        self.font_small = pygame.font.Font(None, 14)

        screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Fly-in")

        self.drone_img = pygame.Surface(
            (DRONE_SIZE, DRONE_SIZE),
            pygame.SRCALPHA,
        )
        pygame.draw.circle(
            self.drone_img,
            (1, 5, 0),
            (DRONE_SIZE // 2, DRONE_SIZE // 2),
            DRONE_SIZE // 2,
        )

        running = True
        simulation_finished = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if not simulation_finished:
                finished = self.sim.step()

                if finished:
                    simulation_finished = True
                    print("total turns = ", self.sim.turns)
                    print(
                        "Simulation finished. "
                        "Close the window to exit."
                    )

                screen.fill((255, 255, 255))
                self.draw_connections(screen)
                self.draw_zones(screen)
                self.draw_drones(screen)
                pygame.display.flip()

                if not simulation_finished:
                    pygame.time.delay(delay_ms)

        pygame.quit()
