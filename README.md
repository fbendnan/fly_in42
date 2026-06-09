# fly_in42


while not all_delivered:
    # 1. Reset connection_usage for this turn
    self.connection_usage.clear()
    
    # 2. Build list of move proposals
    proposals = []  # each proposal = (drone, from_zone, to_zone, connection, move_type)
    
    # 3. Handle drones that are "in_transit" (must arrive this turn)
    
    # 4. Handle drones that are "in_zone" (propose next move from their path)
    
    # 5. Validate proposals against capacities (zone + connection)
    #    - Account for drones leaving zones (they free capacity for same turn)
    #    - For normal moves: check destination zone capacity (after departures)
    #    - For restricted moves: also check that destination will have capacity next turn (reserve)
    
    # 6. Apply valid moves (update zone_occupancy, drone states)
    
    # 7. Build output string for this turn and print/store
    
    # 8. Increment turn