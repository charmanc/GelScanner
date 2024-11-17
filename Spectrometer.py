import sys
from seabreeze.spectrometers import Spectrometer, list_devices
from LinearStage import linearStage
import pandas as pd
import time

class spectrometer:
    """
    A class to represent and interact with a spectrometer.

    Attributes:
    integration_time (int): Integration time for the spectrometer in microseconds.
    spec (Spectrometer): The spectrometer object used to measure the spectrum.
    wavelengths (list): The wavelengths returned from the spectrometer.
    intensities (list): The intensity values corresponding to the wavelengths.

    Methods:
    connect(): Connects to the first available spectrometer and sets its integration time.
    measure(normalize=False, method='max'): Measures the spectrum and optionally normalizes the intensities.
    set_integration_time(int_T): Sets a new integration time for the spectrometer.
    """
    def __init__(self, integration_time=100000):
        """
        Initializes the spectrometer object.

        Args:
        integration_time (int): The integration time in microseconds (default is 100000 (0.1 seconds)).
        """
        self.integration_time = integration_time
        self.spec = None # Placeholder for the Spectrometer object
        self.wavelengths = None # Placeholder for the wavelengths measured
        self.intensities = None # Placeholder for the intensity values measured
        # if self.spec is not None:
        #     self.wavelengths = self.spec.wavelengths() # returns in an array, in nm
        #     self.intensities = self.spec.intensities() # in a.u
        #     # Pixels at the start and end of the array might not be optically active so interpret their returned measurements with care.!!
    def connect(self):
         """
        Connects to the first available spectrometer and sets its integration time.

        If no spectrometer is found, the program exits with an error message.
        """
        try:
            # Connect to the first available spectrometer and set the integration time
            self.spec = Spectrometer.from_first_available()
            self.spec.integration_time_micros(self.integration_time) # Set integration time in microseconds
            print(f'Connected to {self.spec}') # Notify that the connection was successful
            self.wavelengths = self.spec.wavelengths() # Fetch the wavelength range from the spectrometer
        except:
            print('No connected spectrometer is found!')
            sys.exit()  # Exit the program if no spectrometer is found

    def measure(self, normalize = False, method = 'max'):
         """
        Measures the spectrum from the connected spectrometer.

        Args:
        normalize (bool): Whether to normalize the intensity values (default is False).
        method (str): The method used for normalization ('max' or 'sum') (default is 'max').

        Sets:
        intensities (list): The raw or normalized intensity values measured by the spectrometer.
        """
        wavelengths, intensities = self.spec.spectrum() # Get the spectrum (wavelengths and intensities)
        # Normalize the intensities if required
        if normalize:
            if method == 'max':
                normalized_intensity = intensities / max(intensities) # Normalize by maximum intensity

            if method == 'sum':
                normalized_intensity = intensities / sum(intensities) # Normalize by the sum of intensities
            self.intensities = normalized_intensity
        else:
            self.intensities = intensities # Use raw intensities without normalization

        # return df
    def set_integration_time(self, int_T):
         """
        Sets the integration time for the spectrometer.

        Args:
        int_T (int): The integration time in microseconds.
        """
        self.spec.integration_time_micros(int_T) # Set the new integration time
        self.integration_time = int_T # Update the integration time attribute
