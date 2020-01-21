import Errors

class Cryostat():
    """
    This class is a wrapper of functions common to all the components of the Oxford MagLab2000 system in use at INRiM.
    """
    def __init__(self, manager_int, GPIB_adress_int = None, read_terminator_int = 'CR', write_terminator_int = 'CR', ISOBUS_master_int = False, ISOBUS_linked_int = False, ISOBUS_adress_int = None):
        """
        This function is used to initialize an object corresponding to one of the Oxford MagLab2000 components.
        
        Parameters:
            - manager_int: an istance of the Manager class;
            - GPIB_adress_int: the correct GPIB adress for the adressed instrument;
            - read_terminator_int: parameter used to set the appropriate read terminator for the instrument. Available values are 'CR' ('\r' only) or 'CRLF' ('\r\n' combination).
                All the other possible combination (None, 'LF' ['\n'] and 'LFCR' ['\n\r' combination]) are not used and will rise an error indicating this;
            - write_terminator_int: parameter used to set the appropriate write terminator for the instrument. Available values are 'CR' ('\r' only) or 'CRLF' ('\r\n' combination)
                as selected and set by users with the define_communication_protocol commands instrument specific commands. All the other possible combination (None, 'LF' ['\n']
                and 'LFCR' ['\n\r' combination]) are not used and will rise an error indicating this;
            - ISOBUS_master_int: if set to True, the instrument must be treated as an ISOBUS master, so there must be other Oxford instruments linked by ISOBUS to
                the ISOBUS master instrument;
            - ISOBUS_linked_int: if set to True, the instrument is linked by ISOBUS to an ISOBUS master, that is then linked by GPIB to a PC controller;
            - ISOBUS_adress_int: if ISOBUS_linked is set to True, this parameter is used to set a single digit number from 1 to 8 that gives the correct ISOBUS adress for the
                ISOBUS linked instrument.
        """
        try:
            if 'Manager' in str(type(manager_int)):
                self.manager = manager_int
            else:
                raise Errors.InvalidManagerError
        except Errors.InvalidManagerError as error:
            error.error_handler()
            raise
        self.instrument = self.manager.open_instrument(GPIB_adress_int)
        if ISOBUS_master_int:
            self.buffer_radix = '@0'
        elif ISOBUS_linked_int:
            self.buffer_radix = '@{0:G}'.format(ISOBUS_adress_int)
        else:
            self.buffer_radix = ''
        try:
            if read_terminator_int == 'CR' or read_terminator_int == 'CRLF':
                self.instrument.read_termination = '\r'
            else:
                raise Errors.CryostatWrongReadTerminator(read_terminator_int)
        except Errors.CryostatWrongReadTerminator as error:
            error.error_handler()
            raise
        try:
            if write_terminator_int == 'CR' or write_terminator_int == 'CRLF':
                self.instrument.write_termination = '\r'
            else:
                raise Errors.CryostatWrongWriteTerminator(write_terminator_int)
        except Errors.CryostatWrongWriteTerminator as error:
            error.error_handler()
            raise
        self.identity = None
        self.last_queried_status = None
        self.last_decodified_status = None
        self.last_RAM_dump = None
        
    """
    Oxford MagLab 2000 instruments common commands.
    
    The define communication protocol functions is not listed here because there are two of them with different parameters.
    """
        
    """
    Monitor commands
    """
        
    def set_control_mode(self, remote, locked):
        """
        Set the instrument in the appropriate control mode (local/remote) and the display lock (locked, unlocked).
        
        Parameters:
            - remote: if true, put the selected instrument in remote control (from PC with GPIB and/or ISOBUS);
            - locked: if true, locks the instrument control panel.
        """
        try:
            if remote:
                if locked:
                    string = self.instrument.query(self.buffer_radix + 'C1')
                else:
                    string = self.instrument.query(self.buffer_radix + 'C3')
            else:
                if locked:
                    string = self.instrument.query(self.buffer_radix + 'C0')
                else:
                    string = self.instrument.query(self.buffer_radix + 'C2')
            if '?' in string:
                if 'ILM' in self.identity:
                    raise Errors.LMNotResponding
                elif 'IPS' in self.identity:
                    raise Errors.PSNotResponding
                elif 'ITC' in self.identity:
                    raise Errors.TCNotResponding
        except (Errors.LMNotResponding, Errors.PSNotResponding, Errors.TCNotResponding) as error:
            error.error_handler()
            raise

    def set_system_commands_lock(self, unlock_key = 0):
        """
        This command, with the appropriate unlock key to decide the desired level of protection, unlocks all the systems commands.
        
        Parameters:
            - unlock_key: number that indicates which type of system command can be used. Allowed values are:
                - 0: All system commands disabled;
                - 1: '!' command allowed;
                - 1234: 'SLEEP' command issued;
                - 4321: 'WAKE UP' command issued;
                - 9999: 'Y' command unlocked;
        """
        try:
            if unlock_key >= 0 and unlock_key <= 9999:
                string = self.instrument.query(self.buffer_radix + 'U{0:G}'.format(unlock_key))
                if '?' in string:
                    if 'ILM' in self.identity:
                        raise Errors.LMNotResponding
                    elif 'IPS' in self.identity:
                        raise Errors.PSNotResponding
                    elif 'ITC' in self.identity:
                        raise Errors.TCNotResponding
            else:
                raise Errors.CryostatIncorrectUnlockKey(unlock_key)
        except (Errors.LMNotResponding, Errors.PSNotResponding, Errors.TCNotResponding, Errors.CryostatIncorrectUnlockKey) as error:
            error.error_handler()
            raise

    def get_version_string(self):
        """
        Returns a message indicating the instrument type and firmware version number
        """
        try:
            self.identity = self.instrument.query(self.buffer_radix + 'V')
            if '?' in self.identity:
                if isinstance(self, OxfordILM):
                    raise Errors.LMNotResponding
                elif isinstance(self, OxfordIPS):
                    raise Errors.TCNotResponding
                elif isinstance(self, OxfordITC):
                    raise Errors.TCNotResponding
        except (Errors.LMNotResponding, Errors.PSNotResponding, Errors.TCNotResponding) as error:
            error.error_handler()
            raise
        
    def set_wait_time(self, wait_time):
        """
        Sets a delay interval between 2 characters sent by the instrument to a slow computer with no input buffering.
        
        Parameters:
            - delay_time: the time interval between each character sent by the instrument in milliseconds.
        """
        try:
            if delay_time >= 0 and delay_time <= 32767:
                string = self.instrument.query(self.buffer_radix + 'W{0:G}'.format(wait_time))
            else:
                raise Errors.CryostatIncorrectDelayTime(wait_time)
            if '?' in string:
                if 'ILM' in self.identity:
                    raise Errors.LMNotResponding
                elif 'IPS' in self.identity:
                    raise Errors.PSNotResponding
                elif 'ITC' in self.identity:
                    raise Errors.TCNotResponding
        except (Errors.CryostatIncorrectDelayTime(wait_time), Errors.LMNotResponding, Errors.PSNotResponding, Errors.TCNotResponding) as error:
            error.error_handler()
            raise

    def get_status_string(self):
        """
        This function is used to get the current Oxford Instrument status from the instrument.
        """
        try:
            self.last_queried_status = self.instrument.query(self.buffer_radix +'X')
            if '?' in self.last_queried_status:
                if 'ILM' in self.identity:
                    raise Errors.LMNotResponding
                elif 'IPS' in self.identity:
                    raise Errors.PSNotResponding
                elif 'ITC' in self.identity:
                    raise Errors.TCNotResponding
        except (Errors.LMNotResponding, Errors.PSNotResponding, Errors.TCNotResponding) as error:
            error.error_handler()
            raise
        
    """
    System commands
    All these commands must be unlocked previously by sending the appropriate Unlock command.
    """
        
    def _set_RAM_contents_(self):
        """
        This command is used to load contents in the RAM in binary via the serial interface."
        """
        try:
            string = self.instrument.query(self.buffer_radix +'Y8')
            if '?' in string:
                if 'ILM' in self.identity:
                    raise Errors.LMNotResponding
                elif 'IPS' in self.identity:
                    raise Errors.PSNotResponding
                elif 'ITC' in self.identity:
                    raise Errors.TCNotResponding
        except (Errors.LMNotResponding, Errors.PSNotResponding, Errors.TCNotResponding) as error:
            error.error_handler()
            raise
        
    def _get_RAM_contents_(self):
        """
        This command is used to dump contents in the RAM in binary via the serial interface."
        """
        try:
            self.last_RAM_dump = self.instrument.query(self.buffer_radix +'Z8')
            if '?' in string:
                if 'ILM' in self.identity:
                    raise Errors.LMNotResponding
                elif 'IPS' in self.identity:
                    raise Errors.PSNotResponding
                elif 'ITC' in self.identity:
                    raise Errors.TCNotResponding
        except (Errors.LMNotResponding, Errors.PSNotResponding, Errors.TCNotResponding) as error:
            error.error_handler()
            raise
        
    def _set_ISOBUS_adress_(self, adress):
        """
        This command is used to change the ISOBUS adress of one instrument when needed.
        
        Parameters:
            - adress: new ISOBUS adress to be set.
        """
        try:
            if adress >= 0 or adress <= 8:
                string = self.instrument.query(self.buffer_radix + '!{0:G}'.format(adress))
            if '?' in string:
                if 'ILM' in self.identity:
                    raise Errors.LMNotResponding
                elif 'IPS' in self.identity:
                    raise Errors.PSNotResponding
                elif 'ITC' in self.identity:
                    raise Errors.TCNotResponding
                self.buffer_radix = '@{0:G}'.format(adress)
            else:
                raise Errors.CryostatIncorrectISOBUSAdress(adress)
        except (Errors.CryostatIncorrectISOBUSAdress(adress), Errors.LMNotResponding, Errors.PSNotResponding, Errors.TCNotResponding) as error:
            error.error_handler()

    """
    Derived commands

    These commands are supplied in order to give the user a simpler way to make something in the scripts, by combining more commands in one function.
    """
    def _general_close_(self):
        self.set_control_mode(False, False)
        self.instrument.close()