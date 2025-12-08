from shapely import LineString
from navigator.roadmap.edge import Edge
from navigator.roadmap.node import Node

class Road(Edge):

    def __init__(self, start: Node | None, end: Node | None, geometry: LineString,
    max_speed:str, lanes:int | None, oneway:bool, road_type:str, length:float) -> None:
        super().__init__(start, end, geometry)
        # max_speed is in str format ie: "30 mph"
        # so we will parse it and make sure everything is in mph
        max_speed_str, speed_limit_units = max_speed.split()
        self.data['speed_limit'] = int(max_speed_str)
        self.data['speed_limit_units'] = speed_limit_units
        self.data['lanes'] = lanes
        self.data['oneway'] = oneway
        self.data['road_type'] = road_type
        # length is in meters, so we will convert to miles like speed limit
        self.data['length'] = length / 1609.344
        