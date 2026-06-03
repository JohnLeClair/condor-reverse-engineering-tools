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
# filename: xy_stage.py
# This file is part of the EMFI-Target project which is based at least in part
# by NewAE Ballistic Gel project hardware and software. 
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
from shared.stm32h7_swd_target import *
from shared.sram_as6c3216A_emfi_target import *
from shared.arduino_mega2560_target import *
# from xilinx_zynq_7000_target import *
# from xilinx_ultrascalplus_target import *

# Tools control
from shared.cnc_grbl import *
from shared.emfiblaster import *

# Utilities
import math
from time import sleep

# Plotting
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np
import pickle
from PIL import Image

# Definitions
# Target Type
TARGET_TYPE_SRAM                      = 1
TARGET_TYPE_STM32H7                   = 2
TARGET_TYPE_ARDUINO_MEGA2560          = 3
TARGET_TYPE_XILINX_7000_PS            = 4    # ARM32 PS TARGET
TARGET_TYPE_XILINX_7000_PL            = 5    # FPGA PL TARGET
TARGET_TYPE_XILINX_ULTRASCALE_PLUS_PS = 6    # ARM64 PS TARGET
TARGET_TYPE_XILINX_ULTRASCALE_PLUS_PL = 7    # FPGA PL TARGET
TARGET_TYPE_ARM64_TABLET_BOOTLOADER   = 8    # Breaking a encrypted and signed bootloader image
TARGET_TYPE_RNG_CHIP                  = 9    # Specific manufacturer's external Random Number Generator i2c bus chip
TARGET_TYPE_SRAM_999                  = 999  # TODO: remove me probably.

# SRAM TARGET Sub-mode
SRAM_SUB_MODE_SINGLE_SHOT_HIGH_RES    = 1   # One EMP blast to test EMP Probe Tip
SRAM_SUB_MODE_XY_SCAN_HIGH_RES        = 2   # Displays bit-flip locations for all possible SRAM addresses.
SRAM_SUB_MODE_XY_SCAN_LOW_RES         = 3   # Looks for chip die locations that react positively to EMP Pulses.

# Non-SRAM Target Sub-mode
TARGET_SUB_MODE_SINGLE_SHOT           = 1
TARGET_SUB_MODE_XY_SCAN               = 2

# Single-Shot Mode

SINGLE_SHOT_MODE_ENABLED              = 0
SINGLE_SHOT_MODE_ONCE_AND_EXIT        = 1
SINGLE_SHOT_MODE_MULTIPLE             = 2
SINGLE_SHOT_MODE_CONTINUAL            = 3

# Fake scan array for testing the display of results - bmp, graph, etc. 
debug_scan_results_array = np.array([
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
[1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
[1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
[1, 1, 2, 2, 1, 1, 1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1 ],
[1, 1, 1, 2, 1, 1, 1, 1, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1, 1 ],
[1, 1, 2, 2, 1, 1, 1, 1, 1, 4, 4, 4, 4, 1, 4, 1, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 4, 4, 1, 4, 4, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 4, 4, 1, 4, 1, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 4, 4, 1, 4, 1, 1, 1, 1 ],
[1, 1, 1, 4, 1, 1, 1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1 ],
[1, 1, 1, 4, 1, 1, 1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1 ],
[1, 1, 1, 4, 1, 1, 1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
[1, 1, 1, 1, 8, 8, 8, 8, 1, 8, 8, 8, 1, 1, 1, 1, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 8, 8, 8, 8, 8, 8, 8, 8, 8, 1, 1, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 8, 8, 8, 8, 1, 1, 8, 8, 1, 1, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ]
])

def plotScanResults(result_array):
    plt.imshow(result_array, cmap='viridis') #investigate np.meshgrid
    # plt.matshow(result_array)
    plt.colorbar(label='Examine')
    plt.title('2D Scan Results')
    plt.show()
    plt.savefig('my_high_res_image.png', dpi=300)
    input("Press enter to continue")


def testMeshGrid(result_array):
    # Create sample x, y, and 2D array data
    x = np.linespace(0, 20, 20)
    y = np.linespace(0, 20, 20)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) + np.cos(Y)

    # Create a color plot using pcolormesh
    plt.pcolormesh(X, Y, Z, cmap='RdBu')
    plt.colorbar(label='Value')
    plt.title('2D Array Visualization with pcolormesh')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.show()
    
def displaySafetyNotice():
    print("\n*** Danger: Arming EMP Blaster ***")
    print("*** Danger: Arming EMP Blaster ***")
    print("*** Danger: Arming EMP Blaster ***")
    print("\n        THINK SAFETY !\n")
    print("\nSafety Reminders:")
    print("(1) If changing EMP Probe tip - power off and wait at least 2 minutes") 
    print("(2) Assume When EMP Device is powered on - there is always high voltage in charging capacitor bank")
    print("(3) During operation, high voltage high voltage is always in tip. EMP Energy is only creating when")
    print("    current flow is rapidly switch off and back on.")
    print("(4) I speak from experience (1x was enough) - electric shock from some of these EMP devices are extremely painful\n")
    
# Main 
if __name__ == '__main__':
    print("Python version:")
    print(sys.version)

    # Flags TODO: Move this and calibration data etc to config file. 
    debug_xyz_stage_flag = False  # Only runs xy controller motion - no high voltage or debugger
    safe_debug = True             # Turns off high voltage source
    create_bitmap_flag = True     # Generate a bitmap of SRAM impact. 
    use_raw_method = True
    do_plot = True

    # Menu determined flags
    xy_scanner_mode = False     # Determines if all x/y positions are scanned ie: not a single shot. 
    single_shot_mode = SINGLE_SHOT_MODE_ENABLED    # Sends a EMP pulse only once. ie: no cnc controller needed.
    sram_target = False  
    sram_single_shot_mode = SRAM_SUB_MODE_SINGLE_SHOT_HIGH_RES   # No cnc controller needed.       
    high_res_scan_mode = True         
    point_scan_result = None    # Results of a single EMP Pulse on a Target.
    first_point_scan = True     # initialize first run with data.
    
    emp_manual_pulse_repeat = False    # if in single shot mode - have the option to manually strike same position with multiple pulses.
    x_initial_position = 0.0           # x-position single shot probe location
    y_initial_position = 0.0           # y-position single shot probe location        

    # TODO: Remove this test.
    # plotScanResults(debug_scan_results_array)
    # sys.exit()

    # Command line argument parsing
    parser = argparse.ArgumentParser("XY Stage with specific targets")
    parser.add_argument('-p', '--emp',        type=str, help='emp pulse serial port address')
    parser.add_argument('-t', '--target',     type=str, help='emp pulse serial port address')
    parser.add_argument('-c', '--controller', type=str, help='xyz stage controller serial port address')
    parser.add_argument('-r', '--relayboard', type=str, help='relay board serial port address')
    args = parser.parse_args()    

    print(args.emp) 

    print("\nChoose a target: ")
    print("   (1) SRAM EMFI-Target or NewAE Ballistic Gel\u2122")
    print("   (2) STM32H7 Target (SWD Mode Debugger)")
    print("   (3) Arduino ATMEGA-2560 Target (SAM-ICE JTAG)")
    print("   (4) Xilinx Zynq XC7 Series (XSDB/Vivado)")
    print("   (5) Xilinx Zynq Ultrascale+ (XSDB/Vivado)")
    print("   (6) Unnamed ARM64 Tablet Bootloader (Saleae Logic 2 Python Automation API)")
    print("   (999) Single Shot Probe tester into EMFI Target SRAM Board to measure view spread")
    target_type_str = input()
    target_type = int(target_type_str)

    # if the target is SRAM EMFI-Target
    if target_type == TARGET_TYPE_SRAM or target_type == TARGET_TYPE_SRAM_999: # TODO: delete 999 mode as redundant
        print()
        print("Choose a SRAM Target sub-mode:")
        print("   (1) Single-Shot Pulse - high resolution")
        print("   (2) XY-Stage Scan view SRAM corruption coverage - high resolution")
        print("   (3) XY-Stage Recon Scan low-resolution")
        sram_target_sub_mode_str = input()
        sram_target_sub_mode = int(sram_target_sub_mode_str)
        if sram_target_sub_mode > SRAM_SUB_MODE_SINGLE_SHOT_HIGH_RES:
            xy_scanner_mode = True
    else:
        # Target other than SRAM Target - ie: arduino, ultrascale+, etc
        print()
        print("Choose a Target sub-mode:")
        print("   (1) Single-Shot Pulse")
        print("   (2) XY-Stage Recon Scan")        
        target_sub_mode_str = input()
        target_sub_mode = int(target_sub_mode_str)
        if target_sub_mode == TARGET_SUB_MODE_XY_SCAN:
            xy_scanner_mode = True

    # Configure SRAM Mode: single shot pulse request
    if target_type == TARGET_TYPE_SRAM or target_type == TARGET_TYPE_SRAM_999:
        sram_target = True
        if sram_target_sub_mode == SRAM_SUB_MODE_SINGLE_SHOT_HIGH_RES:            
            # For only a single point EMP Pulse. Cheesy Hack to only run the nested for loops once
            x_width_mm = 1.0
            y_width_mm = 1.0
            x_stepsize_mm = 1.0
            y_stepsize_mm = 1.0
        elif sram_target_sub_mode == SRAM_SUB_MODE_XY_SCAN_HIGH_RES:
            high_res_scan_mode = True
        elif sram_target_sub_mode == SRAM_SUB_MODE_XY_SCAN_LOW_RES:
            high_res_scan_mode = False
        else:
            print("Undefined Sub-menu selection. Exiting application ...")
            sys.exit()
    else:
        # Non-SRAM Target sub-mode configuration
        high_res_scan_mode = False  # currently XY Recon scans for all targets except SRAM are always low resolution looking for hot spots. 
        if target_sub_mode == TARGET_SUB_MODE_SINGLE_SHOT:
            single_shot_mode = SINGLE_SHOT_MODE_ENABLED    # Initialize single shot fire mode. It will get changed later (Hack Alert)

        # Force Single Shot - no xy scanner motion. Hack Alert.   
        x_width_mm = 1.0
        y_width_mm = 1.0
        x_stepsize_mm = 1.0
        y_stepsize_mm = 1.0            

    # Handle xy scanner recon dimensions and/or initial probe position.
    if xy_scanner_mode:
        print()
        value = input("Enter x-axis chip or x-scan distance dimension(mm): ")
        x_width_mm = float(value)
        value = input("Enter y-axis chip or y-scan distance dimension(mm): ")
        y_width_mm = float(value)
        value = input("Enter x-step resolution (mm): ")
        x_stepsize_mm = float(value)
        value = input("Enter y-step resolution (mm): ")
        y_stepsize_mm = float(value)
    else:
        # Determine the Single Shot EMP pulse destination on chip. Note: this is highly dependent on calibrated CNC Controller.
        # Entering (0,0) skips the process of moving EMP probe tip
        x_initial_position, y_initial_position = [float(x) for x in input("\nEnter target coordinates x and y in mm (ie: 12.1 12.1):  ").split()] 

    # Handle Manually fired multiple EMP blasts into a single point
    # Repeatable bit flips rarely occurs 100% of the time - more like 60% so hitting the same spot multiple times might help
    # this percentage.
    if single_shot_mode == SINGLE_SHOT_MODE_ENABLED and not sram_target:
        print()
        print("Select EMP pulse repetition method (useful-since duplicating result is only about 60%% successful)")
        print("   (1) Single EMP pulse and exit program")
        print("   (2) Multiple, each manually-triggered EMP Pulses")
        print("   (3) Continual EMP pulses (visually inspect debugger/serial, etc output for changes in target)")
        single_shot_mode_str = input()
        single_shot_mode = int(single_shot_mode_str)

    # Input EMP Pulse Voltage selection
    print()
    print("Enter EMP Pulse Voltage")
    print("   (1) 350 Volts")
    print("   (2) 550 Volts")
    print("   (3) 600 Volts")
    print("   (4) 672 Volts")      
    print("   (5) 750 Volts")
    print("   (6) 950 Volts")
    value = input()
    voltage = int(value)

    # TODO: check parameters. Until then, type carefully. This will probably never get fixed.

    input("\n *** Hit enter to start test and arm EMFI Blaster ***\n")

    # CNC Controller
    # This utiles a target class inherited (or will be soon) from an abstract base class interface class.
##XXX    cnc_controller = CNC_Grbl()
##xxx    cnc_controller.start(args.controller)

    # Initialize and setup target.
    if debug_xyz_stage_flag == False:

        # Startup and initialize the EMP Target
        # A switch case statement would be nice here - but I still need python version < 3.10
        # and do not like pyenv. :-(
        if target_type == TARGET_TYPE_STM32H7:      
            target = Stm32h7_Target_Tests(args.relayboard)
        elif target_type == TARGET_TYPE_SRAM or target_type == TARGET_TYPE_SRAM_999:
            target = sram_emfi_target()
        elif target_type == TARGET_TYPE_ARDUINO_MEGA2560:
            target = arduino_mega2560_target()
        else:
            print("Currently unsupported or temporarily deleted target selection")
            sys.exit()

        target.setup()
        target.load_target()
        print("REMOVE ME")		
        # Initialize and startup EMFI Blaster
##XXX        emp_pulse = EmfiBlaster()

#XXX        retValue = emp_pulse.connect(args.emp)
###        if retValue != True:
###            if cnc_controller.isConnected():
###                cnc_controller.disconnect()
            # if target.isConnected(): TODO
            #    target.disconnect()
###XXX            print("EMFI Pulse Device failed to open")
###xxx            sys.exit()

        # Everthing is setup and aiming at the target. 
        # **** Danger: Arming High Voltage ****
###        if safe_debug:
###            emp_pulse.disarm() # just in case this was left in ARMING position on a different run
###            print("*** Safe Mode - No Arming of EMFI Blaster ***")
###        else:
###xxx            displaySafetyNotice()
            
            # Arm the EMP Device
###XXX            emp_pulse.arm(voltage)
###XXX            time.sleep(5)  # Give time to charge up capacitors

    # Create a 2D array of chip scan results.
    result_row = 0
    result_col = 0
    x_results_array_size = math.ceil(x_width_mm / x_stepsize_mm)
    y_results_array_size = math.ceil(y_width_mm / y_stepsize_mm) 

    scan_results_array = np.ones((x_results_array_size, y_results_array_size))
    # scan_results_array = np.ones((x_width_mm // x_stepsize_mm, y_width_mm // y_stepsize_mm))
    print(f"Calculated 2D Scan Array shape is : {scan_results_array.shape}")

    # Assume scan starts at point (0,0) unless initial position values are set.
    if x_initial_position != 0.0 or y_initial_position != 0.0:
        # Move the EMP Probe
        cnc_controller.move(x_initial_position, y_initial_position, 0)
        sleep(2.0) # not really needed, but EMP pulse shot immediately after moving the probe was irritating me.  

    # Start Scanning the Unit Under Test (UUT)
    positiveMovment = True
    # for y_counts in range(y_width_mm // y_stepsize_mm):
    for y_counts in range(math.ceil(y_width_mm / y_stepsize_mm)):
        result_row = 0
        # for x_counts in range(x_width_mm // x_stepsize_mm):
        for x_counts in range(math.ceil(x_width_mm / x_stepsize_mm)):

            # if not just testing xy-stage - initialize target, fire an EMP pulse, measure, repeat 
            if debug_xyz_stage_flag == False:
                # Step 1: Setup the target with data if applicatable (Re-set the EMFI Target SRAM to random data.

                if target.reload_target():
                    target.load_target()

                # Step 2: Fire EMP Pulse
                if safe_debug != True:
                    emp_pulse.shoot()
                    time.sleep(3.0) # just to make sure EMP is recharged.

                    # Step 2.5: Linger here and manually or automatically EMP blast away based on single-shot mode selected
                    emp_pulse_shoot_fini = False
                    while not emp_pulse_shoot_fini:
                        if single_shot_mode == SINGLE_SHOT_MODE_ENABLED:
                            break
                        elif single_shot_mode == SINGLE_SHOT_MODE_ONCE_AND_EXIT: 
                            break
                        elif single_shot_mode == SINGLE_SHOT_MODE_MULTIPLE:
                            while 1:
                                print("Press Enter to fire emp pulse again or 'q' + enter when done")
                                done_str = input()
                                if (done_str == 'q'):
                                    emp_pulse_shoot_fini = True
                                    break
                                else:
                                    emp_pulse.shoot()
                                    time.sleep(6.0) # just to make sure EMP is recharged + human reaction time = 5 seconds. 
                        elif single_shot_mode == SINGLE_SHOT_MODE_CONTINUAL:
                            # Continual Mode
                            emp_pulse.shoot()
                            time.sleep(5.0) # just to make sure EMP is recharged. 

                            # todo: add exception to handle control-c to cleanly break out of this forever loop.         
                        else:
                            print("single-shot mode: should nver be here")
                            sys.exit()
                
                # Step 3: Check for EMFI bit flips
                if high_res_scan_mode:
                    # High Resolution can be a scan or single-shot
                    point_scan_result = target.examine_target()
                else:
                    # XY Stage scan/recon returns a single value.
                    point_scan_result = target.examine_target_low_resolution()

                # Reset the data in SRAM if previously altered. No need to if single-shot.
                if point_scan_result != target.EXAMINE_RET_CODE.SUCCESS and single_shot_mode != True:
                    target.reload_target()

                # Step 4: Check if a USB failure due to CPU crash from EMP pulse
                #TODO: if (point_scan_result == target.EXAMINE_RET_CODE.USB_ERROR):
                #    target.reset_uut # TODO: check individual codes with AND. 
                #    target.reconnect()

                # Step 5: Populate high_res SRAM error array
                # Currently high resolution mode is only with SRAM target.
                if sram_target and high_res_scan_mode:
                    errdatay = point_scan_result['errdatay']  # TODO: unused at the moment. will store in file eventually (maybe)
                    errdatax = point_scan_result['errdatax']  # TODO: unused at the moment. will store in file eventually (maybe) 
                    errorlist = point_scan_result['errorlist']

                    if first_point_scan:
                        errorlistScanResults = errorlist  # initialize error data array.1 
                        first_point_scan = False

                    # Merge each data point into results scan array.
                    errorlistScanResults = np.bitwise_or(errorlistScanResults, errorlist)                    
                else:
                    scan_results_array[result_row][result_col] = point_scan_result
                    result_row += 1

                # TODO: delete me probably ? Reset statistics (or maybe keep a rolling tally? hence these 3 methods still exist)
                if target_type == TARGET_TYPE_SRAM or target_type == TARGET_TYPE_SRAM_999:
                    target.reset_sram_error_count()
                    target.reset_register_error_count()
                    target.reset_fatal_error_count()

            # Move xy stage if not in  single shot mode. 
            if xy_scanner_mode:
                # Move EMP Blaster to next blast and examine position    
                if positiveMovment:
                    cnc_controller.move(x_stepsize_mm, 0, 0)
                else:
                    cnc_controller.move(-1*x_stepsize_mm, 0, 0) 
                time.sleep(1)

        # Move xy stage if not in  single shot mode. 
        if xy_scanner_mode:
            result_col += 1
            cnc_controller.move(0, y_stepsize_mm, 0)
            time.sleep(0.1) # 100 msec

            # Completed single x-direction scan. now to move 
            # opposite direction for next x-direction scan.
            positiveMovment = not positiveMovment

        # Save scan_array data. but also save metadata, stepsize, voltage, date, time, etc
 ###   TODO: pickle.dump(scan_results_array, open("filename", "wb"))
    
    # Adjust the high resolution data to 1-bit grayscale.
    if high_res_scan_mode:   
        for i in range(len(errorlistScanResults)):
            if errorlistScanResults[i] > 0:
                errorlistScanResults[i] = 0     # black if errors.
            else:
                errorlistScanResults[i] = 255   # white if no errors.

        bmpWidth, bmpHeight = 2048, 2048
        xyArray = errorlistScanResults.reshape ((2048, 2048))
        image = Image.fromarray(xyArray, mode='L')
        image.save('my_bitmap.png')
        image.close()
    else:
        # Low Resolution plot 
        plotScanResults(scan_results_array)

    if debug_xyz_stage_flag == False:
        emp_pulse.disarm()



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
