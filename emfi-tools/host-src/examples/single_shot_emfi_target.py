# Copyright (c) 2018-2019, NewAE Technology Inc
# All rights reserved.
#
# Authors: Colin O'Flynn, Alex Dewar
#
# This file is part of the ChipSHOUTER Ballistic Gel project.
#
#    This project is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This project is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this project.  If not, see <http://www.gnu.org/licenses/>.
#=============================================================================

# Copyright (c) 2025    Condor Embedded Technology, LLC
# All rights reserved.
#
# Author: John LeClair
# Email:  jleclair@condorembeddedtech.com
#
# filename: single_shot_emfi_target.py
#     This file is an example how to use the EMFI-Target in a single EMFI EMP
#     blast mode. This just plots the spread of the beam giving an idea how
#     wide the effects of the EMFI probe is. 
#
#    This project is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This project is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this project.  If not, see <http://www.gnu.org/licenses/>.
#=============================================================================

import sys
import argparse

# Target Unit Under Test (UUT)
from shared.sram_as6c3216A_emfi_target import *

# Utilities
import math
from time import sleep

# Plotting
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np
import pickle
from PIL import Image

def plotScanResults(result_array):
    plt.imshow(result_array, cmap='viridis') #investigate np.meshgrid
    # plt.matshow(result_array)
    plt.colorbar(label='Examine')
    plt.title('2D Scan Results')
    plt.show()
    plt.savefig('my_high_res_image.png', dpi=300)
    input("Press enter to continue")


if __name__ == '__main__':
    print("Python version:")
    print(sys.version)

    # Initialize SRAM Target.
    target = sram_emfi_target()
    target.setup()
    target.load_target()

    input("Press 'enter' to contine")

    # Calculate the bytes/bits that were modified.
    point_scan_result = target.examine_target()

    errdatay = point_scan_result['errdatay']  # TODO: unused at the moment. will store in file eventually (maybe))(no really - maybe)
    errdatax = point_scan_result['errdatax']  # TODO: unused at the moment. will store in file eventually (maybe)(no really - maybe)
    errorlist = point_scan_result['errorlist']
    
    # Plot the results.
    for i in range(len(errorlist)):
        if errorlist[i] > 0:
            errorlist[i] = 0     # black if errors.
        else:
            errorlist[i] = 255   # white if no errors.

    bmpWidth, bmpHeight = 2048, 2048
    xyArray = errorlist.reshape ((2048, 2048))
    image = Image.fromarray(xyArray, mode='L')
    image.save('my_bitmap.png')

    image.show()
    
    image.close()
    






# Developer Time Saver Note: Visual code for when the debugger script gets scrogged yet again.
# {
#     "version": "0.2.0",
#     "configurations": [
#         {
#             "name": "Python Debugger: Current File with Arguments",
#             "type": "debugpy",
#             "request": "launch",
#             "program": "${file}",
#             "console": "integratedTerminal",
#             "args": ["-p/dev/ttyUSB2", "-t/dev/ttyUSB", "-c/dev/ttyUSB1", "-r/dev/ttyUSB4"],
#             "sudo": true
#         }
#     ]
# }
