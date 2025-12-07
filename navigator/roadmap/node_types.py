from typing import Any
from navigator.roadmap.node import Node

class TrafficControl(Node):
    """
    Connects two or more roads and may cause a stop.
    """
    def __init__(self, id: int, x: float, y: float, tags: dict[str, Any]) -> None:
        super().__init__(id, x, y, tags)
        self.data['causes_stops'] = True

class ShapePoint(Node):
    """
    Connects two or more roads but doesn't cause stopping.
    Roads connected by shape points are the same road.
    """
    def __init__(self, id: int, x: float, y: float, tags: dict[str, Any]) -> None:
        super().__init__(id, x, y, tags)
        self.data['causes_stops'] = False

class Junction(Node):
    """
    Connects three or more roads. Is either a junction or an intersection.
    """
    def __init__(self, id: int, x: float, y: float, tags: dict[str, Any], connections:int) -> None:
        super().__init__(id, x, y, tags)
        self.data['connections'] = connections

class DeadEnd(Node):
    def __init__(self, id: int, x: float, y: float, tags: dict[str, Any]) -> None:
        super().__init__(id, x, y, tags)
        self.data['dead_end'] = True
        self.data['connections'] = 1
