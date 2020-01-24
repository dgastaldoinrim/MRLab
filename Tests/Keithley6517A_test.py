from OxfordMagLab2000.General import Manager
from OxfordMagLab2000.KeythleyInstruments import Keithley6517A
    
rm = Manager.Manager()
# Here we apply tested functions to the correct instrument.
electrometer = Keithley6517A.Keithley6517A(rm, 'GPIB0::27::INSTR')
print(type(electrometer))
print(electrometer.manager)
print(electrometer.adress)
print(electrometer.instrument)
print(electrometer.identity)
# Here we apply tested functions to another instrument, a Keithley 2400 SourceMeter.
sourcemeter = Keythley6517A.Keithley6517A(rm, 'GPIB0::23::INSTR')
print(type(sourcemeter))