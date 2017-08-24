#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='secure_ros_tools',
      version='0.1.0',
      description='Secure ROS tools for creating IPSec configuration tools',
      url='http://github.com/SRI-CSL/secure_ros_tools',
      author='Aravind Sundaresan',
      author_email='asundaresan@gmail.com',
      license='BSD',
      packages=['ipsec_tools'],
      scripts=[
        "bin/create_ipsec_conf",
        ],
      zip_safe=False,
      install_requires = [
          "PyYAML"
        ]
      )

