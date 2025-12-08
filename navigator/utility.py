from PIL import Image, ImageDraw
from shapely.geometry import LineString

from navigator.roadmap.edge import Edge
from navigator.roadmap.node import Node
from navigator.roadmap.node_types import TrafficControl, ShapePoint, Junction

def draw_path(img:Image.Image, path: list[Node | Edge], 
                       bbox: tuple[float, float, float, float]|list[float], 
                       image_size: tuple[int, int] = (800, 600), 
                       path_color: tuple[int,int,int]=(255,0,0), 
                       path_width: int=3) -> Image.Image:
    stop_icon = Image.open("./image_assets/stop_icon.png")
    traffic_signals_icon = Image.open("./image_assets/traffic_icon.png")

    min_lon, min_lat, max_lon, max_lat = bbox
    width, height = image_size

    def project(lon, lat) -> tuple[float, float]:
        x = (lon - min_lon) / (max_lon - min_lon) * width
        y = height - (lat - min_lat) / (max_lat - min_lat) * height
        return (x, y)

    draw = ImageDraw.Draw(img)

    deffered_draws = []
    coords = []
    for item in path:
        if isinstance(item, Node):  # Node
            coord = project(item.x, item.y)
            coords.append(coord)
            coord = (int(coord[0]), int(coord[1]))
            if 'highway' in item.tags:
                if item.tags['highway'] == "stop":
                    deffered_draws.append((img.paste, (stop_icon, coord, stop_icon)))
                elif item.tags['highway'] == "traffic_signals":
                    deffered_draws.append((img.paste, (traffic_signals_icon, coord, traffic_signals_icon)))
                else:
                    highway_tag = item.tags['highway']
                    deffered_draws.append((draw.text, (coord, highway_tag, 'black')))
                
        elif isinstance(item, Edge):  # Edge with geometry
            for lon, lat in item.geometry.coords:
                coords.append(project(lon, lat))

    # Draw lines between consecutive points
    if len(coords) >= 2:
        draw.line(coords, fill=path_color, width=path_width)

    for f, a in deffered_draws:
        f(*a)

    return img
