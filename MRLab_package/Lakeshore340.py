import Instruments
import Errors

class Lakeshore340(Instruments.Instruments):
    """
    This class is a wrapper that contains all the necessary functions to setup temperature measurement with a Lakeshore Model 340 temperature controller.
    """

    def __init__(self, manager, adress, read_terminator = 'CRLF', write_terminator = 'CRLF', end_or_identify = True, reset = True):
        """
        This function is used in order to initialize the link to a Lakeshore Model 340 temperature controller. It inherits from the Instruments class (contained in
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
        self.input_A_alarm_parameters = None
        self.input_B_alarm_parameters = None
        self.input_A_alarm_status = None
        self.input_B_alarm_status = None
        self.input_A_celsius_reading = None
        self.input_B_celsius_reading = None
        self.input_A_filter_parameters = None
        self.input_B_filter_parameters = None
        self.input_A_input_curve = None
        self.input_B_input_curve = None
        self.input_A_hardware_setup_parameters = None
        self.input_B_hardware_setup_parameters = None
        self.input_A_type = None
        self.input_B_type = None
        self.input_A_kelvin_reading = None
        self.input_B_kelvin_reading = None
        self.input_A_linear_data = None
        self.input_B_linear_data = None
        self.input_A_linear_data_status = None
        self.input_B_linear_data_status = None
        self.input_A_linear_equation = None
        self.input_B_linear_equation = None
        self.input_A_maxmin_data = None
        self.input_B_maxmin_data = None
        self.input_A_maxmin_status = None
        self.input_B_maxmin_status = None
        self.input_A_maxmin = None
        self.input_B_maxmin = None
        self.input_A_reading_status = None
        self.input_B_reading_status = None
        self.input_A_sensor_units_reading = None
        self.input_B_sensor_units_reading = None
        self.last_curve_header = None
        self.last_curve_point = None
        self.last_program_line = None
        self.last_program_line_position = None
        self.program_memory_status = None
        self.last_program_status = None
        self.last_logging_status = None
        self.last_logging_count = None
        self.last_logging_point = None
        self.last_logging_parameters = None
        self.last_logging_record = None
        if reset:
            self._system_reset_()
            
    def _system_reset_(self):
        """
        This function is used to reset the instrument to productions defaults, if required during the initialization phase.
        """
        try:
            if 'LSCI' in self.identity and 'MODEL340' in self.identity:
                self._self_test_query_()
                self._reset_command_()
                self._clear_status_()
                self._event_enable_(enable_number = 189)
                self._event_enable_query_()
                self._event_status_register_query_()
                self._service_request_enable_command_(enable_number = 255)
                self._service_request_enable_query_()
                self._operation_complete_query_()
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            raise
            
    """
    Input commands
    """

    def set_input_alarm_parameters(self, input, on = False, source = 1, high_value = 320, low_value = 1.5, latch_enable = False, relay_enable = False):
        try:
            if '340' in self.identity:
                buffer = 'ALARM {0},{1:d}'.format(str(input), on)
                if on:
                    buffer += ',{0:d},{1:E},{2:E},{3:d},{4:d}'.format(source, high_value, low_value, latch_enable, relay_enable)
                self.instrument.write(buffer)
                self.get_input_alarm_parameters_reading(input)
                if not(input == 'A' and self.input_A_alarm_parameters == (on, source, high_value, low_value, latch_enable, relay_enable)) or not(input == 'B' and self.input_B_alarm_parameters == (on, source, high_value, low_value, latch_enable, relay_enable)):
                    raise Errors.LS340NotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_input_alarm_parameters_reading(self, input):
        try:
            if '340' in self.identity:
                string = self.instrument.query('ALARM? {0}'.format(str(input)))
                string_list = string.split(',')
                result = (bool(string_list[0]), int(string_list[1]), float(string_list[2]), float(string_list[3]), bool(string_list[4]), bool(string_list[5]))
                if str(input) == 'A':
                    self.input_A_alarm_parameters = result
                else:
                    self.input_B_alarm_parameters = result
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_input_alarm_status_reading(self, input):
        try:
            if '340' in self.identity:
                string = self.instrument.query('ALARMST? {0}'.format(str(input)))
                string_list = string.split(',')
                result = (bool(string_list[0]), bool(string_list[1]))
                if str(input) == 'A':
                    self.input_A_alarm_status = result
                else:
                    self.input_B_alarm_status = result
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_celsius_reading(self, input):
        try:
            if '340' in self.identity:
                string = self.instrument.query('CRDG? {0}'.format(str(input)))
                if str(input) == 'A':
                    self.input_A_celsius_reading = float(string)
                else:
                    self.input_B_celsius_reading = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def set_input_filter_parameters(self, input, on = False, points = 10, percentual_window = 2):
        try:
            if '340' in self.identity:
                buffer = 'FILTER {0},{1:d}'.format(str(input), on)
                if on:
                    buffer += ',{0:d},{1:d}'.format(points, percentual_window)
                self.instrument.write(buffer)
                self.get_input_filter_parameters_reading(input)
                if not(input == 'A' and self.input_A_filter_parameters == (on, points, percentual_window)) or not(input == 'B' and self.input_B_filter_parameters == (on, points, percentual_window)):
                    raise Errors.LS340NotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_input_filter_parameters_reading(self, input):
        try:
            if '340' in self.identity:
                string = self.instrument.query('FILTER? {0}'.format(str(input)))
                string_list = string.split(',')
                result = (bool(string_list[0]), int(string_list[1]), int(string_list[2]))
                if str(input) == 'A':
                    self.input_A_filter_parameters = result
                else:
                    self.input_B_filter_parameters = result
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def set_input_curve_number(self, input, curve_number):
        try:
            if '340' in self.identity:
                self.instrument.write('INCRV {0},{1:d}'.format(str(input), curve_number))
                self.get_input_curve_number_reading(input)
                if not(input == 'A' and self.input_A_input_curve == curve_number) or not(input == 'B' and self.input_B_input_curve == curve_number):
                    raise Errors.LS340NotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_input_curve_number_reading(self, input):
        try:
            if '340' in self.identity:
                string = self.instrument.query('INCRV? {0}'.format(str(input)))
                if str(input) == 'A':
                    self.input_A_input_curve = int(string)
                else:
                    self.input_B_input_curve = int(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def set_hardware_input_setup(self, input, enable = True, compensation = False):
        try:
            if '340' in self.identity:
                self.instrument.write('INSET {0},{1:d},{2:d}'.format(str(input), enable, compensation))
                self.get_hardware_input_setup_reading(input)
                if not(input == 'A' and self.input_A_hardware_setup_parameters == (enable, compensation)) or not(input == 'B' and self.input_B_hardware_setup_parameters == (enable, compensation)):
                    raise Errors.LS340NotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_hardware_input_setup_reading(self, input):
        try:
            if '340' in self.identity:
                string = self.instrument.query('INSET? {0}'.format(str(input)))
                string_list = string.split(',')
                result = (bool(string_list[0]), bool(string_list[1]))
                if str(input) == 'A':
                    self.input_A_hardware_setup_parameters = result
                else:
                    self.input_B_hardware_setup_parameters = result
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def set_input_type_parameters(self, input, type, units, coefficient, excitation, range):
        try:
            if '340' in self.identity:
                self.instrument.write('INTYPE {0},{1:d},{2:d},{3:d},{4:d},{5:d},{6:d}'.format(str(input), type, units, coefficient, excitation, range))
                self.get_input_type_parameters_reading(input)
                if not(input == 'A' and self.input_A_type == (type, units, coefficient, excitation, range)) or not(input == 'B' and self.input_B_type == (type, units, coefficient, excitation, range)):
                    raise Errors.LS340NotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_hardware_input_setup_parameters_reading(self, input):
        try:
            if '340' in self.identity:
                string = self.instrument.query('INTYPE? {0}'.format(str(input)))
                string_list = string.split(',')
                result = (int(string_list[0]), int(string_list[1]), int(string_list[2]), int(string_list[3]), int(string_list[4]))
                if str(input) == 'A':
                    self.input_A_type = result
                else:
                    self.input_B_type = result
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_kelvin_reading(self, input):
        try:
            if '340' in self.identity:
                string = self.instrument.query('KRDG? {0}'.format(str(input)))
                if str(input) == 'A':
                    self.input_A_kelvin_reading = float(string)
                else:
                    self.input_B_kelvin_reading = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_linear_equation_data_reading(self, input):
        try:
            if '340' in self.identity:
                string = self.instrument.query('LDAT? {0}'.format(str(input)))
                if str(input) == 'A':
                    self.input_A_linear_data = float(string)
                else:
                    self.input_B_linear_data = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_linear_equation_data_status(self, input):
        try:
            if '340' in self.identity:
                string = self.instrument.query('LDATST? {0}'.format(str(input)))
                if str(input) == 'A':
                    self.input_A_linear_data = int(string)
                else:
                    self.input_B_linear_data = int(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def set_linear_equation_parameters(self, input, equation, m, x_source, b_source, b):
        try:
            if '340' in self.identity:
                buffer = 'LINEAR {0},{1:d},{2:f},{3:d},{4:d}'.format(str(input),equation,m,x_source,b_source)
                if b_source == 1:
                    buffer += '{0:f}'.format(b)
                self.instrument.write(buffer)
                self.get_linear_equation_parameters_reading(input)
                if not(str(input) == 'A' and self.input_A_linear_equation == (equation, m, x_source, b_source, b)) or not(str(input) == 'B' and self.input_B_linear_equation == (equation, m, x_source, b_source, b)):
                    raise Errors.LS340NotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_linear_equation_parameters(self, input, equation, m, x_source, b_source, b):
        try:
            if '340' in self.identity:
                string = self.instrument.query('LINEAR? {0}'.format(str(input)))
                string_list = string.split(',')
                result = (int(string_list[0]), float(string_list[1]), int(string_list[2]), int(string_list[3]), float(string_list[4]))
                if str(input) == 'A':
                    self.input_A_linear_data = result
                else:
                    self.input_B_linear_data = result
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_max_min_data(self, input):
        try:
            if '340' in self.identity:
                string = self.instrument.query('MDAT? {0}'.format(str(input)))
                string_list = string.split(',')
                result = (float(string_list[0]), float(string_list[1]))
                if str(input) == 'A':
                    self.input_A_maxmin_data = result
                else:
                    self.input_B_maxmin_data = result
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_max_min_status(self, input):
        try:
            if '340' in self.identity:
                string = self.instrument.query('MDATST? {0}'.format(str(input)))
                string_list = string.split(',')
                result = (int(string_list[0]), int(string_list[1]))
                if str(input) == 'A':
                    self.input_A_maxmin_status = result
                else:
                    self.input_B_maxmin_status = result
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def set_max_min(self, input, paused = True, source = 1):
        try:
            if '340' in self.identity:
                if paused:
                    paused_number = 2
                else:
                    paused_number = 1
                self.instrument.write('MNMX {0}, {1}, {2}'.format(str(input),str(paused_number), str(source)))
                self.get_max_min(input)
                if not(input == 'A' and self.input_A_maxmin == (paused, source)) or not(input == 'B' and self.input_B_maxmin == (paused, source)):
                    raise Errors.LS340NotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_max_min(self, input):
        try:
            if '340' in self.identity:
                string = self.instrument.query('MNMX? {0}'.format(str(input)))
                string_list = string.split(',')
                if string_list[0] == '1':
                    result = (False, int(string_list[1]))
                else:
                    result = (True, int(string_list[1]))
                if str(input) == 'A':
                    self.input_A_maxmin_status = result
                else:
                    self.input_B_maxmin_status = result
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_reading_status(self, input):
        try:
            if '340' in self.identity:
                string = self.instrument.query('RDGST? {0}'.format(str(input)))
                if str(input) == 'A':
                    self.input_A_reading_status = int(string)
                else:
                    self.input_B_reading_status = int(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_sensor_units_reading(self, input):
        try:
            if '340' in self.identity:
                string = self.instrument.query('SRDG? {0}'.format(str(input)))
                if str(input) == 'A':
                    self.input_A_sensor_units_reading_reading = float(string)
                else:
                    self.input_B_sensor_units_reading_reading = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    """
    Curve commands
    """

    def set_curve_cancellation(self, curve):
        try:
            if '340' in self.identity:
                self.instrument.write('CRVDEL {0:d}'.format(curve))
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def set_curve_header(self, curve, name = '', serialnumber = '', dataformat = 1, limitvalue = 325., coefficient = 1):
        try:
            if '340' in self.identity:
                self.instrument.write('CRVHDR {0:d}, {1}, {2}, {3:d}, {4:f}, {5:d}'.format(curve,str(name), str(serialnumber), dataformat, limitvalue, coefficient))
                self.get_curve_header(curve)
                if not (self.last_curve_header == (name, serialnumber, dataformat, limitvalue, coefficient)):
                    raise Errors.LS340NotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_curve_header(self, curve):
        try:
            if '340' in self.identity:
                string = self.instrument.query('CRVHDR? {0}'.format(str(curve)))
                string_list = string.split(',')
                self.last_curve_header = (string_list[0], string_list[1], int(string_list[2]),float(string_list[3]),int(string_list[4]))
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def set_curve_point(self, curve, index, unitvalue, temperaturevalue):
        try:
            if '340' in self.identity:
                self.instrument.write('CRVPT {0:d}, {1:d}, {2:f}, {3:f}'.format(curve, index, unitvalue, temperaturevalue))
                self.get_curve_point(curve, index)
                if not (self.last_curve_point == (unitvalue, temperaturevalue)):
                    raise Errors.LS340NotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_curve_point(self, curve, index):
        try:
            if '340' in self.identity:
                string = self.instrument.query('CRVPT? {0:d}, {1:d}'.format(str(curve), str(index)))
                string_list = string.split(',')
                self.last_curve_point = (float(string_list[0]), float(string_list[1]))
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def set_curve_save(self):
        try:
            if '340' in self.identity:
                self.instrument.write('CRVSAV')
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def set_softcal_curve(self, standard, destination, serialnumber, temperature1, voltage1, temperature2, voltage2, temperature3 = None, voltage3 = None):
        try:
            if '340' in self.identity:
                buffer = ('SCAL {0:d}, {1:d}, {2}, {3:f},{4:f},{5:f},{6:f}'.format(standard, destination,str(serialnumber),temperature1, voltage1, temperature2, voltage2))
                if not(temperature3 == None and voltage3 == None):
                    buffer += ',{0:f},{1:f}'.format(temperature3,voltage3)
                self.instrument.write(buffer)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    """
    Program commands
    """

    def set_new_program_line(self, program, command, parameters = ()):
        try:
            if '340' in self.identity:
                buffer = 'PGM {0},{1}'.format(str(program), str(command))
                if parameters != ():
                    buffer += ','
                for parameter in parameters:
                    buffer += '{0}'.format(parameter)
                    if parameter != parameters[-1]:
                        buffer += ','
                self.instrument.write(buffer)
                line_index = 1
                readcommand = None
                while readcommand != '0':
                    self.get_program_line(self, program, line_index)
                    readcommand = self.last_program_line[0]
                    line_index += 1
                self.last_program_line_position = line_index - 1
                self.get_program_line(self, program, self.last_program_line_position)
                if not(command == int(self.last_program_line[0]) and parameters == tuple(self.last_program_line[1:])):
                    raise Errors.LS340NotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_program_line(self, program, line):
        try:
            if '340' in self.identity:
                string = self.instrument.query('PGM? {0},{1}'.format(str(program),str(line)))
                self.last_program_line = string.split(',')
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def set_program_cancellation(self, program):
        try:
            if '340' in self.identity:
                self.instrument.write('PGMDEL {0}'.format(str(program), str(command)))
                self.get_program_line(program, 1)
                if not int(self.last_program_line[0]) == 0:
                    raise Errors.LS340NotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_program_memory_reading(self):
       try:
            if '340' in self.identity:
                self.proprogram_memory_status = int(self.instrument.query('PGM? {0},{1}'.format(str(program),str(line))))
            else:
                raise Errors.IncorrectInstrumentError
       except (Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def set_running_program(self, program, terminate = False):
        try:
            if '340' in self.identity:
                if terminate:
                    self.instrument.write('PGMRUN 0')
                else:
                    self.instrument.write('PGMRUN {0}'.format(str(program)))
                self.get_program_status()
                if (terminate and not int(self.last_program_status[0]) == 0) or not (int(self.last_program_status[0]) == program):
                    raise Errors.LS340NotResponding
                if not(int(self.last_program_status[1]) == 0):
                    raise Errors.LS340InternalProgrammingError(int(self.last_program_status[1]))
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    """
    Data logging commands
    """

    def set_logging_status(self, value = False):
        try:
            if '340' in self.identity:
                self.instrument.write('LOG {0:d}'.format(value))
                self.get_logging_status()
                if not (self.last_logging_status == value):
                    raise Errors.LS340NotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_logging_status(self):
        try:
            if '340' in self.identity:
                self.last_logging_status = bool(self.instrument.query('LOG?'))
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_logging_count(self):
        try:
            if '340' in self.identity:
                self.last_logging_count = int(self.instrument.query('LOGCNT?'))
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def set_logging_point(self, point = 1, type = 1, input = 'A', source = 1):
        try:
            if '340' in self.identity:
                buffer = 'LOGPNT {0:d},{1:d}'.format(point, type)
                if type == 1:
                     buffer += '{0:d},{1:d}'.format(str(input), source)
                self.get_logging_point()
                if not (self.last_logging_point == (point, type, input, source)):
                    raise Errors.LS340NotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_logging_point(self, point = 1):
        try:
            if '340' in self.identity:
                string = self.instrument.query('LOGPNT? {0:d}'.format(point))
                string_list = string.split(',')
                self.last_logging_point = (int(string_list[0]),str(string_list[1]),int(string_list[2]))
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def set_logging_parameters(self, readingslog = True, interval = 10, overwrite = False, continuelog = False):
        try:
            if '340' in self.identity:
                buffer = 'LOGSET {0:d},{1:d},{2:d},{3:d}'.format(int(readingslog) + 1,interval, overwrite, continuelog)
                self.get_logging_point()
                if not (self.last_logging_parameters == (readingslog, interval , overwrite, continuelog)):
                    raise Errors.LS340NotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_logging_parameters(self):
        try:
            if '340' in self.identity:
                string = self.instrument.query('LOGSET?')
                string_list = string.split(',')
                self.last_logging_parameters = (bool(int(string_list[0]) - 1),int(string_list[1]),bool(string_list[2]),bool(string_list[3]))
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_logging_record(self, record, point):
        try:
            if '340' in self.identity:
                string = self.instrument.query('LOGVIEW? {0:d},{1:d}'.format(record, point))
                string_list = string.split(',')
                self.last_logging_record = tuple(string_list)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LS340NotResponding, Errors.ReportInstrumentInternalError, Errors.IncorrectInstrumentError) as error:
            error.error_handler()