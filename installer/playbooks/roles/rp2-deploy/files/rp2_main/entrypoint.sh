#!/bin/bash

# Source the setup.bash file
source ~/local_mount/ros2_ws/install/setup.bash
# bash
# Run rp_launcher
ros2 daemon stop;ros2 daemon start
rp_launcher -r &
ros2 launch rosbridge_server rosbridge_websocket_launch.xml &
ros2 run tf2_web_republisher_py tf2_web_republisher &
ros2 run roslog_elasticsearch_bridge elasticsearch_bridge &
wait
