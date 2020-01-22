import Errors

class Instruments:
    def __init__(self, manager_int, adress_int, read_terminator_int = None, write_terminator_int = 'CRLF', end_or_identify_int = True):
        """
        This function is used to initialize an object corresponding to an SCPI-compliant instrument for use with PyVISA. It defines instrument's manager
            and adress, opens the link between controlling computer and instrument, sets the instrument timeout to infinite and then request the
            instrument's identity and creates an object propriety, called last_error, in which controller can store last answer to an error query given
            by the instrument.
        
        Parameters:
            - manager_int = an istance of Manager class.
            - adress_int = the SCPI-compliant adress for the instrument.
            - read_terminator_int: parameter used to set the appropriate read terminator for the instrument. Available values are None or any possible combination of 'CR' (\r) and 'LF' (\n)
                characters. Result must be parsed into a string;
            - write_terminator_int: parameter used to set the appropriate write terminator for the instrument. Available values are None or any possible combination of 'CR' (\r) and 'LF' (\n)
                characters. Result must be parsed into a string;
            - end_or_identify_int: parameter used to set if the instrument can use EOI (End Or Identify) line to tell the controller if the message sending has ended.
        """ 
        try:
            if 'Manager' in str(type(manager_int)):
                self.manager = manager_int
            else:
                raise Errors.InvalidManagerError
        except Errors.InvalidManagerError as error:
            error.error_handler()
        self.adress = adress_int
        self.instrument = self.manager.open_instrument(self.adress)
        try:
            if read_terminator_int == None:
                self.instrument.read_terminator = ''
            elif read_terminator_int == 'CR':
                self.instrument.read_terminator = '\r'
            elif read_terminator_int == 'CRLF':
                self.instrument.read_terminator = '\r\n'
            elif read_terminator_int == 'LF':
                self.instrument.read_terminator = '\n'
            elif read_terminator_int == 'LFCR':
                self.instrument.read_terminator = '\n\r'
            else:
                raise Errors.InvalidReadTerminatorError()
        except Errors.InvalidReadTerminatorError as error:
            error.error_handler()
        try:
            if write_terminator_int == None:
                self.instrument.write_terminator = ''
            elif write_terminator_int == 'CR':
                self.instrument.write_terminator = '\r'
            elif write_terminator_int == 'CRLF':
                self.instrument.write_terminator = '\r\n'
            elif write_terminator_int == 'LF':
                self.instrument.write_terminator = '\n'
            elif write_terminator_int == 'LFCR':
                self.instrument.write_terminator = '\n\r'
            else:
                raise Errors.InvalidWriteTerminatorError()
        except Errors.InvalidWriteTerminatorError as error:
            error.error_handler()
        self.instrument.send_end = end_or_identify_int;
        self.timeout = None
        self.instrument.timeout = self.timeout
        self.identity = self._identification_query_()
        self.last_internal_error = None
        
    """
    Common RS232/IEEE488(GPIB) commands
    """

    def _process_last_query_(self):
        """
        This function is used only when any RS232-capable instrument is connected via RS232 to order the instrument to reprocess the last query received
        and to send a new answer. This command can not be chained with other commands (must be sent by itself).
        """
        self.instrument.query('?')
        
    def _clear_status_(self):
        """
        This function is used to issue a clear status command to a SCPI-compliant instrument.
        """
        self.instrument.write('*CLS')
        
    def _event_enable_(self, all_disabled = False, enable_number = 0):
        """
        This function is used to enable the event register on the adressed SCPI-compliant instrument.
        
        Parameters:
            - all_disabled = boolean variable used, when true, to completely disable the event register.
            - enable_number = decimal equivalent of the binary number composed by the bits the user wants to enable in the event register.
        """
        if all_disabled:
            self.instrument.write('*ESE 0')
        else:
            self.instrument.write('*ESE {0:d}'.format(enable_number))
                
    def _event_enable_query_(self):
        """
        This function is used to query the event register status on the adressed SCPI-compliant instrument. The instrument answer to the query is the
            decimal equivalent of the bits enabled (i.e. set to 1) in the event register.
        """
        self.instrument.query('*ESE?')
        
    def _event_status_register_query_(self):
        """
        This function is used to query the event register status on the adressed SCPI-compliant instrument and then clear it. The instrument answer is
            the decimal equivalent of the bits enabled (i.e. set to 1) in the event register
        """
        self.instrument.query('*ESR?')
        
    def _identification_query_(self):
        """
        This function is used to query the identity of the adressed SCPI-compliant instrument. The instrument answer is a string containing instrument
            identity, composed at least by manufacturer, model number, serial number and firmware version of the instrument.
        """
        return self.instrument.query('*IDN?')
    
    def _operation_complete_command_(self):
        """
        This function adresses a device to set to 1 the operation complete bit of the status register, after all pendings commands were executed.
        """
        self.instrument.write('*OPC')
        
    def _operation_complete_query_(self):
        """
        This function is used to query if the adressed operations on an SCPI-compliant instrument are completed. The instrument answer to the
            query setting an ASCII 1 into the output queue when all the pending device operations are completed.
        """
        self.instrument.query('*OPC?')
        
    def _options_query_(self):
        """
        This function is used when the user wants to identify if and which optional card is installed in the adressed instrument.
        """
        self.instrument.query('*OPT?')
        
    def _recall_command_(self, save_position):
        """
        This function is used to recall a setup configuration saved in the internal memory at the specified location.
        
        Parameters:
            - save_position = integer number indicating the configuration saving position in the internal memory.
        """
        self.instrument.write('*RCL {0:d}'.format(save_position))
        
    def _reset_command_(self):
        """
        This function is used to reset the adressed instrument to default conditions.
        """
        self.instrument.write('*RST')
        
    def _save_command_(self, save_position):
        """
        This function is used to save the current instrument configuration in the internal memory at the location specified.
        
        Parameters:
            - save_position = integer number indicating the configuration saving position in the internal memory.
        """
        self.instrument.write('*SAV {0:d}'.format(save_position))
        
    def _service_request_enable_command_(self, all_disabled = False, enable_number = 0):
        """
        This function is used to enable the service request register on the adressed SCPI-compliant instrument.
        
        Parameters:
            - all_disabled = boolean variable used, when true, to completely disable the service request register.
            - enable_number = decimal equivalent of the binary number composed by the bits the user wants to enable in the service request register.
        """        
        if all_disabled:
            self.instrument.write('*SRE 0')
        else:
            self.instrument.write('*SRE {0:d}'.format(enable_number))
            
    def _service_request_enable_query_(self):
        """
        This function is used to query the event register status on the adressed SCPI-compliant instrument. The instrument answer is the decimal
            equivalent of the bits enabled (i.e. set to 1) in the event register.
        """
        self.instrument.query('*SRE?')
        
    def _status_byte_query_(self):
        """
        This function is used to query the status byte condition on the adressed SCPI-compliant instrument (1 when all pending operations are
            completed).
        """
        self.instrument.query('*STB?')
        
    def _trigger_command_(self):
        """
        This function is used to send a bus trigger to the adressed instrument.
        """
        self.instrument.write('*TRG')
        
    def _self_test_query_(self):
        """
        This function is used to require an instrument self-test (usually during the instrument initialization phase).
        """
        self.instrument.query('*TST?')
        
    def _wait_to_continue_(self):
        """
        This function is used in order to force the adressed instrument to wait that all previous commands were executed before taking new actions.
        """
        self.instrument.write('*WAI')
        
    def close(self):
        """
        This function is used to close the instrument link with the controlling computer.
        """
        self.instrument.close()
        
    def type_dictionary(self, keys, buffers):
        """
        This function is used when, composing a buffer, is necessary to give more flexibility to the user with the using of literal arguments in functions
            calls. It creates a dictionary where the keys are given by a tiny, title or uppercase string and the buffers are the strings used to complete
            the commands issued to a particular instrument providing the appropriate buffer termination. It raises an error if keys and buffers tuples 
            are not of the same length.
        """
        try:
            if len(keys) == len(buffers):
                lista = []
                for i in range(len(keys)):
                    lista += [(keys[i], buffers[i]),(keys[i].title(), buffers[i]),(keys[i].upper(), buffers[i])]
                return lista
            else:
                raise Errors.InvalidTypeDictionaryError
        except Errors.InvalidTypeDictionaryError as error:
            error.error_handler()
            raise

#Test script (only to be run when the class is running as a standalone)
import Manager

if __name__ == '__main__':
    rm = Manager.Manager()
    sourcemeter = Instruments(rm, 'GPIB0::24::INSTR')
    print(type(sourcemeter))
    print(sourcemeter.manager)
    print(sourcemeter.adress)
    print(sourcemeter.instrument)
    print(sourcemeter.identity)
    sourcemeter.close()
    electrometer = Instruments(rm, 'GPIB0::27::INSTR')
    print(type(electrometer))
    print(electrometer.manager)
    print(electrometer.adress)
    print(electrometer.instrument)
    print(electrometer.identity)
    electrometer.close()
#This last command is used in order to verify the InstrumentNotAvailableError raising.
    notaninstrument = Instruments(rm, 'adress')