"""
All the miscellaneous functions needed
for the entire hand segmentation workflow.

Author: Benned Hedegaard
Last Revised: 7/15/2019
"""
from picamera import PiCamera
from time import sleep
import numpy as np
import PIL.Image

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

def createBox(h,w,border=1):
    rgba = np.zeros([h,w,4], dtype=np.uint8)

    # Fill in red outline
    rgba[0:border,:] = [255,0,0,255]
    rgba[h-border-1:h-1,:] = [255,0,0,255]
    rgba[:,0:border] = [255,0,0,255]
    rgba[:,w-border-1:w-1] = [255,0,0,255]
  
    return rgba
    
def test(camera):
    a = np.zeros((32,32,3), dtype=np.uint8)
    a[16,:,:] = 255
    a[:,16,:] = 255
    a_img = PIL.Image.fromarray(a)
    
    camera.start_preview(alpha=225)
    o = camera.add_overlay(a_img.tobytes(), size = a_img.size,
                           layer = 3, alpha = 60)
    sleep(2)
    camera.stop_preview()
    camera.remove_overlay(o)