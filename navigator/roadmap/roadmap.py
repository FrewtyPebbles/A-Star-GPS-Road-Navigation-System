from navigator.roadmap.roads import Road, Junction
import heapq

class RoadMap:
    """
    This is the graph class that holds the graph
    and is where all the algorithms are written.
    """
    # TODO : replace junctions list with a K-D Tree of junctions for efficiency.
    junctions:list[Junction]
    roads:list[Road]

    def __init__(self, junctions:list[Junction], roads:list[Road]) -> None:
        self.junctions = junctions
        self.roads = roads

    def heuristic(self, junction:Junction) -> float:
        # TODO
        heuristic = 0.0
        return heuristic

    def find_path(self, start:Junction, destination:Junction) -> list[Junction|Road]|None:
        """
        Performs A* graph traversal to find the (hopefully) best
        rout from a start point to a destination.
        
        :return: A path list of junctions and roads.
        :rtype: list[Junction | Road]
        """

        path_cost_lookup: dict[Junction, float] = {start: 0.0}

        came_from_lookup: dict[Junction, tuple[Road | None, Junction | None]] = {
            start: (None, None)
        }
                
        frontier:list[tuple[float, Junction]] = []
        heapq.heappush(frontier, (self.heuristic(start), start))

        explored:set[Junction] = set()

        while frontier:
            _, current_junction = heapq.heappop(frontier)
            
            if current_junction == destination:
                return self._reconstruct_path(came_from_lookup, destination)
            
            explored.add(current_junction)

            for road in current_junction.roads:
                if not any([road.end == j for _, j in frontier]) and \
                road.end not in explored:
                    heapq.heappush(frontier, (path_cost_lookup[current_junction] + self.heuristic(road.end), road.end))# TODO add path cost + heuristic
                else:
                    for frontier_index, (cost, junction) in enumerate(frontier):
                        if road.end == junction and path_cost_lookup[current_junction] < cost:
                            frontier[frontier_index] = (path_cost_lookup[current_junction] + self.heuristic(road.end), road.end)
                            break

        return None

    def _reconstruct_path(self, came_from_lookup: dict[Junction, tuple[Road | None, Junction | None]], end: Junction):
        path:list[Junction | Road] = []
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
    
    
    