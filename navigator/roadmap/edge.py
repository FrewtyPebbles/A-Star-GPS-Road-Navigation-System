from __future__ import annotations
from typing import TYPE_CHECKING, Any, Literal
from shapely.geometry import LineString
from navigator.roadmap.node import Node
from navigator.roadmap.types import EdgeDataDict

class Edge:
    start:Node | None
    end:Node | None
    geometry:LineString
    data:EdgeDataDict
    

    def __init__(self, start:Node | None, end:Node | None, geometry:LineString) -> None:
        self.start = start
        self.end = end
        self.geometry = geometry
        self.data = {}

    def __repr__(self) -> str:
        return f"Edge(start{{{self.start.id if self.start else 'NONE'}}} -> end{{{self.end.id if self.end else 'NONE'}}})"

