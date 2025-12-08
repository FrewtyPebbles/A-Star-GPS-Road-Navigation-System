import math
from navigator.roadmap.edge import Edge
from navigator.roadmap.node import Node
import heapq

from navigator.roadmap.node_types import RoadNode
from navigator.roadmap.types import NodeAndEdgeDataDict
from PIL import Image, ImageDraw
from scipy.spatial import KDTree

EARTHS_RADIUS = 6378137
METERS_PER_MILE = 1609.344

class RoadMap:
    """
    This is the graph class that holds the graph
    and is where all the algorithms are written.
    """
    nodes:list[Node]
    edges:list[Edge]
    node_kd_tree:KDTree

    def __init__(self, nodes:list[Node], edges:list[Edge]) -> None:
        self.nodes = nodes
        self.edges = edges
        self.node_kd_tree = KDTree([self.lonlat_to_mercator(node.x, node.y) for node in nodes])

    @staticmethod
    def lonlat_to_mercator(lon:float, lat:float):
        x = EARTHS_RADIUS * math.radians(lon)
        y = EARTHS_RADIUS * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
        return x / METERS_PER_MILE, y / METERS_PER_MILE
    
    @staticmethod
    def mercator_to_lonlat(x, y):
        lon = math.degrees(x * METERS_PER_MILE / EARTHS_RADIUS)
        lat = math.degrees(2 * math.atan(math.exp(y * METERS_PER_MILE / EARTHS_RADIUS)) - math.pi/2)
        return lon, lat

    def find_node(self, x:float, y:float) -> None | Node:
        dist, idx = self.node_kd_tree.query((x, y))
        return self.nodes[idx]
            

    def road_cost(self, data:NodeAndEdgeDataDict) -> float:
        """
        The current road cost.
        """
        # NodeAndEdgeDataDict must be queried with get(name, default)
        # since some nodes or edges might not include certain data
        cost:float = 0.0
        causes_stops:bool = data.get('causes_stops', False)
        connections:int = data.get('connections', 1)
        dead_end:bool = data.get('dead_end', False)
        lanes:int = data.get('lanes', 1) if data.get('lanes', 1) else 1
        length:float|int = data.get('length', 9999999.0)
        speed_limit:int = data.get('speed_limit', 25)
        oneway:bool = data.get('oneway', True)
        road_type:str = data.get('road_type', "unknown")

        # This would in a non-emulation come from real time traffic data:
        # But in this case we will assume every car is the average length of a Ford F150
        # and assume the cars are all spaced 2 Ford F150s apart per road
        ford_f150_len = 0.0036 # Length of a ford f150 in miles
        number_of_cars_on_road = max(int(length / ford_f150_len) // 3, 1)

        # Try to predict time on the road in hours
        pred = speed_limit - (number_of_cars_on_road - 1) / number_of_cars_on_road * speed_limit
        cost += length / min(max(pred / lanes, 15), speed_limit)
        if causes_stops:
            cost += max(1, 2 * number_of_cars_on_road)/60
        match road_type:
            case "stop":
                cost += max(1, 2 * number_of_cars_on_road) /60
            case "traffic_signals":
                cost += 5/60
            case "crossing":
                cost += 1/60
        return cost
    
    @staticmethod
    def euclidian_distance(x1:float, y1:float, x2:float, y2:float) -> float:
        # Distance
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
    def heuristic(self, node:Node, destination:Node, sample_rate:float) -> float:
        cost:float = 0.0
        node_x, node_y = self.lonlat_to_mercator(node.x, node.y)
        destination_x, destination_y = self.lonlat_to_mercator(destination.x, destination.y)
        distance:float = self.euclidian_distance(node_x, node_y, destination_x, destination_y)
        
        return distance / 30 # assume 30 mph on average for now but swap out for a cummulative average of all the previous roads traveled.

    def a_star_find_path(self, start:Node, destination:Node) -> list[Node|Edge]|None:
        """
        Performs A* graph traversal to find the (hopefully) best
        rout from a start point to a destination.
        
        :return: A path list of junctions and roads.
        :rtype: list[Node | Edge]
        """
        speed_limit_sum = 0
        speed_limit_count = 0
        path_cost_lookup: dict[Node, float] = {start: 0.0}

        came_from_lookup: dict[Node, tuple[Edge | None, Node | None]] = {
            start: (None, None)
        }
                
        counter = 0
        frontier:list[tuple[float, int, Node]] = []
        heapq.heappush(frontier, (self.heuristic(start, destination, 0.5), counter, start)) # type: ignore
        counter += 1

        explored:set[Node] = set()

        while frontier:
            _, _, current_node = heapq.heappop(frontier)

            if current_node in explored:
                continue

            if current_node == destination:
                return self._reconstruct_path(came_from_lookup, destination)

            explored.add(current_node)

            for road in current_node.edges:
                if not road.end:
                    continue

                if road.end in explored:
                    continue

                path_cost = path_cost_lookup[current_node] + self.road_cost(road.data | road.end.data)
                

                if road.end not in path_cost_lookup or path_cost < path_cost_lookup[road.end]:
                    path_cost_lookup[road.end] = path_cost
                    came_from_lookup[road.end] = (road, current_node)
                    heapq.heappush(frontier, (path_cost + self.heuristic(road.end, destination, 0.5), counter, road.end))
                    counter += 1

        return None
    
    def ucs_find_path(self, start:Node, destination:Node) -> list[Node|Edge]|None:
        """
        Performs UCS graph traversal to find the (hopefully) best
        rout from a start point to a destination.
        
        :return: A path list of junctions and roads.
        :rtype: list[Node | Edge]
        """
        path_cost_lookup: dict[Node, float] = {start: 0.0}

        came_from_lookup: dict[Node, tuple[Edge | None, Node | None]] = {
            start: (None, None)
        }
                
        counter = 0
        frontier:list[tuple[float, int, Node]] = []
        heapq.heappush(frontier, (0.0, counter, start)) # type: ignore
        counter += 1

        explored:set[Node] = set()

        while frontier:
            _, _, current_node = heapq.heappop(frontier)

            if current_node in explored:
                continue

            if current_node == destination:
                return self._reconstruct_path(came_from_lookup, destination)

            explored.add(current_node)

            for road in current_node.edges:
                if not road.end:
                    continue

                if road.end in explored:
                    continue

                path_cost = path_cost_lookup[current_node] + self.road_cost(road.data | road.end.data)
                

                if road.end not in path_cost_lookup or path_cost < path_cost_lookup[road.end]:
                    path_cost_lookup[road.end] = path_cost
                    came_from_lookup[road.end] = (road, current_node)
                    heapq.heappush(frontier, (path_cost, counter, road.end))
                    counter += 1

        return None

    def _reconstruct_path(self, came_from_lookup: dict[Node, tuple[Edge | None, Node | None]], end: Node):
        path:list[Node | Edge] = []
        current = end

        while True:
            came_from_result = came_from_lookup.get(current)
            if not came_from_result:
                path.append(current)
                break
            road, prev = came_from_result
            if current:
                path.append(current)
            if prev is None:
                break
            if road:
                path.append(road)
            current = prev

        path.reverse()
        return path
    
    def get_path_time_estimate(self, path:list[Node|Edge]):
        total_cost = 0.0
    
        for i in range(len(path)):
            if isinstance(path[i], Edge):
                edge = path[i]
                if i + 1 < len(path) and isinstance(path[i + 1], Node):
                    node = path[i + 1]
                    total_cost += self.road_cost(edge.data | node.data)
        
        return total_cost

    
    def draw_map(
        self,
        bbox: tuple[float, float, float, float] | list[float],
        image_size: tuple[int, int] = (800, 600),
        path_color: tuple[int, int, int] = (255, 0, 0),
        path_width: int = 3
    ):
        """
        Draws the full road map inside the bounding box.
        """

        stop_icon = Image.open("./image_assets/stop_icon.png").convert("L")
        traffic_signals_icon = Image.open("./image_assets/traffic_icon.png").convert("L")

        min_lon, min_lat, max_lon, max_lat = bbox
        width, height = image_size

        img = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        def project(lon: float, lat: float) -> tuple[int, int]:
            x_norm = (lon - min_lon) / (max_lon - min_lon)
            y_norm = (lat - min_lat) / (max_lat - min_lat)

            x = int(x_norm * width)
            y = int((1 - y_norm) * height)

            return (x, y)

        defered_draws = []
        for edge in self.edges:
            start = edge.start
            end = edge.end

            if not start or not end:
                continue

            if not (min_lon <= start.x <= max_lon and min_lat <= start.y <= max_lat):
                continue
            if not (min_lon <= end.x <= max_lon and min_lat <= end.y <= max_lat):
                continue

            x1, y1 = project(start.x, start.y)
            x2, y2 = coord = project(end.x, end.y)

            draw.line((x1, y1, x2, y2), fill=path_color, width=path_width)

            if 'highway' in end.tags:
                if end.tags['highway'] == "stop":
                    defered_draws.append((img.paste, (stop_icon, coord, stop_icon)))
                elif end.tags['highway'] == "traffic_signals":
                    defered_draws.append((img.paste, (traffic_signals_icon, coord, traffic_signals_icon)))
                else:
                    hw = end.tags['highway']
                    defered_draws.append((draw.text, (coord, hw, 'black')))

        for f,a in defered_draws:
            f(*a)

        return img
    
    