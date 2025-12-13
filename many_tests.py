from argparse import ArgumentParser
import time
from navigator.roadmap_maker import RoadMapMaker
from navigator.utility import draw_path
from PIL import Image, ImageDraw
import random

TEST_COUNT = 200

def main():
    fullerton_bbox = [-117.980, 33.850, -117.850, 33.920]

    pbf = r"./socal-251212.osm.pbf"

    cache_name = "fullerton"

    graph_reader = RoadMapMaker(fullerton_bbox, pbf, cache_name)

    graph = graph_reader.load()
    

    results:list[tuple[int, tuple[float, float], tuple[float, float]]] = []

    for test_num in range(1, TEST_COUNT + 1):

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
        bench1 = end_t - start_t

        if not path:
            print("Failed to find path!")
            results.append(None)
            continue
        
        print(f"A* benchmark: {bench1:.6f} seconds")
        
        time_estimate1 = graph.get_path_time_estimate(path) * 60
        
        print(f"Estimated Arrival in {time_estimate1} minutes")


        # UCS
        
        print("Finding path with UCS...")
        
        start_t = time.perf_counter()
        path = graph.ucs_find_path(start, destination)
        end_t = time.perf_counter()
        bench2 = end_t - start_t

        if not path:
            print("Failed to find path!")
            results.append(None)
            continue
        
        print(f"UCS benchmark: {bench2:.6f} seconds")
        
        time_estimate2 = graph.get_path_time_estimate(path) * 60
        print(f"Estimated Arrival in {time_estimate2} minutes")

        results.append((test_num, (bench1, time_estimate1), (bench2, time_estimate2)))

    # PRINT RESULTS

    print("RESULTS ( A* | UCS ):")
    total_tests = 0
    for backup_num, result in enumerate(results, 1):
        if result:
            test_num, (bench1, time_estimate1), (bench2, time_estimate2) = result
            print(f"#{test_num}: b1:{bench1:.6f}, t1:{time_estimate1:.6f} | b2:{bench2:.6f}, t2:{time_estimate2:.6f}")
            total_tests += 1
        else:
            print(f"#{backup_num} NO PATH FOUND")

    avg_b1 = sum([result[1][0] for result in results if result])/ total_tests
    avg_b2 = sum([result[2][0] for result in results if result])/ total_tests

    avg_t1 = sum([result[1][1] for result in results if result])/ total_tests
    avg_t2 = sum([result[2][1] for result in results if result])/ total_tests

    a_s_better_count = sum([result[1][0] - result[2][0] < 0 for result in results if result])
    percentage_better = a_s_better_count / total_tests
    avg_diff_b_given_better = sum([abs(result[1][0] - result[2][0]) for result in results if result and result[1][0] - result[2][0] < 0])/a_s_better_count
    avg_diff_t_given_better = sum([result[1][1] - result[2][1] for result in results if result and result[1][0] - result[2][0] < 0])/a_s_better_count

    avg_diff_b = avg_b1 - avg_b2
    avg_diff_t = avg_t1 - avg_t2

    print(f"For {total_tests} succesful tests and {TEST_COUNT - total_tests} instances where a path couldn't be found due to disconnected nodes in the map data:")

    print(f"A*'s average benchmark was {avg_b1:.6f} seconds.")
    print(f"UCS's average benchmark was {avg_b2:.6f} seconds.")

    print(f"A*'s average time to arrival was {avg_t1:.6f} minutes.")
    print(f"UCS's average time to arrival was {avg_t2:.6f} minutes.")

    if avg_diff_b > 0:
        print(f"On average A* was {abs(avg_diff_b):.6f} seconds slower to benchmark than UCS.")
    else:
        print(f"On average A* was {abs(avg_diff_b):.6f} seconds faster to benchmark than UCS.")

    if avg_diff_t > 0:
        print(f"On average A* was {abs(avg_diff_t):.6f} minutes slower in estimated time to arrival than UCS.")
    else:
        print(f"On average A* was {abs(avg_diff_t):.6f} minutes faster in estimated time to arrival than UCS.")

    print(f"A*'s heuristic was admissable and made A* benchmark faster than UCS in {percentage_better * 100:.2f}% of the tests.")
    
    print(f"In tests where A* benchmarked faster than UCS, A* was on average {avg_diff_b_given_better:.6f} seconds faster to benchmark than UCS.")

    if avg_diff_t_given_better > 0:
        print(f"In tests where A* benchmarked faster than UCS, A*'s estimated time to arival on average was {avg_diff_t_given_better:.6f} minutes slower than UCS.")
    else:
        print(f"In tests where A* benchmarked faster than UCS, A*'s estimated time to arival on average was {avg_diff_t_given_better:.6f} minutes faster than UCS.")


        


if __name__ == "__main__":
    main()
