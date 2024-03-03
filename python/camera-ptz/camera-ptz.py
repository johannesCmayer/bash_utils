"""
Control camera with a joystick
"""

# TODO: Try if quality improves when running in 4K mode with brio

import pygame
import time
from subprocess import run

import typer

app = typer.Typer()

# Hardcoded value for 4K Brio
PAN_SPEED = 5000
TILT_SPEED = 5000
ZOOM_SPEED = 10

MIN_ZOOM = 100
MAX_ZOOM = 500

# Overwirite the acutal max zoom, because quality degrades signifcantly when
# going much beyond 300 with Brio
MAX_ZOOM = 300

MIN_PAN  = -36000
MAX_PAN  =  36000
MIN_TILT = -36000
MAX_TILT =  36000

PAN_DEFAULT = 0
TILT_DEFAULT = 0
ZOOM_DEFAULT = 0

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

@app.command()
def main(device_index):
    pygame.init()

    # Initialize the joystick module
    pygame.joystick.init()

    # Get the first joystick
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    set_focus(device_index)
    set_exposure(device_index)

    # Setup the starting default values
    pan = PAN_DEFAULT
    tilt = TILT_DEFAULT
    zoom = ZOOM_DEFAULT

    prev_zoom_ax_alt = zoom
    force_alt_zoom = False
    force_zoom_out_mode = False
    saved_zoom = ZOOM_DEFAULT

    # Main loop
    while True:
        # Process events
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True  # Flag that we are done so we exit this loop.

                if event.type == pygame.JOYBUTTONDOWN:
                    print("Joystick button pressed.")
                    if event.button == 0:
                        pan = PAN_DEFAULT
                        tilt = TILT_DEFAULT
                        zoom = ZOOM_DEFAULT
                        if joystick.rumble(0, 0.7, 500):
                            print(f"Rumble effect played on joystick {event.instance_id}")
                    if event.button == 1:
                        force_alt_zoom = True

                    if event.button == 3:
                        force_zoom_out_mode = True
                        saved_zoom = zoom

                if event.type == pygame.JOYBUTTONUP:
                    if event.button == 3:
                        force_zoom_out_mode = False
                        zoom = saved_zoom

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
        zoom_ax_alt =  joystick.get_axis(3)

        DEADZONE = 0.1
     
        if abs(pan_ax) < DEADZONE:
            pan_ax = 0
        if abs(tilt_ax) < DEADZONE:
            tilt_ax = 0
        if abs(zoom_ax) < DEADZONE:
            zoom_ax = 0

        pan = max(MIN_PAN, min(MAX_PAN,   pan  + pan_ax  * PAN_SPEED))
        tilt = max(MIN_TILT, min(MAX_TILT,  tilt + tilt_ax * TILT_SPEED))

        zoom = max(MIN_ZOOM, min(MAX_ZOOM,     zoom + zoom_ax * ZOOM_SPEED))
        if prev_zoom_ax_alt != zoom_ax_alt or force_alt_zoom:
            zoom = MIN_ZOOM + (MAX_ZOOM - MIN_ZOOM) * (1 + zoom_ax_alt) / 2
            force_alt_zoom = False
        if force_zoom_out_mode:
            zoom = MIN_ZOOM

        print("Axis:", f"{pan_ax:.1f}", f"{tilt_ax:.1f}", f"{zoom_ax:.1f}", "    ", "PTZ:", f"{pan:.1f}", f"{tilt:.1f}", f"{zoom:.1f}", end='\r')
        camera_set_ptz(device_index, pan, tilt, zoom)

        prev_zoom_ax_alt = zoom_ax_alt

        # Throttle the loop to save CPU usage
        time.sleep(0.01)

if __name__ == "__main__":
    app()
