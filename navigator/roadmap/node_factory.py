from typing import Any
from navigator.roadmap.node import Node
from pandas import Series
from geopandas import GeoDataFrame

from navigator.roadmap.node_types import Junction, ShapePoint, TrafficControl

class NodeFactory:
    """
    Helper to convert GeoDataFrame rows to Nodes
    """

    @classmethod
    def produce(cls, row:Series, edges_gdf:GeoDataFrame) -> Node:
        if isinstance(row["tags"], dict) and row["tags"].get("highway") in {
            "traffic_signals", "stop", "crossing", "give_way", "roundabout"
        }:
            # road can be driven on
            return TrafficControl(
                row['id'],
                row['lon'],
                row['lat'],
                row.get('tags', {}) if row.get('tags', {}) else {}
            )
        edges_connected = edges_gdf[(edges_gdf.u == row['id']) | (edges_gdf.v == row['id'])]
        if not row["tags"] and len(edges_connected) == 2:
            return ShapePoint(
                row['id'],
                row['lon'],
                row['lat'],
                row.get('tags', {}) if row.get('tags', {}) else {}
            )
        if len(edges_connected) >= 3:
            return Junction(
                row['id'],
                row['lon'],
                row['lat'],
                row.get('tags', {}) if row.get('tags', {}) else {},
                len(edges_connected)
            )
        return Node(
            row['id'],
            row['lon'],
            row['lat'],
            row.get('tags', {}) if row.get('tags', {}) else {}
        )
        
