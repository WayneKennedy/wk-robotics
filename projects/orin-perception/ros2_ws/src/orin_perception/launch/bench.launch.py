# SPDX-License-Identifier: MIT
"""Perception bench: RealSense colour -> /orin/perception_node -> web_video_server (MJPEG in a browser).

  scripts/launch.sh [yolo_engine:=yolov8m.engine] [faces:=false] [objects:=false] [port:=8080]
  watch:  http://<jetson>:8080/stream?topic=/orin/image_annotated
  enrol:  ros2 topic pub --once /orin/enroll std_msgs/msg/String "{data: <name>}"
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('orin_perception')
    return LaunchDescription([
        DeclareLaunchArgument('yolo_engine', default_value='yolov8s.engine'),
        DeclareLaunchArgument('port', default_value='8080'),
        DeclareLaunchArgument('faces', default_value='true'),
        DeclareLaunchArgument('objects', default_value='true'),
        Node(package='realsense2_camera', executable='realsense2_camera_node', name='camera', namespace='camera',
             parameters=[os.path.join(share, 'config', 'realsense.yaml')], output='screen'),
        Node(package='orin_perception', executable='perception_node', name='perception_node', namespace='orin',
             output='screen',
             remappings=[('image', '/camera/camera/color/image_raw')],
             parameters=[os.path.join(share, 'config', 'perception.yaml'),
                         {'yolo_engine': LaunchConfiguration('yolo_engine'),
                          'enable_faces': LaunchConfiguration('faces'),
                          'enable_objects': LaunchConfiguration('objects')}]),
        Node(package='web_video_server', executable='web_video_server', name='web_video_server', output='screen',
             parameters=[{'port': LaunchConfiguration('port'), 'default_stream_type': 'mjpeg'}]),
    ])
