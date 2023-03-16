#!/usr/bin/python3
import rossros as rr
import logging

# logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)

#Class setup


""" Create buses for passing data """
# Initiate data and termination busses
position_bus = rr.Bus([0,0,0],"Position Bus")
color_bus = rr.Bus(None, "Detect Color")
roi_bus = rr.Bus(False, "ROI Bus")
start_pickup_bus = rr.Bus(False, "Start Pickup Bus")

bTerminate = rr.Bus(0, "Termination Bus")


""" Create P/PC/C """
# Reads Greyscale data
readLocation = rr.Producer(
    greyscale_sensor.read_greyscale_data,  # function that will generate data
    (position_bus, color_bus, roi_bus, start_pickup_bus),  # output data bus
    0.1,  # delay between data generation cycles
    bTerminate,  # bus to watch for termination signal
    "Read greyscale data")

#Controls steering
moveArm = rr.Consumer(
    greyscale_control.steer,  # function that will process data
    (position_bus, color_bus, roi_bus, start_pickup_bus),  # input data buses
    0.1,  # delay between data control cycles
    bTerminate,  # bus to watch for termination signal
    "Steering control")

""" Fourth Part: Create RossROS Timer objects """
# Make a timer (a special kind of producer) that turns on the termination
# bus when it triggers
terminationTimer = rr.Timer(
    bTerminate,  # Output data bus
    60,  # Duration
    0.2,  # Delay between checking for termination time
    bTerminate,  # Bus to check for termination signal
    "Termination timer")  # Name of this timer

""" Fifth Part: Concurrent execution """

# Create a list of producer-consumers to execute concurrently
producer_consumer_list = [
                          moveArm,
                          readLocation,
                          terminationTimer]

# Execute the list of producer-consumers concurrently
rr.runConcurrently(producer_consumer_list)
