from typing import Any
from navigator.roadmap.node import Node

class RoadNode(Node):
    """
    This class acts as a base for "road-type" nodes.
    """
    pass

class TrafficControl(RoadNode):
    """
    Connects two or more roads and may cause a stop.
    """
    def __init__(self, id: int, x: float, y: float, tags: dict[str, Any]) -> None:
        super().__init__(id, x, y, tags)
        self.data['dead_end'] = False
        self.data['causes_stops'] = True

    def __repr__(self) -> str:
        return f"TrafficControl(id: {self.id}, x: {self.x}, y: {self.y})"

class ShapePoint(RoadNode):
    """
    Connects two or more roads but doesn't cause stopping.
    Roads connected by shape points are the same road.
    """
    def __init__(self, id: int, x: float, y: float, tags: dict[str, Any]) -> None:
        super().__init__(id, x, y, tags)
        self.data['dead_end'] = False
        self.data['causes_stops'] = False

    def __repr__(self) -> str:
        return f"ShapePoint(id: {self.id}, x: {self.x}, y: {self.y})"

class Junction(RoadNode):
    """
    Connects three or more roads. Is either a junction or an intersection.
    """
    def __init__(self, id: int, x: float, y: float, tags: dict[str, Any], connections:int) -> None:
        super().__init__(id, x, y, tags)
        self.data['dead_end'] = False
        self.data['connections'] = connections

    def __repr__(self) -> str:
        return f"Junction(id: {self.id}, x: {self.x}, y: {self.y})"

class DeadEnd(RoadNode):
    def __init__(self, id: int, x: float, y: float, tags: dict[str, Any]) -> None:
        super().__init__(id, x, y, tags)
        self.data['dead_end'] = True
        self.data['connections'] = 1

    def __repr__(self) -> str:
        return f"DeadEnd(id: {self.id}, x: {self.x}, y: {self.y})"
