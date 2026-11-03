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

        # Waypoints [x, y, z, w]
        self.waypoints = [
            [-1.785, -0.517, -0.139, 0.990],  # HOME
            [1.303, 0.521, -0.003, 0.999],    # A
            [2.000, 1.000, 0.000, 1.000],     # B
            [0.500, 2.000, 0.000, 1.000]      # C
        ]

        self.current_index = 0

        self.send_goal()

    # --------------------------------------------------
    # Goal Send
    # --------------------------------------------------
    def send_goal(self):
        wp = self.waypoints[self.current_index]

        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = "map"
        goal.pose.header.stamp = self.get_clock().now().to_msg()

        goal.pose.pose.position.x = wp[0]
        goal.pose.pose.position.y = wp[1]
        goal.pose.pose.orientation.z = wp[2]
        goal.pose.pose.orientation.w = wp[3]

        self.get_logger().info(
            f"Sending goal [{self.current_index + 1}/{len(self.waypoints)}]"
        )

        future = self.client.send_goal_async(goal)
        future.add_done_callback(self.goal_response_callback)

    # --------------------------------------------------
    # Goal Response
    # --------------------------------------------------
    def goal_response_callback(self, future):
        self.goal_handle = future.result()

        if not self.goal_handle.accepted:
            self.get_logger().error('Goal rejected')
            self.send_goal()
            return

        self.get_logger().info('Goal accepted')

        result_future = self.goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    # --------------------------------------------------
    # Result Callback
    # --------------------------------------------------
    def result_callback(self, future):
        status = future.result().status

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(
                f"Waypoint {self.current_index + 1} reached successfully"
            )

            # Check last waypoint
            self.current_index += 1

            if self.current_index >= len(self.waypoints):
                self.get_logger().info(
                    "All waypoints reached. Shutting down..."
                )
                rclpy.shutdown()
                return

            # Move to next waypoint
            self.send_goal()

        else:
            self.get_logger().warn(
                f"Navigation failed with status: {status}\nRetrying..."
            )

            # Retry current waypoint
            self.send_goal()


def main(args=None):
    rclpy.init(args=args)
    node = WaypointNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
