from ..General import Errors,Instruments

class Keithley2182(Instruments.Instruments):
    """
    This class is a wrapper that contains all the necessary functions to setup an electrical measurement with a Keithley model 2182 Nan0voltmeter.
    """

    def __init__(self, manager, adress, read_terminator = 'LF', write_terminator = 'LF', end_or_identify = True, reset = True):
        """
        This function is used in order to initialize the link to a Keithley model 2182 Nanovoltmeter. It inherits from the Instruments class (contained in
            the Instruments.py code) the general SCPI-Instrument initialization, and then specifies it adding some attributes specific to this instrument.
        
        Parameters:
            - manager = an istance of Manager class.
            - adress = the SCPI-compliant adress for the instrument.
            - read_terminator: parameter used to set the appropriate read terminator for the instrument. Available values are None or any possible combination of 'CR' (\r) and 'LF' (\n)
                characters. Result must be parsed into a string;
            - write_terminator: parameter used to set the appropriate write terminator for the instrument. Available values are None or any possible combination of 'CR' (\r) and 'LF' (\n)
                characters. Result must be parsed into a string;
            - end_or_identify: parameter used to set if the instrument can use EOI (End Or Identify) line to tell the controller if the message sending has ended.
            - reset = boolean parameter that enables (when true) or disables (otherwise) the instrument resetting function execution.
        """
        Instruments.Instruments.__init__(self, manager, adress, read_terminator_int = read_terminator, write_terminator_int = write_terminator, end_or_identify_int = end_or_identify)
        if reset:
            self._system_reset_()
        self.last_measurement = None
            
    def _system_reset_(self, secure_output = True):
        """
        This function is used to reset the instrument to productions defaults, if required during the initialization phase.
        """
        try:
            if 'KEITHLEY' in self.identity and '2182' in self.identity:
                self._self_test_query_()
                self._reset_command_()
                self._clear_status_()
                self._event_enable_(enable_number = 253)
                self._event_enable_query_()
                self._event_status_register_query_()
                self._service_request_enable_command_(enable_number = 189)
                self._service_request_enable_query_()
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            raise

    def _error_query_(self):
        """
        This function is used in order to query if an error occurred during the execution of the last series of commands on the adressed instrument.
        """
        try:
            if 'KEITHLEY' in self.identity and '2182' in self.identity:
                error_query = self.instrument.query(':SYST:ERR?')
                self.last_internal_error = error_query.split(',')
                if self.last_internal_error[0] != '0':
                    raise Errors.ReportInstrumentInternalError(self.last_internal_error[0], self.last_internal_error[1][1:-2])
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            raise

    def configure_voltage_measurement_not_complete(self):
        """
        """
        try:
            if 'KEITHLEY' in self.identity and '2182' in self.identity:
                self.instrument.write('SENS:FUNC:VOLT;SENS:VOLT:CHAN1:RANG:AUTO ON;')
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            raise
        
    def measure_voltage_not_complete(self):
        """
        """
        try:
            if 'KEITHLEY' in self.identity and '2182' in self.identity:
                string = self.instrument.query('MEAS:VOLT?')
            else:
                raise Errors.IncorrectInstrumentError
            self.last_measurement = float(string)
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            raise