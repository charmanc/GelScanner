import sys
import threading

import dearpygui.dearpygui as dpg # Import DearPyGui for GUI creation and control

from LinearStage import linearStage # Import the linearStage class to control the linear stage device
from Spectrometer import spectrometer # Import the spectrometer class to measure spectra

import numpy as np
from datetime import datetime
import time # Import time module for handling sleep between measurements
import glob  # Import glob to check for existing files



# Instantiate the linearStage class to control the linear stage device
LS = linearStage()
LS.connect_and_start()


# Instantiate the spectrometer class with a default integration time of 1 second (1e6 microseconds)
integration_time = 1e6
S = spectrometer(integration_time)
S.connect()

def update_data():
    """
    Continuously updates the Wavelength and Intensity values for the plot.
    The function keeps updating the plot data for each new measurement taken by the spectrometer.
    """

    scan_count = 0

    while True:
        S.measure() # Measure and update the wavelengths and intensities
        scan_count+=1
        # Update the plot with new wavelength and intensity data
        dpg.set_value('series_data', [S.wavelengths, S.intensities]) # set the intensity and wavelength values to the plot
        dpg.set_value('current_scan', scan_count) # Update scan count display
        dpg.fit_axis_data(axis='x_axis') # Fit the x-axis data to the current wavelengths
        dpg.fit_axis_data(axis='y_axis') # Fit the y-axis data to the current intensities


# Global variable to stop the scan when necessary
stop_all = None


def measure():
    """
    Performs the measurement process by moving the linear stage and taking measurements at each step.

    - Uses values entered by the user for the start, stop, and step size of the stage movement.
    - At each position, the spectrometer measures the wavelength and intensity values.
    - Data is optionally saved to files, and the measurement can be interrupted by setting stop_all to True.
    """
    # Retrieve user inputs for the scan range and step size
    _start, _stop, _step = map(float, (dpg.get_value(Start), dpg.get_value(Stop), dpg.get_value(Step)))
    print('Start: ', _start, 'Stop: ', _stop, 'Step: ', _step)
    _save = dpg.get_value(Save)
    print('Save: ', _save)
    global stop_all # Declare the global variable stop_all for controlling the scan

    pos = [] # List to store position data
    wave = None # Placeholder for wavelength data
    ints = [] # List to store intensity data

    for i in np.arange(_start, _stop + _step, _step):
        # Move the linear stage to the next position
        LS.move(i, wait=True)
        pos.append(i)
        # at each step of the stage, measure the wavelength and intensities (which is updated from the update function continuosly)
        time.sleep(integration_time*1e-6) # sleep as much as the integration time so that it is ensured that the measurement is done at the next positon!!
        ints.append(S.intensities) # Store the intensity measurement
        wave = S.wavelengths # Store the wavelengths measured

        if stop_all: # Check if the scan should be stopped
            print('Measurement is stopped!')
            break
    print('Measurement is complete!')

    if _save:
        now = datetime.now().strftime("%d.%m.%Y-%H:%M") # Get the current date and time
        header = (f'integration time [microseconds] = {integration_time}' +
                  f'\ndate-time = {now}' +
                  f'\nstart = {_start}, stop = {_stop}, step= {_step}')
        f_name = dpg.get_value(filename)

        # Prevent overwriting by checking if the file already exists
        counter = 1
        while glob.glob(f'./measurements/*{f_name}*') != []: # Check if filename exists
            f_name = f_name + f'_({str(counter)})'
            counter +=1
        # Save data to text files
        np.savetxt(fname='./measurements/' + f_name + '-data_pos.txt', X=pos, delimiter=' ', header=header, fmt='%.2f') # up to 2 decimals and float
        np.savetxt(fname='./measurements/' + f_name + '-data_w.txt', X=wave, delimiter=' ', header=header)
        np.savetxt(fname='./measurements/' + f_name + '-data.txt', X=ints, delimiter=' ', header=header)
        # np.savetxt(fname='./measurements/' + dpg.get_value(filename) + '-data.txt', X=all_data, delimiter=' ', header='')

# for reading paul's data
# def load_data_file(filename):
#     data = np.loadtxt(filename)
#     comments = []
#     with open(filename) as file:
#         line = file.readline()
#         while line.startswith('#'):
#             comments.append(line)
#             line = file.readline()
def run_measure_thread(): # so that the main program becomes responsive to stop the measurement when pressed!
    """
    Starts the measurement in a separate thread so that the GUI remains responsive.
    """
    global stop_all
    stop_all = False # Reset the stop flag
    measure_thread = threading.Thread(target = measure) # Create a new thread for the measurement process
    measure_thread.start() # Start the measurement thread

def stop_everything():
    """
    Stops the measurement and all movements of the linear stage by setting stop_all to True.
    Also stops the linear stage immediately.
    """
    # stopping by global stop_all for wait = True moves
    global stop_all
    stop_all = True # Set stop_all to True to interrupt the measurement
    LS.stop() # Stop the linear stage movement



def update_position():
    """
    Continuously updates the position of the linear stage.
    Displays the current horizontal and vertical positions in the GUI.
    """
    while True:
        # Get the current position of the horizontal and vertical axes
        h = round(LS.current_position['1'],2)
        v = round(LS.current_position['2'],2)
        # Update the position display on the GUI
        dpg.set_value(item = 'drag_point_location',value= [h,v])
        dpg.set_value(item = horizontal_text, value = f'Horizontal: {h}')
        dpg.set_value(item = vertical_text, value = f'Vertical: {v}')

def move_to_input(sender, app_data, user_data):
    """
    Moves the linear stage to the input position entered by the user for horizontal or vertical axes.
    """
    if sender == 'horizontal':
        horizontal = float(dpg.get_value(H))
        LS.move(horizontal, '1', wait=False) # Move the horizontal axis to the specified position
    else:
        vertical = float(dpg.get_value(V))
        LS.move(vertical, '2', wait=False) # Move the vertical axis to the specified position

def update_integration_time():
    """
    Updates the integration time of the spectrometer based on the user input.
    """
    global integration_time
    integration_time = float(dpg.get_value(int_T)) # Read the integration time from input
    S.set_integration_time(integration_time) # Update the spectrometer's integration time
    print(f'Integration Time is updated to {integration_time} microseconds')

def move_to_click(sender, app_data, user_data):
    """
    Moves the linear stage to the clicked position on the stage position plot.
    """
    h, v = dpg.get_plot_mouse_pos()
    h = round(h, 1)
    v = round(v, 1)
    LS.move(h, '1', wait=False) # Move to the horizontal position
    LS.move(v, '2', wait=False) # Move to the vertical position


# Set up the DearPyGui context and create the main window
dpg.create_context()

# Define the primary window with plot for spectrometer data and linear stage position
with (dpg.window(tag='Primary Window')):

    # Plot for displaying the spectrometer data (Wavelength vs Intensity)
    with dpg.plot(height=450, width=750, pos = [10,10], crosshairs=True): # otherwise due to the positioning of the parameters group, the user cannot interact with buttons/ inputs
        dpg.add_plot_axis(dpg.mvXAxis, label='Wavelength [nm]', tag='x_axis')
        dpg.add_plot_axis(dpg.mvYAxis, label='Counts [a.u]', tag='y_axis')
        dpg.add_line_series([], [], parent='y_axis', tag='series_data')
    
    # Group for parameters and inputs
    with dpg.group(pos = [10,470]):
        
        # Input for Integration Time
        with dpg.group(horizontal=True):
            dpg.add_text(r'Integration Time [microseconds]:')
            int_T = dpg.add_input_text(default_value= "{:.0e}".format(integration_time),
                                       on_enter=True,
                                       callback= update_integration_time,
                                       width=75)
        
        # Filename and Save checkbox
        with dpg.group(horizontal=True):
            dpg.add_text('Filename: ')
            filename = dpg.add_input_text(width = 150)
            Save = dpg.add_checkbox(label='Save', tag='save_checkbox', default_value=True)
        
        # Linear Stage Parameters (Start, Stop, Step)
        with dpg.group(horizontal=True, label='Linear Stage Parameters'):
            dpg.add_text('Start: ')
            Start = dpg.add_input_text( width=50, default_value= 100)
            dpg.add_text('Stop: ')
            Stop = dpg.add_input_text( width=50, default_value= 125)
            dpg.add_text('Step: ')
            Step = dpg.add_input_text( width=50, default_value= 0.5)

        # Start Scan and Stop buttons
        with dpg.group(horizontal=True):
            dpg.add_button(label='Start Scan', tag='start_scan', callback= run_measure_thread)
            dpg.add_button(label='STOP', tag='stop_scan', callback=stop_everything)
            dpg.add_text(default_value='123', tag='current_scan')
    
    # Group for the stage position plot and moving the stages
    with dpg.group(pos = [500,450]): # compared to the width and height of the viewport!
        with dpg.plot(height=260, width=260, crosshairs=True, label="Stage Position", tag='stage_position'):
            x_axis_stage = dpg.add_plot_axis(dpg.mvXAxis, label="Horizontal", invert=True)
            y_axis_stage = dpg.add_plot_axis(dpg.mvYAxis, label="Vertical")
            dpg.set_axis_limits(x_axis_stage,  0,  200)
            dpg.set_axis_limits(y_axis_stage,  0,  200)
            dpg.add_drag_point(label="Stage",
                               tag="drag_point_location")
        
        # Inputs for moving the stage
        with dpg.group(horizontal=True):
            with dpg.group():
                horizontal_text = dpg.add_text()
                with dpg.group(horizontal=True):
                    dpg.add_text('Move to: ') # a way to put the text before the input position!
                    H = dpg.add_input_text(tag= 'horizontal',
                                       width=50, on_enter=True, # only runs when pressed on enter
                                       callback=move_to_input)
            with dpg.group():
                vertical_text = dpg.add_text()
                with dpg.group(horizontal=True):
                    dpg.add_text('Move to: ')
                    V = dpg.add_input_text(tag = 'vertical',
                                       width=50, on_enter=True,
                                       callback=move_to_input)

# Item handler registry for clicking on the stage plot to move the stage
with dpg.item_handler_registry(tag="widget_handler") as handler:
    dpg.add_item_clicked_handler(callback=move_to_click)

dpg.bind_item_handler_registry("stage_position", "widget_handler")

# Setup and start the DearPyGui viewport and GUI loop
dpg.create_viewport(title='GelScanner', width=800, height=800)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window('Primary Window', True)

# Start background threads for updating data and stage position
update_background_data = threading.Thread(target=update_data).start() # run the function and keep on executing, while the rest is still responsive!
update_linearStage_position = threading.Thread(target=update_position).start()

# Start the DearPyGui application
dpg.start_dearpygui()
dpg.destroy_context()
