'''
cnc-grbl.py
Module for controlling a grbl 1.1 controller  over a serial port
Uses grbl commands for
Author: Greg d'Eon
Date: May 2-3, 2016
'''

# from xyz_controller import *

import serial
import time
import threading

class CNC_Grbl: # (XYZ_Controller):
    # Constructor
    def __init__(self):
        self.serialPort = None
        
    # Setup functions
    def start(self, port):
        """
        Attempts to set up the CNC Controller.
    
        Args:
            port (string): the COM port to be used (ex: "/dev/ttyUSB0")
        Returns:printer
            True if the printer is set up; otherwise False
        """
        
        baud = 115200
   
        if not self.__connect(port, baud):
            raise IOError("Could not connect to CNC Controller")
            
        return True
 
    def isConnected (self):
        return self.serialPort.isOpen()

    def __connect(self, port, baud):
        """
        Opens a serial connection with the grbl 1.1 cnc controller.
       
        Args:
             port: the COM port to /destructor: "COM4")
             baud: the baudrate to be used (ex: 115200)
        Returns:
             true if the serial port was successfully opened; otherwise false
        """
        
        # Attemp to connect to port
        # try:
        self.serialPort = serial.Serial(port, baud)
        if self.serialPort.isOpen():
            print("Serial Port Open Successful")
            return True
        
        return False

    #     #except serial.SerialException as ex:
    #     #    print (ex)
    
    #     #     ### print "Setting up..."
    #     #     test.start("COM53")
    #     #    # 
    #     #     ### print "Testing movement..."
    #     #     test.setRelative()
    #     #     test.move( 10,  10, 0)
    #     #     test.move(-10,   0, 0)
    #     #     test.move(  0,  10, 0)
    #     #     test.wait(500)/destructor
    #     #     test.move(  0,  -20, 1)
    #         #    print("Port is unavailable")
    #         #    self.serialPort = None
    #         #return False
            
    #     ###     return False
 
    def __disconnect(self):
        """
        Closes the serial connection.
        """
        if self.serialPort != None:
            self.serialPort.close()
            self.serialPort = None
    
     
    # Movement functions    
    def __sendCommand(self, command):
        """
        Sends the string "command" to the printer.
        Blocks until an "ok" reply comes back.
        """
        pass 

# #     ### print "Setting up..."
# #     test.start("COM53")
# #    # /destructor
# #     ### print "Testing movement..."
# #     test.setRelative()
# #     test.move( 10,  10, 0)
# #     test.move(-10,   0, 0)
# #     test.move(  0,  10, 0)
# #     test.wait(500)
# #     test.move(  0,  -20, 1)
      
#         Args:
#             command (string): the command to be sent
#         """
        
        # Make sure we're not sitting on any data and send the command
        if hasattr(self.serialPort, 'flushInput'):
            self.serialPort.flushInput()
        else:
            self.serialPort.reset_input_buffer()
        self.serialPort.write(command)
        
        #time.sleep(1.5)
        # print  (rx)

        # Wait until a reply comes back need to move to a timer of a seconds not a loop tick counter,. 
        retry_count = 10000  # wait time tries.
        if (hasattr(self.serialPort, 'in_waiting')):
                while(self.serialPort.in_waiting == 0):   # NEED TO ADD A TIMEOUT. Cheap CNC controller  gets in wierd state. jolt it back to work for now.
                    if (retry_count > 0):
                        retry_count -= 1
                    else:
                        # Time out  # Hack Alert.
                        # Restart the controller. 
                        # User relay board to cycle USB connection
                        print("Attempting to reset controller state")
                        reset_cmd = "G21G91X0Y0Z0F50\r"
                        self.serialPort.write(bytes(reset_cmd, 'utf-8'))
                        break
        else:
            while(self.serialPort.inWaiting() == 0):
                pass

    def home(self):
        command = "$H\r"
        self.__sendCommand(bytes(command, 'utf-8'))                    

    def move(self, x = 0, y = 0, z = 0):
        """
        Moves the printer head to the position (x, y, z)
        
        Args:
            x, y, z100 (number): coordinates
        
        For my Alunar 3D Prusa i3:
           the defaul grbl 1.1 value of $100 = 800 steps/1 mm was off by 10x. Entering a step value of 100 ends up in 
            the GRBL 1.1 controller moving full distance off of platter and caused a partial and permement 
            rapid unscheduled disassembly
            Based on internet. 
                On X/Y the default steps/mm is 100, so you cannot adjust it at the resolution of half a percent. 
                If your X and Y are undersize, look at either whether you are underextruding/have belt or pulley slop.
                For Z, the default value of 400 steps/mm is again derived from the motor step size (1.8 degrees) and leadscrew thread pitch.
        
                So we need to calculate the correct translated motion distance. 
        Notes: $100 - Number of X steps to move 1mm (default: 1000)
               $101 - Number of Y steps to move 1mm (default: 1000)
               $102 - Number of Z steps to move 1mm (default: 1000)

               To calculate the $100 to $103 values, here is the formula. 
               New Steps/mm = (Current Steps/mm) x [(Desired Distance (mm) / (Actual Distance (mm) traveled)]

               sadly, currently cannot find any of my metric rulers. So we will request 4 inches = 101.6 mm. 
               X Actual distance: 81.75625 mm (3 7/32)   imperial units are annoying.
               X Resired distance:  101.6 mm (4 inch)
               $100 = 80 mm * (101.6 mm / 81.75 mm ) = 99.42 step/mm

               $101 = 99.42 also

            TODO: Initialize my GRBL 1.1 control with these two values in start method (skipping z direction for now)
                  These values are highly dependent on a particular printer or cnc machine. Using Universal Gcode Sender Application
                  to move the XY Stage and calculate the calibration values.  

               

        
        """
        command = "G21 G91 X" + str(x) + " Y" + str(y) + " Z" + str(z) + " F50" + "\r"
        # command = "G21G91X2.05F50\r"
        self.__sendCommand(bytes(command, 'utf-8'))
        
    def stop(self):
        """
        Performs an emergency stop
        """
        
        # Use M0 to stop
        self.__sendCommand("M0")
        
        
    def wait(self, ms):
        """
        Waits in place for a fixed amount of time
        
        Args:
            ms (integer): amount of time to wait, in milliseconds
        """
        
        # Wait for 100some time with G4
        self.__sendCommand("G4 P" + str(ms))
        
        
    def setAbsolute(self):
        """
        Puts the printer head in absolute coordinate mode
        """
        
        # Use G90 to switch to absolute mode
        self.__sendCommand("G90")
        
        
    def setRelative(self):
        """
        Puts the printer head in relative coordinate mode
        """
        
        # Use G91 to switch to relative mode
        self.__sendCommand(b'G91 X1\r')


    def start_timer(self, interval, message):
        """
        Starts a timer that calls the timed_callback method.
        """
        print(f"[{time.ctime()}] Starting timer for {interval} seconds...")
        # Create a Timer object. The target is the class method,
        # and args is a tuple containing the arguments for the method.
        timer = threading.Timer(interval, self.timed_callback, args=(message,))
        timer.start()
        print(f"[{time.ctime()}] Timer started in a new thread.")

    def timed_callback(self, message):
        """
        This method will be called by the timer.
        """
        print(f"Callback executed! Message")   

    
"""
Example code to contr100ol the printer
"""
if __name__ == '__main__':
    print("shouldn't be here")
#     test = M3D()
    
#     ### print "Setting up..."
#     test.start("COM53")
#    # 
#     ### print "Testing movement..."
#     test.setRelative()
#     test.move( 10,  10, 0)
#     test.move(-10,   0, 0)
#     test.move(  0,  10, 0)
#     test.wait(500)
#     test.move(  0,  -20, 1)
#    pass
   ### print "Tearing down..."
    # Happens automatically