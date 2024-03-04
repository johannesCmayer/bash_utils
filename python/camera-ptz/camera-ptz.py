"""
Control camera with a joystick
"""

# TODO: Try if quality improves when running in 4K mode with brio

import pygame
import time
from subprocess import run
from typing import Optional
import re
from time import sleep

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


def list_devices():
    run(["v4l2-ctl", "--list-devices"])


def set_ctrl(device_idx, cmd_string):
    run(["v4l2-ctl", "-d", str(device_idx), "--set-ctrl", cmd_string], check=True)


def autofocus(device_idx, autofocus : bool):
    value = 1 if autofocus else 0
    set_ctrl(device_idx, f"focus_automatic_continuous={value}")


def set_focus(device_idx, focus : int):
    set_ctrl(device_idx, f"focus_absolute={focus}")


def set_exposure(device_idx, exposure_time=250):
    set_ctrl(device_idx, f"auto_exposure=1")
    set_ctrl(device_idx, f"exposure_time_absolute={exposure_time}")


def camera_set_ptz(device_idx, pan, tilt, zoom):
    for cmd in [f"zoom_absolute={zoom}", f"tilt_absolute={tilt}", f"pan_absolute={pan}"]:
        set_ctrl(device_idx, cmd)


def setup_camera_for_whiteboard(device_idx):
    """
    Setup the camera optimized for whiteboard recording.
    It will be horrible quality when not filming a whiteboard!
    """
    autofocus(device_idx, False)
    set_focus(device_idx, 0)
    set_exposure(device_idx, 250)

    # Make the colors pop out more. This is the main thing that ruins
    # image quality.
    set_ctrl(device_idx, "saturation=215")
    # Setting the sharpness as high as possible helps making the text readable.
    set_ctrl(device_idx, "sharpness=255")
    # Setting the exposure helps make text more readable. Having brighter lights also helps and means
    # this value can be set lower.
    set_ctrl(device_idx, "exposure_time_absolute=700")

    set_ctrl(device_idx, "backlight_compensation=0")


@app.command()
def main(device_idx : Optional[int]=None, joystick_name_regex=None):
    if not device_idx:
        list_devices()
        print("Please provide the device index of one of these cameras.")
        exit(0)

    pygame.init()

    # Initialize the joystick module
    pygame.joystick.init()

    # Get the first joystick
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    setup_camera_for_whiteboard(device_idx)

    # Setup the starting default values
    pan = PAN_DEFAULT
    tilt = TILT_DEFAULT
    zoom = ZOOM_DEFAULT

    prev_zoom_ax_alt = zoom
    force_alt_zoom = False
    force_zoom_out_mode = False
    saved_zoom = ZOOM_DEFAULT


    joysticks = {}
    active_joystick = None

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

                if event.type == pygame.JOYDEVICEADDED:
                    # This event will be generated when the program starts for every
                    # joystick, filling up the list without needing to create them manually.
                    joy = pygame.joystick.Joystick(event.device_index)
                    joysticks[joy.get_instance_id()] = joy
                    print(f"Joystick {joy.get_instance_id()} connencted")
                    print(f"  Name: {joy.get_name()}")
                    print(f"  GUID: {joy.get_guid()}")

                if event.type == pygame.JOYDEVICEREMOVED:
                    print(f"Joystick {event.instance_id} disconnected")
                    print(f"  Name: {joysticks[event.instance_id].get_name()}")
                    print(f"  GUID: {joysticks[event.instance_id].get_guid()}")
                    del joysticks[event.instance_id]

        if not active_joystick:
            if joystick_name_regex:
                selected_joysticks = {k: j for k,j in joysticks.items() if re.search(joystick_name_regex, j.get_name())}
                print(f'Using Regex to select on name: {joystick_name_regex}')
            else:
                print('Using All')
                selected_joysticks = joysticks

            if len(selected_joysticks) > 1:
                print("Could not select a unique joystick. Please use a regex to select (see help).")
                for idx, joy in selected_joysticks.items():
                    print("Index:", idx)
                    print("  Name:", joy.get_name())
                    print("  GUID:", joy.get_guid())
                exit(1)
            elif len(selected_joysticks) == 1:
                active_joystick_idx, active_joystick = list(selected_joysticks.items())[0]
                print(f"Set Joystick {active_joystick_idx} as active:")
                print(f"  Name: {active_joystick.get_name()}")
                print(f"  GUID: {active_joystick.get_guid()}")
            elif len(selected_joysticks) == 0:
                print(selected_joysticks)
                print("No matching Joystick found. Waiting for matching joystick to become available.\r", end="")
                sleep(0.5)
                continue

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

        print("Axis:", f"PAN:{pan_ax:.1f}", f"TILT:{tilt_ax:.1f}", f"ZOOM:{zoom_ax:.1f}", f"ZOOM_ABS:{zoom_ax_alt:.1f}""    ", "PTZ:", f"{pan:.1f}", f"{tilt:.1f}", f"{zoom:.1f}", end='\r')
        camera_set_ptz(device_idx, pan, tilt, zoom)

        prev_zoom_ax_alt = zoom_ax_alt

        # Throttle the loop to save CPU usage
        time.sleep(0.01)

if __name__ == "__main__":
    app()
