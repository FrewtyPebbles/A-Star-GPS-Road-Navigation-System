import math
from navigator.roadmap.edge import Edge
from navigator.roadmap.node import Node
import heapq

from navigator.roadmap.node_types import RoadNode
from navigator.roadmap.types import NodeAndEdgeDataDict
from PIL import Image, ImageDraw

class RoadMap:
    """
    This is the graph class that holds the graph
    and is where all the algorithms are written.
    """
    nodes:list[Node]
    edges:list[Edge]

    def __init__(self, nodes:list[Node], edges:list[Edge]) -> None:
        self.nodes = nodes
        self.edges = edges

    def find_node(self, x_lon:float, y_lat:float) -> None | Node:
        best = None
        best_distance = float('inf')
        for node in self.nodes:
            if isinstance(node, RoadNode):
                current_distance = self.euclidian_distance(x_lon, y_lat, node.x, node.y)
                if current_distance < best_distance:
                    best_distance = current_distance
                    best = node
        return best
            

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
        lanes:int = data.get('lanes', 1)
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
        cost += length / min(max(pred, 15), pred)
        match road_type:
            case "stop":
                cost += max(1, 2 * number_of_cars_on_road) /60
            case "traffic_signals":
                cost += 5/60
            case "crossing":
                cost += 1/60
        return cost
    
    @staticmethod
    def euclidian_distance(x_lon1:float, y_lat1:float, x_lon2:float, y_lat2:float) -> float:
        # Conversions
        lo_to_mi = lambda lo, lat: lo * 69.1 * math.cos(math.radians(lat))
        la_to_mi = lambda la: la * 69.1

        # Distance
        return math.sqrt((lo_to_mi(x_lon1, y_lat1) - lo_to_mi(x_lon2, y_lat2))**2 + (la_to_mi(y_lat1) - la_to_mi(y_lat2))**2)

    def a_star_find_path(self, start:Node, destination:Node) -> list[Node|Edge]|None:
        """
        Performs A* graph traversal to find the (hopefully) best
        rout from a start point to a destination.
        
        :return: A path list of junctions and roads.
        :rtype: list[Node | Edge]
        """

        get_eu_dis = lambda node: self.euclidian_distance(node.x, node.y, destination.x, destination.y)

        path_cost_lookup: dict[Node, float] = {start: 0.0}

        came_from_lookup: dict[Node, tuple[Edge | None, Node | None]] = {
            start: (None, None)
        }
                
        counter = 0
        frontier:list[tuple[float, int, Node]] = []
        heapq.heappush(frontier, (get_eu_dis(start), counter, start)) # type: ignore
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
                    heapq.heappush(frontier, (path_cost + get_eu_dis(road.end), counter, road.end))
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
            road, prev = came_from_lookup[current]
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
    
    