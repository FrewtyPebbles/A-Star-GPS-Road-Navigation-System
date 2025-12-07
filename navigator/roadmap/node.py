from __future__ import annotations
from typing import Any, Literal, TYPE_CHECKING
if TYPE_CHECKING:
    from navigator.roadmap.edge import Edge

class Node:
    id:int
    x:float
    y:float
    tags:dict[str, Any]
    edges:list[Edge]
    data:dict[Literal['causes_stops', 'connections', 'dead_end'], Any]

    def __init__(self, id:int, x:float, y:float, tags:dict[str, Any]) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.edges = []
        self.tags = tags
        self.data = {}

    def __repr__(self) -> str:
        return f"Node(id: {self.id}, x: {self.x}, y: {self.y}, edges(count): {len(self.edges)})"
    
    def __hash__(self) -> int:
        return self.id
