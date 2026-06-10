import sys
from graph import GraphBuilder
# from simulation import Simulation
from display import display
from algo.PathFinder import PathFinder

# from parse.parsing import ParseConfig

# try:
if len(sys.argv) != 2:
    raise ValueError("You should enter: python3 fly_in.py config.txt")
CONFIG_FILE = sys.argv[1]
# parser = ParseConfig(CONFIG_FILE)
# parser.parser()

g = GraphBuilder(CONFIG_FILE)
g.build()
g.add_zone_neighbors()
g.add_costs()


start = g.data.start_hub.name
end = g.data.end_hub.name
# sim = Simulation(g, g.data.nb_drones)
# sim.run_simulation()
path_finder = PathFinder(g)
path = path_finder.dijkstra()

g.create_drones(path)
view = display(g)
view.run(path)



# print("path = ", p.dijkstra())


# print(parser.nb_drones)
# print(parser.start_hub.name, parser.start_hub.x, parser.start_hub.y)
# for hub in parser.hubs:
#     print(hub.name, hub.zone, hub.x, hub.y, hub.color)
# for conn in parser.connections:
#     print(conn.zone1, conn.zone2, conn.max_link_capacity)

# except (Exception, KeyboardInterrupt) as e:
#     print(e)
