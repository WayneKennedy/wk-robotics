# SPDX-License-Identifier: MIT
from glob import glob
from setuptools import setup

package_name = 'orin_perception'
setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Wayne Kennedy',
    maintainer_email='wayne@zappfyre.com',
    description='Perception bench on the Jetson Orin Nano (YOLOv8 + SCRFD/ArcFace on TensorRT).',
    license='MIT',
    entry_points={
        'console_scripts': [
            'perception_node = orin_perception.perception_node:main',
            'enrol = orin_perception.enrol:main',
        ],
    },
)
