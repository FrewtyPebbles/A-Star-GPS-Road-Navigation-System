from argparse import ArgumentParser
import time
from navigator.roadmap_maker import RoadMapMaker
from navigator.utility import draw_path
from PIL import Image, ImageDraw
import random

def main():
    fullerton_bbox = [-117.980, 33.850, -117.850, 33.920]

    pbf = r"./socal-251212.osm.pbf"

    cache_name = "fullerton"

    graph_reader = RoadMapMaker(fullerton_bbox, pbf, cache_name)

    graph = graph_reader.load()


    # make map:
    map_img = graph.draw_map(fullerton_bbox, (1000, 800), path_color=(50,50,100), path_width=2)
    draw = ImageDraw.Draw(map_img)
    t_len = draw.textlength(f"Map of \"{cache_name}\"")
    draw.rectangle([0,0, t_len, 10], "black")
    draw.text((0,0), f"Map of \"{cache_name}\"", fill=(3, 202, 252))
    map_img.show()  # Opens the image
    map_img.save(f"./tests/{cache_name}_map.png")

    rand_start = graph.lonlat_to_mercator(random.uniform(-117.980, -117.850), random.uniform(33.850, 33.920))
    rand_end = graph.lonlat_to_mercator(random.uniform(-117.980, -117.850), random.uniform(33.850, 33.920))
    start = graph.find_node(*rand_start)
    destination = graph.find_node(*rand_end)
    print(f"start: {start}")
    print(f"destination: {destination}")

    
    # A STAR
    
    print("Finding path with A*...")
    
    start_t = time.perf_counter()
    path = graph.a_star_find_path(start, destination)
    end_t = time.perf_counter()
    bench = end_t - start_t
    print(f"A* benchmark: {bench:.6f} seconds")

    if not path:
        print("Failed to find path!")
        return
    
    time_estimate = graph.get_path_time_estimate(path) * 60
    
    print(f"Estimated Arrival in {time_estimate} minutes")

    print(f"Saving A* path to image file './tests/a_star_{cache_name}_{rand_start[0]}_{rand_start[1]}_{rand_end[0]}_{rand_end[1]}.png'...")
    
    image = draw_path(map_img.copy(), path, fullerton_bbox, image_size=(1000, 800))
    
    draw = ImageDraw.Draw(image)
    t_len = draw.textlength(f"Estimated Arrival in {time_estimate:.2f} minutes")
    draw.rectangle([0,10, t_len, 40], "black")
    draw.text((0,10), f"A* PATH for \"{cache_name}\"", fill=(11, 252, 3))
    draw.text((0,20), f"Estimated Arrival in {time_estimate:.2f} minutes", fill=(11, 252, 3))
    draw.text((0,30), f"Benchmark: {bench:.6f} seconds", fill=(11, 252, 3))

    image.show()  # Opens the image
    image.save(f"./tests/a_star_{cache_name}_{rand_start[0]}_{rand_start[1]}_{rand_end[0]}_{rand_end[1]}.png")

    print(f"Saved A* path to image file './tests/a_star_{cache_name}_{rand_start[0]}_{rand_start[1]}_{rand_end[0]}_{rand_end[1]}.png'!")

    # UCS
    
    print("Finding path with UCS...")
    
    start_t = time.perf_counter()
    path = graph.ucs_find_path(start, destination)
    end_t = time.perf_counter()
    bench = end_t - start_t
    print(f"UCS benchmark: {bench:.6f} seconds")

    if not path:
        print("Failed to find path!")
        return
    
    time_estimate = graph.get_path_time_estimate(path) * 60
    print(f"Estimated Arrival in {time_estimate} minutes")

    print(f"Saving UCS path to image file './tests/ucs_{cache_name}_{rand_start[0]}_{rand_start[1]}_{rand_end[0]}_{rand_end[1]}.png'...")
    
    image = draw_path(map_img.copy(), path, fullerton_bbox, image_size=(1000, 800))
    
    draw = ImageDraw.Draw(image)
    t_len = draw.textlength(f"Estimated Arrival in {time_estimate:.2f} minutes")
    draw.rectangle([0,10, t_len, 40], "black")
    draw.text((0,10), f"UCS PATH for \"{cache_name}\"", fill=(11, 252, 3))
    draw.text((0,20), f"Estimated Arrival in {time_estimate:.2f} minutes", fill=(11, 252, 3))
    draw.text((0,30), f"Benchmark: {bench:.6f} seconds", fill=(11, 252, 3))

    image.show()  # Opens the image
    image.save(f"./tests/ucs_{cache_name}_{rand_start[0]}_{rand_start[1]}_{rand_end[0]}_{rand_end[1]}.png")

    print(f"Saved UCS path to image file './tests/ucs_{cache_name}_{rand_start[0]}_{rand_start[1]}_{rand_end[0]}_{rand_end[1]}.png'!")


if __name__ == "__main__":
    main()
