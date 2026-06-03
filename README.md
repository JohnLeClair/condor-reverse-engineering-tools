# condor-reverse-engineering-tools
Contains host control software and the actual hardware and firmware files for various EMFI and Side-Channel Analysis hardware. 

## Overview

## Installation
### Install Linux udev rules
- sudo cp drivers/linux/99-condor-embedded.rules /etc/udev/rules.d/
- sudo udevadm control --reload-rules
- sudo udevadm trigger
- logout or restart computer

### Install Required Host Software (on Ubuntu): 
- sudo apt install python3-pip
- pip install pyswd pyserial libusb1 chipwhisperer matplotlib

### cd <condor-reverse-engineering-tools folder location> 
~~~
pip uninstall -y emfi-tools
pip uninstall -y side-channel-tools

rm -rf emfi-tools/*.egg-info
rm -rf emfi-tools/host-src/*.egg-info
rm -rf emfi-tools/host-src/emfi_tools.egg-info

rm -rf side-channel-tools/*.egg-info
rm -rf side-channel-tools/host-src/*.egg-info
rm -rf side-channel-tools/host-src/emfi_tools.egg-info

pip install -e ./emfi-tools
pip install -e ./side-channel-tools
~~~
