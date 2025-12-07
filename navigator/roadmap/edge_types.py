from shapely import LineString
from navigator.roadmap.edge import Edge
from navigator.roadmap.node import Node

class Road(Edge):

    def __init__(self, start: Node | None, end: Node | None, geometry: LineString,
    max_speed:float | None, lanes:int | None, oneway:bool, road_type:str, length:float) -> None:
        super().__init__(start, end, geometry)
        self.data['max_speed'] = max_speed
        self.data['lanes'] = lanes
        self.data['oneway'] = oneway
        self.data['road_type'] = road_type
        self.data['length'] = length
        