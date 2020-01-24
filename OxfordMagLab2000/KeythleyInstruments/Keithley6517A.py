import math
from ..General import Errors,Instruments

class Keithley6517A(Instruments.Instruments):
    """
    This class is a wrapper that contains all the necessary functions to setup an electrical measurement with a Keithley model 6517A Electrometer.
    """

    def __init__(self, manager, adress, read_terminator = 'LF', write_terminator = 'LF', end_or_identify = True, reset = True):
        """
        This function is used in order to initialize the link to a Keithley 2400 SourceMeterUnit (SMU). It inherits from the Instruments class (contained in
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
        self.arm_count = None
        self.trigger_count = None
        self.sweep_steps = None
        self.output_status = None
        if reset:
            self._system_reset_()
    
    def _error_query_(self):
        """
        This function is used in order to query if an error occurred during the execution of the last series of commands on the adressed instrument.
        """
        try:
            if 'KEITHLEY' in self.identity and '6517A' in self.identity:
                error_query = self.instrument.query(':SYST:ERR?')
                self.last_internal_error = error_query.split(',')
                if self.last_internal_error[0] != '0':
                    raise Errors.ReportInstrumentInternalError(self.last_internal_error[0], self.last_internal_error[1][1:-2])
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            raise

    def _output_off_(self):
        """
        This function is used to set the instrument source off whenever required, registering the action in the appropriate attribute in the object.
        """
        try:
            if 'KEITHLEY' in self.identity and '6517A' in self.identity:
                self.instrument.write(':OUTP OFF;')
                self.output_status = self.instrument.query(':OUTP?')
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            raise
    
    def _output_on_(self):
        """
        This function is used to set the instrument source on whenever required, registering the action in the appropriate attribute in the object.
        """
        try:
            if 'KEITHLEY' in self.identity and '6517A' in self.identity:
                self.instrument.write(':OUTP ON;')
                self.output_status = self.instrument.query(':OUTP?')
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            self._output_off_()
            error.error_handler()
            raise
    
    def _sense_general_configuration_(self, buffer_radix, auto_NPLC, manual_NPLC, reference, auto_digits, manual_digits, average_state, average_type, average_control, average_count, average_noise_tolerance, median_state, median_rank):
        """
        This function is used to configure the options of a measurement that are common to all the possible physical quantities measurable with this
            instrument, that are voltage, current, resistance and charge. To find explanation for the parameters not explicitly treated in this function
            please refer to any of the sense functions given later on (from which this function inherits their parameters).
        
        Parameters:
            - buffer radix = string that gives the radix of all the strings that must be used in the configuration
        """
        try:
            mode_types = dict(self.type_dictionary(('On', 'Once', 'Off'),('ON', 'ONCE', 'OFF')))
            average_types = dict(self.type_dictionary(('None', 'Scalar', 'Advanced'),('NONE', 'SCAL', 'ADV')))
            control_types = dict(self.type_dictionary(('Moving', 'Repeated'),('MOV', 'REP')))
            buffer = buffer_radix + ':NPLC:AUTO {!s};'.format(mode_types[auto_NPLC])
            if auto_NPLC == 'off' or auto_NPLC == 'off'.title() or auto_NPLC == 'off'.upper():
                buffer += buffer_radix + ':NPLC {!s};'.format(manual_NPLC)
            if reference:
                buffer += buffer_radix + ':REF:STAT ON;'
            else:
                buffer += buffer_radix + ':REF:STAT OFF;'
            buffer += buffer_radix + ':DIG:AUTO {!s};'.format(mode_types[auto_digits])
            if auto_digits == 'off' or auto_digits == 'off'.title() or auto_digits == 'off'.upper():
                buffer += buffer_radix + ':DIG {!s};'.format(manual_digits)
            if average_state:
                buffer += buffer_radix + ':AVER:STAT ON;' + buffer_radix + ':AVER:TYPE {!s};'.format(average_types[average_type]) + buffer_radix + ':AVER:TCON {!s};'.format(control_types[average_control]) + buffer_radix + ':AVER:COUN {!s};'.format(average_count)
                if average_type == 'advanced' or average_type == 'advanced'.title() or average_type == 'advanced'.upper():
                    buffer += buffer_radix + ':AVER:ADV:NTOL {!s};'.format(average_noise_tolerance)
            else:
                buffer += buffer_radix + ':AVER:STAT OFF;'
            if median_state:
                buffer += buffer_radix + ':MED:STAT ON;' + buffer_radix + ':MED:RANK {!s};'.format(median_rank)
            return buffer
        except Errors.InvalidTypeDictionaryKeyError as error:
            return None
            error.error_handler()
            raise
        
    def _system_reset_(self, secure_output = True):
        """
        This function is used to reset the instrument to productions defaults, if required during the initialization phase.
        
        Parameters:
            - secure_output = boolean parameter used to secure the source output in the OFF state during the initialization phase.
        """
        try:
            if 'KEITHLEY' in self.identity and '6517A' in self.identity:
                self._self_test_query_()
                self._reset_command_()
                self._clear_status_()
                self._event_enable_(enable_number = 253)
                self._event_enable_query_()
                self._event_status_register_query_()
                self._service_request_enable_command_(enable_number = 189)
                self._service_request_enable_query_()
                if secure_output:
                    self._output_off_()
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError()
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            raise
            
    def acquire_linear_sweeps(self, num_sweeps, start_level, stop_level, points, folder, sample, mode, T = '', H = '', extension = '.txt', auto_range = 'On', manual_range = 2e-2, print_datas = True):
        """
        This function is used to acquire 1 or more measurements making a linear sweep of the internal source of the instrument (configured within this
            function by means of using the correspondent public methods) and then save it to a given file in the given directory.
        
        Parameters:
            - num_sweeps = integer number of sweeps user wants to be measured by the instrument.
            - start_level = internal voltage source start level for sweep.
            - stop_level = internal voltage source stop level for sweep.
            - points = integer number of points of which the sweep must be composed.
            - folder = string giving the complete path to the folder in which user wants the script to save datas.
            - sample = string giving the sample name.
            - mode = string specifing the measurement mode (R vs T, MR, etc.).
            - T = string specifing the (absolute) temperature at which measurement is taken (if not explicitly defined is an empty string).
            - H = string specifing the (magnetizing) field H at which measurement is taken (if not explicitly defined is an empty string).
            - extension = extension to the data file (.txt if not explicitly defined).
            - auto_range = if 'on' enables current auto-range mode, so current range will be automatically selected by the instrument at each sweep step.
            - manual_range = if auto_range mode is 'off', specify here the current measurement manual range.
            - print_datas = boolean value that specifies if the script must print datas on screen after taking them (if true) or not.
        """
        try:
            if 'KEITHLEY' in self.identity and '6517A' in self.identity:
                self.current_sense_configuration(auto_range = auto_range, manual_range = manual_range)
                self.arm_configuration()
                self.trigger_configuration()
                self._output_on_()
                for i in range(num_sweeps):
                    data = []
                    for j in range(points):
                        voltage_level = start_level + (j * (stop_level - start_level) / (points - 1))
                        self.voltage_source_configuration(voltage = voltage_level, meter_connect = True)
                        string = self.instrument.query(':DATA:FRES?')[:-1]
                        self._operation_complete_query_()
                        string_split = string.split(',')
                        save_string = string_split[1] + ',' + string_split[0]
                        data.append(save_string)
                    if print_datas:
                        print(data)
                self._operation_complete_query_()
                self._error_query_()
                self._output_off_()
                for i in range(num_sweeps):
                    filename = folder + sample + '_' + mode + '_T = {!s} K_H = {!s} Oe_linear sweep number {!s}_2 wires'.format(T, H, (i + 1)) + extension
                    with open(filename, 'w') as out_file:
                        for j in range(points):
                            if j != points:
                                out_file.write(data[j] + '\n')
                            else:
                                out_file.write(data[j])
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError, Errors.InvalidTypeDictionaryKeyError) as error:
            error.error_handler()

    def acquire_logarithmic_sweeps(self, num_sweeps, start_level, stop_level, points, folder, sample, mode, T = '', H = '', extension = '.txt', auto_range = 'On', manual_range = 2e-2, print_datas = True):
        """
        This function is used to acquire 1 or more measurements making a logarithmic sweep of the internal source of the instrument (configured within this
            function by means of using the correspondent public methods) and then save it to a given file in the given directory.
        
        Parameters:
            - num_sweeps = integer number of sweeps user wants to be measured by the instrument.
            - start_level = internal voltage source start level for sweep.
            - stop_level = internal voltage source stop level for sweep.
            - points = integer number of points of which the sweep must be composed.
            - folder = string giving the complete path to the folder in which user wants the script to save datas.
            - sample = string giving the sample name.
            - mode = string specifing the measurement mode (R vs T, MR, etc.).
            - T = string specifing the (absolute) temperature at which measurement is taken (if not explicitly defined is an empty string).
            - H = string specifing the (magnetizing) field H at which measurement is taken (if not explicitly defined is an empty string).
            - extension = extension to the data file (.txt if not explicitly defined).
            - auto_range = if 'on' enables current auto-range mode, so current range will be automatically selected by the instrument at each sweep step.
            - manual_range = if auto_range mode is 'off', specify here the current measurement manual range.
            - print_datas = boolean value that specifies if the script must print datas on screen after taking them (if true) or not.
        """
        try:
            if 'KEITHLEY' in self.identity and '6517A' in self.identity:
                self.current_sense_configuration(auto_range = auto_range, manual_range = manual_range)
                self.arm_configuration()
                self.trigger_configuration()
                self._output_on_()
                for i in range(num_sweeps):
                    data = []
                    for j in range(points):
                        voltage_level = 10 ** (math.log10(start_level) + (j * ((math.log10(stop_level) - math.log10(start_level)) / (points - 1))))
                        self.voltage_source_configuration(voltage = voltage_level, meter_connect = True)
                        string = self.instrument.query(':DATA:FRES?')[:-1]
                        self._operation_complete_query_()
                        string_split = string.split(',')
                        save_string = string_split[1] + ',' + string_split[0]
                        data.append(save_string)
                    if print_datas:
                        print(data)
                self._operation_complete_query_()
                self._error_query_()
                self._output_off_()
                for i in range(num_sweeps):
                    filename = folder + sample + '_' + mode + '_T = {!s} K_H = {!s} Oe_logarithmic sweep number {!s}_2 wires'.format(T, H, (i + 1)) + extension
                    with open(filename, 'w') as out_file:
                        for j in range(points):
                            if j != points:
                                out_file.write(data[j] + '\n')
                            else:
                                out_file.write(data[j])
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError, Errors.InvalidTypeDictionaryKeyError) as error:
            error.error_handler()
            
    def acquire_measurements(self, folder, sample, mode, T = '', H = '', extension = '.txt', print_datas = True):
        """
        This function is used to acquire 1 or more one shot measurements with the internal source of the instrument fixed to a value (that has been setup
            previously by users calling the correspondent public method) and then save it to a given file in the given directory. IMPORTANT: also measured
            function configuration must be done outside the function scope.
        
        Parameters:
            - folder = string giving the complete path to the folder in which user wants the script to save datas.
            - sample = string giving the sample name.
            - mode = string specifing the measurement mode (R vs T, MR, etc.).
            - T = string specifing the (absolute) temperature at which measurement is taken (if not explicitly defined is an empty string).
            - H = string specifing the (magnetizing) field H at which measurement is taken (if not explicitly defined is an empty string).
            - extension = extension to the data file (.txt if not explicitly defined).
            - print_datas = boolean value that specifies if the script must print datas on screen after taking them (if true) or not.
        """
        try:
            if 'KEITHLEY' in self.identity and '6517A' in self.identity:
                self._output_on_()
                data = []
                split_data = []
                for i in range(self.trigger_count):
                    string = self.instrument.query(':DATA:FRES?')[:-1]
                    data.append(string)
                self._operation_complete_query_()
                self._error_query_()
                self._output_off_()
                filename = folder + sample + '_' + mode + '_T = {!s} K_H = {!s} Oe_fixed source_2 wires'.format(T, H) + extension
                element_number = len(self.instrument.query(':FORM:ELEM?').split(','))
                if element_number == 1:
                    with open(filename, 'w') as out_file:
                        for i in range(self.trigger_count):
                            row = str(data[i])
                            if i != self.trigger_count:
                                out_file.write(row + '\n')
                            else:
                                out_file.write(row)
                else:    
                    with open(filename, 'w') as out_file:
                        for i in range(self.trigger_count):
                            row = ''
                            string = data[i]
                            for j in range(element_number):
                                row += data[i][((i * element_number) + j)]
                                if j != (element_number - 1):
                                    row += ','
                            split_data.append(row)
                            if i != self.trigger_count:
                                out_file.write(row + '\n')
                            else:
                                out_file.write(row)
                if print_datas:
                    print(data)
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            
    def arm_configuration(self, count = 1):
        """
        This function is used to setup the instrument arm_layer, i.e. telling the instrument how many times the source must get a certain value.
        
        Parameters:
            - count = number of times the source must be armed.
        """
        try:
            if 'KEITHLEY' in self.identity and '6517A' in self.identity:
                self.arm_count = count
                buffer = ':ARM:SOUR IMM;:ARM:COUN {!s};'.format(count)
                self.instrument.write(buffer)
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            
    def charge_sense_configuration(self, auto_NPLC = 'Off', manual_NPLC = 10, reference = False, auto_digits = 'Off', manual_digits = 7, average_state = False, average_type = 'None', average_control = 'Repeated', average_count = 10, average_noise_tolerance = 1, median_state = False, median_rank = 1, auto_range = 'On', manual_range = 2e-9, auto_discharge = False):
        """
        This function is used to configure the charge measurement done by the instrument.
        
        Parameters:
            - auto_NPLC = if true, integration time of electrometer (specified in terms of a float number of Pulse Line Cycle's) is set automatically
                by the instrument itself given that an appropriate service calibration is stored in the instrument's EEPROM's.
            - manual_NPLC = if not in auto_NPLC mode, this parameter is used to set manual aperture (i.e. integration time). The value must be given
                as a float value between 0.01 and 10 Pulse Line cycles.
            - reference = if set, the instrument calculates the measurements subtracting from the conversion with the set source level another measurement
                taken at a reference source value (usually 0 V).
            - auto_digits = if ON, measurement resolution (i.e. lecture digit number) is set automatically by the instrument based on the integration
                time set.
            - manual_digits = if auto_digits is OFF, this parameter is used to set the measurement resolution (integer number of digits between 4 and 7).
            - average_state = if ON, the instrument measurement is given by an averaging of multiple ADC conversions.
            - average_type = selects the averaging mode between 'none' (no averaging), scalar (multiple measurements averaging without filtering) or
                'advanced' (multiple measurement averaging with noise filtering).
            - average_control = select if averaging must be of the 'moving' or 'repeat' type.
            - average_count = integer number of ADC conversion that are used to averaging.
            - average_noise_tolerance = if average filtering in advanced mode is active, this parameter will be used to set conversion's noise tolerance
                (i.e. the max value of noise accepted for a conversion to be used in the measurement average).
            - median_state = if ON, median filtering is active.
            - median_rank = rank of the median filter (integer number).
            - auto_range = if true allows the instrument to automatically set his range to the range that gives best measurement accuracy.
            - manual_range = if auto_range is off, set here the manual measurement range.
            - auto_discharge = if true, instrument resets charge reading to zero when it reaches a predefined level.
        """
        try:
            if 'KEITHLEY' in self.identity and '6517A' in self.identity:
                buffer = ":SYST:ZCH ON;:FUNC 'CHAR';"
                buffer += self._sense_general_configuration_(':CHAR', auto_NPLC, manual_NPLC, reference, auto_digits, manual_digits, average_state, average_type, average_control, average_count, average_noise_tolerance, median_state, median_rank)
                mode_types = dict(self.type_dictionary(('On', 'Once', 'Off'),('ON', 'ONCE', 'OFF')))
                buffer += ':CHAR:RANG:AUTO {!s};'.format(mode_types[auto_range])
                if auto_range == 'off' or auto_range == 'off'.title() or auto_range == 'off'.upper():
                    buffer += ':CHAR:RANG:UPP {!s};'.format(manual_range)
                if auto_discharge:
                    buffer += ':CHAR:ADIS ON;'
                else:
                    buffer += ':CHAR:ADIS OFF;'
                buffer += ':SYST:ZCH OFF;'                
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError, Errors.InvalidTypeDictionaryKeyError) as error:
            error.error_handler()

    def current_sense_configuration(self, auto_NPLC = 'Off', manual_NPLC = 10, reference = False, auto_digits = 'Off', manual_digits = 7, average_state = False, average_type = 'None', average_control = 'Repeated', average_count = 10, average_noise_tolerance = 1, median_state = False, median_rank = 1, auto_range = 'On', manual_range = 2e-2, damping = False):
        """
        This function is used to configure the current measurement done by the instrument.
        
        Parameters:
            - auto_NPLC = if true, integration time of electrometer (specified in terms of a float number of Pulse Line Cycle's) is set automatically
                by the instrument itself given that an appropriate service calibration is stored in the instrument's EEPROM's.
            - manual_NPLC = if not in auto_NPLC mode, this parameter is used to set manual aperture (i.e. integration time). The value must be given
                as a float value between 0.01 and 10 Pulse Line cycles.
            - reference = if set, the instrument calculates the measurements subtracting from the conversion with the set source level another measurement
                taken at a reference source value (usually 0 V).
            - auto_digits = if ON, measurement resolution (i.e. lecture digit number) is set automatically by the instrument based on the integration
                time set.
            - manual_digits = if auto_digits is OFF, this parameter is used to set the measurement resolution (integer number of digits between 4 and 7).
            - average_state = if ON, the instrument measurement is given by an averaging of multiple ADC conversions.
            - average_type = selects the averaging mode between 'none' (no averaging), scalar (multiple measurements averaging without filtering) or
                'advanced' (multiple measurement averaging with noise filtering).
            - average_control = select if averaging must be of the 'moving' or 'repeat' type.
            - average_count = integer number of ADC conversion that are used to averaging.
            - average_noise_tolerance = if average filtering in advanced mode is active, this parameter will be used to set conversion's noise tolerance
                (i.e. the max value of noise accepted for a conversion to be used in the measurement average).
            - median_state = if ON, median filtering is active.
            - median_rank = rank of the median filter (integer number).
            - auto_range = if true allows the instrument to automatically set his range to the range that gives best measurement accuracy.
            - manual_range = if auto_range is off, set here the manual measurement range.
            - damping = when true enables damping for the 2 lowest current ranges (200 and 20 pA). Damping is used to reduce current noise given by the
                high input capacitance.
        """
        try:
            if 'KEITHLEY' in self.identity and '6517A' in self.identity:
                buffer = ":SYST:ZCH ON;:FUNC 'CURR:DC';"
                buffer += self._sense_general_configuration_(':CURR', auto_NPLC, manual_NPLC, reference, auto_digits, manual_digits, average_state, average_type, average_control, average_count, average_noise_tolerance, median_state, median_rank)
                mode_types = dict(self.type_dictionary(('On', 'Once', 'Off'),('ON', 'ONCE', 'OFF')))
                buffer += ':CURR:RANG:AUTO {!s};'.format(mode_types[auto_range])
                if auto_range == 'off' or auto_range == 'off'.title() or auto_range == 'off'.upper():
                    buffer += ':CURR:RANG:UPP {!s};'.format(manual_range)
                if damping:
                    buffer += ':CURR:DAMP ON;'
                else:
                    buffer += ':CURR:DAMP OFF;'
                buffer += ':SYST:ZCH OFF;'                 
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError, Errors.InvalidTypeDictionaryKeyError) as error:
            error.error_handler()
            raise
        
    def display_configuration(self, enable_display = True, enable_status_display = False):
        """
        This function is used to configure the instrument display.
        
        Parameters:
            - enable_display = enables display reading (if true) or disables it.
            - enable_status_display = enables the instrument status display (that display messages related to the current operating state of the intrument).
        """
        try:
            if 'KEITHLEY' in self.identity and '6517A' in self.identity:
                if enable_display:
                    buffer = ':DISP:ENAB ON;'
                    if enable_status_display:
                        buffer += ':DISP:SMES ON;'
                    else:
                        buffer += ':DISP:SMES OFF;'
                else:
                    buffer =':DISP:ENAB OFF;'
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            
    def format_configuration(self, data_format = 'Ascii', normal_order = False, data_elements = 'READ,CHAN,RNUM,UNIT,TST,STAT'):
        """
        This function is used to set input-output formats for the instrument's register and output strings, in addition to the items of output
            and calculations list.
        
        Parameters:
            - data_format = string defining the data read/write format. 'Ascii' stands for decimal format, 'sreal' and 'real32' for 32-bit real data format
                and 'dreal' and 'real64' is for standard double-precision real format.
            - normal_order = when set to true restores normal byte ordering in the output strings (instrument predefined is 'swapped' ordering).
            - data_elements = allows the user to specify of which elements the measurement output string must be composed (READ stands for reading, CHAN for
                channel, RNUM for reading number, UNIT is measurement unit, TST is the timestamp and STAT is instrument status).
        """
        try:
            if 'KEITHLEY' in self.identity and '6517A' in self.identity:
                element_types = dict(self.type_dictionary(('ascii', 'real32', 'real64', 'sreal','dreal'),('ASC','REAL,32', 'REAL,64', 'SRE', 'DRE')))
                buffer = ':FORM {!s};'.format(element_types[data_format])
                if normal_order:
                    buffer += ':FORM:BORD NORM;'
                else:
                    buffer += ':FORM:BORD SWAP;'
                buffer += ':FORM:ELEM {!s};'.format(data_elements.upper())
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError, Errors.InvalidTypeDictionaryKeyError) as error:
            error.error_handler()

    def resistance_sense_configuration(self, auto_NPLC = 'Off', manual_NPLC = 10, reference = False, auto_digits = 'Off', manual_digits = 7, average_state = False, average_type = 'None', average_control = 'Repeated', average_count = 10, average_noise_tolerance = 1, median_state = False, median_rank = 1, auto_source = False, auto_range = 'On', auto_source_resistance_range = 2e+6, manual_source_current_range = 2e-5, current_reference = False, damping = False):
        """
        This function is used to configure the resistance measurement done by the instrument.
        
        Parameters:
            - auto_NPLC = if true, integration time of electrometer (specified in terms of a float number of Pulse Line Cycle's) is set automatically
                by the instrument itself given that an appropriate service calibration is stored in the instrument's EEPROM's.
            - manual_NPLC = if not in auto_NPLC mode, this parameter is used to set manual aperture (i.e. integration time). The value must be given
                as a float value between 0.01 and 10 Pulse Line cycles.
            - reference = if set, the instrument calculates the measurements subtracting from the conversion with the set source level another measurement
                taken at a reference source value (usually 0 V).
            - auto_digits = if ON, measurement resolution (i.e. lecture digit number) is set automatically by the instrument based on the integration
                time set.
            - manual_digits = if auto_digits is OFF, this parameter is used to set the measurement resolution (integer number of digits between 4 and 7).
            - average_state = if ON, the instrument measurement is given by an averaging of multiple ADC conversions.
            - average_type = selects the averaging mode between 'none' (no averaging), scalar (multiple measurements averaging without filtering) or
                'advanced' (multiple measurement averaging with noise filtering).
            - average_control = select if averaging must be of the 'moving' or 'repeat' type.
            - average_count = integer number of ADC conversion that are used to averaging.
            - average_noise_tolerance = if average filtering in advanced mode is active, this parameter will be used to set conversion's noise tolerance
                (i.e. the max value of noise accepted for a conversion to be used in the measurement average).
            - median_state = if ON, median filtering is active.
            - median_rank = rank of the median filter (integer number).
            - auto_source = if this mode is on, the source will automatically be set by the instrument given the measured resistance, in order to achieve a
                reasonable current level to be accurate measured.
            - auto_range = if 'on' allows the instrument to automatically set his range to the range that gives best measurement accuracy.
            - auto_source_resistance_range = float giving the instrument an hint on the resistance that the instrument should e able to measure, in order to
                select the auto_source value in between 40 and 400 V.
            - manual_source_current_range = float setting the instrument current range when manual source mode is selected.
            - damping = when true enables damping for the 2 lowest current ranges (200 and 20 pA). Damping is used to reduce current noise given by the
                high input capacitance.
        """
        try:
            if 'KEITHLEY' in self.identity and '6517A' in self.identity:
                buffer = ":SYST:ZCH ON;:FUNC 'RES';"
                buffer += self._sense_general_configuration_(':RES', auto_NPLC, manual_NPLC, reference, auto_digits, manual_digits, average_state, average_type, average_control, average_count, average_noise_tolerance, median_state, median_rank)
                buffer += ':RES:MSEL NORMAL;'
                mode_types = dict(self.type_dictionary(('On', 'Once', 'Off'),('ON', 'ONCE', 'OFF')))
                if auto_source:
                    buffer += ':RES:VSC AUTO;:RES:RANG:AUTO {!s};'.format(mode_types[auto_range])
                    if auto_range == 'off' or auto_range == 'off'.title() or auto_range == 'off'.upper():
                        buffer += ':RES:RANG {!s};'.format(auto_source_resistance_range)
                else:
                    buffer += ':RES:VSC MAN;:RES:MAN:CRAN:AUTO {!s};'.format(mode_types[auto_range])
                    if auto_range == 'off' or auto_range == 'off'.title() or auto_range == 'off'.upper():
                        buffer += ':RES:MAN:CRAN:UPP {!s};'.format(manual_source_current_range)
                if current_reference:
                    buffer += ':RES:IREF ON;'
                else:
                    buffer += ':RES:IREF OFF;'
                if damping:
                    buffer += ':RES:DAMP ON;'
                else:
                    buffer += ':RES:DAMP OFF;'
                buffer += ':SYST:ZCH OFF;'               
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError, Errors.InvalidTypeDictionaryKeyError) as error:
            error.error_handler()
            
    def system_configuration(self, relative_time_stamp = True, relative_time_stamp_reset = True, reading_number_reset = True, ADlimit = True, temperature_reading = False, humidity_reading = False):
        """
        This function is used to setup the system configuration, first af all loading system defaults values from internal EEPROM's and then configuring the
            instrument to the user's needs.
        
        Parameters:
            - relative_time_stamp = if true sets the instrument's timestamp to be a relative timestamp instead of real-time timestamp.
            - relative_time_stamp_reset = if in relative timestamp mode and if set to true, resets the instrument timestamp of measurements.
            - reading_number_reset = if true resets the reading number channel RNUM
            - ADlimit = if set to true, enables A/D hardware limit error message printing, that gives users the positive indication that measurements could
                be erroneous due to a noise current spyde in the A/D hardware.
            - temperature_reading = if the ambiental temperature monitoring is available, enables the temperature reading.
            - humidity_reading = if the ambiental humidity monitoring is available, enables the humidity reading. 
        """
        try:
            if 'KEITHLEY' in self.identity and '6517A' in self.identity:
                buffer = ':SYST:PRES;'
                if relative_time_stamp:
                    buffer += ':SYST:TST:TYPE REL;'
                    if relative_time_stamp_reset:
                        buffer += ':SYST:TST:REL:RES;'
                else:
                    buffer += ':SYST:TST:TYPE RTC;'
                if reading_number_reset:
                    buffer += ':SYST:RNUM:RES;'
                if ADlimit:
                    buffer += ':SYST:HLC ON;'
                else:
                    buffer += ':SYST:HLC OFF;'
                if temperature_reading:
                    buffer += ':SYST:TSC ON;'
                else:
                    buffer += ':SYST:TSC OFF;'
                if humidity_reading:
                    buffer += ':SYST:HSC ON;'
                else:
                    buffer += ':SYST:HSC OFF;'
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
        
    def trigger_configuration(self, count = 1, delay = 0):
        """
        This function is used to configure the trigger layer of the instrument, in order to be able to execute measurements.
        
        Parameters:
            - count = integer indicating how many times measurement must be triggered.
            - delay = number of second to wait between trigger event detection and execution of the first measurement conversion.
        """
        try:
            if 'KEITHLEY' in self.identity and '6517A' in self.identity:
                self.trigger_count = count
                buffer = ':TRIG:SOUR IMM;:TRIG:COUN {!s};'.format(count)
                if delay != 0:
                    buffer += ':TRIG:DEL {!s};'.format(delay)
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def voltage_sense_configuration(self, auto_NPLC = 'Off', manual_NPLC = 10, reference = False, auto_digits = 'Off', manual_digits = 7, average_state = False, average_type = 'None', average_control = 'Repeated', average_count = 10, average_noise_tolerance = 1, median_state = False, median_rank = 1, auto_range = 'On', manual_range = 200, guard = False, external_feedback = False):
        """
        This function is used to configure the voltage measurement done by the instrument.
        
        Parameters:
            - auto_NPLC = if true, integration time of electrometer (specified in terms of a float number of Pulse Line Cycle's) is set automatically
                    by the instrument itself given that an appropriate service calibration is stored in the instrument's EEPROM's.
            - manual_NPLC = if not in auto_NPLC mode, this parameter is used to set manual aperture (i.e. integration time). The value must be given
                as a float value between 0.01 and 10 Pulse Line cycles.
            - reference = if set, the instrument calculates the measurements subtracting from the conversion with the set source level another measurement
                taken at a reference source value (usually 0 V).
            - auto_digits = if ON, measurement resolution (i.e. lecture digit number) is set automatically by the instrument based on the integration
                time set.
            - manual_digits = if auto_digits is OFF, this parameter is used to set the measurement resolution (integer number of digits between 4 and 7).
            - average_state = if ON, the instrument measurement is given by an averaging of multiple ADC conversions.
            - average_type = selects the averaging mode between 'none' (no averaging), scalar (multiple measurements averaging without filtering) or
                'advanced' (multiple measurement averaging with noise filtering).
            - average_control = select if averaging must be of the 'moving' or 'repeat' type.
            - average_count = integer number of ADC conversion that are used to averaging.
            - average_noise_tolerance = if average filtering in advanced mode is active, this parameter will be used to set conversion's noise tolerance
                (i.e. the max value of noise accepted for a conversion to be used in the measurement average).
            - median_state = if ON, median filtering is active.
            - median_rank = rank of the median filter (integer number).
            - auto_range = if 'on' allows the instrument to automatically set his range to the range that gives best measurement accuracy.
            - manual_range = float setting the instrument current range when manual source mode is selected.
            - guard = if true enables guarded voltage measurements. For more information on guarded measurements search the Keithley 6517A User's Manual.
            - external_feedback = if true enables the instrument to accept an external feedback. For more information on guarded measurements search the
                Keithley 6517A User's Manual.
        """
        try:
            if 'KEITHLEY' in self.identity and '6517A' in self.identity:
                buffer = ":SYST:ZCH ON;:FUNC 'VOLT:DC';"
                buffer += self._sense_general_configuration_(':VOLT', auto_NPLC, manual_NPLC, reference, auto_digits, manual_digits, average_state, average_type, average_control, average_count, average_noise_tolerance, median_state, median_rank)
                mode_types = dict(self.type_dictionary(('On', 'Once', 'Off'),('ON', 'ONCE', 'OFF')))
                buffer += ':VOLT:RANG:AUTO {!s};'.format(mode_types[auto_range])
                if auto_range == 'off' or auto_range == 'off'.title() or auto_range == 'off'.upper():
                    buffer += ':VOLT:RANG:UPP {!s};'.format(manual_range)
                if guard:
                    buffer += ':VOLT:GUARD ON;'
                else:
                    buffer += ':VOLT:GUARD OFF;'
                if external_feedback:
                    buffer += ':VOLT:XFE ON;'
                else:
                    buffer += ':VOLT:XFE OFF;'
                buffer += ':SYST:ZCH OFF;' 
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError, Errors.InvalidTypeDictionaryKeyError) as error:
            error.error_handler()

    def voltage_source_configuration(self, voltage = 20, auto_range = True, voltage_range = 20, enable_V_limit = False, auto_V_limit = True, voltage_limit = 1000, meter_connect = False, enable_I_limit = False, current_limit = 0):
        """
        This function is used to configure the instrument's internal voltage source in all the aspects.
        
        Parameters:
            - voltage = float number giving the user set voltage source level.
            - auto_range = if true enables source auto range determination by the instrument.
            - voltage_range = if auto_range is disabled, the float value of this parameter determines voltage source manual range.
            - enable_V_limit = if true, enables hardware voltage limit for the given instrument.
            - auto_V_limit = if true, leave to the instrument the work of setting hardware voltage limits.
            - voltage_limit = if enable_V_limit is true and auto_V_limit is false, this parameter specifies the manual set hardware voltage limit for the
                given instrument.
            - meter_connect = if true, links (with a relais internal to the instrument) source-LO and meter-LO contacts on the chassis, in order to close
                the measurement circuit for current, resistance and charge measurements.
            - enable_I_limit = if true, sets an hardware limit to the current that the source is capable to source out to the load.
            - current_limit = float manually setting the current source hardware limit, i.e. the maximum current source is capable to source out to loads.
        """
        try:
            if 'KEITHLEY' in self.identity and '6517A' in self.identity:
                if abs(voltage) <= 1000:
                    buffer = ':SOUR:VOLT {!s};'.format(voltage)
                    if auto_range:
                        voltage_range = voltage
                        buffer += ':SOUR:VOLT:RANG {!s};'.format(voltage_range)
                    if enable_V_limit:
                        buffer += ':SOUR:VOLT:LIM:STAT ON;'
                        if auto_V_limit:
                            voltage_limit = voltage
                            buffer += ':SOUR:VOLT:LIM {!s};'.format(voltage_limit)
                        else:
                            buffer += ':SOUR:VOLT:LIM:STAT OFF;'
                    if meter_connect:
                        buffer += ':SOUR:VOLT:MCON ON;'
                    else:
                        buffer += ':SOUR:VOLT:MCON OFF;'
                    if enable_I_limit:
                        buffer += ':SOUR:CURR:RLIMIT:STAT ON;:SOUR:CURR:LIM {!s};'.format(current_limit)
                    else:
                        buffer += ':SOUR:CURR:RLIMIT:STAT OFF;'
                    self.instrument.write(buffer)
                    self._operation_complete_query_()
                    self._error_query_()
                else:
                    raise Errors.Keithley6517AIncorrectSourceValueError
            else:
                raise Errors.IncorrectInstrumentError 
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError, Errors.Keithley6517AIncorrectSourceValueError) as error:
            error.error_handler()
            raise