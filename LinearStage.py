from pipython import GCSDevice, pitools, datarectools # configuration of data recording
# import sys
# Axis '1' is for horizontal movement, Axis '2' is for vertical movement
# These are the labels used to refer to the axes of the linear stage.

class linearStage:
     """
    A class to represent and control a linear stage device.

    Attributes:
    pidevice (GCSDevice): The GCSDevice object representing the linear stage hardware.
    range (dict): The valid movement range for each axis ('1' for horizontal, '2' for vertical).
    current_position (dict): The current position of each axis ('1' for horizontal, '2' for vertical).

    Methods:
    connect_and_start(): Connects to the linear stage device, initializes it, and sets the range and current position.
    get_pos(): Updates the current position of each axis.
    move(target, axis='2', wait=False): Moves the stage to the target position on the specified axis.
    stop(): Stops all movements immediately.
    """
    def __init__(self):
        """
        Initializes the linear stage object, preparing the GCSDevice and setting initial values.
        """
        self.pidevice = GCSDevice('C-843') # Initialize the GCSDevice for the linear stage (C-843 model)
        self.range = None # Placeholder for axis range, to be defined upon connection
        self.current_position = None # Placeholder for the current position of the axes

    def connect_and_start(self):
        """
        Connects to the linear stage device and initializes it.

        Establishes a connection via PCI and performs a startup process.
        Retrieves the range and current position for both horizontal and vertical axes.
        """
        self.pidevice.ConnectPciBoard(board=1)  # Connect to the PCI board (C-843 is connected via PCI)
        print(f'connected: {self.pidevice.qIDN().strip()}', '\n') # Print the device ID
        pitools.startup(self.pidevice, stages=['M-404.8PD', 'M-404.8PD'], refmodes='FRF') # Initialize the stages
        # Retrieve the range for each axis
        self.range = {'1': [self.pidevice.qTMN()['1'], self.pidevice.qTMX()['1']], 
                      '2': [self.pidevice.qTMN()['2'], self.pidevice.qTMX()['2']]}
        # Retrieve the current position for each axis
        
        self.current_position = {'1': self.pidevice.qPOS()['1'], '2': self.pidevice.qPOS()['2']}

    def get_pos(self):
        """
        Updates the current position of the linear stage for both axes.
        """
        # Retrieve and update the current positions for both axes
        self.current_position = {'1': self.pidevice.qPOS()['1'], '2': self.pidevice.qPOS()['2']}

    def move(self, target: float, axis = '2', wait=False): # default axis '2' is vertical axis
        """
        Moves the stage to a specified target position on a given axis.

        Args:
        target (float): The target position to move to (in the units used by the device).
        axis (str): The axis to move ('1' for horizontal, '2' for vertical, default is '2').
        wait (bool): If True, the function waits until the stage reaches the target position before continuing. Default is False.

        Returns:
        None: If the move is successful, updates the current position. If the target is out of range, prints an error message.
        """
        if target >= self.range[axis][0] and target <= self.range[axis][1]:
            # If 'wait' is True, wait for the move to complete
            if wait:
                pitools.moveandwait(self.pidevice, axes=axis , values=target)
            else:
                # Move without waiting for completion
                self.pidevice.MOV(axis, target) # doesnt wait until the linear stage reaches its target
            print('The axis {} is moved to position {:.2f}'.format(axis, target)) # Print the movement status
        else:
            # Print error if the target is out of range
            print('Target is out of LinearStage Range!')
            return None
        # Update the current position for the specified axis
        self.current_position[axis] = float(target)

    def stop(self):
        """
        Immediately stops all movements of the linear stage.
        """
        pitools.stopall(self.pidevice) # stops all the movements immediately

# record data? datarectools??