#!/usr/bin/python

#################################
# RAILtest_utils.py
#
# This Python library provides an abstraction for interfacing with RAILtest
# running on a Silicon Labs EFR32 device on a Wireless Starter Kit (WSTK).
# Currently only TCP is supported, although USB support could be added at some
# point.
#
# v1.0 - 2021-03-28 - kris.young@silabs.com
'''*******************************************************************************
 * # License
 * <b>Copyright 2021 Silicon Laboratories Inc. www.silabs.com</b>
 *******************************************************************************
 *
 * SPDX-License-Identifier: Zlib
 *
 * The licensor of this software is Silicon Laboratories Inc.
 *
 * This software is provided 'as-is', without any express or implied
 * warranty. In no event will the authors be held liable for any damages
 * arising from the use of this software.
 *
 * Permission is granted to anyone to use this software for any purpose,
 * including commercial applications, and to alter it and redistribute it
 * freely, subject to the following restrictions:
 *
 * 1. The origin of this software must not be misrepresented; you must not
 *    claim that you wrote the original software. If you use this software
 *    in a product, an acknowledgment in the product documentation would be
 *    appreciated but is not required.
 * 2. Altered source versions must be plainly marked as such, and must not be
 *    misrepresented as being the original software.
 * 3. This notice may not be removed or altered from any source distribution.
 *
 *******************************************************************************
 * # Evaluation Quality
 * This code has been minimally tested to ensure that it builds and is suitable
 * as a demonstration for evaluation purposes only. This code will be maintained
 * at the sole discretion of Silicon Labs.
 ******************************************************************************/
'''
import telnetlib
import serial
import time

# TODO: supply these as command line arguments
node_ip = "192.168.1.126"
tx_node_name = b"[TX]" # for debug printing

prompt_string = b">" # railtest prompt is ">" character

DEBUG = 5 # 0=debugging messages off, higher numbers print more messages

class RAILtest():
    ''' Perform energy scan and read RSSIs from the device connected to the WSTK at NODE_IP '''
    def __init___(self):
        self.usage()

    def InitNode(self, NodeIp):
        ''' Returns the RX handle after opening the Tx Telnet and initializing or None if it fails'''
        if DEBUG>5: print("START INIT RX:")
        try:
            self.rxser = telnetlib.Telnet(NodeIp, 4901, 5) # Telnet port to the RailTest CLI
        except:
            return(None)
        self.rxser.write(b"rx 0\r\n") # enter idle mode
        resp=self.rxser.read_until(prompt_string,1)
        if DEBUG>9: print(resp)
        if DEBUG>5: print('END INIT RX:')
        return(self.rxser)

    def SetChannel(self, channel):
        ''' Set RAILtest channel'''
        self.rxser.write(b"SetChannel " + str(channel).encode() + b" \r\n")
        resp=self.rxser.read_until(prompt_string,1)
        if DEBUG>9: print(resp)

    def GetRssi(self):
        ''' Enter RX mode, delay, execute getrssi in RAILtest and return the RSSI value'''
        self.rxser.write(b"rx 1 \r\n") # turn on RX
        resp=self.rxser.read_until(prompt_string,1)
        if DEBUG>9: print(resp)
        self.rxser.write(b"getrssi\r\n")
        # Wait for data received from other node
        rssi_resp = self.rxser.expect([prompt_string],2) #nonblock, 1 sec timeout
        if DEBUG>9: print(rssi_resp)
        self.rxser.write(b"rx 0 \r\n") # turn off RX
        resp=self.rxser.read_until(prompt_string,1)
        if DEBUG>9: print(resp)
        if rssi_resp[0] != -1:
            rssival = rssi_resp[2].split(b'{rssi:',1)[1].split(b'}')[0]
            return float(rssival)
        else:
            return 1 #assume positive value returned is error

    def DoCal(self):
        ''' Force IR calibration for PHY and return value'''
        return self.SetCal(0xFFFF)

    def SetConfigIndex(self, configIndex):
        ''' Set config index and wait for prompt to return '''
        self.rxser.write(b"setConfigIndex " + str(configIndex).encode() + b"\r\n") # select config
        resp=self.rxser.read_until(prompt_string,1)
        if DEBUG>9: print(resp)

    def SetCal(self,calValue):
        ''' Set IR calibration to specified value'''
        calstr = "0x{:04X}".format(calValue)
        self.rxser.write(b"setcal " + calstr.encode() + b"\r\n")
        # Wait for processing
        resp = self.rxser.expect([prompt_string],2) #nonblock, 1 sec timeou
        if DEBUG>9: print(resp)
        if len(resp) < 2:
            print("Error!")
            return 0
        if resp[0] != -1:
            ircalval = resp[2].split(b'{IR_Calibration:',1)[1].split(b'}')[0]
            return int(ircalval,16)
        else:
            return 1 #assume positive value returned is error

    def GetCal(self):
        ''' Get IR calibration value for current PHY'''
        self.rxser.write(b"getcal\r\n")
        # Wait for processing
        resp = self.rxser.expect([prompt_string],2) #nonblock, 1 sec timeout
        if DEBUG>9: print(resp)
        if len(resp) < 2:
            print("Error!")
            return 0
        if resp[0] != -1:
            ircalval = resp[2].split(b'{IR_Calibration:',1)[1].split(b'}')[0]
            return int(ircalval,16)
        else:
            return 1 #assume positive value returned is error

    def GetRailVer(self):
        ''' Get verbose rail version and hash'''
        self.rxser.write(b"getversionverbose\r\n")
        # Wait for processing
        resp = self.rxser.expect([prompt_string],2) #nonblock, 1 sec timeout
        if DEBUG>9: print(resp)
        if len(resp) < 2:
            print("Error!")
            return 0
        if resp[0] != -1:
            railverstr = resp[2].split(b'{RAIL:',1)[1].split(b'}')[0]
            print(railverstr)
            hashstr = resp[2].split(b'{hash:',1)[1].split(b'}')[0]
            print(hashstr)
            return [railverstr,hashstr]
        else:
            return [0,0]

    def ResetWSTK(self, wstk_ip):
        ''' Reset the WSTK to be sure we're starting from a known point
            Returns an error code if failed and None if OK
        '''
        try:
            management = telnetlib.Telnet(wstk_ip, 4902, 5)
        except:
            return(-1)

        management.read_until(b'WSTK>',1)
        management.write(b"target reset 3A000108\r\n") # why the 3A000108?
        time.sleep(1) # wait for target to boot
        management.close()
        return(None)

    def usage():
        print("python WSTK_railtest_ZWaveRangeTest [options go here...]")
        print("Use the python -u option to see the print statements come out unbuffered which can help find timing problems")

    def hackRF_tone(freqHz, vgaGain):
        """ Play a CW tone for 4 seconds at the specified amplitude and with the specified frequency and tcxo error """

    # Todo: Check retval (if command fails, notify and exit?)
        retval = os.system("hackrf_transfer -f " + str(freqHz) + " -n 10000000 -c " +
                str(hackrf_amplitude) + " -C " + str(hackrf_tcxo_clock_error_ppm) +
                " -x " + str(vgaGain) + " >/dev/null 2>&1")
