import pickle
import os
from typing import Literal
from pyrosm import OSM
from geopandas import GeoDataFrame
from pathlib import Path

from navigator.roadmap import RoadMap, Junction, Road

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

    def print(self, msg:str):
        if self.stdout_enabled:
            print(msg)

    def get_cache_file_path(self, file_suffix:str) -> Path:
        return self.cache_folder / f"{self.cache_name}{file_suffix}.pkl"

    def cache(self, graph:RoadMap):
        self.print("Saving cache...")

        with open(self.get_cache_file_path("_graph"), "wb") as f:
            pickle.dump(graph, f, protocol=pickle.HIGHEST_PROTOCOL)

        self.print("Cache saved.")

    def cache_load(self) -> RoadMap | None:
        graph_path = self.get_cache_file_path("_graph")
        if graph_path.exists():
            self.print("Loading cached graph data...")

            with open(graph_path, "rb") as f:
                graph = pickle.load(f)

            return graph
        
        return None

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

        junctions_by_id:dict[int, Junction] = {}
        road_list:list[Road] = []

        for _, row in nodes.iterrows():
            junctions_by_id[row['id']] = Junction(row['id'], row['x'], row['y'])

        for _, row in edges.iterrows():
            start_id:int = row['u']
            end_id:int = row['v']

            start_junction = junctions_by_id[start_id]
            end_junction = junctions_by_id[end_id]

            road = Road(
                start_junction,
                end_junction,
                length = row.get('length', 0.0),
                road_type = row.get('highway', 'unknown'),
                oneway = row.get('oneway', True),
                geometry = row.geometry
            )
            start_junction.edges.append(road)
            
            road_list.append(road)

            if not row.get('oneway', True):
                # add a edge in reverse if the road is a twoway street
                reverse_road = Road(
                    end_junction,
                    start_junction,
                    length = row.get('length', 0.0),
                    road_type = row.get('highway', 'unknown'),
                    oneway = False,
                    geometry = row.geometry
                )
                end_junction.edges.append(reverse_road)

                road_list.append(reverse_road)
                
        return RoadMap(list(junctions_by_id.values()), road_list)

    
    def load(self) -> RoadMap:

        # try to load from cache
        graph = self.cache_load()

        if graph:
            # cache hit
            self.print("Cached graph data loaded!")
            return graph
        else:
            # cache miss :^(
            # time for slow loading from pbf
            self.print("No cache found for current graph!\nAttempting to find cached geodataframes...")
            nodes = self._cache_load_gdf(f"{self.cache_name}_nodes")
            edges = self._cache_load_gdf(f"{self.cache_name}_edges")
            if nodes is None or edges is None:
                self.print(f"No cached geodataframes found!\nExtracting from PBF file '{self.pbf_file_path}'.\nThis may take a long time...")
                
                nodes, edges = self._load_raw_graph()

                # cache the map!
                self._cache_gdf(nodes, f"{self.cache_name}_nodes")
                self._cache_gdf(edges, f"{self.cache_name}_edges")

            # convert
            graph = self.convert_gdf_to_graph(nodes, edges)

            self.cache(graph)

        return graph




            
