from ..General import Cryostat,Errors

class OxfordILM(Cryostat.Cryostat):
    """
    This class is a wrapper used as a container of the function used to interface an Oxford Intelligent Level Meter with a PC employing a IEEE488 (GPIB) interface and/or,
    if equipped with the Oxford ISOBUS, also the Oxford ISOBUS interface.
    """
    def __init__(self, manager, GPIB_adress, read_terminator = 'CR', write_terminator = 'CR', ISOBUS_master = False, ISOBUS_linked = False, ISOBUS_adress = None, line_feed = False, ignore_low_LHe_level = False):
        """
        This function is used to initialize the object corresponding to the Oxford Intelligent Level Meter instrument.
        
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
            - line_feed: if set to true, the ILM will send a line feed character after each carriage return character;
            - ignore_low_LHe_level: if set to true, the PC will ignore a low level on the liquid helium channel (not to be used when helium is in the inner cryogenic vessel).
        """
        Cryostat.Cryostat.__init__(self, manager, GPIB_adress_int = GPIB_adress, read_terminator_int = read_terminator, write_terminator_int = write_terminator, ISOBUS_master_int = ISOBUS_master, ISOBUS_linked_int = ISOBUS_linked, ISOBUS_adress_int = ISOBUS_adress)
        self.get_version_string()
        self.set_control_mode(True, True)
        self.set_communication_protocol(line_feed)
        self.messages = self._messages_dictionary_()
        self.channel_1_level = None
        self.channel_2_level = None
        self.channel_3_level = None
        self.needle_valve_position = None
        self.ignore_low_LHe_level = ignore_low_LHe_level
        self.get_status()
        if not (self.last_queried_status[1] == '0'):
            self.get_channel_1_level_reading()
        else:
            self.channel_1_level = None
        if not (self.last_queried_status[2] == '0'):
            self.get_channel_2_level_reading()
        else:
            self.channel_2_level = None
        if not (self.last_queried_status[3] == '0'):
            self.get_channel_3_level_reading()
        else:
            self.channel_3_level = None
        self.get_needle_valve_position_reading()
                    
    """
    Monitor commands
    """

    def set_communication_protocol(self, line_feed):
        """
        Defines the communication protocol.
        
        Parameters:
            - line_feed: if set to true, the ILM will send a line feed character after each carriage return character.
        """
        try:
            if 'ILM' in self.identity:
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
    
    def get_channel_1_level_reading(self):
        """
        This function is used to query to the ILM the channel 1 level reading.
        """
        try:
            if 'ILM' in self.identity:
                self.get_status()
                if self.last_queried_status[1] == 0:
                    raise Errors.LMChannelNotUsed(1)
                elif self.last_queried_status[1] == 9:
                    raise Errors.LMErrorOnChannel(1)
                else:
                    string = self.instrument.query(self.buffer_radix + 'R1')[1:]
                    if '?' in string:
                        raise Errors.LMNotResponding
                    self.channel_1_level = float(string) / 10.
                if self.channel_1_level <= 20. and (self.last_queried_status[1] == '2' or self.last_queried_status[1] == '3') and not(self.ignore_low_LHe_level):
                    raise Errors.Low_LHe_level
                elif self.channel_1_level <= 10. and self.last_queried_status[1] == '1':
                    raise Errors.Low_LN2_level
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LMChannelNotUsed, Errors.LMErrorOnChannel, Errors.LMNotResponding, Errors.IncorrectInstrumentError, Errors.Low_LHe_level, Errors.Low_LN2_level) as error:
            error.error_handler()
            
    def get_channel_2_level_reading(self):
        """
        This function is used to query to the ILM the channel 2 level reading.
        """
        try:
            if 'ILM' in self.identity:
                self.get_status()
                if self.last_queried_status[2] == 0:
                    raise Errors.LMChannelNotUsed(2)
                elif self.last_queried_status[2] == 9:
                    raise Errors.LMErrorOnChannel(2)
                else:
                    string = self.instrument.query(self.buffer_radix + 'R2')[1:]
                    if '?' in string:
                        raise Errors.LMNotResponding
                    self.channel_2_level = float(string) / 10.
                if self.channel_2_level <= 20. and (self.last_queried_status[1] == '2' or self.last_queried_status[1] == '3') and not(self.ignore_low_LHe_level):
                    raise Errors.Low_LHe_level
                elif self.channel_2_level <= 10. and self.last_queried_status[1] == '1':
                    raise Errors.Low_LN2_level
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LMChannelNotUsed, Errors.LMErrorOnChannel, Errors.LMNotResponding, Errors.IncorrectInstrumentError, Errors.Low_LHe_level, Errors.Low_LN2_level) as error:
            error.error_handler()
            
    def get_channel_3_level_reading(self):
        """
        This function is used to query to the ILM the channel 3 level reading.
        """
        try:
            if 'ILM' in self.identity:
                self.get_status()
                if self.last_queried_status[3] == 0:
                    raise Errors.LMChannelNotUsed(3)
                elif self.last_queried_status[3] == 9:
                    raise Errors.LMErrorOnChannel(3)
                else:
                    string = self.instrument.query(self.buffer_radix + 'R3')[1:]
                    if '?' in string:
                        raise Errors.LMNotResponding
                    self.channel_3_level = float(string) / 10.
                if self.channel_3_level <= 20. and (self.last_queried_status[1] == '2' or self.last_queried_status[1] == '3') and not(self.ignore_low_LHe_level):
                    raise Errors.Low_LHe_level
                elif self.channel_3_level <= 10. and self.last_queried_status[1] == '1':
                    raise Errors.Low_LN2_level
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LMChannelNotUsed, Errors.LMErrorOnChannel, Errors.LMNotResponding, Errors.IncorrectInstrumentError, Errors.Low_LHe_level, Errors.Low_LN2_level) as error:
            error.error_handler()
            
    def get_needle_valve_position_reading(self):
        """
        This function is used to query to the ILM the needle valve position.
        """
        try:
            if 'ILM' in self.identity:
                string = self.instrument.query(self.buffer_radix + 'R10')[1:]
                if '?' in string:
                    raise Errors.LMNotResponding
                self.needle_valve_position = float(string) / 10.
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LMNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler()

    def get_status(self):
        """
        This function is used to read the current ILM status from the instrument and to decodify it into a string comprehensible for the user.
        """
        try:
            if 'ILM' in self.identity:
                self.get_status_string()
                if '?' in self.last_queried_status:
                    raise Errors.LMNotResponding
                self._status_decoder_(self.last_queried_status)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LMNotResponding, Errors.IncorrectInstrumentError) as error:
            error.error_handler()
            
    """
    Control commands
    """
    
    def set_channel_1_level_display(self):
        """
        This function is used to display the current channel 1 level reading on the channel 1 display.
        """
        try:
            if 'ILM' in self.identity:
                self.instrument.query(self.buffer_radix + 'F1')
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler()
            
    def set_channel_2_level_display(self):
        """
        This function is used to display the current channel 2 level reading on the channel 1 display.
        """
        try:
            if 'ILM' in self.identity:
                self.instrument.query(self.buffer_radix + 'F2')
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler()
            
    def set_channel_3_level_display(self):
        """
        This function is used to display the current channel 3 level reading on the channel 1 display.
        """
        try:
            if 'ILM' in self.identity:
                self.instrument.query(self.buffer_radix + 'F3')
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler()
    
    def set_needle_valve_position_display(self):
        """
        This function is used to display the current needle valve position on the channel 1 display.
        """
        try:
            if 'ILM' in self.identity:
                self.instrument.query(self.buffer_radix + 'F10')
            else:
                raise Errors.IncorrectInstrumentError
        except Errors.IncorrectInstrumentError as error:
            error.error_handler()
            
    def set_needle_valve_position(self, position):
        """
        This function is used to set the (absolute) position of the needle valve stepper motor.
        """
        try:
            if 'ILM' in self.identity:
                self.instrument.query(self.buffer_radix + 'G{0:G}'.format(position*10))
                self.get_needle_valve_position_reading()
                if not(self.needle_valve_position == position):
                    raise Errors.LMNotResponding
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.IncorrectInstrumentError, Errors.LMNotResponding) as error:
            error.error_handler()
        
    def set_helium_channel_to_slow(self, channel_number):
        """
        This function is used to set the selected channel (channel_number) in slow sampling rate (for helium level channels only).
        
        Parameters:
            - channel_number: the (helium level) channel the user wants to set in slow sampling rate.
        """
        try:
            if 'ILM' in self.identity:
                if channel_number >= 1 and channel_number <= 3:
                    if self.last_queried_status[channel_number] == '2' or self.last_queried_status[channel_number] == '3': 
                        self.instrument.query(self.buffer_radix + 'S{0:G}'.format(channel_number))
                        self.get_status()
                        if (channel_number == 1 and bin(int(self.last_queried_status[5:7],16))[2:].zfill(8)[5] == '0') or (channel_number == 2 and bin(int(self.last_queried_status[7:9],16))[2:].zfill(8)[5] == '0') or (channel_number == 3 and bin(int(self.last_queried_status[9:11],16))[2:].zfill(8)[5] == '0'):
                            raise Errors.LMNotResponding
                    else:
                        raise Errors.LMNotHeliumChannel(channel_number)
                else:
                    raise Errors.LMIncorrectChannelNumber(channel_number)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LMNotResponding, Errors.IncorrectInstrumentError, Errors.LMNotHeliumChannel, Errors.LMIncorrectChannelNumber) as error:
            error.error_handler()
        
    def set_helium_channel_to_fast(self, channel_number):
        """
        This function is used to set the selected channel (channel_number) in fast sampling rate (for helium level channels only).

        Parameters:
            - channel_number: the (helium level) channel the user wants to set in fast sampling rate.
        """
        try:
            if 'ILM' in self.identity:
                if channel_number >= 1 and channel_number <= 3:
                    if self.last_queried_status[channel_number] == '2' or self.last_queried_status[channel_number] == '3': 
                        self.instrument.query(self.buffer_radix + 'T{0:G}'.format(channel_number))
                        self.get_status()
                        if channel_number == 1:
                            if bin(int(self.last_queried_status[5:7],16))[2:].zfill(8)[6] == '0':
                                raise Errors.LMNotResponding
                            self.get_channel_1_level_reading()
                        elif channel_number == 2:
                            if bin(int(self.last_queried_status[7:9],16))[2:].zfill(8)[6] == '0':
                                raise Errors.LMNotResponding
                            self.get_channel_2_level_reading()
                        else:
                            if bin(int(self.last_queried_status[9:11],16))[2:].zfill(8)[6] == '0':
                                raise Errors.LMNotResponding
                            self.get_channel_3_level_reading() 
                    else:
                        raise Errors.LMNotHeliumChannel(channel_number)
                else:
                    raise Errors.LMIncorrectChannelNumber(channel_number)
            else:
                raise Errors.IncorrectInstrumentError
        except (Errors.LMNotResponding, Errors.IncorrectInstrumentError, Errors.LMNotHeliumChannel, Errors.LMIncorrectChannelNumber) as error:
            error.error_handler()

    """
    Derived commands

    These commands are supplied in order to automating some of the tasks connected with the use of this class.
    """

    def _messages_dictionary_(self):
        """
        This function is used to create a dictionary of the possible messages given by the get_status function, in order to give them to the
        status_decoder function in order to translate the status string into a comprehensible message for the user.
        """
        keys = ('X', 'S', 'R')
        channel_1_messages = {'0': 'Channel 1 not in use.', '1': 'Channel 1 used for nitrogen level metering.', '2': 'Channel 1 used for pulsed helium level metering.', '3': 'Channel 1 used for continuous helium level metering.', '9': 'Error on channel 1.'}
        channel_2_messages = {'0': 'Channel 2 not in use.', '1': 'Channel 2 used for nitrogen level metering.', '2': 'Channel 2 used for pulsed helium level metering.', '3': 'Channel 2 used for continuous helium level metering.', '9': 'Error on channel 2.'}
        channel_3_messages = {'0': 'Channel 3 not in use.', '1': 'Channel 3 used for nitrogen level metering.', '2': 'Channel 3 used for pulsed helium level metering.', '3': 'Channel 3 used for continuous helium level metering.', '9': 'Error on channel 3.'}
        channels = {'1': 'Channel 1', '2': 'Channel 2', '3': 'Channel 3'}
        S_bit_0_messages = {'0': '', '1': 'CURRENT FLOWING in helium probe.'}
        S_bit_1_messages = {'0': '', '1': 'Helium probe in FAST rate.'}
        S_bit_2_messages = {'0': '', '1': 'Helium probe in SLOW rate.'}
        S_bit_3_4_messages = {'00': 'END FILLING.', '01': 'NOT FILLING.', '10': 'FILLING.', '11': 'START FILLING.'}
        S_bit_5_messages = {'0': '', '1': 'LOW STATE is active.'}
        S_bit_6_messages = {'0': '', '1': 'ALARM requested.'}
        S_bit_7_messages = {'0': '', '1': 'PRE-PULSE CURRENT is flowing.'}
        R_bit_0_messages = {'0': '', '1': 'In SHUT DOWN state.'}
        R_bit_1_messages = {'0': '', '1': 'Alarm is SOUNDING.'}
        R_bit_2_messages = {'0': '', '1': 'In ALARM state.'}
        R_bit_3_messages = {'0': '', '1': 'Alarm SILENCING is prohibited.'}
        R_bit_4_messages = {'0': '', '1': 'RELAY 1 is active.'}
        R_bit_5_messages = {'0': '', '1': 'RELAY 2 is active.'}
        R_bit_6_messages = {'0': '', '1': 'RELAY 3 is active.'}
        R_bit_7_messages = {'0': '', '1': 'RELAY 4 is active.'}
        messages = {}
        for key in keys:
            if key == 'X':
                for i in channel_1_messages:
                    for j in channel_2_messages:
                        for k in channel_3_messages:
                                messages[key, i, j, k] = channel_1_messages[i] + ' ' + channel_2_messages[j] + ' ' + channel_3_messages[k] + '\n'
            elif key == 'S':
                for channel in channels:
                    for i in S_bit_0_messages:
                        for j in S_bit_1_messages:
                            for k in S_bit_2_messages:
                                for l in S_bit_3_4_messages:
                                    for m in S_bit_5_messages:
                                        for n in S_bit_6_messages:
                                            for o in S_bit_7_messages:
                                                messages[key, channel, i, j, k, l, m, n, o] = channels[channel] + ' ' + S_bit_0_messages[i] + ' ' + S_bit_1_messages[j] + ' ' +  S_bit_2_messages[k] + ' ' + S_bit_3_4_messages[l] + ' ' + S_bit_5_messages[m] + ' ' + S_bit_6_messages[n] + ' ' + S_bit_7_messages[o] + '\n'
            elif key == 'R':
                for i in R_bit_0_messages:
                    for j in R_bit_1_messages:
                        for k in R_bit_2_messages:
                            for l in R_bit_3_messages:
                                for m in R_bit_4_messages:
                                    for n in R_bit_5_messages:
                                        for o in R_bit_6_messages:
                                            for p in R_bit_7_messages:
                                                messages[key, i, j, k, l, m, n, o, p] = R_bit_0_messages[i] + ' ' + R_bit_1_messages[j] + ' ' +  R_bit_2_messages[k] + ' ' + R_bit_3_messages[l] + ' ' + R_bit_4_messages[m] + ' ' + R_bit_5_messages[n] + ' ' + R_bit_6_messages[o] + ' ' + R_bit_7_messages[p]
        return messages
        
    def _status_decoder_(self, status):
        """
        This function is used to decodify the status string (obtained by the examine function) in a message that can be understood by users.
        
        Parameters:
            - status: string obtained by the get_status function.
        """
        self.last_decodified_status = ""
        status_split = (status[:4], status[4:11], status[11:])
        for status in status_split:
            if len(status) == 3:
                key = status[0]
                (bit_7, bit_6, bit_5, bit_4, bit_3, bit_2, bit_1, bit_0) = bin(int(status[1:],16))[2:].zfill(8)
                self.last_decodified_status = self.last_decodified_status + self.messages[key, bit_0, bit_1, bit_2, bit_3, bit_4, bit_5, bit_6, bit_7]
            elif len(status) == 4:
                key = status[0]
                (channel_1, channel_2, channel_3) = status[1:]
                self.last_decodified_status = self.last_decodified_status + self.messages[key, channel_1, channel_2, channel_3]
            else:
                key = status[0]
                channels = ('1', '2', '3')
                channel_statuses = (bin(int(status[1:3],16))[2:].zfill(8), bin(int(status[3:5],16))[2:].zfill(8), bin(int(status[5:],16))[2:].zfill(8))
                for i in channels:
                    (bit_7, bit_6, bit_5, bits_43, bit_2, bit_1, bit_0) = (channel_statuses[int(i) - 1][0], channel_statuses[int(i) - 1][1], channel_statuses[int(i) - 1][2], channel_statuses[int(i) - 1][4] + channel_statuses[int(i) - 1][3], channel_statuses[int(i) - 1][5], channel_statuses[int(i) - 1][6], channel_statuses[int(i) - 1][7])
                    self.last_decodified_status = self.last_decodified_status + self.messages[key, i, bit_0, bit_1, bit_2, bits_43, bit_5, bit_6, bit_7]
                    if i != channels[-1]:
                        self.last_decodified_status = self.last_decodified_status

    def close(self):
        """
        This function is used to put the ILM in a safe state, in which the ILM can be used in LOCAL mode before cutting the link between controller and instrument.
        """
        self.set_needle_valve_position(0)
        self._general_close_()