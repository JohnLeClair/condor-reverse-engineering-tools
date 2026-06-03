
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

if __name__ == '__main__':
    print("Python version:")
    print(sys.version)

    # Initialize SRAM Target.
    target = sram_emfi_target()
    target.setup()
    target.load_target()

    input("Press 'enter' to contine")

    point_scan_result = target.examine_target()







# Developer Time Saver Note: Visual code for when the debugger script gets scrogged again.
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
