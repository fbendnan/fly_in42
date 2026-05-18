import sys
from parser.parsing import ParseConfig


try:
    if len(sys.argv) != 2:
        raise ValueError("You should enter: python3 fly_in.py config.txt")
    CONFIG_FILE = sys.argv[1]
    # configuration = ParseConfig(CONFIG_FILE)
    # configuration.parser()
    parser = ParseConfig(CONFIG_FILE)
    parser.parser()   # parses and validates

    # print(parser.nb_drones)
    # print(parser.start_hub.name, parser.start_hub.x, parser.start_hub.y)
    # for hub in parser.hubs:
    #     print(hub.name, hub.zone, hub.x, hub.y, hub.color)
    # for conn in parser.connections:
    #     print(conn.zone1, conn.zone2, conn.max_link_capacity)
 
except (Exception, KeyboardInterrupt) as e:
    print(e)

