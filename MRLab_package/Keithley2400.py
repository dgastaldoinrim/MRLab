import sys
import Instruments
import Errors

class Keithley2400(Instruments.Instruments):
    """
    This class is a wrapper that contains all the necessary functions to setup an electrical measurement with a Keithley model 2400 SourceMeterUnit.
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
        self.options = None
        if reset:
            self._system_reset_()
    
    def _error_query_(self):
        """
        This function is used in order to query if an error occurred during the execution of the last series of commands on the adressed instrument.
        """
        try:
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
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
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                self.instrument.write(':OUTP:STAT OFF;')
                self.output_status = self.instrument.query(':OUTP:STAT?')
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
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                self.instrument.write(':OUTP:STAT ON;')
                self.output_status = self.instrument.query(':OUTP:STAT?')
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            self._output_off_()
            error.error_handler()
            raise

    def _source_general_configuration_(self, auto_clear, autoclear_mode, auto_settle, settling_delay):
        """
        This function is used to setup a general configuration for a fixed source, applicable to both voltage and current sourcing. It inherits its
            parameters by the voltage_source_fixed_configuration and current_source_fixed_configuration methods described later in this file, for
            explanations of the parameters, please refer to those functions.
        """
        try:
            if auto_clear:
                autoclear_types =dict(self.type_dictionary(('always','on trigger'),('ALW','TCO')))
                buffer = ':SOUR:CLE:AUTO ON;:SOUR:CLE:AUTO:mode {!s};'.format(autoclear_types[autoclear_mode])
            else:
                buffer = ':SOUR:CLE:AUTO OFF;'
            if auto_settle:
                buffer += ':SOUR:DEL:AUTO ON;'
            else:
                buffer += ':SOUR:DEL:AUTO OFF;:SOUR:DEL {!s};'.format(settling_delay)
            return buffer
        except Errors.InvalidTypeDictionaryKeyError as error:
            return None
            error.error_handler()
            raise
    
    def _sweep_configuration_(self, spacing, points, direction, sweep_range_mode, abort_on_compliance):
        """
        This function is used to setup a general configuration for a source sweep, applicable to both voltage and current source sweeps. It inherits its
            parameters by the voltage_source_sweep_configuration and current_source_sweep_configuration methods described later in this file, for
            explanations of the parameters, please refer to those functions.
        """
        try:
            self.sweep_steps = points
            spacing_types = dict(self.type_dictionary(('linear','logarithmic'),('LIN','LOG')))
            directions = dict(self.type_dictionary(('up','down'),('UP','DOWN')))
            range_modes = dict(self.type_dictionary(('best','auto','fixed'),('BEST','AUTO','FIX')))
            abort_modes = dict(self.type_dictionary(('never','early','late'),('NEV','EARL','LATE')))
            buffer = ':SOUR:SWE:SPAC {!s};:SOUR:SWE:POIN {!s};:SOUR:SWE:DIR {!s};:SOUR:SWE:RANG {!s};:SOUR:SWE:CAB {!s};'.format(spacing_types[spacing], points, directions[direction], range_modes[sweep_range_mode], abort_modes[abort_on_compliance])
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
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                self._self_test_query_()
                self._reset_command_()
                self._clear_status_()
                self._event_enable_(enable_number = 255)
                self._event_enable_query_()
                self._event_status_register_query_()
                self.options = self._options_query_()
                self._service_request_enable_command_(enable_number = 189)
                self._service_request_enable_query_()
                if secure_output:
                    self._output_off_()
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            raise

    def acquire_measurements(self, folder, sample, mode, extension = '.txt', T = '', H = '', print_datas = True):
        """
        This function is used to acquire 1 or more measurements with a fixed source value and then save it to a given file in the given directory.
        
        Parameters:
            - folder = string giving the complete path to the folder in which user wants the script to save datas.
            - sample = string giving the sample name.
            - mode  = string specifing the measurement mode  (R vs T, MR, etc.).
            - T = string specifing the (absolute) temperature at which measurement is taken (if not explicitly defined is an empty string).
            - H = string specifing the (magnetizing) field H at which measurement is taken (if not explicitly defined is an empty string).
            - extension = extension to the data file (.txt if not explicitly defined).
            - print_datas = boolean value that specifies if the script must print datas on screen after taking them (if true) or not.
        """
        try:
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                self._output_on_()
                data = []
                string = self.instrument.query(':READ?')[:-1]
                self._operation_complete_query_()
                self._error_query_()
                self._output_off_()
                string_split = string.split(',')
                filename = folder + sample + '_' + mode  + '_T = {!s} K_H = {!s} Oe'.format(T,H) + '_fixed source_'
                if '0' in self.instrument.query(':SYST:RSEN?'):
                    filename += '_2 wires'
                else:
                    filename += '_4 wires'
                filename += extension
                element_number = len(self.instrument.query(':FORM:ELEM?').split(','))
                with open(filename, 'w') as out_file:
                    for i in range(self.trigger_count):
                        row = ''
                        for j in range(element_number):
                            row += string_split[((i * element_number) + j)]
                            if j != (element_number - 1):
                                row += ','
                        data.append(row)
                        if i != self.trigger_count:
                            out_file.write(row + '\n')
                        else:
                            out_file.write(row)
                if print_datas:
                    print(data)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
    
    def acquire_sweeps(self, folder, sample, mode, T = '', H = '', extension = '.txt', print_datas = True):
        """
        This function is used to acquire 1 or more measurements making a sweep of the internal source of the instrument (configured with the correspondent
            public methods) and then save it to a given file in the given directory.
        
        Parameters:
            - folder = string giving the complete path to the folder in which user wants the script to save datas.
            - sample = string giving the sample name.
            - mode  = string specifing the measurement mode  (R vs T, MR, etc.).
            - T = string specifing the (absolute) temperature at which measurement is taken (if not explicitly defined is an empty string).
            - H = string specifing the (magnetizing) field H at which measurement is taken (if not explicitly defined is an empty string).
            - extension = extension to the data file (.txt if not explicitly defined).
            - print_datas = boolean value that specifies if the script must print datas on screen after taking them (if true) or not.
        """
        try:
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                for i in range(self.arm_count):
                    self._output_on_()
                    data = []
                    string = self.instrument.query(':READ?')[:-1]
                    self._operation_complete_query_()
                    self._error_query_()
                    self._output_off_()
                    string_split = string.split(',')
                    filename = folder + sample + '_' + mode  + '_T = {!s} K_H = {!s} Oe'.format(T,H)
                    if 'LIN' in self.instrument.query(':SOUR:SWE:SPAC?'):
                        filename += '_linear sweep number {!s}'.format((i + 1))
                    else:
                        filename += '_logarithmic sweep number {!s}'.format((i + 1))
                    if '0' in self.instrument.query(':SYST:RSEN?'):
                        filename += '_2 wires'
                    else:
                        filename += '_4 wires'
                    filename += extension
                    element_number = len(self.instrument.query(':FORM:ELEM?').split(','))
                    with open(filename, 'w') as out_file:
                        for j in range(self.trigger_count):
                            row = ''
                            for k in range(element_number):
                                row += string_split[((j * element_number) + k)]
                                if k != (element_number - 1):
                                    row += ','
                            data.append(row)
                            if j != self.trigger_count:
                                out_file.write(row + '\n')
                            else:
                                out_file.write(row)
                    if print_datas:
                        print(data)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def arm_configuration(self, count = 1):
        """
        This function is used to setup the instrument arm_layer, i.e. telling the instrument how many times the source must get a certain value or perform a
            certain sweep.
        
        Parameters:
            - count = number of times the source must be armed.
        """
        try:
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                if count >= 1:
                    if count <= 2500:
                        self.arm_count = count
                        buffer = ':ARM:COUN {!s};:ARM:SOUR IMM;'.format(count)
                        self.instrument.write(buffer)
                        self._operation_complete_query_()
                        self._error_query_()
                    else:
                        raise Errors.Keithley2400TooManyArms
                else:
                    raise Errors.Keithley2400NegativeArmCountError
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError, Errors.Keithley2400TooManyArms, Errors.Keithley2400NegativeArmCountError) as error:
            error.error_handler()
            
    def current_sense_configuration(self, auto_range = True, manual_range = 1e-4, NPLCs = 10):
        """
        This function is used to configure the current measurement.
        
        Parameters:
            - auto_range = boolean parameter that enables (true) or disables auto current ranging (i.e. the instrument is able or not to auto-determine the
                most accurate measurement range).
            - manual_range = if auto ranging is disabled,the user can specify the desired manual range here.
            - NPLCs = measurement integration time (in units of pulse line cycles or PLCs).
        """
        try:
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                buffer = ':SENS:FUNC:CONC ON;:SENS:FUNC:ALL;'
                if auto_range:
                    buffer += ':SENS:CURR:RANG:AUTO ON;'
                else:
                    buffer += ':SENS:CURR:RANG:AUTO OFF;:SENS:CURR:RANG {!s};'.format(manual_range)
                    buffer += ':SENS:CURR:NPLC {!s};'.format(NPLCs)
                    self.instrument.write(buffer)
                    self._operation_complete_query_()
                    self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            
    def current_source_fixed_configuration(self, auto_clear = False, autoclear_mode = 'Always', auto_settle = True, settling_delay = 0, auto_range = True, manual_range = 1e-2, source_level = 1e-3, set_level_mode = 'Immediate', triggered_scaling = False, scaling_factor = 1, compliance_value = 20):
        """
        This function is used to setup the source in order to deliver to the load a fixed value of current.
        
        Parameters:
            - auto_clear = boolean parameter used in order to enable (when true) or disable auto clear mode of the instrument digital I/O.
            - auto_clear_mode = string that defines if digital I/O auto clear must be done at every new source value ('on trigger') or at every mode  
                measurement conversion ('always').
            - auto_settle = boolean parameter used to enable (true) or disable the auto settling time selection. If true, instrument will select source
                settling time based on the source range used.
            - settling_delay = floating number given the desired manual settling time, in seconds.
            - auto_range = boolean parameter that, if true, makes the instrument setting source range automatically according to the set source value.
            - manual_range = if not in source auto ranging mode , this parameter allows the user to manually set source range as a floating number.
            - source_level = float indicating the manually set source level.
            - set_level_mode = sets if the change in source has to be immediate ('immediate') or has to be done after receiving a trigger signal ('on
                trigger').
            - triggered_scaling = if on trigger source set mode is selected, it allows user to define if a scaling factor (between desired and actually
                applied source level) must be applied.
            - scaling_factor =  if on trigger source set mode is selected, it allows user to define if a scaling factor between the desired source level and
                the value actually sourced.
            - compliance_value = the maximum voltage value the source could achieve while attempting to source the desired current.
        """
        try:
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                buffer = self._source_general_configuration_(auto_clear, autoclear_mode, auto_settle, settling_delay)
                buffer += ':SOUR:FUNC CURR;:SOUR:CURR:MODE FIX;'
                if auto_range:
                    buffer += ':SOUR:CURR:RANG:AUTO ON;'
                else:
                    buffer += ':SOUR:CURR:RANG:AUTO OFF;:SOUR:CURR:RANG {!s}'.format(manual_range)
                if set_level_mode == 'immediate' or set_level_mode == 'immediate'.title() or set_level_mode == 'immediate'.upper():
                    buffer += ':SOUR:CURR {!s};'.format(source_level)
                elif set_level_mode == 'triggered' or set_level_mode == 'triggered'.title() or set_level_mode == 'triggered'.upper():
                    buffer += ':SOUR:CURR:TRIG {!s};'.format(source_level)
                    if triggered_scaling:
                        buffer += ':SOUR:CURR:TRIG:SFAC ON;:SOUR:CURR:TRIG:SFAC {!s}'.format(scaling_factor)
                    else:
                        buffer += ':SOUR:CURR:TRIG:SFAC OFF;'
                buffer += ':SENS:VOLT:PROT {!s};'.format(compliance_value)
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError, Errors.InvalidTypeDictionaryKeyError) as error:
            error.error_handler()
            
    def current_source_sweep_configuration(self, autoclear = False, autoclear_mode = 'Always', auto_settle = True, settling_delay = 0, start_level = -1, stop_level = +1, spacing = 'Linear', points = 2500, direction = 'Up', sweep_range_mode = 'Best', abort_on_compliance = 'Never', compliance_value = 1e-4):
        """
        This function is used to setup the current source in order to deliver to the load a current sweep (linear or logarithmic at user choice) between 2
            levels defined by users.
        
        Parameters:
            - auto_clear = boolean parameter used in order to enable (when true) or disable auto clear mode of the instrument digital I/O.
            - auto_clear_mode = string that defines if digital I/O auto clear must be done at every new source value ('on trigger') or at every mode 
                measurement conversion ('always').
            - auto_settle = boolean parameter used to enable (true) or disable the auto settling time selection. If true, instrument will select source
                settling time based on the source range used.
            - settling_delay = floating number given the desired manual settling time, in seconds.
            - start_level = float indicating the start level of source sweep.
            - stop_level = float indicating the stop level of source sweep.
            - spacing = parameter that enables the user to setup a linear ('linear') or logarithmic based 10 ('logarithmic') spaced sweep.
            - auto_range = boolean parameter that, if true, makes the instrument setting source range automatically according to the set source value.
            - manual_range = if not in source auto ranging mode , this parameter allows the user to manually set source range as a float number.
            - points = the number of points of which the sweep will be composed (maximum 2500).
            - direction = from maximum to minimum in 'down' direction and viceversa in 'up' direction
            - sweep_range_mode = allows the user to select the sweep auto-ranging mode between 'best' mode  (in which the instrument sets automatically the
                best and only range that can accomodate all the sweep measurement), an 'auto' mode  (in which range settings can vary automatically at each
                conversion) and a 'fixed' mode  (range choosen and fixed after the first conversion).
            - abort_on_compliance = allows the user to select if he does not want to stop the sweep even after a compliance is detected ('never' set), wants
                to stop the sweep just as compliance appears ('early') or after a complete sweep in which compliance is detected ('late' set).
            - compliance_value = the maximum voltage value the source could achieve while attempting to source the desired current.
        """
        try:
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                buffer = self._source_general_configuration_(autoclear, autoclear_mode, auto_settle, settling_delay)
                buffer += ':SOUR:FUNC CURR;:SOUR:CURR:mode SWE;:SOUR:CURR:STAR {!s};:SOUR:CURR:STOP {!s};'.format(start_level, stop_level)
                buffer += self._sweep_configuration_(spacing, points, direction, sweep_range_mode, abort_on_compliance)
                buffer += ':SENS:VOLT:PROT {!s};'.format(compliance_value)
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError, Errors.InvalidTypeDictionaryKeyError) as error:
            error.error_handler()
            
    def display_configuration(self, enable_display = True, enable_state_display = False, digits = 7):
        """
        This function is used to configure the instrument display.
        
        Parameters:
            - enable_display = enables display reading (if true) or disables it.
            - enable_state_display = enables the conversion state display (indicating in which of the conversion's phase is currently the instrument in
                between Source, Delay or Measure phases.)
            - digits = sets display resolution between 4 and 7 digits.
        """
        try:
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                if enable_display:
                    buffer = ':DISP:ENAB ON;'
                    if enable_state_display:
                        buffer += ':DISP:CND;'
                    else:
                        buffer += ':DISP:DIG {!s};'.format(digits)
                else:
                    buffer =':DISP:ENAB OFF;'
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            
    def filter_measurements(self, active = False, mode  = 'Repeat', counts = 10):
        """
        This function is used to enable and setup measurement filtering.
        
        Parameter:
            - active = boolean parameter that defines if filtering must be enabled (True) or disabled (False, predefined).
            - mode  = string that defines filtering mode in between moving averaging ('moving') or repeated averaging ('repeated').
            - counts = defines the number of ADC conversions to be filtered before sending datas to the output channel.
        """
        try:
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                if active:
                    buffer = ':SENS:AVER:STAT ON;'
                    filter_types = dict(self.type_dictionary(('moving', 'repeat'), ('MOV', 'REP')))
                    buffer += ':SENS:AVER:TCON {0:G};:SENS:AVER:COUN {1!s}'.format((filter_types[mode ],counts))
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError, Errors.InvalidTypeDictionaryKeyError) as error:
            error.error_handler()
            
    def format_configuration(self, sreg_format = 'Ascii', data_format = 'Ascii', normal_order = False, data_elements = 'VOLT,CURR,RES,TIME', calc_enable = False, calc_elements = 'CALC', source2_enable = False, source2_format = 'Ascii'):
        """
        This function is used to set input-output formats for the instrument's register and output strings, in addition to the items of output
            and calculations list.
        
        Parameters:
            - sreg_format = string defining the status register read/write format. 'Ascii' stands for decimal format, 'hexadecimal', 'octal' and 'binary' are
                self explaining formats.
            - data_format = string defining the data read/write format. 'Ascii' stands for decimal format, 'real' and 'real32' for 32-bit real data format
                and 'sreal' is for standard single-precision real format.
            - normal_order = when set to true restores normal byte ordering in the output strings (instrument predefined is 'swapped' ordering).
            - data_elements = allows the user to specify of which elements the measurement output string must be composed ('VOLT' stands for voltage, 'CUR'
                for current, 'RES' for resistance and 'TIME' for the timestamp).
            - calc_enable = allows the user to define if calc (internal calculation) output must be enabled or not.
            - calc_elements = allows the user to define calc output string elements (predefined is 'CALC', calculation results only).
            - source2_enable = allows the user to enable the source2 status read/write register.
            - source2_format = allows the user to set source2 register format. Available formats are the same of sreg_format parameter.
        """
        try:
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                format_types = dict(self.type_dictionary(('ascii', 'hexadecimal', 'octal', 'binary'), ('ASC', 'HEX', 'OCT', 'BIN')))
                buffer = ':FORM:SREG {!s};'.format(format_types[sreg_format])
                element_types = dict(self.type_dictionary(('ascii', 'real', 'real32', 'sreal'),('ASC','REAL', 'REAL,32', 'SREAL')))
                buffer += ':FORM {!s};'.format(element_types[data_format])
                if normal_order:
                    buffer += ':FORM:BORD NORM;'
                else:
                    buffer += ':FORM:BORD SWAP;'
                buffer += ':FORM:ELEM {!s};'.format(data_elements.upper())
                if calc_enable:
                    buffer += ':FORM:CALC:ELEM {!s}'.format(calc_elements.upper())
                if source2_enable:
                    buffer += ':FORM:SOUR {!s}'.format(format_types[source2_format])
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError, Errors.InvalidTypeDictionaryKeyError) as error:
            error.error_handler()
            
    def output_configuration(self, output_enable = False, output_off_mode = 'Normal'):
        """
        This function is used to set the output off behaviour of the source.
        
        Parameters:
            - output_enable = if true, source can not be turned on until a trigger signal is received on the Output Enable line (pin 8 of trigger link).
            - output_off_mode = allows the user to set the source output off mode between 'normal', 'hi-z', 'zero' and 'guard' modes. For an explanation of
                differences between the various modes, please refer to the Keithley 2400 SourceMeter user's manual.
        """
        try:
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                if output_enable:
                    buffer = ':OUTP:ENAB ON;'
                else:
                    buffer = ':OUTP:ENAB OFF;'
                types = dict(self.type_dictionary(('hi-z', 'normal', 'zero', 'guard'), ('HIMP', 'NORM', 'ZERO', 'GUAR')))
                buffer += ':OUTP:SMODE {!s};'.format(types[output_off_mode])
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError, Errors.InvalidTypeDictionaryKeyError) as error:
            error.error_handler()
            
    def resistance_sense_configuration(self, auto_mode = False, offset_compensation = False, auto_range = True, manual_range = 2e+5, NPLCs = 10):
        """
        This function is used to configure the resistance measurement.
        
        Parameters:
            - auto_mode = boolean parameter that enables (true) or disables auto resistance mode , i.e. the instrument choose the best source value and ranges
                for the given measurement.
            - offset compensation = boolean parameter that enables (true) or disables offset compensation for resistance measurements. This mode allows to
                correct for instrument offset measuring resistances as the differential value of measurements taken at 2 different source levels.
            - auto_range = boolean parameter that enables (true) or disables auto resistance ranging (i.e. if the instrument will be able or not to determine
                automatically the most accurate measurement range).
            - manual_range = if auto ranging is disabled,the user can specify the desired manual range here.
            - NPLCs = measurement integration time (in units of pulse line cycles or PLCs)
        """
        try:
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                buffer = ':SENS:FUNC:CONC ON;:SENS:FUNC:ALL;'
                if auto_mode:
                    buffer += ':SENS:RES:mode AUTO;'
                else:
                    buffer += ':SENS:RES:mode MAN;'
                if offset_compensation:
                    buffer += ':SENS:RES:OCOM ON;'
                else:
                    buffer += ':SENS:RES:OCOM OFF;'
                if auto_range:
                    buffer += ':SENS:RES:RANG:AUTO ON;'
                else:
                    buffer += ':SENS:RES:RANG:AUTO OFF;:SENS:RES:RANG {!s};'.format(manual_range)
                buffer += ':SENS:RES:NPLC {!s};'.format(NPLCs)
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            
    def route_configuration(self, terminals = 'Front'):
        """
        This function allows the user to set the source-meter terminals in between 'front' (predefined) and 'rear' terminals.
        """
        try:
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                types = dict(self.type_dictionary(('front', 'rear'), ('FRON', 'REAR')))
                buffer = ':ROUT:TERM {!s};'.format(types[terminals])
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError, Errors.InvalidTypeDictionaryKeyError) as error:
            error.error_handler()
            
    def system_configuration(self, beep = True, timestamp_reset = True, remote_sense = False):
        """
        This function is used to setup the system configuration, first af all loading system defaults values from internal EEPROM's and then configuring the
            instrument to the user's needs.
        
        Parameters:
            - beep = boolean value that allows the user to choose if the instrument must emit a beep when activating the source (true set) or not.
            - timestamp_reset = if true resets the instrument timestamp of measurements.
            - remote_sense = used to enable (when true) or disable (false, predefined) 4 wires (remote) sensing.
        """
        try:
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                buffer = ':SYST:PRES;'
                if beep:
                    buffer += ':SYST:BEEP:STAT ON;'
                else:
                    buffer += ':SYST:BEEP:STAT OFF;'
                if timestamp_reset:
                    buffer += ':SYST:TIME:RES:AUTO ON;'
                else:
                    buffer += ':SYST:TIME:RES:AUTO OFF;'
                if remote_sense:
                    buffer += ':SYST:RSEN ON;'
                else:
                    buffer += ':SYST:RSEN OFF;'
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
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                if count >= 1:
                    if count <= 2500 // self.arm_count:
                        self.trigger_count = count
                        buffer = ':TRIG:SOUR IMM;:TRIG:COUN %s;' %count
                        if delay != 0:
                            buffer += ':TRIG:DEL %s;' %delay
                        self.instrument.write(buffer)
                        self._operation_complete_query_()
                        self._error_query_()
                    else:
                        raise Errors.Keithley2400TooManyTriggers
                else:
                    raise Errors.Keithley2400NegativeTriggerCountError
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError, Errors.Keithley2400TooManyTriggers, Errors.Keithley2400NegativeTriggerCountError) as error:
            error.error_handler()
            
    def voltage_sense_configuration(self, auto_range = True, manual_range = 21, NPLCs = 10):
        """
        This function is used to configure the voltage measurement.
        
        Parameters:
            - auto_range = boolean parameter that enables (true) or disables auto voltage ranging (i.e. the instrument is able or not to auto-determine the
                most accurate measurement range).
            - manual_range = if auto ranging is disabled,the user can specify the desired manual range here.
            - NPLCs = measurement integration time (in units of pulse line cycles or PLCs)
        """
        try:
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                buffer = ':SENS:FUNC:CONC ON;:SENS:FUNC:ALL;'
                if auto_range:
                    buffer += ':SENS:VOLT:RANG:AUTO ON;'
                else:
                    buffer += ':SENS:VOLT:RANG:AUTO OFF;:SENS:VOLT:RANG {!s};'.format(manual_range)
                buffer += ':SENS:VOLT:NPLC {!s};'.format(NPLCs)
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            
    def voltage_source_fixed_configuration(self, autoclear = False, autoclear_mode = 'Always', auto_settle = True, settling_delay = 0, voltage_protection = 200, auto_range = True, manual_range = 20, source_level = 1, set_level_mode = 'Immediate', triggered_scaling = False, scaling_factor = 1, compliance_value = 1e-4):
        """
        This function is used to setup the source in order to deliver to the load a fixed value of voltage.
        
        Parameters:
            - auto_clear = boolean parameter used in order to enable (when true) or disable auto clear mode of the instrument digital I/O.
            - auto_clear_mode = string that defines if digital I/O auto clear must be done at every new source value ('on trigger') or at every mode 
                measurement conversion ('always').
            - auto_settle = boolean parameter used to enable (true) or disable the auto settling time selection. If true, instrument will select source
                settling time based on the source range used.
            - settling_delay = floating number given the desired manual settling time, in seconds.
            - voltage_protection = let the users set the maximum voltage admissible on the output contacts.
            - auto_range = boolean parameter that, if true, makes the instrument setting source range automatically according to the set source value.
            - manual_range = if not in source auto ranging mode , this parameter allows the user to manually set source range as a floating number.
            - source_level = float indicating the manually set source level.
            - set_level_mode = sets if the change in source has to be immediate ('immediate') or has to be done after receiving a trigger signal 
                ('on trigger').
            - triggered_scaling = if on trigger source set mode is selected, it allows user to define if a scaling factor (between desired and actually
                applied source level) must be applied.
            - scaling_factor =  if on trigger source set mode is selected, it allows user to define if a scaling factor between the desired source level and
                the value actually sourced.
            - compliance_value = the maximum current value the source could achieve while attempting to source the desired voltage.
        """
        try:
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                buffer = self._source_general_configuration_(autoclear, autoclear_mode, auto_settle, settling_delay)
                buffer += ':SOUR:FUNC VOLT;:SOUR:VOLT:mode FIX;:SOUR:VOLT:PROT {!s};'.format(voltage_protection)
                if auto_range:
                    buffer += ':SOUR:VOLT:RANG:AUTO ON;'
                else:
                    buffer += ':SOUR:VOLT:RANG:AUTO OFF;:SOUR:VOLT:RANG {!s}'.format(manual_range)
                if set_level_mode == 'immediate' or set_level_mode == 'immediate'.title() or set_level_mode == 'immediate'.upper():
                    buffer += ':SOUR:VOLT {!s};'.format(source_level)
                elif set_level_mode == 'triggered' or set_level_mode == 'triggered'.title() or set_level_mode == 'triggered'.upper():
                    buffer += ':SOUR:VOLT:TRIG {!s};'.format(source_level)
                    if triggered_scaling:
                        buffer += ':SOUR:VOLT:TRIG:SFAC ON;:SOUR:VOLT:TRIG:SFAC {!s}'.format(scaling_factor)
                    else:
                        buffer += ':SOUR:VOLT:TRIG:SFAC OFF;'
                else:
                    print("You did not choose a correct mode for this instrument's source. Execution aborted.")
                    sys.exit()
                buffer += ':SENS:CURR:PROT {!s};'.format(compliance_value)
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError, Errors.InvalidTypeDictionaryKeyError) as error:
            error.error_handler()
            
    def voltage_source_sweep_configuration(self, autoclear = False, autoclear_mode = 'Always', auto_settle = True, settling_delay = 0, voltage_protection = 200, start_level = -1, stop_level = +1, spacing = 'Linear', points = 2500, direction = 'Up', sweep_range_mode = 'Best', abort_on_compliance = 'Never', compliance_value = 1e-4):
        """
        This function is used to setup the voltage source in order to deliver to the load a voltage sweep (linear or logarithmic at user choice) between 2
            levels defined by users.
        
        Parameters:
            - auto_clear = boolean parameter used in order to enable (when true) or disable auto clear mode of the instrument digital I/O.
            - auto_clear_mode = string that defines if digital I/O auto clear must be done at every new source value ('on trigger') or at every mode 
                measurement conversion ('always').
            - auto_settle = boolean parameter used to enable (true) or disable the auto settling time selection. If true, instrument will select source
                settling time based on the source range used.
            - settling_delay = floating number given the desired manual settling time, in seconds.
            - voltage_protection = let the users set the maximum voltage admissible on the output contacts.
            - start_level = float indicating the start level of source sweep.
            - stop_level = float indicating the stop level of source sweep.
            - spacing = parameter that enables the user to setup a linear ('linear') or logarithmic based 10 ('logarithmic') spaced sweep .
            - auto_range = boolean parameter that, if true, makes the instrument setting source range automatically according to the set source value.
            - manual_range = if not in source auto ranging mode , this parameter allows the user to manually set source range as a floating number.
            - points = the number of points of which the sweep will be composed (maximum 2500).
            - direction = from maximum to minimum in 'down' direction and viceversa in 'up' direction.
            - sweep_range_mode = allows the user to select the sweep auto-ranging mode between 'best' mode  (in which the instrument sets automatically the
                best and only range that can accomodate all the sweep measurement), an 'auto' mode  (in which range settings can vary automatically at each
                conversion) and a 'fixed' mode  (range choosen and fixed after the first conversion).
            - abort_on_compliance = allows the user to select if he does not want to stop the sweep even after a compliance is detected ('never' set),
                wants to stop the sweep just as compliance appears ('early') or after a complete sweep in which compliance is detected ('late' set).
            - compliance_value = the maximum current value the source could achieve while attempting to source the desired voltage.
        """
        try:
            if 'KEITHLEY' in self.identity and '2400' in self.identity:
                buffer = self._source_general_configuration_(autoclear, autoclear_mode, auto_settle, settling_delay)
                buffer += ':SOUR:FUNC VOLT;:SOUR:VOLT:mode SWE;:SOUR:VOLT:PROT {!s};:SOUR:VOLT:STAR {!s};:SOUR:VOLT:STOP {!s};'.format(voltage_protection, start_level, stop_level)
                buffer += self._sweep_configuration_(spacing, points, direction, sweep_range_mode, abort_on_compliance)
                buffer += ':SENS:CURR:PROT {!s};'.format(compliance_value)
                self.instrument.write(buffer)
                self._operation_complete_query_()
                self._error_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError, Errors.InvalidTypeDictionaryKeyError) as error:
            error.error_handler()

##mode scripts (only to be run when the class is running as a standalone)
#import Manager

#if __name__ == '__main__':
#    #temperatures = (280, 290, 300)
#    #fields = (-10, 0, 10)
#    rm = Manager.Manager()
## Here we apply mode functions to the correct instrument.
#    sourcemeter = Keithley2400(rm, 'GPIB0::23::INSTR')
#    print(type(sourcemeter))
#    print(sourcemeter.manager)
#    print(sourcemeter.adress)
#    print(sourcemeter.instrument)
#    print(sourcemeter.identity)
#    sourcemeter.system_configuration(beep = False)
#    sourcemeter.display_configuration()
#    sourcemeter.format_configuration(data_elements = 'RES')
#    sourcemeter.voltage_sense_configuration()
#    sourcemeter.current_sense_configuration()
#    sourcemeter.resistance_sense_configuration()
#    sourcemeter.voltage_source_fixed_configuration(auto_settle = True, source_level = 10, compliance_value = 1e-3)
#    sourcemeter.arm_configuration()
#    sourcemeter.trigger_configuration()
## Test mode 01: single resistance measurement with 2 terminals and fixed voltage source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_measurements('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 01', 'MR', T = temperature, H = field)
#    sourcemeter.trigger_configuration(count = 20)
## Test mode 02: multiple resistance measurement with 2 terminals and fixed voltage source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_measurements('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 02', 'MR', T = temperature, H = field)
#    sourcemeter.current_source_fixed_configuration(auto_settle = True, source_level = 1e-8, compliance_value = 200)
#    sourcemeter.trigger_configuration()
## Test mode 03: single resistance measurement with 2 terminals and fixed current source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_measurements('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 03', 'MR', T = temperature, H = field)
#    sourcemeter.trigger_configuration(count = 20)
## Test mode 04: multiple resistance measurement with 2 terminals and fixed current source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_measurements('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 04', 'MR', T = temperature, H = field)
#    sourcemeter.format_configuration(data_elements = 'VOLT,CURR')
#    sourcemeter.voltage_source_sweep_configuration(auto_settle = True, start_level = -10, stop_level = +10, points = 20, abort_on_compliance = 'Early', compliance_value = 1e-3)
## Test mode 05: single I(V) measurement with 2 terminals and linearly sweeped voltage source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_sweeps('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 05', 'MR', T = temperature, H = field)
#    sourcemeter.arm_configuration(count = 2)
## Test mode 06: multiple I(V) measurements with 2 terminals and linearly sweeped voltage source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_sweeps('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 06', 'MR', T = temperature, H = field)
#    sourcemeter.voltage_source_sweep_configuration(auto_settle = True, start_level = 0.1, stop_level = 10, points = 20, spacing = 'Logarithmic', abort_on_compliance = 'Early', compliance_value = 1e-3)
#    sourcemeter.arm_configuration()
## Test mode 07: single I(V) measurement with 2 terminals and logarithmic sweeped voltage source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_sweeps('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 07', 'MR', T = temperature, H = field)
#    sourcemeter.arm_configuration(count = 2)
## Test mode 08: multiple I(V) measurement with 2 terminals and logarithmic sweeped voltage source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_sweeps('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 08', 'MR', T = temperature, H = field)
#    sourcemeter.current_source_sweep_configuration(auto_settle = True, start_level = -1e-8, stop_level = +1e-8, points = 20, abort_on_compliance = 'early', compliance_value = 200)
## Test mode 09: single I(V) measurement with 2 terminals and linearly sweeped current source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_sweeps('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 09', 'MR', T = temperature, H = field)
#    sourcemeter.arm_configuration(count = 2)
## Test mode 10: multiple I(V) measurements with 2 terminals and linearly sweeped current source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_sweeps('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 10', 'MR', T = temperature, H = field)
#    sourcemeter.current_source_sweep_configuration(auto_settle = True, start_level = 1e-9, stop_level = 1e-7, points = 20, spacing = 'Logarithmic', abort_on_compliance = 'early', compliance_value = 200)
#    sourcemeter.arm_configuration()
## Test mode 11: single I(V) measurement with 2 terminals and logarithmic sweeped current source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_sweeps('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 11', 'MR', T = temperature, H = field)
#    sourcemeter.arm_configuration(count = 2)
## Test mode 12: multiple I(V) measurements with 2 terminals and logarithmic sweeped current source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_sweeps('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 12', 'MR', T = temperature, H = field)
#    sourcemeter.system_configuration(beep = False, remote_sense = True)
#    sourcemeter.format_configuration(data_elements = 'RES')
#    sourcemeter.voltage_source_fixed_configuration(auto_settle = True, source_level = 10, compliance_value = 1e-3)
#    sourcemeter.arm_configuration()
#    sourcemeter.trigger_configuration()
## Test mode 13: single resistance measurement with 2 terminals and fixed voltage source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_measurements('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 13', 'MR', T = temperature, H = field)
#    sourcemeter.trigger_configuration(count = 20)
## Test mode 14: multiple resistance measurement with 2 terminals and fixed voltage source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_measurements('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 14', 'MR', T = temperature, H = field)
#    sourcemeter.current_source_fixed_configuration(auto_settle = True, source_level = 1e-8, compliance_value = 200)
#    sourcemeter.trigger_configuration()
## Test mode 15: single resistance measurement with 2 terminals and fixed current source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_measurements('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 15', 'MR', T = temperature, H = field)
#    sourcemeter.trigger_configuration(count = 20)
## Test mode 16: multiple resistance measurement with 2 terminals and fixed current source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_measurements('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 16', 'MR', T = temperature, H = field)
#    sourcemeter.format_configuration(data_elements = 'VOLT,CURR')
#    sourcemeter.voltage_source_sweep_configuration(auto_settle = True, start_level = -10, stop_level = +10, points = 20, abort_on_compliance = 'Early', compliance_value = 1e-3)
## Test mode 17: single I(V) measurement with 2 terminals and linearly sweeped voltage source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_sweeps('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 17', 'MR', T = temperature, H = field)
#    sourcemeter.arm_configuration(count = 2)
## Test mode 18: multiple I(V) measurements with 2 terminals and linearly sweeped voltage source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_sweeps('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 18', 'MR', T = temperature, H = field)
#    sourcemeter.voltage_source_sweep_configuration(auto_settle = True, start_level = 0.1, stop_level = 10, points = 20, spacing = 'Logarithmic', abort_on_compliance = 'Early', compliance_value = 1e-3)
#    sourcemeter.arm_configuration()
## Test mode 19: single I(V) measurement with 2 terminals and logarithmic sweeped voltage source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_sweeps('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 19', 'MR', T = temperature, H = field)
#    sourcemeter.arm_configuration(count = 2)
## Test mode 20: multiple I(V) measurement with 2 terminals and logarithmic sweeped voltage source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_sweeps('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 20', 'MR', T = temperature, H = field)
#    sourcemeter.current_source_sweep_configuration(auto_settle = True, start_level = -1e-8, stop_level = +1e-8, points = 20, abort_on_compliance = 'early', compliance_value = 200)
## Test mode 21: single I(V) measurement with 2 terminals and linearly sweeped current source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_sweeps('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 21', 'MR', T = temperature, H = field)
#    sourcemeter.arm_configuration(count = 2)
## Test mode 22: multiple I(V) measurements with 2 terminals and linearly sweeped current source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_sweeps('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 22', 'MR', T = temperature, H = field)
#    sourcemeter.current_source_sweep_configuration(auto_settle = True, start_level = 1e-9, stop_level = 1e-7, points = 20, spacing = 'Logarithmic', abort_on_compliance = 'early', compliance_value = 200)
#    sourcemeter.arm_configuration()
## Test mode 23: single I(V) measurement with 2 terminals and logarithmic sweeped current source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_sweeps('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 23', 'MR', T = temperature, H = field)
#    sourcemeter.arm_configuration(count = 2)
## Test mode 24: multiple I(V) measurements with 2 terminals and logarithmic sweeped current source for 3 temperatures and 3 fields.
#    for temperature in temperatures:
#        for field in fields:
#            sourcemeter.acquire_sweeps('C:/Users/Daniele Gastaldo/Google Drive/Dati PhD Daniele/Prove MRLab/Dati esame/2400/', 'Banco resistenze mode 24', 'MR', T = temperature, H = field)
    #sourcemeter.close()
## Here we apply tested functions to another instrument, a Keithley 6517A electrometer.
#    electrometer = Keithley2400(rm, 'GPIB0::27::INSTR')
#    print(type(electrometer))
#    print(electrometer.manager)
#    print(electrometer.adress)
#    print(electrometer.instrument)
#    print(electrometer.identity)
#    print(electrometer._error_query_())
#    electrometer.close()