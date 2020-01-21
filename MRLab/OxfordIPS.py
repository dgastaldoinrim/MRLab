import Errors
import Cryostat

class OxfordIPS(Cryostat.Cryostat):
    """
    This class is a wrapper used as a container of the function used to interface an Oxford Intelligent Power Supply with a PC employing a IEEE488 (GPIB) interface and/or,
    if equipped with the Oxford ISOBUS, also the Oxford ISOBUS interface.
    """
    def __init__(self, manager, GPIB_adress = None, read_terminator = 'CR', write_terminator = 'CR', ISOBUS_master = False, ISOBUS_linked = False, ISOBUS_adress = None, extended_resolution = True, line_feed = False):
        """
        This function is used to initialize the object corresponding to the Oxford Intelligent Power Supply instrument.
        
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
            - extended_resolution = if set to true, IPS will extend its resolution on field and current measurements by one digit;
            - line_feed: if set to true, IPS will send a line feed character after each carriage return character.
        """
        Cryostat.Cryostat.__init__(self, manager, GPIB_adress_int = GPIB_adress, read_terminator_int = read_terminator, write_terminator_int = write_terminator, ISOBUS_master_int = ISOBUS_master, ISOBUS_linked_int = ISOBUS_linked, ISOBUS_adress_int = ISOBUS_adress)
        self.get_version_string()
        self.set_control_mode(True, True)
        self.set_communication_protocol(extended_resolution, line_feed)
        self.extended_resolution = extended_resolution
        self.messages = self._messages_dictionary_()
        self.output_current = None
        self.output_voltage = None
        self.magnet_current = None
        self.current_set_point = None
        self.current_sweep_rate = None
        self.output_field = None
        self.field_set_point = None
        self.field_sweep_rate = None
        self.software_voltage_limit = None
        self.persistent_current = None
        self.trip_current = None
        self.persistent_field = None
        self.trip_field = None
        self.switch_heater_current = None
        self.safe_current_negative_limit = None
        self.safe_current_positive_limit = None
        self.lead_resistance = None
        self.magnet_inductance = None
        self.get_output_current_reading()
        self.get_output_voltage_reading()
        self.get_magnet_current_reading()
        self.get_current_set_point_reading()
        self.get_current_sweep_rate_reading()
        self.get_output_field_reading()
        self.get_field_set_point_reading()
        self.get_field_sweep_rate_reading()
        self.get_software_voltage_limit_reading()
        self.get_persistent_current_reading()
        self.get_trip_current_reading()
        self.get_persistent_field_reading()
        self.get_trip_field_reading()
        self.get_switch_heater_current_reading()
        self.get_safe_current_negative_limit_reading()
        self.get_safe_current_positive_limit_reading()
        self.get_lead_resistance_reading()
        self.get_magnet_inductance_reading()
        self.set_activity()
                
    """
    Monitor commands
    """

    def set_communication_protocol(self, extended_resolution, line_feed):
        """
        Defines the communication protocol.
        
        Parameters:
            - extended_resolution: if set to true, IPS reports all the values with a resolution extended of one order of magnitude.
            - line_feed: if set to true, the IPS will send a line feed character after each carriage return character.
        """
        if line_feed:
            if extended_resolution:
                self.instrument.write(self.buffer_radix + 'Q6')
            else:
                self.instrument.write(self.buffer_radix + 'Q2')
            self.instrument.read_termination = '\r\n'
        else:
            if extended_resolution:
                self.instrument.write(self.buffer_radix + 'Q4')
            else:
                self.instrument.write(self.buffer_radix + 'Q0')
            self.instrument.read_termination = '\r'
                
    def get_output_current_reading(self):
        """
        The function reads the current output current of the power supply
        """
        try:
            if 'IPS' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R0')[1:]
                if '?' in string:
                    raise Errors.PSNotResponding
                self.output_current = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler
            
    def get_output_voltage_reading(self):
        """
        The function reads the current output voltage of the power supply
        """
        try:
            if 'IPS' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R1')[1:]
                if '?' in string:
                    raise Errors.PSNotResponding
                self.output_voltage = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler
            
    def get_magnet_current_reading(self):
        """
        The function reads the measured magnet current
        """
        try:
            if 'IPS' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R2')[1:]
                if '?' in string:
                    raise Errors.PSNotResponding
                self.magnet_current = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler

    def get_current_set_point_reading(self):
        """
        This function is used to read the power supply current set point.
        """
        try:
            if 'IPS' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R5')[1:]
                if '?' in string:
                    raise Errors.PSNotResponding
                self.current_set_point = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler
            
    def get_current_sweep_rate_reading(self):
        """
        Function used to monitor current sweep rate.
        """
        try:
            if 'IPS' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R6')[1:]
                if '?' in string:
                    raise Errors.PSNotResponding
                self.current_sweep_rate = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler
            
    def get_output_field_reading(self):
        """
        Function used to read the output given by the power supply in terms of field
        """
        try:
            if 'IPS' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R7')[1:]
                if '?' in string:
                    raise Errors.PSNotResponding
                self.output_field = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler

    def get_field_set_point_reading(self):
        """
        This function is used to read the field set point of the power supply.
        """
        try:
            if 'IPS' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R8')[1:]
                if '?' in string:
                    raise Errors.PSNotResponding
                self.field_set_point = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler
            
    def get_field_sweep_rate_reading(self):
        """
        This function is used to read the field sweep rate of the power supply.
        """
        try:
            if 'IPS' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R9')[1:]
                if '?' in string:
                    raise Errors.PSNotResponding
                self.field_sweep_rate = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler

    def get_software_voltage_limit_reading(self):
        """
        This function is used to read magnet persistent current.
        """
        try:
            if 'IPS' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R15')[1:]
                if '?' in string:
                    raise Errors.PSNotResponding
                self.software_voltage_limit= float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler
            
    def get_persistent_current_reading(self):
        """
        This function is used to read magnet persistent current.
        """
        try:
            if 'IPS' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R16')[1:]
                if '?' in string:
                    raise Errors.PSNotResponding
                self.persistent_current = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler
            
    def get_trip_current_reading(self):
        """
        This function is used to read the trip current (persistent current reading before the last quench) of a persistent magnet.
        """
        try:
            if 'IPS' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R17')[1:]
                if '?' in string:
                    raise Errors.PSNotResponding
                self.trip_current = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler
       
    def get_persistent_field_reading(self):
        """
        This function is used to read magnet persistent field.
        """
        try:
            if 'IPS' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R18')[1:]
                if '?' in string:
                    raise Errors.PSNotResponding
                self.persistent_field = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler
            
    def get_trip_field_reading(self):
        """
        This function is used to read the trip field (persistent field reading before the last quench) of a persistent magnet.
        """
        try:
            if 'IPS' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R19')[1:]
                if '?' in string:
                    raise Errors.PSNotResponding
                self.trip_field = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler
            
    def get_switch_heater_current_reading(self):
        """
        Function used to read the current supplied to the superconductive switch heater
        """
        try:
            if 'IPS' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R20')[1:]
                if '?' in string:
                    raise Errors.PSNotResponding
                self.switch_heater_current = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler

    def get_safe_current_negative_limit_reading(self):
        """
        Function used to read the most negative safe current limit
        """
        try:
            if 'IPS' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R21')[1:]
                if '?' in string:
                    raise Errors.PSNotResponding
                self.safe_current_negative_limit = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler

    def get_safe_current_positive_limit_reading(self):
        """
        Function used to read the most positive safe current limit
        """
        try:
            if 'IPS' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R21')[1:]
                if '?' in string:
                    raise Errors.PSNotResponding
                self.safe_current_positive_limit = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler

    def get_lead_resistance_reading(self):
        """
        Function used to read the current supplie dto the superconductive switch heater
        """
        try:
            if 'IPS' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R23')[1:]
                if '?' in string:
                    raise Errors.PSNotResponding
                self.lead_resistance = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler

    def get_magnet_inductance_reading(self):
        """
        Function used to read the calibrated magnet inductance.
        """
        try:
            if 'IPS' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R24')[1:]
                if '?' in string:
                    raise Errors.PSNotResponding
                self.magnet_inductance = float(string)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler
            
    def get_status(self):
        """
        This function is used to read the current ILM status from the instrument and to decodify it into a string comprehensible for the user.
        """
        try:
            if 'IPS' in self.identity:
                self.last_queried_status = self.instrument.query(self.buffer_radix + 'X')
                if '?' in self.last_queried_status:
                    raise Errors.PSNotResponding
                self._status_decoder_(self.last_queried_status)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.IncorrectInstrumentError, Errors.PSNotResponding) as error:
            error.error_handler
            
    """
    Control commands
    """
                
    def set_activity(self, hold = True, to_set_point = False, to_zero = False, clamped = False):
        """
        This command is used to mimic the behaviour of the front panel switches "HOLD", "TO SET POINT" and "TO ZERO".
        
        Parameters:
            - hold = when true selects the "HOLD" activity;
            - to_set_point = when true selects the "TO SET POINT" activity;
            - to_zero = when true selects the "TO ZERO" activity;
            - clamped = when true selects the "CLAMP" activity, in which the magnet is set to 0 field and then activities like "TO SET POINT" or "TO ZERO" will
                not be recognized. To deselect it select "HOLD" activity.
        """
        try:
            if 'IPS' in self.identity:
                if hold:
                    self.instrument.query(self.buffer_radix + 'A0')
                elif to_set_point:
                    self.instrument.query(self.buffer_radix + 'A1')
                elif to_zero:
                    self.instrument.query(self.buffer_radix + 'A2')
                elif clamped:
                    self.instrument.query(self.buffer_radix + 'A4')
                self.get_status()
                if (hold and not(self.last_queried_status[4] == '0')) or (to_set_point and not(self.last_queried_status[4] == '1')) or (to_zero and not(self.last_queried_status[4] == '2'))  or (clamped and not(self.last_queried_status[4] == '4')):
                    raise Errors.PSNotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler
            
    def set_output_current_display(self):
        """
        The function reads the current output current of the power supply
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + 'F0')[1:]
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler
            
    def set_output_voltage_display(self):
        """
        The function reads the current output voltage of the power supply
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + 'F1')[1:]
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler
            
    def set_magnet_current_display(self):
        """
        The function reads the measured magnet current
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + 'F2')[1:]
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler

    def set_current_set_point_display(self):
        """
        This function is used to read the power supply current set point.
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + 'F5')[1:]
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler
            
    def set_current_sweep_rate_display(self):
        """
        Function used to monitor current sweep rate.
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + 'F6')[1:]
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler
            
    def set_output_field_display(self):
        """
        Function used to read the output given by the power supply in terms of field
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + 'F7')[1:]
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler

    def set_field_set_point_display(self):
        """
        This function is used to read the field set point of the power supply.
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + 'F8')[1:]
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler
            
    def set_field_sweep_rate_display(self):
        """
        This function is used to read the field sweep rate of the power supply.
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + 'F9')[1:]
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler

    def set_software_voltage_limit_display(self):
        """
        This function is used to read magnet persistent current.
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + 'F15')[1:]
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler
            
    def set_persistent_current_display(self):
        """
        This function is used to read magnet persistent current.
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + 'F16')[1:]
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler
            
    def set_trip_current_display(self):
        """
        This function is used to read the trip current (persistent current display before the last quench) of a persistent magnet.
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + 'F17')[1:]
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler
       
    def set_persistent_field_display(self):
        """
        This function is used to read magnet persistent field.
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + 'F18')[1:]
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler
            
    def set_trip_field_display(self):
        """
        This function is used to read the trip field (persistent field display before the last quench) of a persistent magnet.
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + 'F19')[1:]
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler
            
    def set_switch_heater_current_display(self):
        """
        Function used to read the current supplied to the superconductive switch heater
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + 'F20')[1:]
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler

    def set_safe_current_negative_limit_display(self):
        """
        Function used to read the most negative safe current limit
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + 'F21')[1:]
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler

    def set_safe_current_positive_limit_display(self):
        """
        Function used to read the most positive safe current limit
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + 'F21')[1:]
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler

    def set_lead_resistance_display(self):
        """
        Function used to read the current supplie dto the superconductive switch heater
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + 'F23')[1:]
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler

    def set_magnet_inductance_display(self):
        """
        Function used to read the calibrated magnet inductance.
        """
        try:
            if 'IPS' in self.identity:
                self.instrument.query(self.buffer_radix + 'F24')[1:]
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler
            
    def set_switch_heater(self, opened = False):
        """
        This function is supplied in order to command the activation of the switch heater, in order to open/close the superconductive switch (if fitted).
        
        Parameters:
            - opened: if set to True, allows current to flow in the switch heater that, by heating the superconductive switch, will let current from the
                power supply flow into the superconductive magnet.
        """
        try:
            if 'IPS' in self.identity:
                if opened:
                    self.instrument.query(self.buffer_radix + 'H1')
                else:
                    self.instrument.query(self.buffer_radix + 'H0')
                self.get_status()
                if (opened and not(self.last_queried_status[8] == '1')) or (not(opened) and (self.last_queried_status[8] == '0' or self.last_queried_status[8] == '2')):
                    raise Errors.PSNotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler
    
    def set_target_current(self, current):
        """
        Function used to set a target current for the power supply and the magnet.
        
        Parameters:
            - current: the desired current (in A).
        """
        try:
            if 'IPS' in self.identity:
                if abs(current) <= 98.46:
                    if self.extended_resolution:
                        self.instrument.query(self.buffer_radix + 'I{0:+.4f}'.format(current))
                    else:
                        self.instrument.query(self.buffer_radix + 'I{0:+.3f}'.format(current))
                    self.get_current_set_point_reading()
                    if not (self.current_set_point == current):
                        raise Errors.PSNotResponding
                else:
                    raise Errors.PSWrongOutputCurrent(current)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.PSWrongOutputCurrent, Errors.IncorrectInstrumentError) as error:
            error.error_handler
    
    def set_target_field(self, field):
        """
        Function used to set a target applied field for the power supply and the magnet.
        
        Parameters:
            - field: the desired field (in T).
        """
        try:
            if 'IPS' in self.identity:
                if abs(field) <= 7:
                    if self.extended_resolution:
                        self.instrument.query(self.buffer_radix + 'J{0:+.5f}'.format(field))
                    else:
                        self.instrument.query(self.buffer_radix + 'J{0:+.4f}'.format(field))
                    self.get_field_set_point_reading()
                    if not (self.field_set_point == field):
                        raise Errors.PSNotResponding
                else:
                    raise Errors.PSWrongOutputField(field)
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler
            
    def set_mode(self, field_display = True, no_modify_sweep_mode = False, sweep_fast_mode = True):
        """
        This function is used to select if display current or field in the front panel and to conversely set the sweep rate.
        
        Parameters:
            - field_display = if set to true, the front panel display will display a field value (in T) instead of a current value (in A);
            - no_modify_sweep_mode = if set to true does not want to change the sweep rate profile;
            - sweep_fast_mode = if set to true, selects the fast sweep rate profile instead of the slow one.
        """
        try:
            if 'IPS' in self.identity:
                if field_display:
                    if no_modify_sweep_mode:
                        self.instrument.query(self.buffer_radix + 'M9')
                    elif sweep_fast_mode:
                        self.instrument.query(self.buffer_radix + 'M1')
                    else:
                        self.instrument.query(self.buffer_radix + 'M5')
                else:
                    if no_modify_sweep_mode:
                        self.instrument.query(self.buffer_radix + 'M8')
                    elif sweep_fast_mode:
                        self.instrument.query(self.buffer_radix + 'M0')
                    else:
                        self.instrument.query(self.buffer_radix + 'M4')
                self.get_status()
                if field_display:
                    if (sweep_fast_mode and not(self.last_queried_status[10] == '1')) or (not(sweep_fast_mode) and not(self.last_queried_Status[10] == '5')):
                        raise Errors.PSNotResponding
                else:
                    if (sweep_fast_mode and not(self.last_queried_status[10] == '0')) or (not(sweep_fast_mode) and not(self.last_queried_Status[10] == '4')):
                        raise Errors.PSNotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding,Errors.IncorrectInstrumentError) as error:
            error.error_handler
            
    def set_polarity(self, no_action = True, positive_polarity = False, swap_polarity = False):
        """
        This function is used to set the polarity of the current supplied by the power supply. It is here only for compatibility issues with the older PS120-10 power
        supplies.
        
        Parameters:
            - no_action: if set to true, the function call will not affect the current polarity;
            - positive_polarity = if set to true, the function call will set positive polarity for the current;
            - swap_polarity = if set to true, the function call will swap the current polarity.
        """
        try:
            if 'IPS' in self.identity:
                if no_action:
                    self.instrument.query(self.buffer_radix + 'P0')
                elif positive_polarity:
                    self.instrument.query(self.buffer_radix + 'P1')
                elif swap_polarity:
                    self.instrument.query(self.buffer_radix + 'P4')
                else:
                    self.instrument.query(self.buffer_radix + 'P2')
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler

    def set_current_sweep_rate(self, rate):
        """
        Function used to set a new current sweep rate (in ampere per minute) when the power suppply is in SWEEP mode.
        
        Parameters:
            - rate = specified current sweep rate (in ampere per minute).
        """
        try:
            if 'IPS' in self.identity:
                if abs(rate) <= 16.88:
                    if self.extended_resolution:
                        self.instrument.query(self.buffer_radix + 'S{0:+.4f}'.format(rate))
                    else:
                        self.instrument.query(self.buffer_radix + 'S{0:+.3f}'.format(rate))
                    self.get_current_sweep_rate_reading()
                    if not(self.current_sweep_rate == rate):
                        Errors.PSNotResponding
                else:
                    Errors.PSWrongCurrentSweepRate(rate)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.PSWrongCurrentSweepRate, Errors.IncorrectInstrumentError) as error:
            error.error_handler
        
    def set_field_sweep_rate(self, rate):
        """
        Function used to set a new field sweep rate (in tesla per minute) when the power suppply is in SWEEP mode.
        
        Parameters:
            - rate = specified field sweep rate (in tesla per minute).
        """
        try:
            if 'IPS' in self.identity:
                if abs(rate) <= 1.2:
                    if self.extended_resolution:
                        self.instrument.query(self.buffer_radix + 'T{0:+.4f}'.format(rate))
                    else:
                        self.instrument.query(self.buffer_radix + 'T{0:+.3f}'.format(rate))
                    self.get_field_sweep_rate_reading()
                    if not(self.field_sweep_rate == rate):
                        Errors.PSNotResponding
                else:
                    raise Errors.PSWrongFieldSweepRate(rate)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.PSNotResponding, Errors.PSWrongFieldSweepRate, Errors.IncorrectInstrumentError) as error:
            error.error_handler
        
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
        """
        This function is used to create a dictionary of the possible messages given by the examine_status function, in order to give them to the
        status_decoder function in order to translate the status string into a comprehensible message for the user.
        """
        keys = ('X', 'A', 'C', 'H', 'M', 'P')
        X_m_messages = {'0': 'Magnet NORMAL.', '1': 'Magnet QUENCHED.', '2': 'Power supply OVER HEATED.', '4': 'Magnet is WARMING UP.', '8': 'Magnet is at FAULT.'}
        X_n_messages = {'0': 'Power supply NORMAL.\n', '1': 'Power supply ON POSITIVE VOLTAGE LIMIT.\n', '2': 'Power supply ON NEGATIVE VOLTAGE LIMIT.\n', '4': 'Power supply OUTSIDE NEGATIVE CURRENT LIMIT.\n', '8': 'Power supply OUTSIDE POSITIVE CURRENT LIMIT.\n'}
        A_messages = {'0': 'Power supply output is in HOLD state.\n', '1': 'Power supply output is sweeping TO SET POINT.\n', '2': 'Power supply output is sweeping TO ZERO.\n', '4': 'Power supply output is CLAMPED.\n'}
        C_messages = {'0': 'Power supply in LOCAL AND LOCKED.\n', '1': 'Power supply in REMOTE AND LOCKED.\n', '2': 'Power supply in LOCAL AND UNLOCKED.\n', '3': 'Power supply in REMOTE AND UNLOCKED.\n', '4': 'Power supply in AUTO-RUN-DOWN.\n', '5': 'Power supply in AUTO-RUN-DOWN.\n', '6': 'Power supply in AUTO-RUN-DOWN.\n', '7': 'Power supply in AUTO-RUN-DOWN.\n'}
        H_messages = {'0': 'Switch heater is OFF with MAGNET AT ZERO field.\n', '1': 'Switch heater is ON.\n', '2': 'Switch heater is OFF with MAGNET AT FIELD.\n', '5': 'Switch heater is at FAULT.\n', '8': 'There is NO SWITCH HEATER fitted.\n'}
        M_m_messages = {'0': 'Power supply in AMPS FAST sweep mode.', '1': 'Power supply in FIELD FAST sweep mode.', '4': 'Power supply in AMPS SLOW sweep mode.', '5': 'Power supply in FIELD SLOW sweep mode.'}
        M_n_messages = {'0': 'Power supply is AT REST.\n', '1': 'Power supply is SWEEPING (current in magnet).\n', '2': 'Power supply is SWEEP LIMITING (current in switch)).\n', '3': 'Power supply is SWEEPING (current in magnet) buth with a SWEEP LIMITING in rate.\n'}
        P_m_messages = {'0': 'Polarities: POS, POS, POS.', '1': 'Polarities: POS, POS, NEG.', '2': 'Polarities: POS, NEG, POS.', '3': 'Polarities: POS, NEG, NEG.', '4': 'Polarities: NEG, POS, POS.', '5': 'Polarities: NEG, POS, NEG.', '6': 'Polarities: NEG, NEG, POS.', '7': 'Polarities: NEG, NEG, NEG.'}
        P_n_messages = {'1': 'Negative contactor closed.', '2': 'Positive contactor closed.', '3': 'Both contactors open.', '4': 'Both contactors closed.', '7': 'Output clamped.'}
        messages = {}
        for key in keys:
            if key == 'X':
                for m in X_m_messages:
                    for n in X_n_messages:
                        messages[key, m, n] = X_m_messages[m] + ' ' + X_n_messages[n]
            elif key == 'A':
                for n in A_messages:
                    messages[key, n] = A_messages[n]
            elif key == 'C':
                for n in C_messages:
                    messages[key, n] = C_messages[n]
            elif key == 'H':
                for n in H_messages:
                    messages[key, n] = H_messages[n]
            elif key == 'M':
                for m in M_m_messages:
                    for n in M_n_messages: 
                        messages[key, m, n] = M_m_messages[m] + ' ' + M_n_messages[n]
            elif key == 'P':
                for m in P_m_messages:
                    for n in P_n_messages:
                        messages[key, m, n] = P_m_messages[m] + ' ' + P_n_messages[n]
        return messages
        
    def _status_decoder_(self, status):
        """
        This function is used to decodify the status string (obtained by the examine function) in a message that can be understood by users.
        
        Parameters:
            - status: string obtained by the examine_status function.
        """
        self.last_decodified_status = ""
        status_split = (status[:3], status[3:5], status[5:7], status[7:9], status[9:12], status[12:])
        for status in status_split:
            if len(status) == 2:
                key = status[0]
                n = status[1:]
                self.last_decodified_status = self.last_decodified_status + self.messages[key, n]
            else:
                key = status[0]
                m = status[1]
                n = status[2]
                self.last_decodified_status = self.last_decodified_status + self.messages[key, m, n]

    def set_non_persistent_current(self, current):
        """
        This command is used to set a new non persistent current set point in a sequence, automating the switch heating and field sweep sequence.
        """
        self.get_status()
        if not(self.last_queried_status[8] == '1'):
            self.get_current_set_point_reading()
            self.get_persistent_current_reading()
            if not self.current_set_point == self.persistent_current:
                self.set_target_current(self.persistent_current)
            if not(self.last_queried_status[4] == '1'):
                self.set_activity(hold = False, to_set_point = True)
                self.get_status()
                while not (self.last_queried_status[11] == '0'):
                    time.sleep(1)
                    self.get_status()
            self.set_switch_heater(opened = True)
            time.sleep(20)
        self.set_target_current(current)
        self.get_status()
        while not (self.last_queried_status[11] == '0'):
            time.sleep(1)
            self.get_status()

    def set_persistent_current(self, current):
        """
        This command is used to set a new persistent current set point in a sequence, automating the switch heating and field sweep sequence.
        """
        self.get_status()
        if not(self.last_queried_status[8] == '1'):
            self.get_current_set_point_reading()
            self.get_persistent_current_reading()
            if not self.current_set_point == self.persistent_current:
                self.set_target_current(self.persistent_current)
            if not(self.last_queried_status[4] == '1'):
                self.set_activity(hold = False, to_set_point = True)
                self.get_status()
                while not (self.last_queried_status[11] == '0'):
                    time.sleep(1)
                    self.get_status()
            self.set_switch_heater(opened = True)
            time.sleep(20)
        self.set_target_current(current)
        self.get_status()
        while not (self.last_queried_status[11] == '0'):
            time.sleep(1)
            self.get_status()
        self.set_switch_heater(opened = False)
        time.sleep(20)
        self.set_activity(hold = False, to_zero = True)

    def set_non_persistent_field(self, field):
        """
        This command is used to set a new non persistent field set point in a sequence, automating the switch heating and field sweep sequence.
        """
        self.get_status()
        if not(self.last_queried_status[8] == '1'):
            self.get_field_set_point_reading()
            self.get_persistent_field_reading()
            if not self.field_set_point == self.persistent_field:
                self.set_target_field(self.persistent_field)
            if not(self.last_queried_status[4] == '1'):
                self.set_activity(hold = False, to_set_point = True)
                self.get_status()
                while not (self.last_queried_status[11] == '0'):
                    time.sleep(1)
                    self.get_status()
            self.set_switch_heater(opened = True)
            time.sleep(20)
        self.set_target_field(field)
        self.get_status()
        while not (self.last_queried_status[11] == '0'):
            time.sleep(1)
            self.get_status()

    def set_persistent_field(self, current):
        """
        This command is used to set a new persistent field set point in a sequence, automating the switch heating and field sweep sequence.
        """
        self.get_status()
        if not(self.last_queried_status[8] == '1'):
            self.get_field_set_point_reading()
            self.get_persistent_field_reading()
            if not self.field_set_point == self.persistent_field:
                self.set_target_field(self.persistent_field)
            if not(self.last_queried_status[4] == '1'):
                self.set_activity(hold = False, to_set_point = True)
                self.get_status()
                while not (self.last_queried_status[11] == '0'):
                    time.sleep(1)
                    self.get_status()
            self.set_switch_heater(opened = True)
            time.sleep(20)
        self.set_target_field(field)
        self.get_status()
        while not (self.last_queried_status[11] == '0'):
            time.sleep(1)
            self.get_status()
        self.set_switch_heater(opened = False)
        time.sleep(20)
        self.set_activity(hold = False, to_zero = True)

    def close(self):
        """
        This function is used to put the IPS in a safe state, in which the ILM can be used in LOCAL mode before cutting the link between controller and instrument.
        """
        self.set_switch_heater(opened=False)
        self.set_activity(hold=False, clamped=True)
        self._general_close_()