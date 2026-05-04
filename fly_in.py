import sys
from parser.parsing import ParseConfig


try:
    if len(sys.argv) != 2:
        raise ValueError("You should enter: python3 fly_in.py config.txt")
    CONFIG_FILE = sys.argv[1]
    configuration = ParseConfig(CONFIG_FILE)
    configuration.parser()
 
except (Exception, KeyboardInterrupt) as e:
    print(e)

