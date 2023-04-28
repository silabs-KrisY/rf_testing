#!/usr/bin/python

#################################
# HackRF_utils.py
#
# This Python library provides functions to use the HackRF SDR as an RF test
# instrument. It is connected locally via USB and requires the HackRF executables
# and libraries be installed on the host.
#
# v1.0 - 2021-03-28 - kris.young@silabs.com
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

import os   #gives us the ability to run shell commands

class HackRF():
    ''' Functions to use the HackRF as an RF test instrument - connected locally via USB '''

    def hackRF_tone(self, freqHz, hackrf_amplitude, hackrf_vgaGain,
        hackrf_tcxo_clock_error_ppm, hackrf_tone_duration_ms):
        """ Play a CW tone at the specified amplitude and with the specified
            frequency and tcxo error. Sample rate is 10 MHz (default), which is
            a period of 0.1us per sample, so the millisecond duration argument
            is multiplied by 10000 """

        retval = os.system("hackrf_transfer -f " + str(freqHz) + " -n " +
                str(hackrf_tone_duration_ms * 10000) + " -c " + str(hackrf_amplitude) +
                " -C " + str(hackrf_tcxo_clock_error_ppm) +
                " -x " + str(hackrf_vgaGain) + " >/dev/null 2>&1")
        if retval != 0:
            # Error occurred - print hex code and exit
            print("Error executing hackrf utility: {:#x}".format(retval))
            exit(1) #this doesn't exit because it's running in a separate thread
                    # TODO: cause a returned error to exit
