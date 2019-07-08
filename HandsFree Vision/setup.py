"""
Setup methods for the hand segmentation process.
Author: Benned Hedegaard
Created: 7/4/2019
Last revised: 7/4/2019
"""
from picamera import PiCamera
from time import sleep
import numpy as np
from scipy.misc import imsave

def setupCamera(resolution=(640,400)):
    # Returns a camera with specified settings.
    camera = PiCamera() # Instance of the main class of picamera.
    camera.rotation = 180 # Rotates image so it's right-side up.
    camera.hflip = True # Horizontal flip.
    camera.resolution = resolution
    # Need 15 framerate to use maximum resolution.
    if resolution[0] == 2592 and resolution[1] == 1944:
        camera.framerate = 15
    return camera

def preview(camera, seconds=2):
    camera.start_preview(alpha=225) # alpha adjusts transparency 0-255
    sleep(seconds)
    camera.stop_preview()

def main():
    camera = setupCamera()
    while (True):
        instr = input("What should we do?\n* 1 - Adjust bounding boxes\n* 2 - Adjust resolution\n* 3 - Ready\n* q - Quit program\n")
        if instr == "q":
            print("Program terminated")
            break
        preview(camera)

if __name__ == "__main__":
    main()