class Zone():
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.neighbors = []
        self.is_visited = False