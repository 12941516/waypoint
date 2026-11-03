# waypoint
package for practicing nav2 and action, ATOM

## To Run
1. run gazebo or bringup
2. run nav2
3. use under command
```bash
~$ ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py use_sim_time:=True
~$ ros2 launch turtlebot3_navigation2 navigation2.launch.py map:=$HOME/map.yaml use_sim_time:=True
~$ ros2 run waypoint waypoint_node
```
