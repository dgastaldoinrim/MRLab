from OxfordMagLab2000.General import Manager,Instruments

rm = Manager.Manager()
instrument = Instruments(rm, rm.resources[0])
print(type(instrument))
print(instrument.manager)
print(instrument.adress)
print(instrument.instrument)
print(instrument.identity)
instrument.close()
#This last command is used in order to verify the InstrumentNotAvailableError raising.
notaninstrument = Instruments(rm, 'adress')