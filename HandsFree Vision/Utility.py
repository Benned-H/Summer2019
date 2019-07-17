"""
All the miscellaneous functions needed
for the entire hand segmentation workflow.

Author: Benned Hedegaard
Last Revised: 7/17/2019
"""
from picamera import PiCamera
from time import sleep
import numpy as np
import PIL.Image

def setupCamera(resolution=(640,416)):
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
    
def previewText(camera,text,seconds=2):
    save_text = camera.annotate_text
    camera.annotate_text = text
    camera.start_preview(alpha=225) # alpha adjusts transparency 0-255
    sleep(seconds)
    camera.stop_preview()
    camera.annotate_text = save_text

def addBox(mask,r,c,h,w):
    """Adds a red box to the given mask at [r,c]
    with height h and width w."""
    if w < 2 or h < 2:
        print("Invalid input: Box dimension < 2.")
        return mask
    if r < 0 or r >= mask.shape[0] or r + h >= mask.shape[0]:
        print("Invalid input: Row out of bounds.")
        return mask
    if c < 0 or c >= mask.shape[1] or c + w >= mask.shape[1]:
        print("Invalid input: Column out of bounds.")
        return mask
    
    pixel_val = [255,0,0,255]
    print(mask.shape)
    mask[r,c:c+w] = pixel_val # Top side.
    mask[r+1,c:c+w] = pixel_val
    mask[r+h,c:c+w] = pixel_val # Bottom side.
    mask[r+h-1,c:c+w] = pixel_val
    mask[r:r+h,c] = pixel_val # Left side.
    mask[r:r+h,c+1] = pixel_val
    mask[r:r+h,c+w] = pixel_val # Right side.
    mask[r:r+h,c+w-1] = pixel_val
    return mask

def createMask(camera,r,c,h,w,seconds=2):
    res = camera.resolution # This will be columns by rows.
    mask = np.zeros((res[1],res[0],4), dtype=np.uint8)
    mask = addBox(mask,r,c,h,w)
    mask_img = PIL.Image.fromarray(mask)
    # mask_img.save("test.png")
    return mask_img

def showMask(camera,mask_img,seconds=2):
    camera.start_preview(alpha=225)
    o = camera.add_overlay(mask_img.tobytes(), size = mask_img.size,
                           layer = 3, alpha = 10)
    sleep(seconds)
    camera.stop_preview()
    camera.remove_overlay(o)