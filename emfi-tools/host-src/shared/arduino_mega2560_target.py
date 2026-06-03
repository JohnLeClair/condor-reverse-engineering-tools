# Copyright (c) 2025    Condor Embedded Technology, LLC
# All rights reserved.
#
# Author: John LeClair
# Email:  jleclair@condorembeddedtech.com
#
# filename: sram_as6c3216A_emfi_target.py
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

import time

# Notes: actual chip size is 14 mm x 14 mm.

class arduino_mega2560_target:
    class EXAMINE_RET_CODE:
        SUCCESS             = 0x1     # No bit errors or USB(CPU crash) issues.
        USB_ERROR           = 0x2     # Fatal Error with CPU or USB connection.     
        SRAM_BIT_ERRORS     = 0x4     # Target's SRAM Bank comparision ended with bit flips.
        REGISTER_BIT_ERRORS = 0x8     # Target's Register File comparison ended with bit flips.

    def setup(self):
        return self.EXAMINE_RET_CODE.SUCCESS

    def load_target(self):
        return self.EXAMINE_RET_CODE.SUCCESS

    def examine_target(self):
        return self.EXAMINE_RET_CODE.SUCCESS
 
    def examine_target_low_resolution(self):
        pass
  
    def reload_target(self):
        return self.EXAMINE_RET_CODE.SUCCESS

    def reconnect(self):
        pass