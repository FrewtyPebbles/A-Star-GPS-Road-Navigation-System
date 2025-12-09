# GPS Road Navigation System

This GPS Road System will find the (hopefully) shortest path to a destination using the A* graph traversal algorithm.  The graph is designed to use data from [Open Street Map](https://www.openstreetmap.org).

The dataset we used specifically was from [this page](https://download.geofabrik.de/north-america/us/california.html).  If you would like to download the dataset directly you can do so from [this link](https://download.geofabrik.de/north-america/us/california-251205.osm.pbf).

# Tests

Here are some tests navigating to and from random places within the Fullerton, CA area.

---
---
---

## A*

![A* test](tests/a_star_fullerton_-8152.207095985362_2495.2867764046973_-8159.574648414691_2491.437884082884.png)

*Benchmark* : 374 ms

*Arrival*: 41.94 min

## UCS

![UCS test](tests/ucs_fullerton_-8152.207095985362_2495.2867764046973_-8159.574648414691_2491.437884082884.png)

*Benchmark* : 446 ms

*Arrival*: 41.94 min

---
---
---

## A*

![A* test](tests/a_star_fullerton_-8153.807306255795_2491.020486397002_-8152.061953049231_2491.271865099904.png)

*Benchmark* : 103 ms

*Arrival*: 24.72 min

## UCS

![UCS test](tests/ucs_fullerton_-8153.807306255795_2491.020486397002_-8152.061953049231_2491.271865099904.png)

*Benchmark* : 183 ms

*Arrival*: 24.72 min

---
---
---

## A*

![A* test](tests/a_star_fullerton_-8156.074590433435_2492.3207273517323_-8155.031864678875_2491.893627238422.png)

*Benchmark* : 11 ms

*Arrival*: 6.07 min

## UCS

![UCS test](tests/ucs_fullerton_-8156.074590433435_2492.3207273517323_-8155.031864678875_2491.893627238422.png)

*Benchmark* : 21 ms

*Arrival*: 6.07 min

---
---
---