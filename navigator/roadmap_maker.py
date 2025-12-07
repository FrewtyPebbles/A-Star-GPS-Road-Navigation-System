import pickle
import os
from typing import Any, Literal
from pyrosm import OSM
from geopandas import GeoDataFrame
from pathlib import Path

from navigator.roadmap import RoadMap, Node, Edge, NodeFactory, EdgeFactory

class RoadMapMaker:
    """
    This class reads the graph data file and
    turns it into a graph called a `RoadMap`.
    """
    bounding_box:list[float]
    pbf_file_path:Path
    cache_name:str
    cache_folder:Path
    stdout_enabled:bool
    
    def __init__(self,
        bounding_box:list[float],
        pbf_file_path:str,
        cache_name:str,
        cache_folder_name:str = ".GEOCACHE",
        stdout_enabled:bool = True
    ):
        self.bounding_box = bounding_box
        self.pbf_file_path = Path(pbf_file_path)
        self.cache_name = cache_name
        self.cache_folder = Path("./" + cache_folder_name)
        self.cache_folder.mkdir(exist_ok=True)
        self.stdout_enabled = stdout_enabled

    def print(self, msg:Any):
        if self.stdout_enabled:
            print(str(msg))

    def get_cache_file_path(self, file_suffix:str) -> Path:
        return self.cache_folder / f"{self.cache_name}{file_suffix}.pkl"

    def _cache_gdf(self, gdf:GeoDataFrame, tag:str):
        self.print(f"Saving geodataframe cache with tag: {tag}")

        with open(self.get_cache_file_path(f"_{tag}_gdf"), "wb") as f:
            pickle.dump(gdf, f, protocol=pickle.HIGHEST_PROTOCOL)

        self.print(f"Geodataframe cache saved with tag: {tag}")

    def _cache_load_gdf(self, tag:str) -> GeoDataFrame | None:
        gdf_path = self.get_cache_file_path(f"_{tag}_gdf")
        if gdf_path.exists():
            self.print(f"Loading cached geodataframe with tag: {tag}")

            with open(gdf_path, "rb") as f:
                gdf = pickle.load(f)

            self.print(f"Loaded cached geodataframe with tag: {tag}")

            return gdf
        
        return None

    def _load_raw_graph(self) -> tuple[GeoDataFrame, GeoDataFrame]:
        osm = OSM(str(self.pbf_file_path), bounding_box=self.bounding_box)
        result = osm.get_network(
            network_type="driving",
            nodes=True
        )
        if result:
            nodes:GeoDataFrame = GeoDataFrame(result[0])
            edges:GeoDataFrame = GeoDataFrame(result[1])
        else:
            raise RuntimeError(f"Failed to load pbf file at {self.pbf_file_path!r}!")

        return nodes, edges
    
    def convert_gdf_to_graph(self, nodes:GeoDataFrame, edges:GeoDataFrame) -> RoadMap:
        self.print("Building graph...")

        node_by_id:dict[int, Node] = {}
        edge_list:list[Edge] = []

        for _, row in nodes.iterrows():
            node_by_id[row['id']] = NodeFactory.produce(row, edges)

        for _, row in edges.iterrows():
            start_id:int = row['u']
            end_id:int = row['v']

            start_node = node_by_id.get(start_id, None)
            end_node = node_by_id.get(end_id, None)

            edge = EdgeFactory.produce(row, start_node, end_node)
            if row.get('junction', 'unknown'):
                self.print(f"junction: {row.get('junction', 'unknown')}")
            if start_node:
                start_node.edges.append(edge)
            
            edge_list.append(edge)

            if not row.get('oneway', True):
                # add a edge in reverse if the road is a twoway street
                reverse_edge = EdgeFactory.produce(row, end_node, start_node)
                if end_node:
                    end_node.edges.append(reverse_edge)

                edge_list.append(reverse_edge)
                
        return RoadMap(list(node_by_id.values()), edge_list)

    
    def load(self) -> RoadMap:
        self.print("Creating Edge Map...")
        self.print("Attempting to find cached geodataframes...")
        nodes = self._cache_load_gdf(f"{self.cache_name}_nodes")
        edges = self._cache_load_gdf(f"{self.cache_name}_edges")
        if nodes is None or edges is None:
            self.print(f"No cached geodataframes found!\nExtracting from PBF file '{self.pbf_file_path}'.\nThis may take a long time...")
            
            nodes, edges = self._load_raw_graph()

            # cache the map!
            self._cache_gdf(nodes, f"{self.cache_name}_nodes")
            self._cache_gdf(edges, f"{self.cache_name}_edges")
        else:
            self.print("Found cached geodataframes!")

        self.print(f"NODE COLUMNS: {', '.join(nodes.columns)}")
        self.print(f"EDGE COLUMNS: {', '.join(edges.columns)}")
        # convert the gdfs to roadmap
        graph = self.convert_gdf_to_graph(nodes, edges)

        return graph




            
