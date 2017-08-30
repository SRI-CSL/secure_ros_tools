Secure ROS tools 
================

``secure_ros_tools`` contains tools to create configuration files for IPSec for the "Secure ROS" project. This can be used to configure IPsec in transport mode for any application. Currently only Ubuntu Linux is supported. 

Installation
------------ 

Install ``racoon`` and ``ipsec-tools``. ::

  sudo apt-get install racoon ipsec-tools python-pip python3-pip

To install the package::

  sudo pip install git+https://github.com/SRI-CSL/secure_ros_tools.git

Usage
-----

In order to use IPSec among a set of computers, you need to create some configuration files. Optionally, you can create public-private key pairs.

You need to provide a dict containing the key-value pairs of ``hostname`` and ``ip_address``. You may then create the public-private keys and necessary configuration files as follows. ::

  create_ipsec_conf -i data/examples.yaml

where the ``data/examples.yaml`` file contains the key value pairs. An example is provided below. ::

  machine1: 192.168.10.201
  machine2: 192.168.10.202
  machine3: 192.168.10.203

Optionally, you may provide the information as a JSON string. ::

  create_ipsec_conf -d '{ "machine1": "192.168.10.201", "machine2": "192.168.10.202", "machine3": "192.168.10.203" }'

The following files are then created. ::

  output/machine1/etc/ipsec-tools.conf
  output/machine1/etc/racoon/certs/machine1
  output/machine1/etc/racoon/certs/machine1.pub
  output/machine1/etc/racoon/certs/machine2.pub
  output/machine1/etc/racoon/certs/machine3.pub
  output/machine1/etc/racoon/racoon.conf

  output/machine2/etc/ipsec-tools.conf
  output/machine2/etc/racoon/certs/machine1.pub
  output/machine2/etc/racoon/certs/machine2
  output/machine2/etc/racoon/certs/machine2.pub
  output/machine2/etc/racoon/certs/machine3.pub
  output/machine2/etc/racoon/racoon.conf

  output/machine3/etc/ipsec-tools.conf
  output/machine3/etc/racoon/certs/machine1.pub
  output/machine3/etc/racoon/certs/machine2.pub
  output/machine3/etc/racoon/certs/machine3
  output/machine3/etc/racoon/certs/machine3.pub
  output/machine3/etc/racoon/racoon.conf


Additionally, a ``tar.gz`` file is created for each machine. ::

  output/machine1.tar.gz
  output/machine2.tar.gz
  output/machine3.tar.gz


Copy the ``tar.gz`` files to the appropriate machines and untar them into the appropriate folder on the respective machines. 

E.g., on ``machine1``, untar the contents of ``machine1.tgz``. ::

  sudo tar xzf machine1.tgz -C /


