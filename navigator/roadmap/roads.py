from __future__ import annotations
from shapely.geometry import Point, LineString

class Junction:
    id:int
    x:float
    y:float
    roads:list[Road]

    def __init__(self, id:int, x:float, y:float) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.edges = []

    def __repr__(self) -> str:
        return f"Junction(id: {self.id}, x: {self.x}, y: {self.y}, roads(count): {len(self.roads)})"
    
    def __hash__(self) -> int:
        return self.id
    
class Road:
    start:Junction
    end:Junction
    length:float
    road_type:str # TODO : Replace with an enumerator
    oneway:bool
    geometry:LineString

    def __init__(self, start:Junction, end:Junction, length:float, road_type:str, oneway:bool, geometry:LineString) -> None:
        self.start = start
        self.end = end
        self.length = length
        self.road_type = road_type
        self.oneway = oneway
        self.geometry = geometry

    def __repr__(self) -> str:
        return f"Road(start{{{self.start.id}}} -> end{{{self.end.id}}}, length: {self.length}m, type: {self.road_type}, oneway: {self.oneway})"
