rm = Manager.Manager()
# Here we apply mode functions to the correct instrument.
sourcemeter = Keithley2400(rm, 'GPIB0::23::INSTR')
print(type(sourcemeter))
print(sourcemeter.manager)
print(sourcemeter.adress)
print(sourcemeter.instrument)
print(sourcemeter.identity)
sourcemeter.close()
# Here we apply tested functions to another instrument, a Keithley 6517A electrometer.
electrometer = Keithley2400(rm, 'GPIB0::27::INSTR')