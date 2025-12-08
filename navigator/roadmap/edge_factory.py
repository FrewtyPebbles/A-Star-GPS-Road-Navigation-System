from typing import Any
from pandas import Series
from navigator.roadmap.edge_types import Road
from navigator.roadmap.edge import Edge
from navigator.roadmap.node import Node


class EdgeFactory(Edge):
    """
    Helper to convert GeoDataFrame rows to Edges
    """

    HIGHWAY_DRIVABLE = {
        "motorway", "motorway_link",
        "trunk", "trunk_link",
        "primary", "primary_link",
        "secondary", "secondary_link",
        "tertiary", "tertiary_link",
        "residential",
        "unclassified",
        "service", "living_street", "services"
    }

    @classmethod
    def produce(cls, row:Series, start_node:Node | None, end_node:Node | None) -> Edge:
        if row["highway"] in cls.HIGHWAY_DRIVABLE:
            # road can be driven on
            return Road(
                start_node,
                end_node,
                geometry = row.geometry,
                max_speed = row.get('maxspeed', "25 mph") if row.get('maxspeed', "25 mph") else "25 mph",
                lanes = row.get('lanes', 1),
                oneway = row.get('oneway', True),
                road_type = row.get('highway', "unknown"),
                length = row.get('length', 9999999.0)
            )
        else:
            return Edge(
                start_node,
                end_node,
                geometry = row.geometry
            )