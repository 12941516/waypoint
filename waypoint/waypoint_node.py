#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from nav2_msgs.action import NavigateToPose

class WaypointNode(Node):

    def __init__(self):
        super().__init__('waypoint_node')

        # Nav2 Action Client
        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.get_logger().info('Waiting for Nav2 action server...')
        self.client.wait_for_server()

        # Waypoints
        self.waypoints = {
            "HOME": {'x': -1.785, 'y': -0.517, 'z': -0.139, 'w': 0.990},
            "A": {'x': 1.303, 'y': 0.521, 'z': -0.003, 'w': 0.999}
        }

        self.current_target = "A"
        self.send_goal(self.waypoints["A"])

    # --------------------------------------------------
    # Goal Send
    # --------------------------------------------------
    def send_goal(self, wp):
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = "map"
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = wp['x']
        goal.pose.pose.position.y = wp['y']
        goal.pose.pose.orientation.z = wp['z']
        goal.pose.pose.orientation.w = wp['w']

        self.get_logger().info(f"Sending goal -> {self.current_target}")

        future = self.client.send_goal_async(goal)
        future.add_done_callback(self.goal_response_callback)

    # --------------------------------------------------
    # Goal Response
    # --------------------------------------------------
    def goal_response_callback(self, future):
        self.goal_handle = future.result()
        
        if not self.goal_handle.accepted:
            self.get_logger().error('Goal rejected')
            return

        self.get_logger().info('Goal accepted')

        result_future = self.goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    # --------------------------------------------------
    # Result Callback
    # --------------------------------------------------
    def result_callback(self, future):
        status = future.result().status

        # STATUS_SUCCEEDED
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f"{self.current_target} reached successfully")

            # Go to HOME after reaching A
            if self.current_target == "A":
                self.get_logger().info("Returning HOME...")
                self.current_target = "HOME"
                self.send_goal(self.waypoints["HOME"])

            # Shutdown after reaching HOME
            elif self.current_target == "HOME":
                self.get_logger().info("Mission complete. Shutting down...")
                rclpy.shutdown()

        else:
            self.get_logger().warn(f"Navigation failed with status: {status}\nRetrying...")
            self.send_goal(self.waypoints[self.current_target])


def main(args=None):
    rclpy.init(args=args)
    node = WaypointNode()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
