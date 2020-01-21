import pyvisa as visa
import Errors

class Manager:
    """
    This class is used to provide users with access to PyVisa resource management functions. It also implements a number of functions used to automate
    the manager refreshing process, in order to deal swiftly with new instruments and tools added after the first initialization. 
    """
    def __init__(self):
        """
        Manager initialization function. It uses methods imported by the PyVISA (version > 1.8) package in order to create an object capable to manage the
        tools interfaced with the PC via IEEE standard interfaces, like GPIB (IEEE 488.1/.2 standards) and RS232 (EIA-RS232). It tries to open a 
        PyVisa.ResourceManager object and then, if succesfull, attempts to create a list of resources available to this Manager.
        """
        try:
            if float(visa.__version__[:3]) < 1.8:
                raise Errors.ManagerInitializationError
            else:
                self.manager = visa.ResourceManager()
        except Errors.ManagerInitializationError as error:
            error.error_handler()
        try:
            self.resources = self.manager.list_resources()
            if self.resources == ():
                self._refresh_resources_()
        except Errors.VoidManagerError as error:
            error.error_handler()
    
    def _is_resource_(self, adress):
        """
        This function was created to check that the address given is available for management by a given manager object. It simply return True when the
        given adress is in the list of available resources for a manager, giving false otherwise.
        
        Parameters:
            - adress: complete string giving the VISA adress of the instrument (for GPIB interfaces is something like GPIB0::01::INSTR).
        """
        return adress in self.resources

    def _refresh_resources_(self):
        """
        This function is used all the times when it's necessary to refresh the list of resources available to the manager (like when we initialize the
        manager or we try to open a just connected instrument).
        """
        try:
            initial_resources = self.resources
            self.resources = self.manager.list_resources()
            if self.resources == initial_resources:
                if self.resources == ():
                    raise Errors.VoidManagerError
                else:
                    raise Errors.InstrumentNotAvailableError
        except (Errors.VoidManagerError, Errors.InstrumentNotAvailableError) as error:
            error.error_handler()
            raise
            
    def open_instrument(self, adress):
        """
        This function is needed to create open the link between the computer and the instrument, creating an object corresponding to the instrument at
        the given adress.
       
        Parameters:
            - adress: complete string giving the VISA adress of the instrument (for GPIB interfaces is something like GPIB0::1::INSTR or GPIB0::24::INSTR).
        """
        try:
            if self._is_resource_(adress):
                return self.manager.open_resource(adress)
            else:
                self._refresh_resources_()
                if self._is_resource_(adress):
                    return self.manager.open_resource(adress)
                else:
                    raise Errors.InstrumentNotAvailableError            
        except Errors.InstrumentNotAvailableError as error:
            error.error_handler()

#Test script (only to be run when the class is running as a standalone)
if __name__ == '__main__':
    rm = Manager()
    print(rm)
    print(type(rm))
#    print(rm.manager)
#    print(rm.resources)
#    sourcemeter = rm.open_instrument('GPIB0::23::INSTR')
#    print(sourcemeter.query('*IDN?'))
#    sourcemeter.close()
#    electrometer = rm.open_instrument('GPIB0::27::INSTR')
#    print(electrometer.query('*IDN?'))
#    electrometer.close()
##This last command is used in order to verify the InstrumentNotAvailableError raising.
#    notaninstrument = rm.open_instrument('adress')