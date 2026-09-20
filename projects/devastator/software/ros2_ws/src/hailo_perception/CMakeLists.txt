cmake_minimum_required(VERSION 3.16)
project(hailo_perception)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()
add_compile_options(-Wall -Wextra)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(vision_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(OpenCV REQUIRED COMPONENTS core imgproc calib3d imgcodecs)

# HailoRT is installed by the h10-hailort .deb: /usr/include/hailo, /usr/lib/libhailort.so
find_path(HAILORT_INCLUDE_DIR hailo/hailort.hpp REQUIRED)
find_library(HAILORT_LIBRARY hailort REQUIRED)

add_executable(perception_node
  src/perception_node.cpp
  src/hailo_model.cpp)
target_include_directories(perception_node PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${HAILORT_INCLUDE_DIR}
  ${OpenCV_INCLUDE_DIRS})
ament_target_dependencies(perception_node rclcpp sensor_msgs vision_msgs std_msgs cv_bridge)
target_link_libraries(perception_node ${HAILORT_LIBRARY} ${OpenCV_LIBS})

install(TARGETS perception_node DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME})

ament_package()
