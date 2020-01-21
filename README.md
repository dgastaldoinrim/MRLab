# MRLab
A project that contains the Python classes needed to interface an Oxford MagLab2000 cryogenic system and other tools with any computer using USB-GPIB adapters and Virtual Instrument software architecture (VISA) libraries.

# Requires
The code contained requires the use of Python 3.5 or superior.

It requires for sure the installation of the pyvisa python package, available for install with the command
pip install pyvisa

Also, a functional VISA library must be installed and wrapped for the use with your Python installation.
This could be a NI (National Instruments) VISA or a Keysight (formerly Agilent) VISA library.

The first one is usually integrated in a NI-Labview installation and requires a proper licence.
The second one is freely available, but the download requires registration into Keysight sites.

A completely Python backend is also available from the package pyvisa-py, available for install using the command
pip install pyvisa-py

# Tested systems
Files in this repository were cloned on different OS and tested against 
TO BE CONTINUED
