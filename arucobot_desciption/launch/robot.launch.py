import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch_ros.descriptions import ParameterValue
from launch.substitutions import LaunchConfiguration, Command, PythonExpression

import xacro

def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')

    # Process the URDF file
    pkg_path = os.path.join(get_package_share_directory('arucobot_description'))
    xacro_file = os.path.join(pkg_path,'urdf','robot.urdf.xacro')
    bridge_config = os.path.join(pkg_path,'config','bridge.yaml')
    robot_description_config = xacro.process_file(xacro_file)
    rviz_path = os.path.join(pkg_path, 'config', 'display.rviz')
    controller_config = os.path.join(pkg_path, 'config', 'controller.yaml')

    # Create a robot_state_publisher node
    params = {'robot_description': robot_description_config.toxml(), 'use_sim_time': use_sim_time}
    robot_state_publisher = Node(package = 'robot_state_publisher',
                            executable = 'robot_state_publisher',
                            name='robot_state_publisher',
                            parameters = [{'robot_description': ParameterValue(Command( \
                                        ['xacro ', xacro_file,
                                        # ' kinect_enabled:=', "true",
                                        # ' lidar_enabled:=', "true",
                                        # ' camera_enabled:=', camera_enabled,
                                        ]), value_type=str)}]
                            )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_path],
        output='screen'
    )

    ros_gz_bridge = Node(
                package="ros_gz_bridge", 
                executable="parameter_bridge",
                parameters = [
                    {'config_file': bridge_config}],
                # condition=IfCondition(with_bridge)
                )

    spawn_robot = Node(package = "ros_gz_sim",
                           executable = "create",
                           arguments = ["-topic", "/robot_description",
                                        "-name", "arucobot",
                                        "-allow_renaming", "true",
                                        "-z", "0.0",
                                        "-x", "0.0",
                                        "-y", "0.0",
                                        "-Y", "0.0",
                                        ],
							output='screen'
                           )
    
    load_controller = Node(
            package='controller_manager',
            executable='ros2_control_node',
            parameters=[controller_config]
        )
    
    arg_use_sim_time = DeclareLaunchArgument('use_sim_time',
											default_value='true',
											description="Enable sim time from /clock")


    # Launch!
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use sim time if true'),

        robot_state_publisher,
        load_controller,
        spawn_robot,
        ros_gz_bridge,
        arg_use_sim_time
    ])
