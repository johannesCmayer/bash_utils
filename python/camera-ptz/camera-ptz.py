"""
Control camera with a joystick
"""

import pygame
import time
from subprocess import run

DEVICE_IDX=5

def set_ctrl(device_idx, cmd_string):
    run(["v4l2-ctl", "-d", str(device_idx), "--set-ctrl", cmd_string], check=True)

def set_focus(device_idx, focus=0):
    """Disable automatic focus and set the focus"""
    set_ctrl(device_idx, "focus_automatic_continuous=0")
    set_ctrl(device_idx, f"focus_absolute={focus}")

def set_exposure(device_idx, exposure_time=250):
    set_ctrl(device_idx, f"auto_exposure=1")
    set_ctrl(device_idx, f"exposure_time_absolute={exposure_time}")

def camera_set_ptz(device_idx, pan, tilt, zoom):
    for cmd in [f"zoom_absolute={zoom}", f"tilt_absolute={tilt}", f"pan_absolute={pan}"]:
        set_ctrl(device_idx, cmd)

pygame.init()

# Initialize the joystick module
pygame.joystick.init()

# Get the first joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

set_focus(DEVICE_IDX)
set_exposure(DEVICE_IDX)

pan = 128
tilt = 128
zoom = 100

# Main loop
while True:
    # Process events
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True  # Flag that we are done so we exit this loop.

            if event.type == pygame.JOYBUTTONDOWN:
                print("Joystick button pressed.")
                if event.button == 0:
                    if joystick.rumble(0, 0.7, 500):
                        print(f"Rumble effect played on joystick {event.instance_id}")

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                # This event will be generated when the program starts for every
                # joystick, filling up the list without needing to create them manually.
                joystick = pygame.joystick.Joystick(event.device_index)
                print(f"New joystick {event.device_index} connected. Using this joystick now.")

            if event.type == pygame.JOYDEVICEREMOVED:
                print(f"Joystick {event.instance_id} disconnected, please connect a new joystick.")

    n_axes = joystick.get_numaxes()
    if n_axes < 3:
        print("We need a joystick with at least 3 axis!")
        exit(1)
    pan_ax  =  joystick.get_axis(0)
    tilt_ax = -joystick.get_axis(1)
    zoom_ax =  joystick.get_axis(2)

    DEADZONE = 0.1
 
    if abs(pan_ax) < DEADZONE:
        pan_ax = 0
    if abs(tilt_ax) < DEADZONE:
        tilt_ax = 0
    if abs(zoom_ax) < DEADZONE:
        zoom_ax = 0

    MIN_ZOOM = 100
    MAX_ZOOM = 500

    zoom_slowdown = (1 - (MIN_ZOOM - zoom) / (MAX_ZOOM - MIN_ZOOM))

    pan = max(-36000, min(36000,   pan  + pan_ax  * 5000))
    tilt = max(-36000, min(36000,  tilt + tilt_ax * 5000))
    zoom = max(MIN_ZOOM, min(MAX_ZOOM,     zoom + zoom_ax * 6))

    print("Axis:", pan_ax, tilt_ax, zoom_ax)
    print("PTZ:", pan, tilt, zoom)
    camera_set_ptz(DEVICE_IDX, pan, tilt, zoom)

    # Throttle the loop to save CPU usage
    time.sleep(0.01)

