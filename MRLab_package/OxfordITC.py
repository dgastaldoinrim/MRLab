import Errors
import Cryostat

class OxfordITC(Cryostat.Cryostat):
    """
    This class is a wrapper used as a container of the function used to interface an Oxford Intelligent Temperature Controller with a PC employing a IEEE488
    (GPIB) interface.
    """
    def __init__(self, manager, GPIB_adress = None, read_terminator = 'CR', write_terminator = 'CR', ISOBUS_master = False, ISOBUS_linked = False, ISOBUS_adress = None, line_feed = False):
        """
        This function is used to initialize the object corresponding to the Oxford Intelligent Temperature Controller instrument.
        
        Parameters:
            - manager: an istance of the Manager class;
            - GPIB_adress: the correct GPIB adress for the adressed instrument;
            - read_terminator: parameter used to set the appropriate read terminator for the instrument. Available values are 'CR' ('\r' only) or 'CRLF' ('\r\n' combination).
                All the other possible combination (None, 'LF' ['\n'] and 'LFCR' ['\n\r' combination]) are not used and will rise an error indicating this;
            - write_terminator: parameter used to set the appropriate read terminator for the instrument. Available values are 'CR' ('\r' only) or 'CRLF' ('\r\n' combination)
                as selected and set by users with the define_communication_protocol commands instrument specific commands. All the other possible combination (None, 'LF' ['\n']
                and 'LFCR' ['\n\r' combination]) are not used and will rise an error indicating this;
            - ISOBUS_master: if set to True, the instrument must be treated as an ISOBUS master, so there must be other Oxford instruments linked by ISOBUS to
                the ISOBUS master instrument;
            - ISOBUS_linked: if set to True, the instrument is linked by ISOBUS to an ISOBUS master, that is then linked by GPIB to a PC controller;
            - ISOBUS_adress: if ISOBUS_linked is set to True, this parameter is used to set a single digit number from 1 to 8 that gives the correct ISOBUS adress for the
                ISOBUS linked instrument;
            - line_feed: if set to true, ITC will send a line feed character after each carriage return character.
        """
        Cryostat.Cryostat.__init__(self, manager, GPIB_adress_int = GPIB_adress, read_terminator_int = read_terminator, write_terminator_int = write_terminator, ISOBUS_master_int = ISOBUS_master, ISOBUS_linked_int = ISOBUS_linked, ISOBUS_adress_int = ISOBUS_adress)
        self.get_version_string()
        self.set_control_mode(True, True)
        self.set_communication_protocol(line_feed)
        self.messages = self._messages_dictionary_()
        self.temperature_set_point = None
        self.sensor_1_temperature = None
        self.sensor_2_temperature = None
        self.sensor_3_temperature = None
        self.heater_operating_point = None
        self.needle_valve_operating_point = None
        self.P_term = None
        self.I_term = None
        self.D_term = None
        self.heater_automatic_control = None
        self.needle_valve_automatic_control = None
        self.auto_PIDS_mode = None
        self.heater_controlling_sensor = None
        self.maximum_heater_output = None
        self.sweep_step = None
        self.get_status()
        self.get_temperature_set_point_reading()
        self.get_sensor_1_temperature_reading()
        self.get_sensor_2_temperature_reading()
        self.get_sensor_3_temperature_reading()
        self.get_heater_operating_point_reading()
        self.get_needle_valve_operating_point_reading()
        self.get_P_term_reading()
        self.get_I_term_reading()
        self.get_D_term_reading()
        self.get_temperature_control_mode_reading()
        self.get_auto_PIDs_mode_reading()
        self.get_heater_controlling_sensor_reading()
        self.get_sweep_step_reading()

    """
    Monitor commands
    """

    def set_communication_protocol(self, line_feed):
        """
        Defines the communication protocol.
        
        Parameters:
            - line_feed: if set to true, the ITC will send a line feed character after each carriage return character.
        """
        try:
            if 'ITC' in self.identity:
                if line_feed:
                    self.instrument.write(self.buffer_radix + 'Q2')
                    self.instrument.read_termination = '\r\n'
                else:
                    self.instrument.write(self.buffer_radix + 'Q0')
                    self.instrument.read_termination = '\r'
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler()
            
    def get_temperature_set_point_reading(self):
        """
        This function is used to read the temperature set-point from the ITC.
        """
        try:
            if 'ITC' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R0')[1:]
                if '?' in string:
                    raise Errors.TCNotResponding
                self.temperature_set_point = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            
    def get_sensor_1_temperature_reading(self):
        """
        This function is used to read the sensor 1 measured temperature from the ITC.
        """
        try:
            if 'ITC' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R1')[1:]
                if '?' in string:
                    raise Errors.TCNotResponding
                self.sensor_1_temperature = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_sensor_2_temperature_reading(self):
        """
        This function is used to read the sensor 2 measured temperature from the ITC.
        """
        try:
            if 'ITC' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R2')[1:]
                if '?' in string:
                    raise Errors.TCNotResponding
                self.sensor_2_temperature = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_sensor_3_temperature_reading(self):
        """
        This function is used to read the sensor 3 measured temperature from the ITC.
        """
        try:
            if 'ITC' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R3')[1:]
                if '?' in string:
                    raise Errors.TCNotResponding
                self.sensor_3_temperature = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            
    def get_heater_operating_point_reading(self):
        """
        This function is used to read the heater operating point.
        """
        try:
            if 'ITC' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R5')[1:]
                if '?' in string:
                    raise Errors.TCNotResponding
                self.heater_operating_point = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
    
    def get_needle_valve_operating_point_reading(self):
        """
        This function is used to know the setting of the needle valve.
        """
        try:
            if 'ITC' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R7')[1:]
                if '?' in string:
                    raise Errors.TCNotResponding
                self.needle_valve_operating_point = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
    
    def get_P_term_reading(self):
        """
        This function is used to read the set value for the P term of the temperature controller, i.e. to read the PROPORTIONAL BAND value in kelvin.
        """
        try:
            if 'ITC' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R8')[1:]
                if '?' in string:
                    raise Errors.TCNotResponding
                self.P_term = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
    
    def get_I_term_reading(self):
        """
        This function is used to read the set value for the I term of the temperature controller, i.e. to read the INTEGRAL ACTION TIME value in minutes.
        """
        try:
            if 'ITC' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R9')[1:]
                if '?' in string:
                    raise Errors.TCNotResponding
                self.I_term = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_D_term_reading(self):
        """
        This function is used to read the set value for the D term of the temperature controller, i.e. to read the DERIVATIVE ACTION TIME value in minutes.
        """
        try:
            if 'ITC' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R10')[1:]
                if '?' in string:
                    raise Errors.TCNotResponding
                self.D_term = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            
    def get_status(self):
        """
        This function is used to read the current ITC status from the instrument and to decodify it into a string comprehensible for the user.
        """
        try:
            if 'ITC' in self.identity:
                self.get_status_string()
                if '?' in self.last_queried_status:
                    raise Errors.TCNotResponding
                self._status_decoder_(self.last_queried_status)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
        
    """
    Control commands
    """

    def set_temperature_control_mode(self, auto_heater = False, auto_gas_flow = False):
        """
        This function is used to set the heater and needle valve control mode. If one of the parameters is set to AUTO, the controller routine will use the parameter
        to automatically control the temperature reading by the controlling sensor. Instead, if one of the parameters is set to MANUAL, the controller will not use
        these parameter to control temperature, because it will be set manually or via the interface by the user using the appropriate command.
        
        Parameters:
            - auto_heater: if set to true, heater will be controlled by the ITC controller in order to stabilize the temperature;
            - auto_gas_flow: if set to true, needle valve aperture will be controlled by the ITC controller in order to stabilize the temperature.
        """
        try:
            if 'ITC' in self.identity:
                if auto_heater:
                    if auto_gas_flow:
                        self.instrument.query(self.buffer_radix + 'A3')
                    else:
                        self.instrument.query(self.buffer_radix + 'A1')
                else:
                    if auto_gas_flow:
                        self.instrument.query(self.buffer_radix + 'A2')
                    else:
                        self.instrument.query(self.buffer_radix + 'A0')
                self.get_temperature_control_mode_reading()
                if not ((self.heater_automatic_control == auto_heater) and (self.needle_valve_automatic_control == auto_gas_flow)):
                    raise Errors.TCNotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def set_P_control_term(self, P):
        """
        This function is used to set the PROPORTIONAL BAND (P) term of the automatic controller.
        The proportional band is the value in kelvin for which the controller output will be proportional to the error (i.e. difference) between the set-point
        temperature and the sensor reading temperature.
        
        Parameters:
            - P = PROPORTIONAL BAND value in kelvin.
        """
        try:
            if 'ITC' in self.identity:
                if P >= 5 and P <= 50:
                    self.instrument.query(self.buffer_radix + 'P{0:G}'.format(P))
                    self.get_P_term_reading()
                    if not(self.P_term == P):
                        raise Errors.TCNotResponding
                else:
                    raise Errors.TCPOutOfRange
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.TCPOutOfRange, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            
    def set_I_control_term(self, I):
        """
        This function is used to set the INTEGRAL ACTION TIME (I) term of the automatic controller.
        The integral action time is the value in minutes of the integration period of the integral part of the controller. The controller integrates error (i.e.
        diffrence between the set-point temperature and the sensor reading temperature) data until the given integration time and then add its output to the heater.
        
        Parameters:
            - I = integral action time value in minutes.
        """
        try:
            if 'ITC' in self.identity:
                if I >= 0 and I <= 140:
                    self.instrument.query(self.buffer_radix + 'I{0:G}'.format(I))
                    self.get_I_term_reading()
                    if not(self.I_term == I):
                        raise Errors.TCNotResponding
                else:
                    raise Errors.TCIOutOfRange
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.TCIOutOfRange, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def set_D_control_term(self, D):
        """
        This function is used to set the DERIVATIVE ACTION TIME (I) term of the automatic controller.
        The integral action time is the value in minutes of the derivation period of the derivative part of the controller. The controller derivates error (i.e.
        diffrence between the set-point temperature and the sensor reading temperature) data until the given derivation time and then add its output to the heater.
        
        Parameters:
            - D = integral action time value in minuted.
        """
        try:
            if 'ITC' in self.identity:
                if D >= 0 and D <= 140:
                    self.instrument.query(self.buffer_radix + 'D{0:G}'.format(D))
                    self.get_D_term_reading()
                    if not(self.D_term == D):
                        raise Errors.TCNotResponding
                else:
                    raise Errors.TCDOutOfRange
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.TCDOutOfRange, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def set_temperature_set_point_display(self):
        """
        This function is used to display the temperature set-point from the ITC.
        """
        try:
            if 'ITC' in self.identity:
                self.instrument.query(self.buffer_radix + 'F0')
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler()
            
    def set_sensor_1_temperature_display(self):
        """
        This function is used to display the sensor 1 measured temperature from the ITC.
        """
        try:
            if 'ITC' in self.identity:
                self.instrument.query(self.buffer_radix + 'F1')
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler()

    def set_sensor_2_temperature_display(self):
        """
        This function is used to display the sensor 2 measured temperature from the ITC.
        """
        try:
            if 'ITC' in self.identity:
                self.instrument.query(self.buffer_radix + 'F2')
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler()

    def set_sensor_3_temperature_display(self):
        """
        This function is used to display the sensor 3 measured temperature from the ITC.
        """
        try:
            if 'ITC' in self.identity:
                self.instrument.query(self.buffer_radix + 'F3')
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler()
            
    def set_heater_operating_point_display(self):
        """
        This function is used to display the heater operating point.
        """
        try:
            if 'ITC' in self.identity:
                self.instrument.query(self.buffer_radix + 'F5')
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler()
    
    def set_needle_valve_operating_point_display(self):
        """
        This function is used to know the setting of the needle valve.
        """
        try:
            if 'ITC' in self.identity:
                self.instrument.query(self.buffer_radix + 'F7')
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler()
    
    def set_P_term_display(self):
        """
        This function is used to display the set value for the P term of the temperature controller, i.e. to display the PROPORTIONAL BAND value in kelvin.
        """
        try:
            if 'ITC' in self.identity:
                self.instrument.query(self.buffer_radix + 'F8')
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler()
    
    def set_I_term_display(self):
        """
        This function is used to display the set value for the I term of the temperature controller, i.e. to display the INTEGRAL ACTION TIME value in minutes.
        """
        try:
            if 'ITC' in self.identity:
                self.instrument.query(self.buffer_radix + 'F9')
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler()

    def set_D_term_display(self):
        """
        This function is used to display the set value for the D term of the temperature controller, i.e. to display the DERIVATIVE ACTION TIME value in minutes.
        """
        try:
            if 'ITC' in self.identity:
                self.instrument.query(self.buffer_radix + 'F10')
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler()

    def set_auto_PIDs_mode(self, auto_PIDs = False):
        try:
            if 'ITC' in self.identity:
                if auto_PIDs:
                    self.instrument.query(self.buffer_radix + 'L1')
                else:
                    self.instrument.query(self.buffer_radix + 'L0')
                self.get_auto_PIDs_mode_reading()
                if not(self.auto_PIDs_mode == auto_PIDs):
                    raise Errors.TCNotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
    
    def set_heater_controlling_sensor(self, sensor_number):
        try:
            if 'ITC' in self.identity:
                if sensor_number >= 1 and sensor_number <= 3:
                    self.instrument.query(self.buffer_radix + 'H{0:G}'.format(sensor_number))
                    self.get_heater_controlling_sensor_reading()
                    if not(self.heater_controlling_sensor == sensor_number):
                        raise Errors.TCNotResponding
                else:
                    raise Errors.TCWrongControllingSensorNumber(sensor_number)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
    
    def set_manual_gas_flow(self, percentage):
        try:
            if 'ITC' in self.identity:
                if percentage >= 0 and percentage <= 100:
                    self.instrument.query(self.buffer_radix + 'G{0:G}'.format(percentage))
                    self.get_needle_valve_operating_point_reading()
                    if not(self.needle_valve_operating_point == percentage):
                        raise Errors.TCNotResponding
                else:
                    raise Errors.TCWrongPercentage(percentage)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.TCWrongPercentage, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
        
    def set_manual_heater(self, percentage):
        try:
            if 'ITC' in self.identity:
                if percentage >= 0 and percentage <= 100:
                    self.instrument.query(self.buffer_radix + 'O{0:G}'.format(percentage))
                    self.get_heater_operating_point_reading()
                    if not(self.heater_operating_point == percentage):
                        raise Errors.TCNotResponding
                else:
                    raise Errors.TCWrongPercentage(percentage)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.TCWrongPercentage, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def set_manual_maximum_heater_output(self, max_voltage):
        try:
            if 'ITC' in self.identity:
                if max_voltage >= 0 and max_voltage <= 40:
                    self.instrument.query(self.buffer_radix + 'M{0:G}'.format(max_voltage))
                    self.maximum_heater_output = max_voltage
                else:
                    raise Errors.TCWrongMaxOutputVoltage(max_voltage)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCWrongMaxOutputVoltage, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
        
    def set_temperature_set_point(self, set_point):
        try:
            if 'ITC' in self.identity:
                if set_point >= 0 and set_point <= 420:
                    self.instrument.query(self.buffer_radix + 'T{0:G}'.format(set_point))
                    self.get_temperature_set_point_reading()
                    if not (self.temperature_set_point == set_point):
                        raise Errors.TCNotResponding
                else:
                    raise Errors.TCWrongSetPoint(set_point)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.TCWrongSetPoint, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
    
    def set_sweep_command(self, stop_sweep = False, starting_point = 1):
        try:
            if 'ITC' in self.identity:
                if starting_point >= 1 and starting_point <= 32:
                    if stop_sweep:
                        self.instrument.query(self.buffer_radix + 'S0')
                    else:
                        self.instrument.query(self.buffer_radix + 'S{0:G}'.format(starting_point))
                    self.get_sweep_reading()
                    if not (self.sweep_step == 0 and stop_sweep) or not (self.sweep_step == starting_point):
                        raise Errors.TCNotResponding
                else:
                    raise Errors.TCWrongSweepStartingPoint(starting_point)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.TCNotResponding, Errors.TCWrongSweepStartingPoint, Errors.IncorrectInstrumentError) as error:
            error.error_handler()    
        
    """
    System commands
    """
    
    def set_calibration_data_storage(self):
        """
        This function is used to store any change made to the calibration datas of the power supply, in order not to lose them at the power-up.
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + '~')
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler

    """
    Derived commands

    These commands are supplied in order to automating some of the tasks connected with the use of this class.
    """

    def _messages_dictionary_(self):
        keys = ('X', 'A', 'C', 'S', 'H', 'L')
        X_messages = {'0': 'Temperature controller NORMAL operative mode.\n'}
        A_messages = {'0': 'Heater in MANUAL mode. Gas flow in MANUAL mode.\n', '1': 'Heater in AUTO mode. Gas flow in MANUAL mode.\n', '2': 'Heater in MANUAL mode. Gas flow in AUTO mode.\n', '3': 'Heater in AUTO mode. Gas flow in AUTO mode.\n'}
        C_messages = {'0': 'Temperature controller in LOCAL and LOCKED state.\n', '1': 'Temperature controller in REMOTE and LOCKED state.\n', '2': 'Temperature controller in LOCAL and UNLOCKED state.\n', '3': 'Temperature controller in REMOTE and UNLOCKED state.\n'}
        H_messages = {'1': 'Temperature is controlled by CHANNEL 1 sensor.\n', '2': 'Temperature is controlled by CHANNEL 2 sensor.\n', '3': 'Temperature is controlled by CHANNEL 3 sensor.\n'}
        L_messages = {'0': 'Auto (learned) PIDs are DISABLED.', '1': 'Auto (learned) PIDs are ENABLED.'}
        messages = {}
        for key in keys:
            if key == 'X':
                for n in X_messages:
                    messages[key, n] = X_messages[n]
            elif key == 'A':
                for n in A_messages:
                    messages[key, n] = A_messages[n]
            elif key == 'C':
                for n in C_messages:
                    messages[key, n] = C_messages[n]
            elif key == 'S':
                messages[key,'00'] = 'Sweep mode is not active.\n'
                for nn in range(1,32):
                    if nn % 2 == 1:
                        messages[key, nn] = 'Sweeping to step number {0:G} set temperature.\n'.format((nn + 1) // 2)
                    else:
                        messages[key, nn] = 'Holding the step number {0:G} set temperature.\n'.format(nn // 2)
            elif key == 'H':
                for n in H_messages:
                    messages[key, n] = H_messages[n]
            elif key == 'L':
                for n in L_messages:
                    messages[key, n] = L_messages[n]
        return messages
        
    def _status_decoder_(self, status):
        self.last_decodified_status = ""
        status_split = (status[:2], status[2:4], status[4:6], status[6:9], status[9:11], status[11:])
        for string in status_split:
            if len(string) == 2:
                key = string[0]
                n = string[1]
                self.last_decodified_status = self.last_decodified_status + self.messages[key, n]
            else:
                key = string[0]
                if key == 'S':
                    nn = string[1:]
                    self.last_decodified_status = self.last_decodified_status + self.messages[key, nn]
                else:
                    m = string[1]
                    n = string[2]
                    self.last_decodified_status = self.last_decodified_status + self.messages[key, m, n]

    def close(self):
        """
        This function is used to put the ILM in a safe state, in which the ILM can be used in LOCAL mode before cutting the link between controller and instrument.
        """
        self.set_temperature_control_mode(False, False)
        self.set_temperature_set_point(0)
        self.set_manual_heater(0)
        self.set_manual_gas_flow(0)
        self._general_close_()

    def get_temperature_control_mode_reading(self):
        self.get_status()
        if float(self.last_queried_status[3]) == 0:
            self.heater_automatic_control = False
            self.needle_valve_automatic_control = False
        elif float(self.last_queried_status[3]) == 1:
            self.heater_automatic_control = True
            self.needle_valve_automatic_control = False
        elif float(self.last_queried_status[3]) == 2:
            self.heater_automatic_control = False
            self.needle_valve_automatic_control = True
        elif float(self.last_queried_status[3]) == 3:
            self.heater_automatic_control = True
            self.needle_valve_automatic_control = True

    def get_auto_PIDs_mode_reading(self):
        self.get_status()
        if float(self.last_queried_status[12]) == 0:
            self.auto_PIDS_mode = False
        elif float(self.last_queried_status[12]) == 1:
            self.auto_PIDS_mode = True

    def get_heater_controlling_sensor_reading(self):
        self.get_status()
        self.heater_controlling_sensor = int(self.last_queried_status[10])

    def get_sweep_step_reading(self):
        self.get_status()
        self.sweep_step = float(self.last_queried_status[7:9])