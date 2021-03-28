# WSTK RF Test Scripts
Some RF testing scripts that communicate with a Wireless Starter Kit (WSTK) with a device running the RAILTest firmware.

# Contents
- Railtest_utils.py - This Python library provides an abstraction for interfacing with RAILtest running on a Silicon Labs EFR32 device on a Wireless Starter Kit (WSTK). Currently only TCP is supported, although USB VCOM support could be added at some point.

- HackRF_utils.py - This Python library provides an abstraction for using the HackRF SDR as an RF test instrument. It is connected locally via USB and requires the HackRF executables and libraries be installed on the host.

- RSSI_sweep.py - Performs a CW sweep of a device running RAILtest on a WSTK and using a HackRF SDR to generate the CW signal.

- image_rejection_test.py - Performs some iterative testing on different PHYs with different IR calibration values.

# Contact
Kris Young - kris.young@silabs.com
