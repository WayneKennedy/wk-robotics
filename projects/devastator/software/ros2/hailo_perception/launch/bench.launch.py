"""The perception bench: webcam -> hailo_perception -> web_video_server.

Browser: http://<host>:8080/stream?topic=/hailo/image_annotated
Enrol a face: ros2 topic pub --once /hailo/enroll std_msgs/msg/String "{data: wayne}"
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory("hailo_perception")
    models = os.path.expanduser("~/hailo/models")
    return LaunchDescription([
        # usb_cam 0.8.1 only accepts a real /dev/videoN, not a /dev/v4l/by-id symlink; the
        # C920 clone re-enumerated as /dev/video4 mid-run (2026-09-19), so bench.sh on the
        # host resolves the by-id link with readlink -f and passes the result here.
        DeclareLaunchArgument("video_device", default_value="/dev/video0"),
        DeclareLaunchArgument("params", default_value=os.path.join(share, "config", "bench.yaml")),
        Node(
            package="usb_cam", executable="usb_cam_node_exe", name="usb_cam", output="screen",
            respawn=True, respawn_delay=2.0,  # usb_cam 0.8.1 has aborted mid-run on the C920 clone (2026-09-19)
            parameters=[{
                "video_device": LaunchConfiguration("video_device"),
                "image_width": 640, "image_height": 480, "framerate": 30.0,  # 720p mjpeg2rgb segfaults usb_cam 0.8.1 on the C920 clone (2026-09-19)
                "pixel_format": "mjpeg2rgb", "camera_name": "webcam", "frame_id": "camera",
            }],
        ),
        Node(
            package="hailo_perception", executable="perception_node", name="hailo_perception",
            namespace="hailo", output="screen",
            parameters=[LaunchConfiguration("params"), {
                "hef_objects": os.path.join(models, "yolov8s.hef"),
                "hef_face_det": os.path.join(models, "scrfd_2.5g.hef"),
                "hef_face_id": os.path.join(models, "arcface_mobilefacenet.hef"),
            }],
            remappings=[("image", "/image_raw")],
        ),
        Node(package="web_video_server", executable="web_video_server", name="web_video_server", output="screen",
             parameters=[{"port": 8080, "default_stream_type": "mjpeg"}]),
    ])
