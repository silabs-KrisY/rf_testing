#!/usr/bin/python

#################################
# RSSI_sweep.py
#
# This program performs energy scans on a WSTK connected device running RAILtest in
# conjunction with commanding a HackRF to output tones. The RSSI from each energy
# scan is averaged and logged. The purpose of this is to characterize the frequency
# response of the DUT.
#
# v1.0 - 2020-04-13 - kris.young@silabs.com
#################################
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

from RAILtest_utils import RAILtest
from HackRF_utils import HackRF
#import telnetlib
#import serial
import datetime
import threading
#import os   #gives us the ability to run shell commands
import csv
import time

# TODO: supply these as command line arguments
node_ip = "192.168.1.147"

railtest_channel = 0

DEBUG = 5 # 0=debugging messages off, higher numbers print more messages


hackrf_amplitude = 127
hackrf_tcxo_clock_error_ppm = -16
hackrf_tx_vga_gain = 0     # 0-47 in 1dB steps

start_freq_hz = 900000000
stop_freq_hz = 904000000
step_freq_hz = 10000

trial_name = "ch0_phy_test"

csv_logging = True
csv_filename = trial_name + ".csv"


# Init our RAILtest object and HackRF (CW source)
R = RAILtest()
H = HackRF()

# Reset the WSTK to start with a clean setup
if R.ResetWSTK(node_ip) != None:
    print("failed to open WSTK port")
    exit()

# open the telnet port and initialize the WSTK
rxser=R.InitNode(node_ip)
if rxser == None:
    print("failed to open WSTK Telnet")
    exit()

R.SetChannel(railtest_channel)

if csv_logging == True:
        csvfile = open(csv_filename,"w")
        writer = csv.writer(csvfile)
        print("Running trial {}".format(trial_name))
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        railver, hash = R.GetRailVer()
        print("RAILver: {}, hash: {}".format(railver,hash))
        # Add the trial name to the data to make it easy to combine data
        # from multiple runs
        writer.writerow(["trial name","frequency","rssi"])

start_time = time.time()

for freq in range(start_freq_hz,stop_freq_hz+step_freq_hz,step_freq_hz):
    rssi_values = []
    for loop in range(0,10,1): # Loop 10 times for averaging
        # Start the hackRF tone in its own thread so it can run in parallel
        txthread=threading.Thread(target=H.hackRF_tone, args=(freq,
            hackrf_amplitude, hackrf_tx_vga_gain,
            hackrf_tcxo_clock_error_ppm))
        txthread.start() # start thread
        time.sleep(1) # Wait a sec for signal to stablize
        rssi_values.append(R.GetRssi())
        txthread.join() # wait for hackRF thread to finish before continuing
                        # with the loop
    average_rssi = sum(rssi_values) / len(rssi_values)
    print("Freq: {} Hz, RSSI: {:.02f} dBm".format(freq,average_rssi)) # Read RSSI
    if csv_logging == True:
        writer.writerow([trial_name,freq,average_rssi])

# How long did it take (good to know for next time)
print("Total time: {} seconds".format(time.time() - start_time))

if csv_logging == True:
    csvfile.close()
