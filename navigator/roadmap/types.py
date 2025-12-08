
from typing import Any, Literal


EdgeDataDict = dict[Literal['speed_limit','speed_limit_units','lanes','oneway','road_type','length'], Any]
NodeDataDict = dict[Literal['causes_stops', 'connections', 'dead_end'], Any]
NodeAndEdgeDataDict = dict[Literal[
    'speed_limit','speed_limit_units','lanes','oneway','road_type','length','causes_stops', 'connections', 'dead_end'
    ], Any]