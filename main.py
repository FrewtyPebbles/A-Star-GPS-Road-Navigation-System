from argparse import ArgumentParser
from navigator.road_map_maker import RoadMapMaker

def main():
    fullerton_bbox = [-117.980, 33.850, -117.850, 33.920]

    pbf = r"./socal-251205.osm.pbf"

    cache_name = "fullerton"

    graph_reader = RoadMapMaker(fullerton_bbox, pbf, cache_name)

    graph = graph_reader.load()

if __name__ == "__main__":
    main()
